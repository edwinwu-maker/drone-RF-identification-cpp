# FAM 算法实现文档与 Python 参考代码

本文按照 `raw/CSP Estimators The FFT Accumulation Method – Cyclostationary Signal Processing Ch.md` 中的 Step 1-5 组织，实现 FFT Accumulation Method (FAM) 对 spectral correlation function / second-order cyclic spectrum 的估计。

## 目标

给定一段离散 complex IQ 信号：

$$
x[n],\quad n=0,1,\ldots,M-1
$$

FAM 的目标是估计：

$$
S_x^\alpha(f)
$$

其中：

- $f$ 是 spectral frequency。
- $\alpha$ 是 cycle frequency。
- 本实现内部默认使用 normalized frequency，单位为 cycles/sample。

如果需要 Hz 单位，最后再乘以采样率 $f_s$：

$$
f_{\text{Hz}}=f_{\text{norm}}f_s
$$

$$
\alpha_{\text{Hz}}=\alpha_{\text{norm}}f_s
$$

## 符号约定

| 符号 | 含义 |
|---|---|
| $x[n]$ | 输入 complex IQ 序列 |
| $N^{\prime}$ | channelizer 的短时 FFT 点数 |
| $L$ | hop size，相邻 data block 起点间隔 |
| $P$ | data block 数量，也是第二阶段 FFT 长度 |
| $k,l$ | 第一阶段 FFT 的两个频率通道索引 |
| $q$ | 第二阶段 FFT 的索引 |
| $f_k,f_l$ | 第一阶段 FFT 频率 bin，normalized frequency |
| $\beta_q$ | 第二阶段 FFT 给出的 cycle-frequency 细分量 |

FAM 的坐标映射为：

$$
f=\frac{f_k+f_l}{2}
$$

$$
\alpha=(f_k-f_l)+\beta_q
$$

其中：

$$
\beta_q=\frac{q_c}{PL}
$$

$q_c$ 是 `fftshift` 后的中心化第二阶段 FFT 索引。

## Step 1: 查找并排列 $N^{\prime}$ 点 data blocks

按 hop size $L$ 从输入序列中提取长度为 $N^{\prime}$ 的 data blocks。若末尾长度不足，可以 zero-padding。

若第 $p$ 个 block 从全局样本 $pL$ 开始，则：

$$
x_p[m]=x[pL+m],\quad m=0,1,\ldots,N^{\prime}-1
$$

raw 文档采用 MATLAB 风格排列：每一列是一个 data block，因此矩阵形状为：

$$
\text{blocks}_{\text{raw}}\in\mathbb{C}^{N^{\prime}\times P}
$$

当前 Python 实现采用转置布局：每一行是一个 data block，因此矩阵形状为：

$$
\text{blocks}_{\text{py}}\in\mathbb{C}^{P\times N^{\prime}}
$$

二者只是数组存储方向不同，不是算法差异：

$$
\text{blocks}_{\text{py}}[p,m]=\text{blocks}_{\text{raw}}[m,p]
$$

采用 `(P, nfft)` 的原因是 NumPy 中可以直接用 `np.fft.fft(blocks_w, axis=1)` 对每一行做 $N^{\prime}$ 点 FFT；后续 Step 4 也可以用 `x_tilde[:, k]` 直接取第 $k$ 个频率通道沿短时时间轴 $p$ 的序列。

当前实现中，`n_blocks` 对应 $P$。若调用时不显式指定 `n_blocks`，则由输入长度、$N^{\prime}$ 和 $L$ 自动计算：

$$
P=
\begin{cases}
1, & M\le N^{\prime}\\
\left\lceil \dfrac{M-N^{\prime}}{L}\right\rceil+1, & M>N^{\prime}
\end{cases}
$$

因此最后一个 block 可能越过原始输入末尾。实现中 `_channelize()` 调用 `_make_blocks(..., pad=True)`，会在末尾 zero-padding 以保留这个尾部 block。若手动调用 `_make_blocks(..., pad=False)`，输入长度不足以覆盖指定 $P$ 个 block 时会直接报错。

## Step 2: 对 data blocks 施加 tapering window

对每个 block 乘以长度为 $N^{\prime}$ 的 window，例如 Hamming window：

