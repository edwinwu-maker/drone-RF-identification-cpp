# FAM 的归一化

FAM（FFT Accumulation Method）的归一化可以分成三层：

- 时间平均归一化
- 窗口能量归一化
- coherence 归一化

不同论文和代码实现中的常数因子可能略有差异，但核心逻辑一致。

## 1. 第二次 FFT 后要除以窗口数 $P$

FAM Step 4 计算：

$$
Z_{k,l}[q]=
\sum_{r=0}^{P-1}
Y_{k,l}[r]e^{-j2\pi rq/P}
$$

其中：

$$
Y_{k,l}[r]=\tilde{X}[r,k]\tilde{Y}^*[r,l]
$$

这个 FFT 本质上是在做带循环频率解调的时间平均。因此，如果使用 NumPy/MATLAB 默认未归一化 FFT，需要除以 $P$：

$$
\hat{S}_{xy}^{\alpha}(f)
=
\frac{1}{P}
Z_{k,l}[q]
$$

否则结果只是累加值，不是平均值。

## 2. 要除以短时分析窗能量

短时 FFT 前通常会使用窗函数 $a[n]$，例如 Hamming 或 Hann 窗。窗函数会改变谱幅度，因此需要进行窗能量归一化。

窗能量定义为：

$$
U=\sum_{n=0}^{N^{\prime}-1}|a[n]|^2
$$

于是更完整的 SCF 估计可写成：

$$
\hat{S}_{xy}^{\alpha}(f)
=
\frac{1}{PU}
\sum_{r=0}^{P-1}
\tilde{X}[r,k]\tilde{Y}^*[r,l]
e^{-j2\pi rq/P}
$$

如果要保留物理单位，例如 Hz 下的 spectral density，还常写成：

$$
\hat{S}_{xy}^{\alpha}(f)
=
\frac{1}{P f_s U}
\sum_{r=0}^{P-1}
\tilde{X}[r,k]\tilde{Y}^*[r,l]
e^{-j2\pi rq/P}
$$

其中 $f_s$ 是采样率。如果使用 normalized frequency，通常取 $f_s=1$，这一项可以省略。

## 3. 第一阶段 FFT 的归一化要保持一致

NumPy 和 MATLAB 默认 FFT 不除以 $N^{\prime}$：

```python
X = np.fft.fft(blocks, axis=1)
```

这种情况下，通常用窗能量 $U$ 做谱密度归一化。

如果自己使用 normalized FFT：

```python
X = np.fft.fft(blocks, axis=1) / Np
```

那么后面的尺度会多出 $1/N^{\prime 2}$，需要相应调整。

工程上建议：

> 第一阶段 FFT 不归一化，只在最后统一除以 $P U$ 或 $P f_s U$。

## 4. Coherence 归一化是另一层

如果最终要计算 spectral coherence，不只是 SCF，还需要再除以两个 PSD 项。

non-conjugate coherence 通常写为：

$$
C_x^\alpha(f)
=
\frac{S_x^\alpha(f)}
{\left[
S_x^0(f+\alpha/2)
S_x^0(f-\alpha/2)
\right]^{1/2}}
$$

这个归一化会把结果变成无量纲，通常幅度在 $[0,1]$ 附近，更适合检测 cycle frequency。

## 5. $f$ 和 $\alpha$ 的归一化发生在坐标映射阶段

前面几节讨论的是谱幅值归一化。频率坐标 $f$ 和循环频率坐标 $\alpha$ 的归一化是另一件事。

在离散采样信号中，FAM 内部通常使用 normalized frequency：

$$
f_{\text{norm}}=\frac{f_{\text{Hz}}}{f_s}
$$

$$
\alpha_{\text{norm}}=\frac{\alpha_{\text{Hz}}}{f_s}
$$

单位是 cycles/sample。

### 第一阶段 FFT 建立频率通道时

短时 FFT 的频率 bin 本来就是 normalized frequency：

$$
f_k=\frac{k}{N^{\prime}}
$$

如果使用 `fftshift`，则通常写成：

$$
f_k=\frac{k-N^{\prime}/2}{N^{\prime}}
$$

此时频率范围通常为：

$$
f_k\in[-0.5,0.5)
$$

所以从 Step 3 开始，$f_k$ 就应当被视为归一化频率。

### Phase-shift 阶段

phase-shift 使用：

$$
e^{-j2\pi f_k pL}
$$

其中 $pL$ 是样本数，因此 $f_k$ 必须是 cycles/sample。如果使用 Hz，则应写成：

$$
e^{-j2\pi f_{\text{Hz}}pLT_s}
$$

二者等价，因为：

$$
f_{\text{norm}}=f_{\text{Hz}}T_s=\frac{f_{\text{Hz}}}{f_s}
$$

### Step 5 映射 $(f,\alpha)$ 时

FAM 最终坐标由：

$$
f=\frac{f_k+f_l}{2}
$$

$$
\alpha=(f_k-f_l)+\frac{q_c}{PL}
$$

得到。

这里的 $f_k$、$f_l$ 和 $q_c/(PL)$ 都是 normalized frequency，所以得到的 $f$ 和 $\alpha$ 也是 normalized frequency。

因此，$f$ 和 $\alpha$ 的归一化发生在频率坐标轴构造和 $(f,\alpha)$ 映射阶段，而不是发生在谱幅值归一化阶段。

### 输出 Hz 时再反归一化

如果最终需要用物理频率单位展示或保存结果，再乘以采样率：

$$
f_{\text{Hz}}=f_{\text{norm}}f_s
$$

$$
\alpha_{\text{Hz}}=\alpha_{\text{norm}}f_s
$$

一句话总结：

> FAM 中 $f$ 和 $\alpha$ 应该从一开始就用 normalized frequency 参与计算，尤其是在 phase-shift 和 $(f,\alpha)$ 映射阶段；只有最终显示或和物理频率比较时，才乘以 $f_s$ 转回 Hz。

## 推荐实现形式

如果使用 normalized frequency：

```python
U = np.sum(np.abs(window)**2)

Ykl = X_tilde[:, k] * np.conj(Y_tilde[:, l])
Z = np.fft.fft(Ykl)

Skl = Z / (P * U)
```

如果需要保留 Hz 下的谱密度单位：

```python
Skl = Z / (P * fs * U)
```

## 总结

FAM 的基本归一化通常可以写成：

$$
\boxed{
\hat{S}_{xy}^{\alpha}(f)
=
\frac{1}{PU}
\operatorname{FFT}_r
\left\{
\tilde{X}[r,k]\tilde{Y}^*[r,l]
\right\}
}
$$

如果需要物理频率单位，则使用：

$$
\boxed{
\hat{S}_{xy}^{\alpha}(f)
=
\frac{1}{P f_s U}
\operatorname{FFT}_r
\left\{
\tilde{X}[r,k]\tilde{Y}^*[r,l]
\right\}
}
$$

如果只关心谱峰位置，常数因子影响不大；如果要比较幅度、估计 coherence 或和理论 SCF 对齐，就必须明确这些归一化。
