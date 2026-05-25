# CSP Estimators: The FFT Accumulation Method

## Source

Chad Spooner. "CSP Estimators: The FFT Accumulation Method." *Cyclostationary Signal Processing*. Source URL: `https://cyclostationary.blog/2018/06/01/csp-estimators-the-fft-accumulation-method/`.

Raw file: `raw/CSP Estimators The FFT Accumulation Method – Cyclostationary Signal Processing.md`

## Core View

该文章解释 `FAM (FFT Accumulation Method)` 作为 `SCF (spectral correlation function)` 的一种高效估计器。它属于 time-smoothing 类方法，目标是在 spectral frequency $f$ 与 cycle frequency $\alpha$ 的主定义域内生成大量 `spectral correlation` 点估计。

对本仓库而言，FAM 是 `CPP` 生成链路中的数值估计步骤：先由 IQ 信号估计 `SCS/SCF`，再归一化为 `NSCMS`，最后映射为 `CPP` 图像。

## Method

FAM 先用短时 Fourier transform 对输入信号进行 channelization。对长度为 $N^{\prime}$ 的滑动子块做加窗与 FFT，得到随时间跳变的频率通道序列：

$$
X_T(n,f)=\sum_r a(r)x(n-r)e^{-i2\pi f(n-r)T_s}
$$

随后选择两个频率通道 $f_k$ 与 $f_l$，做共轭乘积并沿时间索引再做一次 Fourier transform，从而得到 cross spectral correlation function 的点估计：

$$
S_{xy_T}^{\alpha_i+q\Delta\alpha}(nL,f_j)_{\Delta t}
=
\sum_r X_T(rL,f_k)Y_T^*(rL,f_l)g_c(n-r)e^{-i2\pi rq/P}
$$

其中频率通道对与 $(f,\alpha)$ 的对应关系为：

$$
\alpha_i=f_k-f_l
$$

$$
f_j=\frac{f_k+f_l}{2}
$$

循环频率分辨率在 normalized-frequency units 下为：

$$
\Delta\alpha=\frac{1}{N}
$$

## Implementation Notes

文章给出的软件实现思路可以概括为：

1. 将输入数据按 $N^{\prime}$ 点滑动子块排列为矩阵。
2. 对每个子块施加 tapering window，如 Hamming window。
3. 对每列子块做 FFT，得到 channelized transform。
4. 对不同频率通道做共轭乘积。
5. 对乘积序列做输出 FFT，并把每个输出点映射到正确的 $(f,\alpha)$。
6. 丢弃不在 spectral correlation principal domain 内的点。

该流程说明了为什么实现 FAM 时最容易出错的部分不是 FFT 本身，而是输出点与正确 $(f,\alpha)$ 坐标之间的映射。

## Coherence Normalization

文章还讨论了 spectral coherence。对 non-conjugate spectral correlation，coherence 可写为：

$$
C_x^\alpha(f)
=
\frac{S_x^\alpha(f)}
{\left[S_x^0(f+\alpha/2)S_x^0(f-\alpha/2)\right]^{1/2}}
$$

这与本仓库 `CPP/NSCMS` 使用的归一化思想一致：用 $\alpha=0$ 的 PSD 项对循环谱幅值做归一化，使结果更少受信号功率和噪声功率影响。

## Relevance to CPP

在 `CPP` 任务中，FAM 不直接给出图像，而是给出 $f-\alpha$ 平面上的 `SCF/SCS` 点估计。后续步骤为：

```text
FAM point estimates
-> assemble SCS/SCF surface
-> normalize to coherence magnitude / NSCMS
-> top-view matrix
-> CPP image
```

因此，该文章适合作为理解 `FAM -> SCS/NSCMS -> CPP` 的方法参考，尤其有助于解释：

- 为什么 FAM 需要短时 FFT 与时间方向累积。
- 为什么 $N$、$N^{\prime}$、$L$ 会影响 cycle-frequency resolution、spectral resolution 与估计方差。
- 为什么 FAM 输出必须正确映射到 $(f,\alpha)$ 坐标。
- 为什么 coherence/NSCMS normalization 能降低功率尺度影响。

## Related Pages

- [Summary: Cyclic Features for RF Signal Identification](../summary.md)
- [Cyclic Spectrum](../concepts/cyclic-spectrum.md)
- [CPP](../concepts/cpp.md)

## Terms

- [Cyclic Spectrum](../concepts/cyclic-spectrum.md): `SCF/SCS`
- [CPP](../concepts/cpp.md): cyclic-paw-print
- FAM: FFT Accumulation Method
- SCF: spectral correlation function
- SCS: second-order cyclic spectrum
- SSCA: strip spectral correlation analyzer
- PSD: power spectral density
