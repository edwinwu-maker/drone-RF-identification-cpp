# RF-Based UAV Identification Using CPP

## Source

Yan, Xiao; Zhao, Minghui; Wang, Qian; Wu, Hsiao-Chun; Liu, Guannan; Wu, Yiyan. "Radio-Frequency-Based Unmanned-Aerial-Vehicle Identification Using Cyclic-Paw-Print." IEEE International Symposium on Broadband Multimedia Systems and Broadcasting (BMSB), 2025. DOI: `10.1109/BMSB65076.2025.11165560`.

Raw file: `raw/Yan 等 - 2025 - Radio-Frequency-Based Unmanned-Aerial-Vehicle Identification Using Cyclic-Paw-Print.pdf`

## Core View

论文把 cyclic-paw-print (CPP) 从 modulation classification 扩展到 RF-based UAV identification。核心观点是：UAV 的 TT&C 和 digital data-transmission (DDT) RF signals 可通过 ST-ESER 选帧，再把选中片段的 cyclic spectrum 转换为 CPP tensor，输入 lightweight ResNet-18 识别 UAV 类型。

## Method

系统包含三部分：RF signal acquisition and segmentation、CPP extraction、lightweight DL classification。接收 RF waveform 被划分为 image-transmission intervals (ITIs)、silent intervals (SIs) 和 frequency-hopping intervals (FHIs)，只有 ITIs 和 FHIs 用于识别。

分帧后计算 short-time energy-to-spectral-entropy ratio (ST-ESER)，用于选择有效 signal subsequences。对选中帧做 cyclic-spectrum analysis，构造 normalized spectral correlation magnitude surface (NSCMS)，再取 top view 得到 CPP。CPP 被转换为 `224 x 224 x 3` tensor，输入 ResNet-18。

### IQ/RF Signal Processing Flow

论文没有把 I/Q 拆成两个独立通道处理，而是把接收信号表示为离散 RF sequence：

$$
r(n),\quad n=0,1,\ldots,M-1
$$

如果底层 dataset 以 complex IQ 存储，则这里的 $r(n)$ 和后续 $x(n)$ 可理解为复基带 IQ samples。处理流程不是直接把整段 waveform 输入网络，而是先进行检测、分段和筛选。

首先使用长度为 $N$、步长为 $L$ 的 sliding window 分帧：

$$
\zeta_i(n)=r(n+(i-1)L),\quad n=0,1,\ldots,N-1
$$

相邻帧的 overlap samples 为 $N-L$，帧数为：

$$
I=\left\lfloor\frac{M-N+L}{L}\right\rfloor
$$

然后对每一帧做 DFT：

$$
U_i(m)=
\sum_{n=0}^{N-1}
\zeta_i(n)e^{-j2\pi nm/N}
$$

基于谱能量构造 spectral probability sequence：

$$
p_i(m)=
\frac{|U_i(m)|^2}
{\sum_{m=0}^{N-1}|U_i(m)|^2}
$$

并计算 spectral entropy：

$$
H_i=
-\sum_{m=0}^{N-1}
p_i(m)\ln p_i(m)
$$

论文定义 ST-ESER 为：

$$
\rho_i=
\frac{\sum_{m=0}^{N-1}|U_i(m)|^2}{H_i}
$$

其直觉是：UAV signal 出现时，frame energy 较高而 spectral entropy 较低，因此 $\rho_i$ 较大。帧选择规则为：

$$
\rho_i\ge \hbar
$$

其中阈值为：

$$
\hbar=
\varsigma \frac{1}{I}\sum_{i=1}^{I}\rho_i
$$

论文建议 $0.5\le\varsigma\le0.9$。连续通过 ST-ESER 检测的帧会被聚合成有效信号段 $x(n)$，主要对应 image-transmission intervals (ITIs) 和 frequency-hopping intervals (FHIs)，silent intervals (SIs) 不用于特征提取。