$$
x_p^{(w)}[m]=x_p[m]w[m]
$$

window energy 为：

$$
U=\sum_{m=0}^{N^{\prime}-1}|w[m]|^2
$$

后续可用 $U$ 做谱幅值归一化。

## Step 3: 对加窗后的 blocks 做 FFT 并 phase-shift

普通 FFT 得到：

$$
B[p,k]=
\sum_{m=0}^{N^{\prime}-1}
x[pL+m]w[m]e^{-j2\pi km/N^{\prime}}
$$

但 FAM 的 complex demodulate 需要保留全局时间相位：

$$
X[p,k]=
\sum_{m=0}^{N^{\prime}-1}
x[pL+m]w[m]e^{-j2\pi f_k(pL+m)}
$$

由于：

$$
e^{-j2\pi f_k(pL+m)}
=
e^{-j2\pi f_kpL}
e^{-j2\pi f_km}
$$

所以 FFT 后需要补偿：

$$
\tilde{X}[p,k]=B[p,k]e^{-j2\pi f_kpL}
$$

注意：这里的 $f_k$ 必须是 normalized frequency，单位为 cycles/sample。

## Step 4: 将 channelized subblocks 相乘并做第二次 FFT

对每个频率通道对 $(k,l)$，构造 auto-SCF 的 channelizer product vector：

$$
Y_{k,l}[p]=\tilde{X}[p,k]\tilde{X}^{*}[p,l]
$$

然后沿 block index $p$ 做长度为 $P$ 的 FFT：

$$
Z_{k,l}[q]=
\sum_{p=0}^{P-1}
Y_{k,l}[p]e^{-j2\pi pq/P}
$$

如果使用 NumPy 默认未归一化 FFT，谱值可写为：

$$
\hat{S}^{\alpha}_{x}(f)
=
\frac{1}{PU}Z_{k,l}[q]
$$

若需要 Hz 下的谱密度单位，则使用：

$$
\hat{S}^{\alpha}_{x}(f)
=
\frac{1}{P f_s U}Z_{k,l}[q]
$$

## Step 5: 将 FFT 输出映射到正确的 $(f,\alpha)$

对于每个通道对 $(k,l)$ 和第二阶段 FFT bin $q$：

$$
f=\frac{f_k+f_l}{2}
$$

$$
\alpha=(f_k-f_l)+\beta_q
$$

其中：

$$
\beta_q=\operatorname{fftshift}(\operatorname{fftfreq}(P,d=L))
$$

该 $\beta_q$ 的单位也是 cycles/sample。

对于 non-conjugate SCF，常用 principal domain 可写为：

$$
|f|+\frac{|\alpha|}{2}\le \frac{1}{2}
$$

不在该区域的点可以丢弃。

## Python 参考实现

下面代码强调清晰性和与 Step 1-5 的对应关系。它不会一次性构造 $N^{\prime}\times N^{\prime}\times P$ 的巨大三维张量，而是逐个或分批处理频率通道对。

这份实现的边界如下：

- 输入只有一维 complex IQ 序列 `x`，用于估计 auto non-conjugate SCF。
- 不再提供 `y` 参数；cross-SCF 不在当前函数范围内。
- 不再提供 `use_hz` 参数；函数内部始终使用 normalized frequency，单位为 cycles/sample。
- 若需要 Hz 坐标，只在函数外部做 `f_hz = result.f * fs` 和 `alpha_hz = result.alpha * fs`。
- Step 4 使用 `x_tilde[:, k] * np.conj(x_tilde[:, l])`，因此对应 non-conjugate SCF；conjugate SCF 需要改成不取共轭的乘积和另一套 principal domain。

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np


@dataclass
class FAMResult:
    """FAM 输出点估计。

    f:
        spectral frequency 坐标。默认 normalized frequency，单位 cycles/sample。
    alpha:
        cycle frequency 坐标。默认 normalized frequency，单位 cycles/sample。
    value:
        对应的 complex SCF 估计值。
    """

    f: np.ndarray
    alpha: np.ndarray
    value: np.ndarray


