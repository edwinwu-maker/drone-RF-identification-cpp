---
type: note
tags: [cpp, drone-rfa, implementation]
---

# DroneRFa CPP 图生成思路

本文说明如何基于 `DroneRFa` 数据集将无人机 RF IQ 信号转换为可视化的 `CPP (cyclic-paw-print)` 图。这里假设一张 CPP 图对应 $10^6$ 个 IQ 点，输出可用于 `ResNet-18` 等 CNN 模型的 $224\times224\times3$ pseudo-color image。

## 基本假设

- 原始数据为复数 IQ 序列：$x[n]=I[n]+jQ[n]$。
- 每张图使用连续 $10^6$ 个 IQ 点。
- 图像标签继承该 IQ 片段所属的 drone class 或 no-drone class。
- CPP 生成链路为 `IQ segment -> FAM -> SCS -> NSCMS -> CPP image`。

## 总体流程

推荐的最小可用 pipeline 为：

```text
DroneRFa IQ
-> class-wise 1M segmentation
-> DC removal + RMS normalization
-> split each 1M segment into 16384-point FAM blocks
-> estimate SCS per block
-> average SCS across blocks
-> normalize to NSCMS
-> resize to 224 x 224
-> apply colormap
-> save PNG + label CSV
```

核心思想是：$10^6$ 个 IQ 点作为一个统计观测窗口，不直接做一次超大 FAM，而是在窗口内部划分多个 FAM 子块，先分别估计循环谱，再跨子块累积平均，从而得到更稳定的 CPP。

## 1M IQ 切片

对每一类 DroneRFa 信号，按 $10^6$ 个 IQ 点切成样本：

$$
x_i[n]=x[iH+n],\quad n=0,\dots,10^6-1
$$

其中 $H$ 是滑动步长。如果希望样本之间尽量独立，可取：

$$
H=10^6
$$

如果希望扩增样本量，可取：

$$
H=5\times10^5
$$

但此时需要注意 train/test split 不能把高度重叠的片段分到不同集合，否则会产生 data leakage。

## 预处理

对每个 1M IQ 片段先去 DC：

$$
x[n]\leftarrow x[n]-\frac{1}{N}\sum_{n=0}^{N-1}x[n]
$$

再做 RMS normalization：

$$
x[n]\leftarrow
\frac{x[n]}
{\sqrt{\frac{1}{N}\sum_{n=0}^{N-1}|x[n]|^2}+\epsilon}
$$

其中 $N=10^6$。这样可以降低接收功率、增益和 DC offset 对 CPP 的影响，使图像更突出 cyclostationary structure。

## FAM 子块划分

参考 DroneRFa 相关论文中的设置，可以将每个 1M IQ 片段划分为多个 FAM 子块：

$$
N_{\mathrm{fam}}=16384
$$

一张图对应的子块数量约为：

$$
B=\left\lfloor \frac{10^6}{16384}\right\rfloor \approx 61
$$

每个子块记为：

$$
x_b[n]=x[bN_{\mathrm{fam}}+n],\quad n=0,\dots,N_{\mathrm{fam}}-1
$$

如果希望使用更多上下文，也可以对子块设置 overlap。但最小可用版本建议先使用 non-overlap block，便于复现实验。

## FAM 估计 SCS

对第 $b$ 个子块做 `FAM (FFT Accumulation Method)`，估计 second-order cyclic spectrum：

$$
\hat{S}_{x_b}^{\alpha}(f)
=
\mathbb{E}\left[
X_b\left(f+\frac{\alpha}{2}\right)
X_b^*\left(f-\frac{\alpha}{2}\right)
\right]
$$

实际实现中，FAM 用短时 FFT、共轭乘积和累积平均近似上式。推荐初始参数为：

- FAM sample size：$N_{\mathrm{fam}}=16384$
- FAM FFT window：$N^{\prime}=256$
- 输出频率网格：保留与论文一致的 SCS/NSCMS 矩阵结构

对所有子块的 SCS 做平均，得到该 1M IQ 片段的稳定估计：

$$
\hat{S}_{x}^{\alpha}(f)
=
\frac{1}{B}\sum_{b=1}^{B}\hat{S}_{x_b}^{\alpha}(f)
$$

