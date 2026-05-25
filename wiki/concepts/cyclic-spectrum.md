---
type: concept
tags: [concept, cyclic-feature]
---

# Cyclic Spectrum

`cyclic spectrum`（`SCF`, spectral correlation function）描述循环平稳信号在 $f-\alpha$ 平面上的二阶统计相关性，是 `CPP` 与 `FLOCS` 的共同基础。

## 循环谱理论与公式

循环自相关函数（`CAF`）定义为：

$$
R_x^{\alpha}(\tau)=\lim_{T\to\infty}\frac{1}{T}\int_{-T/2}^{T/2}x\left(t+\frac{\tau}{2}\right)x^*\left(t-\frac{\tau}{2}\right)e^{-j2\pi\alpha t}\,dt
$$

对时延 $\tau$ 做傅里叶变换得到循环谱：

$$
S_x^{\alpha}(f)=\int_{-\infty}^{\infty}R_x^{\alpha}(\tau)e^{-j2\pi f\tau}\,d\tau
$$

### 从 CAF 到等价频域表达式的推导

将 $R_x^{\alpha}(\tau)$ 代入 $S_x^{\alpha}(f)$：

$$
S_x^{\alpha}(f)=\lim_{T\to\infty}\frac{1}{T}
\int_{-T/2}^{T/2}\int_{-\infty}^{\infty}
x\left(t+\frac{\tau}{2}\right)x^*\left(t-\frac{\tau}{2}\right)
e^{-j2\pi\alpha t}e^{-j2\pi f\tau}\,d\tau\,dt
$$

令

$$
u=t+\frac{\tau}{2},\quad v=t-\frac{\tau}{2}
\Rightarrow
t=\frac{u+v}{2},\ \tau=u-v,\ d\tau\,dt=du\,dv
$$

可得

$$
S_x^{\alpha}(f)=\lim_{T\to\infty}\frac{1}{T}
\iint x(u)x^*(v)
e^{-j2\pi\left(f+\frac{\alpha}{2}\right)u}
e^{+j2\pi\left(f-\frac{\alpha}{2}\right)v}
\,du\,dv
$$

定义有限时长 Fourier transform：

$$
X_T(\nu)=\int_{-T/2}^{T/2}x(t)e^{-j2\pi \nu t}dt
$$

于是

$$
S_x^{\alpha}(f)=\lim_{T\to\infty}\frac{1}{T}\,
\mathbb{E}\!\left[
X_T\!\left(f+\frac{\alpha}{2}\right)
X_T^*\!\left(f-\frac{\alpha}{2}\right)
\right]
$$

标准等价频域表达式：

$$
S_x^{\alpha}(f)=\mathbb{E}\!\left\{
X\!\left(f+\frac{\alpha}{2}\right)X^*\!\left(f-\frac{\alpha}{2}\right)
\right\}
$$

归一化形式（用于 `NSCMS/CPP`）：

$$
\widetilde{S}_x^{\alpha}(f)=\frac{|S_x^{\alpha}(f)|}{\sqrt{S_x^{0}(f+\alpha/2)S_x^{0}(f-\alpha/2)}+\epsilon}
$$

## FAM 理论基础与推导

`FAM (FFT Accumulation Method)` 是 `SCF` 的离散估计算法，不是新的统计特征。核心是“分段 FFT + 共轭乘积 + 累积平均”近似期望。

设离散信号为 $x[n]$，分段长度为 $N^{\prime}$，步长为 $L$，窗函数为 $w[r]$，第 $m$ 段短时 FFT 为：

$$
X_m[k]=\sum_{r=0}^{N^{\prime}-1}x[mL+r]\,w[r]\,e^{-j2\pi kr/N^{\prime}}
$$

循环相关积：

$$
I_m(k,\ell)=X_m[k+\ell]\,X_m^*[k-\ell]
$$

离散网格上有 $\alpha \propto 2\ell/N^{\prime}$，对 $m$ 累积平均得到估计：

$$
\hat{S}_x^{\alpha}(f_k)\approx \frac{1}{M}\sum_{m=0}^{M-1}I_m(k,\ell)
$$

## 与循环谱的关系和区别

- 关系：`SCF` 是理论统计量，`FAM` 是其数值估计器。
- 区别：`SCF` 回答“是什么”，`FAM` 回答“怎么算”。
- 折中：$N^{\prime}$、$L$、窗函数、平均段数 $M$ 共同决定分辨率与方差。
- 本仓库链路：`FAM -> SCS/NSCMS -> CPP`。

## 循环谱阶数说明

标准 `cyclic spectrum/SCF` 是**二阶**循环统计量，对应二阶循环自相关函数 $R_x^{\alpha}(\tau)$ 与二阶循环谱 $S_x^{\alpha}(f)$。

循环谱“阶数”由所采用的**统计量阶次**决定，而不是由 FFT 或分帧参数决定：

- 二阶：由二阶矩/相关定义（两个信号因子）决定。
- 四阶及更高阶：由四阶或更高阶矩/累积量定义（更多信号因子）决定。
- `FLOCS`：由分数低阶指数参数（如 $p$ 或 $b$）决定所用低阶统计形式。

说明：$N^{\prime}$、$L$、窗函数、平均段数 $M$ 只影响估计分辨率、方差与稳定性，不改变循环谱阶数本身。

## 与 raw 论文对应

- `2024 ACMC`：`FAM FFT window size = 64`，映射到 `CPP (65 x 2049)`。
- `2025 UAV RF`：`FAM FFT window size N^{\prime} = 256`、`sample size N = 16384`，中间矩阵 `32769 x 257`，再变换为 `224 x 224 x 3`。

## Related Papers

- [CSP Estimators: The FFT Accumulation Method](../sources/2018-csp-estimators-fam.md)
- [Automatic Composite-Modulation Classification Using CPP](../sources/2024-automatic-composite-modulation-classification-cpp.md)
- [Automatic Composite-Modulation Classification Using ULWNet Based on CPP](../sources/2024-acmc-ulwnet-cpp.md)
- [RF-Based UAV Identification Using CPP](../sources/2025-rf-based-uav-identification-cpp.md)