def _make_blocks(
    x: np.ndarray,
    nfft: int,
    hop: int,
    *,
    n_blocks: Optional[int] = None,
    pad: bool = True,
) -> np.ndarray:
    """Step 1: 将一维 IQ 信号切成 data blocks。

    pad:
        当输入信号长度不够凑齐最后一个 block 时，是否在末尾补零。

    返回 shape = (P, nfft) 的矩阵，每一行是一个 block。
    """

    x = np.asarray(x, dtype=np.complex128)
    if x.ndim != 1:
        raise ValueError("x must be a one-dimensional complex IQ sequence")
    if nfft <= 0:
        raise ValueError("nfft must be positive")
    if hop <= 0:
        raise ValueError("hop must be positive")

    if n_blocks is None:
        if len(x) <= nfft:
            n_blocks = 1
        else:
            n_blocks = int(np.ceil((len(x) - nfft) / hop)) + 1

    total_needed = (n_blocks - 1) * hop + nfft
    if len(x) < total_needed:
        if not pad:
            raise ValueError("input is too short for requested n_blocks without padding")
        x = np.pad(x, (0, total_needed - len(x)))

    starts = np.arange(n_blocks) * hop
    # 通过广播生成每个 block 的采样索引，shape = (P, nfft)。
    sample_index = starts[:, None] + np.arange(nfft)[None, :]
    return x[sample_index]


def _window(name: str, nfft: int) -> np.ndarray:
    """Step 2: 生成 channelizer data-tapering window。"""

    name = name.lower()
    if name in {"hamming", "hamm"}:
        return np.hamming(nfft)
    if name in {"hann", "hanning"}:
        return np.hanning(nfft)
    if name in {"rect", "boxcar", "rectangle"}:
        return np.ones(nfft)
    raise ValueError(f"unsupported window: {name}")