这一步是“一张图对应 1M IQ 点”的关键：1M 点主要用于提高循环谱估计稳定性，而不是直接扩大最终图片尺寸。

## 归一化为 NSCMS

CPP 通常不直接使用原始 SCS，而是使用 `NSCMS (normalized spectral correlation magnitude surface)`：

$$
\mathrm{NSCMS}_{x}^{\alpha}(f)
=
\frac{
\left|\hat{S}_{x}^{\alpha}(f)\right|
}{
\sqrt{
\hat{S}_{x}^{0}(f+\alpha/2)
\hat{S}_{x}^{0}(f-\alpha/2)
}
+\epsilon
}
$$

在离散网格上得到矩阵：

$$
\mathbf{C}[u,v]=\mathrm{NSCMS}_{x}^{\alpha_u}(f_v)
$$

其中 $u$ 对应 cyclic frequency $\alpha$，$v$ 对应 spectral frequency $f$。

## CPP 图像化

先将 NSCMS 矩阵归一化到 $[0,1]$：

$$
\mathbf{C}_{norm}
=
\frac{\mathbf{C}-\min(\mathbf{C})}
{\max(\mathbf{C})-\min(\mathbf{C})+\epsilon}
$$

再进行 $b$ bit 量化：

$$
\mathbf{P}[u,v]
=
\left\lfloor
(2^b-1)\mathbf{C}_{norm}[u,v]+\frac{1}{2}
\right\rfloor
$$

如果用于 CNN，统一 resize 到 $224\times224$：

$$
\widetilde{\mathbf{P}}
=
\operatorname{Resize}_{224\times224}(\mathbf{P})
$$

最后通过 colormap $\mathcal{M}$ 映射为 RGB tensor：

$$
\mathbf{P}^{RGB}[i,j]
=
\mathcal{M}\left(\widetilde{\mathbf{P}}[i,j]\right)
$$

Python 实现中可优先使用 `viridis`，如果需要更贴近论文表述，可使用 `parula` 的第三方实现。

## 推荐保存格式

建议同时保存图像和元数据：

```text
data_cpp/
  train/
    class_001/
      sample_000001.png
  val/
    class_001/
      sample_000001.png
  metadata.csv
```

`metadata.csv` 建议包含：

```text
image_path,class_id,source_file,start_iq,end_iq,sample_rate,n_iq,n_fam,n_fft
```

这样可以追踪每张 CPP 图来自哪个原始文件、哪个 IQ 区间，以及使用了哪些 FAM 参数。

## 参数建议

| 参数 | 建议值 | 说明 |
|---|---:|---|
| 每图 IQ 点数 | $10^6$ | 用户设定 |
| FAM block size | $16384$ | 贴近 DroneRFa CPP 论文设置 |
| FAM FFT window $N^{\prime}$ | $256$ | 控制谱频率分辨率 |
| 子块数量 | $\approx61$ | 每张图内跨子块平均 |
| 输出尺寸 | $224\times224\times3$ | 适合 `ResNet-18` |
| colormap | `viridis` 或 `parula` | `viridis` 工程上更易用 |
| 保存格式 | `PNG + CSV` | 图像训练与实验追踪兼顾 |

## 与论文设置的关系

DroneRFa 相关 CPP 论文中的典型设置为：frame length $N=10000$、step $L=2500$、FAM sample size $N=16384$、FAM FFT window size $N^{\prime}=256$，中间矩阵为 $32769\times257$，最终转换为 $224\times224\times3$ CPP tensor。

在“一张图对应 1M IQ 点”的设定下，建议保留 $N_{\mathrm{fam}}=16384$ 和 $N^{\prime}=256$，把 1M 点作为多个 FAM 子块的累积窗口。这样既贴近论文参数，又能利用更长 IQ 片段带来的统计稳定性。

## Related Concepts

- [CPP](wiki/concepts/cpp.md)
- [Cyclic Spectrum](wiki/concepts/cyclic-spectrum.md)
- [DroneRFa Dataset](wiki/concepts/drone-rfa.md)
- [RF-Based UAV Identification Using CPP](wiki/sources/2025-rf-based-uav-identification-cpp.md)
