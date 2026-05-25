---
type: concept
tags: [concept, cyclic-feature]
---

# CPP

`CPP (cyclic-paw-print)` 是将归一化 `cyclic spectrum` 的俯视结构映射为图像特征的方法，便于后续 `DCT/DWT` 或 `CNN` 使用。它不是新的循环统计量，而是把 `FAM` 估计得到的二阶 `SCF/SCS` 表面转换为稳定、可输入视觉模型的矩阵或 RGB tensor。

## 关键点

- 本质是循环域特征的图像化表达。
- 核心链路为 `FAM -> SCS -> normalized SCS/NSCMS -> DNSCS -> CPP`。
- 兼具可解释性与模型可用性，适合 ACMC 与 UAV RF identification。
- 完整提取流水线（ULWNet 论文）：DNSCS -> b-bit quantizer -> 方形插值/抽取 -> parula pseudo-color -> $224\times224\times3$ RGB tensor。

## 从 FAM 到 CPP 的理论链路

设接收离散信号为 $r[n]$。`FAM (FFT Accumulation Method)` 的作用是估计二阶循环谱，即频率平面上两个相隔 $\alpha$ 的谱分量之间的相关性。理论上的 `SCF` 可写为：

$$
S_r^{\alpha}(f)=\mathbb{E}\left[
R\left(f+\frac{\alpha}{2}\right)
R^*\left(f-\frac{\alpha}{2}\right)
\right]
$$

其中 $f$ 是谱频率，$\alpha$ 是循环频率。FAM 用有限长度分段 FFT 和段间累积平均近似上式的期望。设短时 FFT 窗长为 $N^{\prime}$，步长为 $L$，窗函数为 $w[q]$，第 $m$ 段的 FFT 为：

$$
R_m[k]=\sum_{q=0}^{N^{\prime}-1}r[mL+q]w[q]e^{-j2\pi kq/N^{\prime}}
$$

对关于中心频率对称的两个 FFT bin 做共轭乘积：

$$
I_m[k,l]=R_m[k+l]R_m^*[k-l]
$$

再对 $M$ 个分段累积平均，得到 FAM 形式的 cyclic periodogram / SCS 估计：

$$
\hat{S}_r^{\alpha_l}(f_k)=\frac{1}{M}\sum_{m=0}^{M-1}I_m[k,l]
$$

这里 $f_k$ 与 FFT bin $k$ 对应，$\alpha_l$ 与 bin 间隔 $2l$ 对应。直观地看，$l=0$ 时退化为普通功率谱估计；$l\neq0$ 时衡量频率 $f_k+\alpha_l/2$ 与 $f_k-\alpha_l/2$ 两侧分量的循环相关强度。

## 归一化循环谱

原始 $\hat{S}_r^{\alpha}(f)$ 的幅值会受信号功率、增益和噪声水平影响。CPP 通常不直接使用原始 SCS(second-order cyclic spectrum)，而使用 normalized cyclic spectrum 或 `NSCMS(normalized spectral correlation magnitude surface)`。一种常见归一化形式为：

$$
\bar{S}_r^{\alpha}(f)=
\frac{\left|\hat{S}_r^{\alpha}(f)\right|}
{\sqrt{\hat{S}_r^{0}(f+\alpha/2)\hat{S}_r^{0}(f-\alpha/2)}+\epsilon}
$$

其中 $\hat{S}_r^{0}(\cdot)$ 是普通谱相关的零循环频率分量，$\epsilon$ 用于避免分母为零。归一化后，$\bar{S}_r^{\alpha}(f)$ 更接近“谱相关强度图”，而不是单纯的能量图。

## 离散矩阵到 CPP 图像

在离散网格上取循环频率集合 $\{\alpha_u\}$ 与谱频率集合 $\{f_v\}$，可得到 `DNSCS` 矩阵：

$$
\mathbf{C}[u,v]=\bar{S}_r^{\alpha_u}(f_v)
$$

论文中的 top-view CPP 可以理解为从三维曲面 $(\alpha,f,\bar{S})$ 的上方观察：横轴和纵轴分别对应 $\alpha$ 与 $f$，像素强度对应归一化谱相关幅值。因此 gray-scale CPP 可表示为：

$$
\mathbf{P}[u,v]=Q_b\left(\mathbf{C}[u,v]\right)
$$

其中 $Q_b(\cdot)$ 是 $b$ bit 量化器。例如当 $\mathbf{C}[u,v]$ 已归一化到 $[0,1]$ 时：

$$
Q_b(x)=\left\lfloor (2^b-1)x+\frac{1}{2}\right\rfloor
$$

若需要输入 CNN，通常再把 $\mathbf{P}$ 通过插值或抽取变换到固定方阵尺寸 $\Lambda\times\Lambda$：

$$
\widetilde{\mathbf{P}}=\operatorname{Resize}_{\Lambda\times\Lambda}(\mathbf{P})
$$

最后通过 colormap $\mathcal{M}$ 映射为 pseudo-color RGB tensor：

$$
\mathbf{P}^{\mathrm{RGB}}[i,j]=\mathcal{M}\left(\widetilde{\mathbf{P}}[i,j]\right)
=
\left[
\widetilde{\mathbf{P}}^{R}[i,j],
\widetilde{\mathbf{P}}^{G}[i,j],
\widetilde{\mathbf{P}}^{B}[i,j]
\right]
$$

因此，从 FAM 到 CPP 的完整数学关系可概括为：

$$
r[n]
\xrightarrow{\mathrm{FAM}}
\hat{S}_r^{\alpha}(f)
\xrightarrow{\mathrm{normalize}}
\bar{S}_r^{\alpha}(f)
\xrightarrow{\mathrm{sample}}
\mathbf{C}[u,v]
\xrightarrow{Q_b,\ \mathrm{resize},\ \mathcal{M}}
\mathbf{P}^{\mathrm{RGB}}
$$

## 判别意义

CPP 保留的是信号的 cyclostationary structure：调制符号率、载波/子载波结构、周期性编码或脉冲形态会在 $\alpha-f$ 平面形成稳定纹理。与直接的 I/Q 或 STFT 图相比，CPP 更强调跨频率谱分量的循环相关，而不是瞬时能量分布。因此在 ACMC、UAV RF identification 和 RF fingerprinting 中，CPP 可作为兼具物理含义与图像模型友好性的中间表示。

## 与 raw 论文对应

- `2024 ACMC`：FAM 生成 normalized second-order cyclic spectrum，top view 映射为 gray-scale CPP，尺寸为 $65\times2049$，后续用 `DCT/DWT + SMO-SVM` 分类。
- `2024 ULWNet`：FAM 得到 SCS $R_r^{\alpha}(f)$，归一化为 NSCS $\bar{R}_r^{\alpha}(f)$，离散化为 DNSCS $\bar{R}_r^{\alpha_u}(f_v)$，再转为 $224\times224\times3$ CPP tensor。
- `2025 UAV RF`：对 ST-ESER 选出的有效 UAV RF frame 做 FAM cyclic-spectrum analysis，构造 NSCMS，取 top view 得到 CPP，再输入 `ResNet-18`。

## Related Papers

- [Automatic Composite-Modulation Classification Using CPP](../sources/2024-automatic-composite-modulation-classification-cpp.md)
- [Automatic Composite-Modulation Classification Using ULWNet Based on CPP](../sources/2024-acmc-ulwnet-cpp.md)
- [RF-Based UAV Identification Using CPP](../sources/2025-rf-based-uav-identification-cpp.md)