def _channelize(
    x: np.ndarray,
    *,
    nfft: int,
    hop: int,
    window: str = "hamming",
    n_blocks: Optional[int] = None,
    fftshift: bool = True,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Step 1-3: 分块、加窗、FFT、phase-shift。

    返回：
        X_tilde:
            shape = (P, nfft)，每一列对应一个频率通道。
        freqs:
            第一阶段 FFT 的 normalized frequency，单位 cycles/sample。
        window_energy:
            sum(abs(w)**2)，用于谱幅值归一化。
    """

    blocks = _make_blocks(x, nfft, hop, n_blocks=n_blocks, pad=True)
    p_count = blocks.shape[0]

    # Step 2: 对每个 block 乘以 tapering window。
    w = _window(window, nfft).astype(float)
    window_energy = float(np.sum(np.abs(w) ** 2))
    blocks_w = blocks * w[None, :]

    # Step 3: 对每个 block 做 FFT。
    spectrum = np.fft.fft(blocks_w, axis=1)
    freqs = np.fft.fftfreq(nfft, d=1.0)

    if fftshift:
        spectrum = np.fft.fftshift(spectrum, axes=1)
        freqs = np.fft.fftshift(freqs)

    # Step 3: phase-shift，恢复不同 blocks 之间的全局时间相位关系。
    # phase[p, k] = exp(-j 2pi f_k pL)
    p = np.arange(p_count)
    phase = np.exp(-1j * 2.0 * np.pi * p[:, None] * hop * freqs[None, :])
    x_tilde = spectrum * phase

    return x_tilde, freqs, window_energy


def _principal_domain_mask(f: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """non-conjugate SCF 常用 principal domain。

    normalized frequency 下：
        |f| + |alpha|/2 <= 1/2
    """

    return np.abs(f) + 0.5 * np.abs(alpha) <= 0.5


def fam_scf_points(
    x: np.ndarray,
    *,
    nfft: int = 256,
    hop: int = 64,
    n_blocks: Optional[int] = None,
    window: str = "hamming",
    keep_principal_domain: bool = True,
    pair_indices: Optional[Iterable[tuple[int, int]]] = None,
    fftshift: bool = True,
    normalize: bool = True,
) -> FAMResult:
    """按 FAM Step 1-5 估计 SCF 点。

    Parameters
    ----------
    x:
        输入 complex IQ 序列。
    nfft:
        N prime，channelizer 短时 FFT 点数。
    hop:
        L，data block hop size。
    n_blocks:
        P，使用的 data block 数。若为 None，则由输入长度自动决定。
    window:
        channelizer tapering window，支持 "hamming"、"hann"、"rect"。
    keep_principal_domain:
        是否丢弃 non-conjugate SCF principal domain 之外的点。
    pair_indices:
        可选的 (k, l) 通道对列表。若为 None，则 exhaustive 计算所有通道对。
        注意这里的 k,l 是 fftshift 后频率数组中的索引。
    fftshift:
        是否对第一阶段和第二阶段 FFT 使用中心化频率顺序。
    normalize:
        若为 True，谱值除以 P * window_energy。函数始终使用 normalized
        frequency；如果需要 Hz 坐标，由调用者在函数外部乘以采样率 fs。

    Returns
    -------
    FAMResult:
        一组三元点估计 (f, alpha, value)。
    """

    x_tilde, freqs, window_energy = _channelize(
        x,
        nfft=nfft,
        hop=hop,
        window=window,
        n_blocks=n_blocks,
        fftshift=fftshift,
    )
    p_count = x_tilde.shape[0]

    # 第二阶段 FFT 的 cycle-frequency 细分量 beta，单位 cycles/sample。
    beta = np.fft.fftfreq(p_count, d=hop)
    if fftshift:
        beta = np.fft.fftshift(beta)

    if pair_indices is None:
        pair_indices = ((k, l) for k in range(nfft) for l in range(nfft))

    f_chunks: list[np.ndarray] = []
    alpha_chunks: list[np.ndarray] = []
    value_chunks: list[np.ndarray] = []

    scale = 1.0
    if normalize:
        scale = p_count * window_energy

    for k, l in pair_indices:
        fk = freqs[k]
        fl = freqs[l]

        # Step 4: 构造长度 P 的 channelizer product vector。
        product = x_tilde[:, k] * np.conj(x_tilde[:, l])

        # Step 4: 沿窗口序号做第二次 FFT。
        z = np.fft.fft(product)
        if fftshift:
            z = np.fft.fftshift(z)

        if normalize:
            z = z / scale

        # Step 5: 映射到 (f, alpha)。
        f_value = 0.5 * (fk + fl)
        alpha = (fk - fl) + beta
        f = np.full_like(alpha, f_value, dtype=float)

        if keep_principal_domain:
            mask = _principal_domain_mask(f, alpha)
            if not np.any(mask):
                continue
            f = f[mask]
            alpha = alpha[mask]
            z = z[mask]

        f_chunks.append(f)
        alpha_chunks.append(alpha)
        value_chunks.append(z)

    if not f_chunks:
        return FAMResult(
            f=np.empty(0, dtype=float),
            alpha=np.empty(0, dtype=float),
            value=np.empty(0, dtype=np.complex128),
        )

    return FAMResult(
        f=np.concatenate(f_chunks),
        alpha=np.concatenate(alpha_chunks),
        value=np.concatenate(value_chunks),
    )
```

## 使用示例

```python
import numpy as np

# 示例 complex IQ 信号
fs = 10_000_000.0
x = np.random.randn(100_000) + 1j * np.random.randn(100_000)

result = fam_scf_points(
    x,
    nfft=256,
    hop=64,
    window="hamming",
    keep_principal_domain=True,
    normalize=True,
)

# 可用于绘图的 normalized 坐标和值
f = result.f
alpha = result.alpha
scf_mag = np.abs(result.value)

# 如果需要 Hz 坐标，在函数外部转换。
f_hz = f * fs
alpha_hz = alpha * fs
```

如果只想计算一部分通道对，避免 exhaustive FAM 的大计算量：

```python
# 只计算若干个 (k, l) pair；索引对应 fftshift 后的频率数组。
pairs = [(120, 120), (121, 120), (122, 119)]

result = fam_scf_points(
    x,
    nfft=256,
    hop=64,
    pair_indices=pairs,
    keep_principal_domain=True,
)
```

## 将点估计栅格化为图像

FAM 的输出天然是一组 $(f,\alpha,value)$ 点。若要形成 CPP/NSCMS image，可把点映射到二维网格。

下面给出一个简单的 nearest-bin 聚合示例：

```python
def points_to_grid(
    f: np.ndarray,
    alpha: np.ndarray,
    value: np.ndarray,
    *,
    f_bins: int = 257,
    alpha_bins: int = 513,
    f_range: tuple[float, float] = (-0.5, 0.5),
    alpha_range: tuple[float, float] = (-1.0, 1.0),
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """把 FAM 点估计聚合成 |SCF| 图像矩阵。

    若多个点落入同一 bin，这里取最大幅度。也可以替换为平均。
    """

    image = np.zeros((alpha_bins, f_bins), dtype=float)

    f_idx = np.floor(
        (f - f_range[0]) / (f_range[1] - f_range[0]) * (f_bins - 1)
    ).astype(int)
    a_idx = np.floor(
        (alpha - alpha_range[0])
        / (alpha_range[1] - alpha_range[0])
        * (alpha_bins - 1)
    ).astype(int)

    valid = (
        (f_idx >= 0)
        & (f_idx < f_bins)
        & (a_idx >= 0)
        & (a_idx < alpha_bins)
    )

    mag = np.abs(value)
    for ai, fi, v in zip(a_idx[valid], f_idx[valid], mag[valid]):
        image[ai, fi] = max(image[ai, fi], v)

    if image.max() > 0:
        image = image / image.max()

    f_axis = np.linspace(f_range[0], f_range[1], f_bins)
    alpha_axis = np.linspace(alpha_range[0], alpha_range[1], alpha_bins)
    return image, f_axis, alpha_axis
```

## 实现注意事项

### 1. 频率坐标从一开始就使用 normalized frequency

Phase-shift 中使用：

$$
e^{-j2\pi f_kpL}
$$

其中 $pL$ 是样本数，所以 $f_k$ 必须是 cycles/sample。若使用 Hz，则应写成：

$$
e^{-j2\pi f_{\text{Hz}}pLT_s}
$$

二者等价。

### 2. Step 4 是主要计算瓶颈

若 exhaustive 计算所有 $(k,l)$，通道对数量为：

$$
N^{\prime 2}
$$

每个通道对需要一次长度为 $P$ 的 FFT，因此 Step 4 复杂度为：

$$
O(N^{\prime 2}P\log P)
$$

实际无人机识别任务中通常应考虑：

- 只计算 principal domain。
- 只计算感兴趣的 $\alpha$ 或 $f$ 区域。
- 分批处理 $(k,l)$ 通道对。
- 先粗分辨率搜索，再局部精算。

### 3. 归一化分为谱值归一化和坐标归一化

谱值归一化常用：

$$
\frac{1}{PU}
$$

其中 $P$ 对应时间平均，$U$ 对应 window energy。

坐标归一化指 $f$ 和 $\alpha$ 使用 cycles/sample。只有最终显示或和物理频率比较时，才乘以 $f_s$ 转成 Hz。

## 最小验证建议

实现后建议用以下信号做 sanity check：

1. 纯噪声：SCF 不应出现稳定强峰。
2. 单音或 BPSK：应出现可解释的 cycle-frequency ridge/peak。
3. 同一信号重复运行：峰值位置应稳定。
4. 在函数外部改变 `fs` 做坐标转换：$f_{\text{Hz}}$ 和 $\alpha_{\text{Hz}}$ 应按采样率线性缩放。

## 总结

这份实现与 raw 文档的对应关系如下：

| raw 文档步骤 | Python 实现位置 |
|---|---|
| Step 1: 查找并排列 data blocks | `_make_blocks()` |
| Step 2: 施加 tapering window | `_window()` 与 `_channelize()` |
| Step 3: FFT + phase-shift | `_channelize()` |
| Step 4: 通道乘积 + 第二次 FFT | `fam_scf_points()` 主循环 |
| Step 5: 映射到 $(f,\alpha)$ | `fam_scf_points()` 中的坐标计算 |

核心实现公式为：

$$
\tilde{X}[p,k]=
\operatorname{FFT}\{x[pL+m]w[m]\}_k
e^{-j2\pi f_kpL}
$$

$$
Z_{k,l}[q]=
\operatorname{FFT}_p
\left\{
\tilde{X}[p,k]\tilde{X}^{*}[p,l]
\right\}
$$

$$
f=\frac{f_k+f_l}{2},\quad
\alpha=(f_k-f_l)+\frac{q_c}{PL}
$$
