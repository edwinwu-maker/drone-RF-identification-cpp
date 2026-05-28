---
title: "PySDR: 使用 Python 学习 SDR 与 DSP 指南（中文翻译）"
source: "https://pysdr.org/content/cyclostationary.html"
author:
  - "[[Dr. Marc Lichtman - marc@pysdr.org]]"
published:
created: 2026-05-26
description: "PySDR 第 22 章 Cyclostationary Processing 的中文翻译，公式已整理为更适合 Obsidian 渲染的 LaTeX。"
tags:
  - "clippings"
  - "translation"
---

## 22\. Cyclostationary Processing

共同作者：[Sam Brown](https://www.linkedin.com/in/samuel-brown-vt)

本章解释 cyclostationary signal processing，也称 CSP。这是 RF signal processing 中相对小众的一类方法，用于分析或检测具有 cyclostationary property 的信号，尤其适用于很低 SNR 的场景。大多数现代数字调制信号都具有这类性质。本章覆盖 Cyclic Autocorrelation Function（CAF）、Spectral Correlation Function（SCF）、Spectral Coherence Function（COH）、这些函数的 conjugate version，以及它们的应用。章节中包含多个完整 Python 实现，示例涉及 BPSK、QPSK、OFDM 和多个混合信号。

## Introduction

Cyclostationary signal processing（CSP，或简称 cyclostationary processing）是一组利用实际通信信号中 cyclostationary property 的技术。这类信号包括 AM/FM/TV broadcast、cellular、WiFi 等调制信号，也包括 radar signal，以及其他统计量具有周期性的信号。大量传统 signal processing 方法假设信号是 stationary 的，即均值、方差和高阶矩等统计量不随时间变化。然而，大多数真实 RF 信号是 cyclostationary 的，也就是说信号统计量会随时间*周期性*变化。CSP 技术利用这种性质，可用于检测噪声中的信号、进行 modulation recognition，以及分离在时间和频率上重叠的信号。

如果读完本章并用 Python 练习后还想深入学习 CSP，可以参考 William Gardner 1994 年的教材 [Cyclostationarity in Communications and Signal Processing](https://faculty.engineering.ucdavis.edu/gardner/wp-content/uploads/sites/146/2014/05/Cyclostationarity.pdf)、1987 年的教材 [Statistical Spectral Analysis](https://faculty.engineering.ucdavis.edu/gardner/wp-content/uploads/sites/146/2013/02/Statistical_Spectral_Analysis_A_Nonprobabilistic_Theory.pdf)，或者 Chad Spooner 的 [blog posts collection](https://cyclostationary.blog/)。

这里有一个其他教材中通常没有的资源：在 SCF 小节末尾有一个 interactive JavaScript app，可以直接在浏览器中调整示例信号和 SCF 参数，观察 SCF 如何变化。这些交互式 demo 对所有人免费开放，主要依靠 PySDR [Patreon](https://www.patreon.com/PySDR) 成员支持。

## Review of Autocorrelation

即使你认为自己已经熟悉 autocorrelation function，也值得先复习一下，因为它是 CSP 的基础。Autocorrelation function 衡量一个信号与其时间平移版本之间的相似性，也就是 correlation。直观上，它表示信号呈现重复行为的程度。信号 $x(t)$ 的 autocorrelation 定义为：

$$
R_x(\tau)=E[x(t)x^*(t-\tau)]
$$

其中 $E$ 是 expectation operator，$\tau$ 是 time delay，$*$ 表示 complex conjugate。在离散时间、有限样本的情况下，也就是我们更关心的情况，它变为：

$$
R_x(\tau)=\frac{1}{N}\sum_{n=-N/2}^{N/2}x\left[n+\frac{\tau}{2}\right]x^*\left[n-\frac{\tau}{2}\right]
$$

其中 $N$ 是信号样本数。

如果信号在某种意义上具有周期性，例如 QPSK 信号重复出现的 symbol shape，那么在一系列 $\tau$ 上计算的 autocorrelation 也会具有周期性。例如，如果一个 QPSK 信号每个 symbol 有 8 个 samples，那么当 $\tau$ 是 8 的整数倍时，相似性度量会明显强于其他 $\tau$。Autocorrelation 的这个周期就是 CSP 技术最终要检测的对象。

## The Cyclic Autocorrelation Function (CAF)

上一节讨论过，我们希望找出 autocorrelation 中何时存在周期性。回忆 Fourier transform 公式：如果想测试某个频率 $f$ 在任意信号 $x(t)$ 中有多强，可以计算：

$$
X(f)=\int x(t)e^{-j2\pi ft}\,dt
$$

因此，如果想找 autocorrelation 中的周期性，只需计算：

$$
R_x(\tau,\alpha)=\lim_{T\rightarrow\infty}\frac{1}{T}\int_{-T/2}^{T/2}x(t+\tau/2)x^*(t-\tau/2)e^{-j2\pi\alpha t}\,dt
$$

离散时间形式为：

$$
R_x(\tau,\alpha)=\frac{1}{N}\sum_{n=-N/2}^{N/2}x\left[n+\frac{\tau}{2}\right]x^*\left[n-\frac{\tau}{2}\right]e^{-j2\pi\alpha n}
$$

这个式子用于测试频率 $\alpha$ 的强度，称为 Cyclic Autocorrelation Function（CAF）。另一种理解方式是：CAF 是描述这种周期性的 Fourier series coefficients。换句话说，CAF 表示信号 autocorrelation 中各个 harmonic 的幅度与相位。我们用 cyclostationary 这个词描述具有周期或近似周期 autocorrelation 的信号。CAF 是传统 autocorrelation function 面向 cyclostationary signals 的扩展。

CAF 是 delay $\tau$ 与 cycle frequency $\alpha$ 的二元函数。CSP 中的 cycle frequency 表示信号统计量变化的速率；对于 CAF 来说，对应 second-order moment 或 variance。因此，cycle frequency 往往对应通信信号中的显著周期行为，例如调制 symbol。后面会看到 BPSK 信号的 symbol rate 及其整数倍 harmonic 如何表现为 CAF 中的 cycle frequency。

在 Python 中，给定 baseband signal `samples`、`alpha` 和 `tau`，CAF 可按如下方式计算：

```python
CAF = (np.exp(1j * np.pi * alpha * tau) *
       np.sum(samples * np.conj(np.roll(samples, tau)) *
              np.exp(-2j * np.pi * alpha * np.arange(N))))
```

这里使用 `np.roll()` 将其中一组 samples 平移 $\tau$，因为实际只能平移整数个 samples。如果同时向相反方向平移两组 samples，就会跳过一半的 shift。还需要加入一个 frequency shift，用来补偿一次只在一侧平移 1 个 sample 的事实，而不是像基础 CAF 公式那样两侧各平移半个 sample。这个 shift 的频率是 `alpha/2`。

为了用 Python 观察 CAF，先模拟一个示例信号。这里使用 rectangular BPSK signal，也就是没有 pulse shaping 的 BPSK，每个 symbol 有 20 个 samples，并加入 white Gaussian noise（AWGN）。我们还会给 BPSK 信号施加 frequency offset，后面可以展示 cyclostationary processing 如何同时估计 frequency offset 和 cyclic frequency。这个 frequency offset 相当于接收机没有完全对准信号中心，可能稍微偏一点，也可能偏很多，但不能偏到让信号超出采样带宽。

下面的代码生成后续两个小节使用的 IQ samples：

```python
N = 100000 # number of samples to simulate
f_offset = 0.2 # Hz normalized
sps = 20 # cyclic freq (alpha) will be 1/sps or 0.05 Hz normalized

symbols = np.random.randint(0, 2, int(np.ceil(N/sps))) * 2 - 1 # random 1's and -1's
bpsk = np.repeat(symbols, sps)  # repeat each symbol sps times to make rectangular BPSK
bpsk = bpsk[:N]  # clip off the extra samples
bpsk = bpsk * np.exp(2j * np.pi * f_offset * np.arange(N)) # Freq shift up the BPSK, this is also what makes it complex
noise = np.random.randn(N) + 1j*np.random.randn(N) # complex white Gaussian noise
samples = bpsk + 0.1*noise  # add noise to the signal
```

由于本章中绝对 sample rate 和 symbol rate 并不重要，我们使用 normalized frequency。这等价于令 sample rate 为 1 Hz，因此信号必须位于 -0.5 到 +0.5 Hz 之间。你不会在代码片段中看到 `sample_rate` 变量，这是有意为之；我们用 samples per symbol（`sps`）来工作。

先看一下未做任何 CSP 之前，信号本身的 power spectral density（PSD，也就是 FFT）：

[![PSD of BPSK used for CAF](https://pysdr.org/_images/psd_of_bpsk_used_for_caf.svg)](https://pysdr.org/_images/psd_of_bpsk_used_for_caf.svg)

可以看到我们施加的 0.2 Hz frequency shift。每个 symbol 20 个 samples 使信号相对较窄，但由于没有 pulse shaping，信号在频域中衰减很慢。

现在在正确的 alpha 上，并在一系列 tau 上计算 CAF。这里先使用 $\tau$ 从 -50 到 +50。正确的 alpha 是 samples per symbol 的倒数，也就是 $1/20=0.05$ Hz。Python 中可通过遍历 tau 生成 CAF：

```python
# CAF only at the correct alpha
alpha_of_interest = 1/sps # equates to 0.05 Hz
taus = np.arange(-50, 51)
CAF = np.zeros(len(taus), dtype=complex)
for i in range(len(taus)):
    CAF[i] = (np.exp(1j * np.pi * alpha_of_interest * taus[i]) * # This term is to make up for the fact we're shifting by 1 sample at a time, and only on one side
              np.sum(samples * np.conj(np.roll(samples, taus[i])) *
                     np.exp(-2j * np.pi * alpha_of_interest * np.arange(N))))
```

用 `plt.plot(taus, np.real(CAF))` 绘制 `CAF` 的实部：

[![CAF at correct alpha](https://pysdr.org/_images/caf_at_correct_alpha.svg)](https://pysdr.org/_images/caf_at_correct_alpha.svg)

图形看起来有点奇怪，但要记住 tau 表示 time domain。关键点是：在这个 alpha 上 CAF 有大量能量，因为它对应信号中的一个 cyclic frequency。为了证明这一点，可以看错误 alpha（例如 0.08 Hz）下的 CAF：

[![CAF at incorrect alpha](https://pysdr.org/_images/caf_at_incorrect_alpha.svg)](https://pysdr.org/_images/caf_at_incorrect_alpha.svg)

注意 y 轴，此时 CAF 中的能量小得多。上面看到的具体图案现在不必过度关注，学习下一节 SCF 后会更容易理解。

还可以在一系列 alpha 上计算 CAF，并在每个 alpha 上通过取 magnitude 后求和或求平均来得到 CAF power。把这些 power 随 alpha 绘制出来，就能看到信号中 cyclic frequency 对应的尖峰。下面代码增加了一个 `for` loop，并使用 0.005 Hz 的 alpha step size。注意，这会运行较长时间：

```python
alphas = np.arange(0, 0.5, 0.005)
CAF = np.zeros((len(alphas), len(taus)), dtype=complex)
for j in range(len(alphas)):
    for i in range(len(taus)):
        CAF[j, i] = (np.exp(1j * np.pi * alphas[j] * taus[i]) *
                     np.sum(samples * np.conj(np.roll(samples, taus[i])) *
                            np.exp(-2j * np.pi * alphas[j] * np.arange(N))))
CAF_magnitudes = np.average(np.abs(CAF), axis=1) # at each alpha, calc power in the CAF
plt.plot(alphas, CAF_magnitudes)
plt.xlabel('Alpha')
plt.ylabel('CAF Power')
```

[![CAF average over alpha](https://pysdr.org/_images/caf_avg_over_alpha.svg)](https://pysdr.org/_images/caf_avg_over_alpha.svg)

除了预期的 0.05 Hz 尖峰，还能看到 0.05 Hz 的整数倍尖峰。这是因为 CAF 本质上是 Fourier series，fundamental frequency 的 harmonics 会出现在 CAF 中，尤其是在观察未做 pulse shaping 的 PSK/QAM 信号时。alpha = 0 处的能量是信号 PSD 的总功率；实际绘图时通常会把它置零，因为我们经常单独绘制 PSD，而且它会破坏后续 2D colormap 的 dynamic range。

CAF 很有用，但我们通常希望观察 cyclic frequency *over RF frequency*，而不只是单独看 cyclic frequency。这就引出下一节的 Spectral Correlation Function（SCF）。

## The Spectral Correlation Function (SCF)

正如 CAF 展示信号 autocorrelation 中的周期性，SCF 展示信号 PSD 中的周期性。Autocorrelation 与 PSD 实际上是一对 Fourier transform pair，因此 CAF 与 SCF 也是 Fourier transform pair 并不意外。这个关系称为 *Cyclic Wiener Relationship*。当考虑到 $\alpha=0$ 时 CAF 和 SCF 分别就是 autocorrelation 和 PSD，这一点会更自然。

可以直接对 CAF 做 Fourier transform 得到 SCF。回到每个 symbol 20 个 samples 的 BPSK 信号，在正确 alpha（0.05 Hz）上观察 SCF。只需对 CAF 做 FFT 并绘制 magnitude：

```python
f = np.linspace(-0.5, 0.5, len(taus))
SCF = np.fft.fftshift(np.fft.fft(CAF))
plt.plot(f, np.abs(SCF))
plt.xlabel('Frequency')
plt.ylabel('SCF')
```

[![FFT of CAF](https://pysdr.org/_images/fft_of_caf.svg)](https://pysdr.org/_images/fft_of_caf.svg)

可以看到模拟 BPSK 时施加的 0.2 Hz frequency offset。它与 cyclic frequency 或 samples per symbol 无关。这也是 CAF 在 tau domain 看起来像正弦的原因：主导因素是示例中相对较高的 RF frequency。

遗憾的是，对成千上万个甚至上百万个 alpha 这样计算，计算量极大。直接对 CAF 做 FFT 的另一个缺点是没有 averaging。高效、实用地计算 SCF 通常需要某种 averaging，可以是 time-based，也可以是 frequency-based。下面两节会讨论。

原文在这里提供了一个 interactive JavaScript app，用于调整 signal 和 SCF 参数建立直觉。信号频率是很直接的旋钮，可以展示 SCF 识别 RF frequency 的能力。取消勾选 Rectangular Pulse 以加入 pulse shaping，并调整不同 roll-off 值。注意，使用默认 alpha-step 时，并不是所有 samples per symbol 都会在 SCF 中形成可见尖峰。降低 alpha-step 可以改善这一点，但会增加处理时间。

## Frequency Smoothing Method (FSM)

有了 SCF 的概念理解后，看如何高效计算它。先考虑 periodogram，它只是信号 Fourier transform 的 squared magnitude：

$$
I(u,f)=\frac{1}{N}|X(u,f)|^2
$$

通过两个频移后的 Fourier transform 相乘，可以得到 cyclic periodogram：

$$
I(u,f,\alpha)=\frac{1}{N}X(u,f+\alpha/2)X^*(u,f-\alpha/2)
$$

这两个式子分别是 PSD 和 SCF 的估计。要得到 SCF 的真实值，必须对时间或频率做 averaging。对时间 averaging 称为 Time Smoothing Method（TSM）：

$$
S_X(f,\alpha)=\lim_{T\rightarrow\infty}\frac{1}{T}\lim_{U\rightarrow\infty}\frac{1}{U}\int_{-U/2}^{U/2}X(t,f+\alpha/2)X^*(t,f-\alpha/2)\,dt
$$

对频率 averaging 称为 Frequency Smoothing Method（FSM）：

$$
S_X(f,\alpha)=\lim_{\Delta\rightarrow0}\lim_{T\rightarrow\infty}\frac{1}{T}g_\Delta(f)\otimes\left[X(t,f+\alpha/2)X^*(t,f-\alpha/2)\right]
$$

其中 $g_\Delta(f)$ 是 frequency smoothing function，用于在一个较小频率范围内求平均。

下面是 FSM 的最小 Python 实现。FSM 是一种基于频率 averaging 的 SCF 计算方法。它先通过两个 shifted FFT 相乘得到 cyclic periodogram，然后用 window function 对每个 slice 进行滤波；window 长度决定最终 SCF estimate 的 resolution。更长的 window 会得到更平滑但 resolution 更低的结果，更短的 window 则相反。

```python
alphas = np.arange(0, 0.3, 0.001)
Nw = 256 # window length
N = len(samples) # signal length
window = np.hanning(Nw)

X = np.fft.fftshift(np.fft.fft(samples)) # FFT of entire signal

num_freqs = int(np.ceil(N/Nw)) # freq resolution after decimation
SCF = np.zeros((len(alphas), num_freqs), dtype=complex)
for i in range(len(alphas)):
    shift = int(alphas[i] * N/2)
    SCF_slice = np.roll(X, -shift) * np.conj(np.roll(X, shift))
    SCF[i, :] = np.convolve(SCF_slice, window, mode='same')[::Nw] # apply window and decimate by Nw
SCF = np.abs(SCF)
SCF[0, :] = 0 # null out alpha=0 which is just the PSD of the signal, it throws off the dynamic range

extent = (-0.5, 0.5, float(np.max(alphas)), float(np.min(alphas)))
plt.imshow(SCF, aspect='auto', extent=extent, vmax=np.max(SCF)/2)
plt.xlabel('Frequency [Normalized Hz]')
plt.ylabel('Cyclic Frequency [Normalized Hz]')
plt.show()
```

注意，由于 shift 的计算方式会四舍五入为整数个 samples，一次处理至少 `2 / alpha_resolution` 个 samples 会更合适。

对前面使用的 rectangular BPSK 信号计算 SCF：每个 symbol 20 个 samples，cyclic frequency 范围 0 到 0.3，step size 为 0.001：

[![SCF with the Frequency Smoothing Method (FSM), showing cyclostationary signal processing](https://pysdr.org/_images/scf_freq_smoothing.svg)](https://pysdr.org/_images/scf_freq_smoothing.svg)

这个方法的优点是只需要一次大型 FFT；缺点是 smoothing 需要大量 convolution。注意 `convolve` 后的 `[::Nw]` decimation。它是可选的，但强烈建议使用，因为这样能减少最终需要显示的 pixels 数量；同时根据 SCF 的计算方式，用 `Nw` 做 decimation 并不会丢掉信息。

## Time Smoothing Method (TSM)

接下来看 TSM 的 Python 实现。下面代码把信号分成 `num_windows` 个 block，每个 block 长度为 `Nw`，重叠量为 `Noverlap`。Overlap 并非必需，但通常能让输出更好看。信号随后乘以 window function（这里是 Hanning，也可以是其他 window）并做 FFT。SCF 通过对每个 block 的结果 averaging 得到。Window length 与 FSM 中作用相同，决定 resolution 与 smoothness 的取舍。

```python
alphas = np.arange(0, 0.3, 0.001)
Nw = 256 # window length
N = len(samples) # signal length
Noverlap = int(2/3*Nw) # block overlap
num_windows = int((N - Noverlap) / (Nw - Noverlap)) # Number of windows
window = np.hanning(Nw)

SCF = np.zeros((len(alphas), Nw), dtype=complex)
for ii in range(len(alphas)): # Loop over cyclic frequencies
    neg = samples * np.exp(-1j*np.pi*alphas[ii]*np.arange(N))
    pos = samples * np.exp( 1j*np.pi*alphas[ii]*np.arange(N))
    for i in range(num_windows):
        pos_slice = window * pos[i*(Nw-Noverlap):i*(Nw-Noverlap)+Nw]
        neg_slice = window * neg[i*(Nw-Noverlap):i*(Nw-Noverlap)+Nw]
        SCF[ii, :] += np.fft.fft(neg_slice) * np.conj(np.fft.fft(pos_slice)) # Cross Cyclic Power Spectrum
SCF = np.fft.fftshift(SCF, axes=1) # shift the RF freq axis
SCF = np.abs(SCF)
SCF[0, :] = 0 # null out alpha=0 which is just the PSD of the signal, it throws off the dynamic range

extent = (-0.5, 0.5, float(np.max(alphas)), float(np.min(alphas)))
plt.imshow(SCF, aspect='auto', extent=extent, vmax=np.max(SCF)/2)
plt.xlabel('Frequency [Normalized Hz]')
plt.ylabel('Cyclic Frequency [Normalized Hz]')
plt.show()
```

[![SCF with the Time Smoothing Method (TSM), showing cyclostationary signal processing](https://pysdr.org/_images/scf_time_smoothing.svg)](https://pysdr.org/_images/scf_time_smoothing.svg)

结果与 FSM 大致相同。

## Pulse-Shaped BPSK

到目前为止，我们只研究了 *rectangular* BPSK signal 的 CSP。然而在真实 RF 系统中，几乎不会看到 rectangular pulses；一个例外是 direct-sequence spread spectrum（DSSS）中的 BPSK chipping sequence，它通常近似 rectangular。

现在观察带 raised-cosine（RC）pulse shape 的 BPSK signal。RC pulse shape 是数字通信中常用的 pulse shape，相比 rectangular BPSK 可减少 occupied bandwidth。如 [Pulse Shaping](https://pysdr.org/content/pulse_shaping.html#pulse-shaping-chapter) 章节所述，RC pulse shape 在 time domain 中为：

$$
h(t)=\operatorname{sinc}\left(\frac{t}{T}\right)\frac{\cos\left(\frac{\pi\beta t}{T}\right)}{1-\left(\frac{2\beta t}{T}\right)^2}
$$

$\beta$ 参数决定 filter 在 time domain 中衰减的快慢，它与 frequency domain 中的衰减速度成反比：

[![The raised cosine filter in the frequency domain with a variety of roll-off values](https://pysdr.org/_images/raised_cosine_freq.svg)](https://pysdr.org/_images/raised_cosine_freq.svg)

注意 $\beta=0$ 对应无限长 pulse shape，因此不实用。还要注意 $\beta=1$ 并不对应 rectangular pulse shape。实际中 roll-off factor 通常选在 0.2 到 0.4 之间。

下面代码模拟使用 raised-cosine pulse shaping 的 BPSK 信号。注意前 5 行和最后 4 行与 rectangular BPSK 相同：

```python
N = 100000 # number of samples to simulate
f_offset = 0.2 # Hz normalized
sps = 20 # cyclic freq (alpha) will be 1/sps or 0.05 Hz normalized
num_symbols = int(np.ceil(N/sps))
symbols = np.random.randint(0, 2, num_symbols) * 2 - 1 # random 1's and -1's

pulse_train = np.zeros(num_symbols * sps)
pulse_train[::sps] = symbols # easier explained by looking at an example output
print(pulse_train[0:96].astype(int))

# Raised-Cosine Filter for Pulse Shaping
beta = 0.3 # roll-off parameter (avoid exactly 0.2, 0.25, 0.5, and 1.0)
num_taps = 101 # somewhat arbitrary
t = np.arange(num_taps) - (num_taps-1)//2
h = np.sinc(t/sps) * np.cos(np.pi*beta*t/sps) / (1 - (2*beta*t/sps)**2) # RC equation
bpsk = np.convolve(pulse_train, h, 'same') # apply the pulse shaping

bpsk = bpsk[:N]  # clip off the extra samples
bpsk = bpsk * np.exp(2j * np.pi * f_offset * np.arange(N)) # Freq shift up the BPSK, this is also what makes it complex
noise = np.random.randn(N) + 1j*np.random.randn(N) # complex white Gaussian noise
samples = bpsk + 0.1*noise  # add noise to the signal
```

`pulse_train` 就是按顺序排列的 symbols，每个 symbol 后面跟着 `sps - 1` 个零，例如：

```bash
[ 1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  0
  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  0  0  0  0  0
  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  0
  0  0  0  0  0  0  0  0 -1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0...
```

下图显示加入 noise 和 frequency shift 之前，time domain 中的 pulse-shaped BPSK：

[![Pulse-shaped BPSK signal with a raised-cosine pulse shape](https://pysdr.org/_images/pulse_shaped_BSPK.svg)](https://pysdr.org/_images/pulse_shaped_BSPK.svg)

现在计算 roll-off 分别为 0.3、0.6 和 0.9 的 pulse-shaped BPSK 的 SCF。为了公平比较，使用同样的 0.2 Hz frequency shift、FSM implementation、FSM 参数和 symbol length：

`beta = 0.3`：

[![SCF of pulse-shaped BPSK using the Frequency Smoothing Method (FSM) beta 0.3](https://pysdr.org/_images/scf_freq_smoothing_pulse_shaped_bpsk.svg)](https://pysdr.org/_images/scf_freq_smoothing_pulse_shaped_bpsk.svg)

`beta = 0.6`：

[![SCF of pulse-shaped BPSK using the Frequency Smoothing Method (FSM) beta 0.6](https://pysdr.org/_images/scf_freq_smoothing_pulse_shaped_bpsk2.svg)](https://pysdr.org/_images/scf_freq_smoothing_pulse_shaped_bpsk2.svg)

`beta = 0.9`：

[![SCF of pulse-shaped BPSK using the Frequency Smoothing Method (FSM) beta 0.9](https://pysdr.org/_images/scf_freq_smoothing_pulse_shaped_bpsk3.svg)](https://pysdr.org/_images/scf_freq_smoothing_pulse_shaped_bpsk3.svg)

三种情况下，frequency axis 上不再出现原先的 sidelobes，cyclic frequency axis 上也没有 fundamental cyclic frequency 的强 harmonic。这是因为 raised-cosine pulse shape 的 spectral containment 明显好于 rectangular pulse shape，sidelobes 更低。因此 pulse-shaped signals 的 SCF 往往比 rectangular signals 更干净，看起来像一个 single spike，上方带有一些 smear。这个结论不仅适用于 BPSK，也适用于所有 single carrier digitally modulated signals。随着 beta 增大，信号占用更宽 bandwidth，frequency axis 上的尖峰也会变宽。

## SNR and Number of Symbols

即将补充。这里会讨论为什么到某个程度后，更高 SNR 不再有帮助，反而需要更多 symbols；还会讨论 packet-based waveform 为什么会导致每次 transmission 中 symbol 数有限。

## QPSK and Higher-Order Modulation

即将补充。内容将包括 QPSK、更高阶 PSK、QAM，以及 higher-order cyclic moments 和 cumulants 的简要介绍。

## Multiple Overlapping Signals

到目前为止，我们每次只观察一个信号。但如果接收信号包含多个独立信号，并且它们在 frequency、time，甚至 cyclic frequency 上重叠，也就是具有相同 samples per symbol，该怎么办？如果信号完全不在 frequency 上重叠，可以用简单 filtering 分离它们，并在它们高于 noise floor 时用 PSD 检测。如果它们不在 time 上重叠，可以检测每次 transmission 的 rising edge 和 falling edge，再用 time-gating 分离各自的 signal processing。在 CSP 中，我们通常关注的是检测那些在 time 和 frequency 上都重叠，但 cyclic frequency 不同的信号。

模拟三个具有不同属性的信号：

- Signal 1: Rectangular BPSK with 20 samples per symbol and 0.2 Hz frequency offset
- Signal 2: Pulse-shaped BPSK with 20 samples per symbol, -0.1 Hz frequency offset, and 0.35 roll-off
- Signal 3: Pulse-shaped QPSK with 4 samples per symbol, 0.2 Hz frequency offset, and 0.21 roll-off

可以看到，有两个信号具有相同 cyclic frequency，还有两个信号具有相同 RF frequency。这让我们可以实验不同程度的参数重叠。

每个信号都会应用一个任意 fractional delay filter，也就是非整数 delay，避免因为样本完全对齐而产生奇怪 artifact。相关内容可参考 [Synchronization](https://pysdr.org/content/sync.html#sync-chapter) 章节。Rectangular BPSK signal 的功率被调低，因为 rectangular-pulsed signals 表现出很强的 cyclostationary properties，容易主导 SCF。

展开查看模拟三个信号的 Python 代码：

```python
N = 1000000 # number of samples to simulate

def fractional_delay(x, delay):
    N = 21 # number of taps
    n = np.arange(-N//2, N//2) # ...-3,-2,-1,0,1,2,3...
    h = np.sinc(n - delay) # calc filter taps
    h *= np.hamming(N) # window the filter to make sure it decays to 0 on both sides
    h /= np.sum(h) # normalize to get unity gain, we don't want to change the amplitude/power
    return np.convolve(x, h, 'same') # apply filter

# Signal 1, Rect BPSK
sps = 20
f_offset = 0.2
signal1 = np.repeat(np.random.randint(0, 2, int(np.ceil(N/sps))) * 2 - 1, sps)
signal1 = signal1[:N] * np.exp(2j * np.pi * f_offset * np.arange(N))
signal1 = fractional_delay(signal1, 0.12345)

# Signal 2, Pulse-shaped BPSK
sps = 20
f_offset = -0.1
beta = 0.35
symbols = np.random.randint(0, 2, int(np.ceil(N/sps))) * 2 - 1
pulse_train = np.zeros(int(np.ceil(N/sps)) * sps)
pulse_train[::sps] = symbols
t = np.arange(101) - (101-1)//2
h = np.sinc(t/sps) * np.cos(np.pi*beta*t/sps) / (1 - (2*beta*t/sps)**2)
signal2 = np.convolve(pulse_train, h, 'same')
signal2 = signal2[:N] * np.exp(2j * np.pi * f_offset * np.arange(N))
signal2 = fractional_delay(signal2, 0.52634)

# Signal 3, Pulse-shaped QPSK
sps = 4
f_offset = 0.2
beta = 0.21
data = x_int = np.random.randint(0, 4, int(np.ceil(N/sps))) # 0 to 3
data_degrees = data*360/4.0 + 45 # 45, 135, 225, 315 degrees
symbols = np.cos(data_degrees*np.pi/180.0) + 1j*np.sin(data_degrees*np.pi/180.0)
pulse_train = np.zeros(int(np.ceil(N/sps)) * sps, dtype=complex)
pulse_train[::sps] = symbols
t = np.arange(101) - (101-1)//2
h = np.sinc(t/sps) * np.cos(np.pi*beta*t/sps) / (1 - (2*beta*t/sps)**2)
signal3 = np.convolve(pulse_train, h, 'same')
signal3 = signal3[:N] * np.exp(2j * np.pi * f_offset * np.arange(N))
signal3 = fractional_delay(signal3, 0.3526)

# Add noise
noise = np.random.randn(N) + 1j*np.random.randn(N)
samples = 0.5*signal1 + signal2 + 1.5*signal3 + 0.1*noise
```

进入 CSP 前，先看这个信号的 PSD：

[![PSD of three different signals](https://pysdr.org/_images/psd_of_multiple_signals.svg)](https://pysdr.org/_images/psd_of_multiple_signals.svg)

Signal 1 和 Signal 3 位于 PSD 的正频率侧并且发生重叠，几乎只能看到更窄的 Signal 1 从中露出一点。也能从图中感受 noise level。

现在用 FSM 计算这些组合信号的 SCF：

[![SCF of three different signals using the Frequency Smoothing Method (FSM)](https://pysdr.org/_images/scf_freq_smoothing_pulse_multiple_signals.svg)](https://pysdr.org/_images/scf_freq_smoothing_pulse_multiple_signals.svg)

注意 Signal 1 虽然是 rectangular pulse-shaped，但它的 harmonics 大多被 Signal 3 上方的 cone 掩盖。回想 PSD 中 Signal 1 是藏在 Signal 3 后面的。通过 CSP，我们可以检测到 Signal 1 存在，并得到其 cyclic frequency 的近似值，进而用于同步。这就是 cyclostationary signal processing 的威力。

## Alternative CSP Features

SCF 不是检测信号 cyclostationarity 的唯一方式，尤其是在不关心 cyclic frequency over RF frequency 的情况下。一个概念和计算复杂度都很简单的方法是对信号的 **magnitude 做 FFT**，然后寻找尖峰。Python 中非常简单：

```python
samples_mag = np.abs(samples)
#samples_mag = samples * np.conj(samples) # pretty much the same as line above
magnitude_metric = np.abs(np.fft.fft(samples_mag))
```

这个方法本质上等价于先让信号乘以自身的 complex conjugate，再做 FFT。

绘制 metric 前，先把 DC component 置零，因为它包含大量能量，会破坏 dynamic range。还要去掉 FFT 输出的一半，因为 FFT 输入是 real，输出对称。随后绘制 metric 并观察尖峰：

```python
magnitude_metric = magnitude_metric[:len(magnitude_metric)//2] # only need half because input is real
magnitude_metric[0] = 0 # null out the DC component
f = np.linspace(-0.5, 0.5, len(samples))
plt.plot(f, magnitude_metric)
```

之后可以使用 peak finding algorithm，例如 SciPy 的 `signal.find_peaks()`。下图对 Multiple Overlapping Signals 小节中的三个信号分别绘制 `magnitude_metric`，然后绘制组合信号：

[![Metric for detecting cyclostationarity in a signal without using a CAF or SCF](https://pysdr.org/_images/non_csp_metric.svg)](https://pysdr.org/_images/non_csp_metric.svg)

Rectangular BPSK 的 harmonics 不幸与另一个信号的 cyclic frequencies 重叠，但这也展示了该替代方法的一个缺点：它不像 SCF 那样能观察 cyclic frequency over RF frequency。

虽然这个方法利用了信号中的 cyclostationarity，但可能因为过于简单，它通常不被视为严格意义上的 CSP technique。

对于寻找信号 RF frequency，也就是 carrier frequency offset，还有一个类似技巧。对 BPSK 信号，只需要对信号平方后做 FFT；它会在 carrier frequency offset 的两倍处出现尖峰。对 QPSK 信号，可以对信号的四次方做 FFT；它会在 carrier frequency offset 的四倍处出现尖峰。

```python
samples_squared = samples**2
squared_metric = np.abs(np.fft.fftshift(np.fft.fft(samples_squared)))/len(samples)
squared_metric[len(squared_metric)//2] = 0 # null out the DC component

samples_quartic = samples**4
quartic_metric = np.abs(np.fft.fftshift(np.fft.fft(samples_quartic)))/len(samples)
quartic_metric[len(quartic_metric)//2] = 0 # null out the DC component
```

可以在自己的模拟或采集信号上尝试这个方法；它在 CSP 之外也很有用。

## Spectral Coherence Function (COH)

*TLDR：spectral coherence function 是 SCF 的归一化版本，在某些场景下值得用它替代普通 SCF。*

另一个 cyclostationarity 度量是 Spectral Coherence Function（COH）。在许多情况下，它比 raw SCF 更有解释力。COH 对 SCF 进行归一化，使结果位于 -1 到 1 之间；实际通常观察 magnitude，所以范围为 0 到 1。这很有用，因为 raw SCF 同时包含信号 cyclostationarity 信息和 signal power spectrum 信息，而归一化会移除 power spectrum 信息，只留下 cyclic correlation 的影响。

为了理解 COH，可以回顾统计学中的 [correlation coefficient](https://en.wikipedia.org/wiki/Pearson_correlation_coefficient)。Correlation coefficient $\rho_{X,Y}$ 描述两个 random variables $X$ 和 $Y$ 的相关程度，范围为 -1 到 1。它定义为 covariance 除以 standard deviations 的乘积：

$$
\rho_{X,Y}=\frac{E[(X-\mu_X)(Y-\mu_Y)]}{\sigma_X\sigma_Y}
$$

COH 将这个概念扩展到 spectral correlation，用来量化信号在一个频率处的 PSD 与同一信号在另一个频率处的 PSD 的相关程度。这两个频率就是计算 SCF 时施加的 frequency shifts。计算 COH 时，先像之前一样计算 SCF，记作 $S_X(f,\alpha)$，然后用两个 shifted PSD terms 的乘积归一化，类似于用 standard deviations 的乘积归一化：

$$
\rho=C_x(f,\alpha)=\frac{S_X(f,\alpha)}{\sqrt{C_x^0(f+\alpha/2)C_x^0(f-\alpha/2)}}
$$

分母是新的关键部分。$C_x^0(f+\alpha/2)$ 和 $C_x^0(f-\alpha/2)$ 就是分别平移 $\alpha/2$ 和 $-\alpha/2$ 的 PSD。另一种理解是：SCF 是 cross-spectral density，也就是涉及两个输入信号的 power spectrum；分母中的 normalization terms 是 auto-spectral densities，也就是只涉及单个输入信号的 power spectra。

把它应用到 Python 代码中，具体是 frequency smoothing method（FSM）下的 SCF。由于 FSM 在 frequency domain 做 averaging，我们已经有 $C_x^0(f+\alpha/2)$ 和 $C_x^0(f-\alpha/2)$。在 Python 中它们就是 `np.roll(X, -shift)` 和 `np.roll(X, shift)`，因为 `X` 是信号做 FFT 后的结果。因此只需把二者相乘、开平方，再用 SCF slice 除以结果。注意这发生在 alpha loop 内部：

```python
COH_slice = SCF_slice / np.sqrt(np.roll(X, -shift) * np.roll(X, shift))
```

最后重复计算 final SCF slice 时使用的 convolve 和 decimation：

```python
COH[i, :] = np.convolve(COH_slice, window, mode='same')[::Nw]
```

展开查看同时生成并绘制 SCF 与 COH 的完整代码：

```python
alphas = np.arange(0, 0.3, 0.001)
Nw = 256 # window length
N = len(samples) # signal length
window = np.hanning(Nw)

X = np.fft.fftshift(np.fft.fft(samples)) # FFT of entire signal

num_freqs = int(np.ceil(N/Nw)) # freq resolution after decimation
SCF = np.zeros((len(alphas), num_freqs), dtype=complex)
COH = np.zeros((len(alphas), num_freqs), dtype=complex)
for i in range(len(alphas)):
    shift = int(alphas[i] * N/2)
    SCF_slice = np.roll(X, -shift) * np.conj(np.roll(X, shift))
    SCF[i, :] = np.convolve(SCF_slice, window, mode='same')[::Nw] # apply window and decimate by Nw
    COH_slice = SCF_slice / np.sqrt(np.roll(X, -shift) * np.roll(X, shift))
    COH[i, :] = np.convolve(COH_slice, window, mode='same')[::Nw] # apply the same windowing + decimation
SCF = np.abs(SCF)
COH = np.abs(COH)

# null out alpha=0 for both so that it doesnt hurt our dynamic range and ability to see the non-zero alphas
SCF[np.argmin(np.abs(alphas)), :] = 0
COH[np.argmin(np.abs(alphas)), :] = 0

extent = (-0.5, 0.5, float(np.max(alphas)), float(np.min(alphas)))
fig, [ax0, ax1] = plt.subplots(1, 2, figsize=(10, 5))
ax0.imshow(SCF, aspect='auto', extent=extent, vmax=np.max(SCF)/2)
ax0.set_xlabel('Frequency [Normalized Hz]')
ax0.set_ylabel('Cyclic Frequency [Normalized Hz]')
ax0.set_title('Regular SCF')
ax1.imshow(COH, aspect='auto', extent=extent, vmax=np.max(COH)/2)
ax1.set_xlabel('Frequency [Normalized Hz]')
ax1.set_title('Spectral Coherence Function (COH)')
plt.show()
```

现在对每个 symbol 20 个 samples、0.2 Hz frequency offset 的 rectangular BPSK 信号计算 COH 和普通 SCF：

[![SCF and COH of a rectangular BPSK signal with 20 samples per symbol and 0.2 Hz frequency offset](https://pysdr.org/_images/scf_coherence.svg)](https://pysdr.org/_images/scf_coherence.svg)

可以看到，在 COH 中 higher alphas 比在 SCF 中明显得多。对 pulse-shaped BPSK signal 运行同样代码，差异没有那么大：

[![SCF and COH of a pulse-shaped BPSK signal with 20 samples per symbol and 0.2 Hz frequency offset](https://pysdr.org/_images/scf_coherence_pulse_shaped.svg)](https://pysdr.org/_images/scf_coherence_pulse_shaped.svg)

实际应用中可以同时生成 SCF 和 COH，看哪个更适合。

## Conjugates

到目前为止，CAF 与 SCF 使用的公式都在第二项中使用了信号的 complex conjugate（$*$ 符号）：

$$
R_x(\tau,\alpha)=\lim_{T\rightarrow\infty}\frac{1}{T}\int_{-T/2}^{T/2}x(t+\tau/2)x^*(t-\tau/2)e^{-j2\pi\alpha t}\,dt
$$

$$
S_X(f,\alpha)=\lim_{T\rightarrow\infty}\frac{1}{T}\lim_{U\rightarrow\infty}\frac{1}{U}\int_{-U/2}^{U/2}X(t,f+\alpha/2)X^*(t,f-\alpha/2)\,dt
$$

不过，CAF 和 SCF 还有一种不包含 conjugate 的替代形式。这些形式分别称为 *conjugate CAF* 和 *conjugate SCF*。命名有点容易混淆，但主要记住：CAF/SCF 有一个 normal version，也有一个 conjugate version。Conjugate version 可用于从信号中提取更多信息，但是否必要取决于信号。Conjugate CAF 和 SCF 定义为：

$$
R_{x^*}(\tau,\alpha)=\lim_{T\rightarrow\infty}\frac{1}{T}\int_{-T/2}^{T/2}x(t+\tau/2)x(t-\tau/2)e^{-j2\pi\alpha t}\,dt
$$

$$
S_{x^*}(f,\alpha)=\lim_{T\rightarrow\infty}\frac{1}{T}\lim_{U\rightarrow\infty}\frac{1}{U}\int_{-U/2}^{U/2}X(t,f+\alpha/2)X(t,f-\alpha/2)\,dt
$$

它们与原始 CAF 和 SCF 相同，只是移除了 conjugate。离散时间版本也只是去掉 conjugate。

为了理解 conjugate forms 的意义，考虑 real-valued bandpass signal 的 quadrature representation：

$$
y(t)=x_I(t)\cos(2\pi f_ct+\phi)+x_Q(t)\sin(2\pi f_ct+\phi)
$$

$x_I(t)$ 和 $x_Q(t)$ 分别是信号的 in-phase（I）和 quadrature（Q）components。我们最终在 baseband 上用 CSP 处理的就是这些 IQ samples。

使用 Euler 公式 $e^{jx}=\cos(x)+j\sin(x)$，可将上式改写为 complex exponentials：

$$
y(t)=\frac{x_I(t)-jx_Q(t)}{2}e^{j2\pi f_ct+j\phi}+\frac{x_I(t)+jx_Q(t)}{2}e^{-j2\pi f_ct-j\phi}
$$

如果信号 bandwidth 远小于 carrier frequency $f_c$，这在 RF 应用中通常成立，就可以用 complex envelope（记为 $z(t)$）表示 real-valued signal $y(t)$：

$$
y(t)=z(t)e^{j2\pi f_ct+j\phi}+z^*(t)e^{-j2\pi f_ct-j\phi}
$$

这称为 complex-baseband representation。

回到 CAF，尝试计算 CAF 中称为 lag product 的部分，也就是 $x(t+\tau/2)x(t-\tau/2)$：

$$
\begin{aligned}
&\left(z(t+\tau/2)e^{j2\pi f_c(t+\tau/2)+j\phi}+z^*(t+\tau/2)e^{-j2\pi f_c(t+\tau/2)-j\phi}\right) \\
&\quad\times
\left(z(t-\tau/2)e^{j2\pi f_c(t-\tau/2)+j\phi}+z^*(t-\tau/2)e^{-j2\pi f_c(t-\tau/2)-j\phi}\right)
\end{aligned}
$$

虽然不一定一眼能看出，但这个结果包含四项，对应 $z(t)$ 的 conjugated 和 non-conjugated 的四种组合：

$$
\begin{aligned}
&z(t+\tau/2)z(t-\tau/2)e^{(\ldots)}\\
&z(t+\tau/2)z^*(t-\tau/2)e^{(\ldots)}\\
&z^*(t+\tau/2)z(t-\tau/2)e^{(\ldots)}\\
&z^*(t+\tau/2)z^*(t-\tau/2)e^{(\ldots)}
\end{aligned}
$$

事实证明，就可获得的信息而言，第 1 项和第 4 项基本等价，第 2 项和第 3 项也基本等价。因此真正关心的只有两种情况：conjugate case 和 non-conjugate case。总结来说，如果希望从 $y(t)$ 中获得完整统计信息，就需要考虑 conjugated 与 non-conjugated terms 的每种组合。

要用 frequency smoothing method 实现 conjugate SCF，除了移除 `conj()` 之外还需要一个额外步骤，因为这里做的是一次大 FFT，然后在 frequency domain averaging。Fourier transform 有一个性质：time domain 中的 complex conjugate 对应 frequency domain 翻转并 conjugate：

$$
x^*(t)\leftrightarrow X^*(-f)
$$

normal SCF 中第二项已经做过 complex conjugate，也就是代码 `SCF_slice = np.roll(X, -shift) * np.conj(np.roll(X, shift))`。当再次 complex conjugate 时，conjugate 会抵消，留下：

```python
SCF_slice = np.roll(X, -shift) * np.flip(np.roll(X, -shift - 1))
```

注意新增的 `np.flip()`，并且 `roll()` 需要反方向进行。Conjugate SCF 的完整 FSM 实现如下：

```python
alphas = np.arange(-1, 1, 0.01) # Conj SCF should be calculated from -1 to +1
Nw = 256 # window length
N = len(samples) # signal length
window = np.hanning(Nw)

X = np.fft.fftshift(np.fft.fft(samples)) # FFT of entire signal

num_freqs = int(np.ceil(N/Nw)) # freq resolution after decimation
SCF = np.zeros((len(alphas), num_freqs), dtype=complex)
for i in range(len(alphas)):
    shift = int(np.round(alphas[i] * N/2))
    SCF_slice = np.roll(X, -shift) * np.flip(np.roll(X, -shift - 1)) # THIS LINE IS THE ONLY DIFFERENCE
    SCF[i, :] = np.convolve(SCF_slice, window, mode='same')[::Nw]
SCF = np.abs(SCF)

extent = (-0.5, 0.5, float(np.min(alphas)), float(np.max(alphas)))
plt.imshow(SCF, aspect='auto', extent=extent, vmax=np.max(SCF)/2, origin='lower')
plt.xlabel('Frequency [Normalized Hz]')
plt.ylabel('Cyclic Frequency [Normalized Hz]')
plt.show()
```

Conjugate SCF 的另一个重要变化是 alpha 需要在 -1 到 +1 之间计算，而 normal SCF 因为 symmetry 只计算 0.0 到 0.5。观察示例信号的 conjugate SCF 后会直观看到原因。

Conjugate SCF 的意义是什么？先看每个 symbol 20 个 samples（cyclic frequency 为 0.05 Hz）、0.2 Hz frequency offset 的基本 rectangular BPSK 信号的 conjugate SCF：

[![Conjugate SCF of rectangular BPSK using the Frequency Smoothing Method (FSM)](https://pysdr.org/_images/scf_conj_rect_bpsk.svg)](https://pysdr.org/_images/scf_conj_rect_bpsk.svg)

本节最重要的 takeaway 是：conjugate SCF 中最终得到的是 cyclic frequency 加减 **两倍** carrier frequency offset 的尖峰，这里把 carrier frequency offset 记为 $f_c$。在 frequency axis 上，它会以 0 Hz 为中心，而不是以 $f_c$ 为中心。示例的 frequency offset 是 0.2 Hz，因此得到的尖峰位于 0.4 Hz 加减 0.05 Hz 的 cyclic frequency。记住 conjugate SCF 时，应该预期尖峰出现在：

$$
2f_c\pm\alpha
$$

再看相同 0.2 Hz offset、20 samples per symbol、0.3 roll-off 的 pulse-shaped BPSK：

[![Conjugate SCF of raised cosine pulse-shaped BPSK using the Frequency Smoothing Method (FSM)](https://pysdr.org/_images/scf_conj_pulseshaped_bpsk.svg)](https://pysdr.org/_images/scf_conj_pulseshaped_bpsk.svg)

这与前面看到的 BPSK normal SCF pattern 是一致的。

有趣的是，观察相同 0.2 Hz 和 20 samples per symbol 下 rectangular QPSK 的 conjugate SCF：

[![Conjugate SCF of rectangular QPSK using the Frequency Smoothing Method (FSM)](https://pysdr.org/_images/scf_conj_rect_qpsk.svg)](https://pysdr.org/_images/scf_conj_rect_qpsk.svg)

乍看可能像代码有 bug，但要看 colorbar，它表示颜色对应的数值。使用 `plt.imshow()` 自动缩放时，颜色会始终从输入 2D array 的最小值映射到最大值。对于 QPSK 的 conjugate SCF，整体输出都很低，因为事实是：*QPSK 的 conjugate SCF 中没有尖峰*。下面是相同 QPSK 输出，但使用与前面 BPSK 示例相同的 scaling：

[![Conjugate SCF of rectangular QPSK using the Frequency Smoothing Method (FSM) with scaling](https://pysdr.org/_images/scf_conj_rect_qpsk_scaled.svg)](https://pysdr.org/_images/scf_conj_rect_qpsk_scaled.svg)

注意 colorbar 的范围。

QPSK 以及更高阶 PSK 和 QAM 的 conjugate SCF 基本为零或噪声。这意味着即使有大量 QPSK/QAM 信号与 BPSK 重叠，也可以用 conjugate SCF 检测 BPSK 的存在，例如 DSSS 中的 chipping sequence。这是 CSP 工具箱中非常强大的工具。

在前面多次使用的三信号场景中运行 conjugate SCF，其中包含：

- Signal 1: Rectangular BPSK with 20 samples per symbol and 0.2 Hz frequency offset
- Signal 2: Pulse-shaped BPSK with 20 samples per symbol, -0.1 Hz frequency offset, and 0.35 roll-off
- Signal 3: Pulse-shaped QPSK with 4 samples per symbol, 0.2 Hz frequency offset, and 0.21 roll-off

[![Conjugate SCF of three different signals using the Frequency Smoothing Method (FSM)](https://pysdr.org/_images/scf_conj_multiple_signals.svg)](https://pysdr.org/_images/scf_conj_multiple_signals.svg)

可以看到两个 BPSK 信号，但 QPSK 信号没有出现；否则会在 alpha = 0.65 和 0.15 Hz 看到尖峰。不放大可能不太容易看清，但图中在 0.4 +/- 0.05 Hz 和 -0.2 +/- 0.05 Hz 处有尖峰。

## FFT Accumulation Method (FAM)

前面介绍的 FSM 和 TSM 很好用，尤其是在想计算一组特定 cyclic frequencies 时。注意两种实现都以 cyclic frequency 为外层 loop。不过，还有一种更高效的 SCF 实现，称为 FFT Accumulation Method（FAM）。FAM 会天然计算完整的 cyclic frequencies 集合，也就是信号每个整数 shift 对应的 cyclic frequencies；数量取决于 signal length。还有一种类似技术叫 [Strip Spectral Correlation Analyzer (SSCA)](https://cyclostationary.blog/2016/03/22/csp-estimators-the-strip-spectral-correlation-analyzer/)，也会一次计算所有 cyclic frequencies，但本章为避免重复不展开。一次性计算所有 cyclic frequencies 的这类技术有时称为 blind estimators，因为它们常用于不知道 cyclic frequencies 先验信息的场景；否则通常可以预先知道该算哪些 cyclic frequencies，并使用 FSM 或 TSM。FAM 是一种 time-smoothing method，可以理解为更复杂的 TSM；SSCA 则类似更复杂的 FSM。

实现 FAM 的最小 Python 代码其实相当简单，只是因为不再遍历 alpha，所以没那么容易直接对应数学公式。与 TSM 类似，先把信号分成一系列有重叠的 time windows，并对每个 sample chunk 应用 Hanning window。FAM 算法中会执行两阶段 FFT。注意代码中第一阶段 FFT 作用在 2D array 上，因此一行代码完成了很多 FFT。经过 frequency shift 后，再做第二阶段 FFT 来构建 SCF，随后取 magnitude squared。更完整的 FAM 解释见本节末尾 external resources。

```text
Input samples
Split into overlapping windows
Apply Hanning window
First FFT across each window
Frequency shift
Second FFT
Magnitude squared
SCF estimate
```

```python
N = 2**14
x = samples[0:N]
Np = 512 # Number of input channels, should be power of 2
L = Np//4 # Offset between points in the same column at consecutive rows in the same channelization matrix. It should be chosen to be less than or equal to Np/4
num_windows = (len(x) - Np) // L + 1
Pe = int(np.floor(int(np.log(num_windows)/np.log(2))))
P = 2**Pe
N = L*P

# channelization
xs = np.zeros((num_windows, Np), dtype=complex)
for i in range(num_windows):
    xs[i,:] = x[i*L:i*L+Np]
xs2 = xs[0:P,:]

# windowing
xw = xs2 * np.tile(np.hanning(Np), (P,1))

# first FFT
XF1 = np.fft.fftshift(np.fft.fft(xw))

# freq shift down
f = np.arange(Np)/float(Np) - 0.5
f = np.tile(f, (P, 1))
t = np.arange(P)*L
t = t.reshape(-1,1) # make it a column vector
t = np.tile(t, (1, Np))
XD = XF1 * np.exp(-2j*np.pi*f*t)

# main calcs
SCF = np.zeros((2*N, Np))
Mp = N//Np//2
for k in range(Np):
    for l in range(Np):
        XF2 = np.fft.fftshift(np.fft.fft(XD[:,k]*np.conj(XD[:,l]))) # second FFT
        i = (k + l) // 2
        a = int(((k - l) / Np + 1) * N)
        SCF[a-Mp:a+Mp, i] = np.abs(XF2[(P//2-Mp):(P//2+Mp)])**2
```

[![SCF with the FFT Accumulation Method (FAM), showing cyclostationary signal processing](https://pysdr.org/_images/scf_fam.svg)](https://pysdr.org/_images/scf_fam.svg)

放大 0.2 Hz 附近和低 cyclic frequencies 区域，查看更多细节：

[![Zoomed in version of SCF with the FFT Accumulation Method (FAM), showing cyclostationary signal processing](https://pysdr.org/_images/scf_fam_zoomedin.svg)](https://pysdr.org/_images/scf_fam_zoomedin.svg)

0.05 Hz 处有明显 hot spot，0.1 Hz 处也有一个较弱的点，只是当前 colorscale 下不太容易看见。

也可以压缩 RF frequency axis，将 SCF 画成 1D，更容易观察存在哪些 cyclic frequencies：

[![Cyclic freq plot using the FFT Accumulation Method (FAM), showing cyclostationary signal processing](https://pysdr.org/_images/scf_fam_1d.svg)](https://pysdr.org/_images/scf_fam_1d.svg)

FAM 的一个大坑是：它会生成极多 pixels，数量取决于 signal size。当 `imshow()` 中只有一两行包含能量时，它们有时会因为显示器上的缩放而被掩盖。一定要注意 2D SCF matrix 的大小。如果想减少 cyclic frequency axis 上的 pixels 数量，可以使用 max pooling 或 mean pooling。把下面代码放在 SCF 计算之后、绘图之前。可能需要先 `pip install scikit-image`：

```python
# Max pooling in cyclic domain
import skimage.measure
print("Old shape of SCF:", SCF.shape)
SCF = skimage.measure.block_reduce(SCF, block_size=(16, 1), func=np.max) # type: ignore
print("New shape of SCF:", SCF.shape)
```

FAM 的 external resources：

- R.S. Roberts, W. A. Brown, and H. H. Loomis, Jr., “Computationally Efficient Algorithms for Cyclic Spectral Analysis,” IEEE Signal Processing Magazine, April 1991, pp. 38-49. [Available here](https://www.researchgate.net/profile/Faxin-Zhang-2/publication/353071530_Computationally_efficient_algorithms_for_cyclic_spectral_analysis/links/60e69d2d30e8e50c01eb9484/Computationally-efficient-algorithms-for-cyclic-spectral-analysis.pdf)
- Da Costa, Evandro Luiz. Detection and identification of cyclostationary signals. Diss. Naval Postgraduate School, 1996. [Available here](https://apps.dtic.mil/sti/pdfs/ADA311555.pdf)
- Chad 的 FAM blog post: [https://cyclostationary.blog/2018/06/01/csp-estimators-the-fft-accumulation-method/](https://cyclostationary.blog/2018/06/01/csp-estimators-the-fft-accumulation-method/)

## OFDM

由于 OFDM 使用 cyclic prefix（CP），OFDM 信号中的 cyclostationarity 特别强。CP 是把每个 OFDM symbol 末尾的若干 samples 复制并添加到 OFDM symbol 的开头。这会产生一个强 cyclic frequency，对应 OFDM symbol length，也就是 subcarrier spacing 的倒数加上 CP duration。

现在观察一个 OFDM 信号。下面模拟带 CP 的 OFDM signal，使用 64 个 subcarriers、25% CP，并在每个 subcarrier 上使用 QPSK modulation。这里做 2x interpolation 来模拟以合理 sample rate 接收，因此 OFDM symbol length 以 samples 计为 $(64+64\times0.25)\times2=160$ samples。这意味着应在 $1/160$ 的整数倍处看到尖峰，例如 0.00625、0.0125、0.01875 等。模拟 200k samples，对应 1250 个 OFDM symbols。注意每个 OFDM symbol 本身相当长。

```python
from scipy.signal import resample
N = 200000 # number of samples to simulate
num_subcarriers = 64
cp_len = num_subcarriers // 4 # length of the cyclic prefix in symbols, in this case 25% of the starting OFDM symbol
print("CP length in samples", cp_len*2) # remember there is 2x interpolation at the end
print("OFDM symbol length in samples", (num_subcarriers+cp_len)*2) # remember there is 2x interpolation at the end
num_symbols = int(np.floor(N/(num_subcarriers+cp_len))) // 2 # remember the interpolate by 2
print("Number of OFDM symbols:", num_symbols)

qpsk_mapping = {
    (0,0) : 1+1j,
    (0,1) : 1-1j,
    (1,0) : -1+1j,
    (1,1) : -1-1j,
}
bits_per_symbol = 2

samples = np.empty(0, dtype=np.complex64)
for _ in range(num_symbols):
    data = np.random.binomial(1, 0.5, num_subcarriers*bits_per_symbol) # 1's and 0's
    data = data.reshape((num_subcarriers, bits_per_symbol)) # group into subcarriers
    symbol_freq = np.array([qpsk_mapping[tuple(b)] for b in data]) # remember we start in the freq domain with OFDM
    symbol_time = np.fft.ifft(symbol_freq)
    symbol_time = np.hstack([symbol_time[-cp_len:], symbol_time]) # take the last CP samples and stick them at the start of the symbol
    samples = np.concatenate((samples, symbol_time)) # add symbol to samples buffer

samples = resample(samples, len(samples)*2) # interpolate by 2x
samples = samples[:N] # clip off the few extra samples

# Add noise
SNR_dB = 5
n = np.sqrt(np.var(samples) * 10**(-SNR_dB/10) / 2) * (np.random.randn(N) + 1j*np.random.randn(N))
samples = samples + n
```

因为预期在 0.00625、0.0125、0.01875 处出现尖峰，我们使用 1e-5 的 cyclic frequency resolution，这样能得到整数倍。在使用这么细 resolution 不现实，或者 cyclic frequencies 未知的情况下，可以使用 oversampling，例如增加 samples per symbol；这个 OFDM 示例中的 oversampling factor 是 2。FSM 方法还要求一次至少处理 `2 / alpha_resolution` 个 samples，所以这里需要 200k samples。下面结果使用 `alphas = np.arange(0, 0.02, 1e-5)`，并开启 max pooling：

[![SCF of OFDM using the Frequency Smoothing Method (FSM)](https://pysdr.org/_images/scf_freq_smoothing_ofdm_zoomed_in.svg)](https://pysdr.org/_images/scf_freq_smoothing_ofdm_zoomed_in.svg)

注意三个尖峰。如果压缩 RF frequency 并将 cyclic frequency 画成 1D，它们会更加明显。

OFDM 与 CSP 相关 external resources：

1. Sutton, Paul D., Keith E. Nolan, and Linda E. Doyle. “Cyclostationary signatures in practical cognitive radio applications.” IEEE Journal on selected areas in Communications 26.1 (2008): 13-24. [Available here](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=4413137&casa_token=81U1yMeRKMsAAAAA:6sQr9-VngNa2p_OW4zVyeQsRdUrZPkx3L-6ZPsH9LCo-pnTxs_AhjfAx27MFBbo4kl3YlgdkQJk&tag=1)

## Signal Detection With Known Cyclic Frequency

在一些应用中，可能希望用 CSP 检测已知 signal 或 waveform，例如 802.11、LTE、5G 等变体。如果已知信号的 cyclic frequency，也知道 sample rate，那么实际上只需要计算一个 alpha 和一个 tau。后续会加入一个使用 WiFi RF recording 的示例。

## External Resources

1. Antonio Napolitano 的教材 [Cyclostationary Processes and Time Series: Theory, Applications, and Generalizations](https://www.sciencedirect.com/book/monograph/9780081027080/cyclostationary-processes-and-time-series)
2. R.S. Roberts, W. A. Brown, and H. H. Loomis, Jr., “Computationally Efficient Algorithms for Cyclic Spectral Analysis,” IEEE Signal Processing Magazine, April 1991, pp. 38-49. [Available here](https://www.researchgate.net/profile/Faxin-Zhang-2/publication/353071530_Computationally_efficient_algorithms_for_cyclic_spectral_analysis/links/60e69d2d30e8e50c01eb9484/Computationally-efficient-algorithms-for-cyclic-spectral-analysis.pdf)
3. Da Costa, Evandro Luiz. Detection and identification of cyclostationary signals. Diss. Naval Postgraduate School, 1996. [Available here](https://apps.dtic.mil/sti/pdfs/ADA311555.pdf)
4. [Chad Spooner 的 Cyclostationary blog/website](https://cyclostationary.blog/)
5. Sutton, Paul D., Keith E. Nolan, and Linda E. Doyle. “Cyclostationary signatures in practical cognitive radio applications.” IEEE Journal on selected areas in Communications 26.1 (2008): 13-24. [Available here](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=4413137&casa_token=81U1yMeRKMsAAAAA:6sQr9-VngNa2p_OW4zVyeQsRdUrZPkx3L-6ZPsH9LCo-pnTxs_AhjfAx27MFBbo4kl3YlgdkQJk&tag=1)
