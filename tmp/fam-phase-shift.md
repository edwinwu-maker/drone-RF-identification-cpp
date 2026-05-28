# FAM Step 3 中 phase-shift 的具体实现

## 背景

在 FAM（FFT Accumulation Method）的 Step 3 中，对每个加窗后的 data block 做 FFT 后，还需要进行 phase-shift。

原因是：普通 FFT 对每个 block 使用的是 block 内部索引作为时间参考，而 FAM 的 complex demodulate 公式需要保留不同 block 之间的全局时间相位关系。

换句话说，phase-shift 的作用是：

> 把每个短时 FFT 的相位参考点从 block 内部起点改回全局时间索引。

## 推导

设第 $p$ 个 block 从全局样本 $pL$ 开始，block 长度为 $N^{\prime}$，hop size 为 $L$。普通 FFT 计算的是：

$$
B[p,k]=
\sum_{m=0}^{N^{\prime}-1}
x[pL+m]a[m]e^{-j2\pi km/N^{\prime}}
$$

这里指数只包含 block 内部索引 $m$。

但 FAM 公式里的 complex demodulate 需要的是带全局时间索引的形式：

$$
X[p,k]=
\sum_{m=0}^{N^{\prime}-1}
x[pL+m]a[m]e^{-j2\pi f_k(pL+m)}
$$

其中 $f_k$ 是归一化频率，单位是 cycles/sample：

$$
f_k=\frac{k}{N^{\prime}}
$$

指数项可以拆成：

$$
e^{-j2\pi f_k(pL+m)}
=
e^{-j2\pi f_kpL}
e^{-j2\pi f_km}
$$

因此：

$$
X[p,k]=
e^{-j2\pi f_kpL}B[p,k]
$$

所以 phase-shift 的具体实现就是：

$$
\tilde{X}[p,k]
=
B[p,k]e^{-j2\pi f_kpL}
$$

如果矩阵是文档中的形式，即“行 = 频率 bin，列 = block”，则写成：

$$
\tilde{X}[k,p]
=
B[k,p]e^{-j2\pi f_kpL}
$$

## Python 实现

如果 `blocks` 的形状是 `(P, Np)`，即每一行是一个加窗后的 block：

```python
import numpy as np

# blocks: shape = (P, Np)
# P: block 数量
# Np: 每个 block 的 FFT 长度
# L: hop size

B = np.fft.fft(blocks, axis=1)

# 未 fftshift 时的归一化频率，单位 cycles/sample
f = np.fft.fftfreq(Np, d=1.0)      # shape = (Np,)
p = np.arange(P)                   # shape = (P,)

phase = np.exp(-1j * 2*np.pi * p[:, None] * L * f[None, :])

X_tilde = B * phase
```

如果使用 `fftshift`：

```python
import numpy as np

B = np.fft.fftshift(np.fft.fft(blocks, axis=1), axes=1)

f = np.fft.fftshift(np.fft.fftfreq(Np, d=1.0))
p = np.arange(P)

phase = np.exp(-1j * 2*np.pi * p[:, None] * L * f[None, :])

X_tilde = B * phase
```

## MATLAB 实现

如果矩阵是 `Np x P`，即每一列是一个 block：

```matlab
B = fft(blocks, [], 1);          % Np x P

f = (0:Np-1).' / Np;             % 未 fftshift 的 normalized frequency
p = 0:P-1;

phase = exp(-1j*2*pi * f * (p*L));

X_tilde = B .* phase;
```

如果使用中心化频率：

```matlab
B = fftshift(fft(blocks, [], 1), 1);

f = (-Np/2:Np/2-1).' / Np;
p = 0:P-1;

phase = exp(-1j*2*pi * f * (p*L));

X_tilde = B .* phase;
```

## 注意事项

1. 如果 block 的参考点不是起点 $pL$，而是中心点或其他全局时间点，则 phase 中的 $pL$ 应替换成对应的全局参考时间。
2. 指数符号要与 FFT 约定一致。NumPy 和 MATLAB 的 `fft` 使用 $e^{-j2\pi kn/N}$，因此上面的 phase-shift 使用负号。
3. 如果对频率轴做了 `fftshift`，必须同时使用 `fftshift` 后的频率数组 $f_k$，否则相位会和频率 bin 对不上。
4. 对输入 $y(t)$ 做 cross-SCF 时，$Y$ 通道也需要使用相同规则进行 phase-shift；如果 $x(t)=y(t)$，则可以复用同一个 channelized result。

## 总结

FAM Step 3 的 phase-shift 不是额外的滤波或平滑操作，而是补偿普通 FFT 丢失的全局时间相位。

核心公式是：

$$
\tilde{X}[p,k]
=
B[p,k]e^{-j2\pi f_kpL}
$$

它保证后续计算频率通道乘积 $Y_{k,l}[p]$ 时，不同 block 之间的相位关系与 FAM 的 complex demodulate 定义一致。