对聚合后的 $x(n)$，论文使用 FAM 估计 second-order cyclic spectrum (SCS)。time-smoothed cyclic periodogram 写为：

$$
S_x^\epsilon(n,f)_{\Delta t}
=
\sum_\lambda
X_T(\lambda,f_1)X_T^*(\lambda,f_2)g^{\prime}(n-\lambda)
$$

其中：

$$
f_1=f+\epsilon/2,\quad f_2=f-\epsilon/2
$$

complex demodulate 为：

$$
X_T(n,f)=
\sum_{\lambda=-N^{\prime}/2}^{N^{\prime}/2-1}
\hat{w}(\lambda)x(n-\lambda)
e^{-j2\pi f(n-\lambda)T_s}
$$

最后把 SCS 幅度归一化为 NSCMS：

$$
\left|S_x^\epsilon(f)\right|
=
\frac{|S_x^\epsilon(f)|}
{\max_{\epsilon,f}|S_x^\epsilon(f)|}
$$

NSCMS 的 top view 在 $\epsilon-f$ plane 上形成四个对称区域，即 CPP。论文再将 NSCMS 量化成矩阵：

$$
\gamma_{u,v}
=
\left\lfloor
(2^b-1)\left|S_x^{\epsilon_u}(f_v)\right|
\right\rfloor
$$

其中 $b=16$。该矩阵随后 reshape 为 square matrix，并通过 MATLAB `parula` colormap 转换为 pseudo-color RGB image，最终形成 ResNet-18 的输入 tensor。

## Data & Experiments

实验使用公开 DroneRFa dataset，包含 `24` 类 drone-controller RF communication signals 和 `1` 类 no-drone background signal，覆盖常见商业/民用小中型 UAV。论文把原始 UAV RF signals 视为 clean signals，并加入 AWGN 控制 SNR，范围为 `-10 dB` 到 `15 dB`。

训练阶段每类收集 `M=10^7` samples。分帧参数为 frame length `N=10000`、step `L=2500`。生成 SCS 的 FAM FFT window size 为 `N'=256`，sample size `N=16384`。得到的矩阵为 `32769 x 257`，再变换为 `224 x 224 x 3`。训练/验证比例为 `7:3`，optimizer 为 Adam，learning rate `0.001`，mini-batch size `32`。

结果显示，在 noise-free 条件下，CPP-based ResNet-18 与 STFT-based baseline 均达到 `Pcc=98.7%`。加入 AWGN 后，CPP-based method 在各 SNR 下的 `Pcc` 始终不低于 STFT baseline；当 SNR `>=10 dB` 时，两者均可达到约 `98%`，但 CPP 方法整体更优。与 ShuffleNet-V2 和 Vision Transformer 相比，ResNet-18 在 CPP features 上表现最好。

## Conclusion

该论文给出了一个面向 airspace surveillance 和 air-traffic control 的 RF UAV identification pipeline。贡献在于用 ST-ESER 筛选有效 RF frames，用 CPP 表征 cyclostationary structure，并用轻量 ResNet-18 完成分类。实验支持 CPP 比 STFT 更适合作为 UAV RF identification 的输入特征。

## Related Pages

- [Summary: Cyclic Features for RF Signal Identification](../summary.md)
- [Citation Order](../citation-order.md)

## Terms

- [UAV RF Identification](../concepts/uav-rf-identification.md): RF-based drone-controller signal identification task
- RF: radio frequency
- [TT&C](../concepts/ttc.md): telemetry, tracking, and command
- DDT: digital data-transmission
- [ST-ESER](../concepts/st-eser.md): short-time energy-to-spectral-entropy ratio
- [CPP](../concepts/cpp.md): cyclic-paw-print
- NSCMS: normalized spectral correlation magnitude surface
- [ResNet-18](../concepts/resnet-18.md)
- [DroneRFa dataset](../concepts/drone-rfa.md)
