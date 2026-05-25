# RF-Based UAV Identification Using CPP

## Source

Yan, Xiao; Zhao, Minghui; Wang, Qian; Wu, Hsiao-Chun; Liu, Guannan; Wu, Yiyan. "Radio-Frequency-Based Unmanned-Aerial-Vehicle Identification Using Cyclic-Paw-Print." IEEE International Symposium on Broadband Multimedia Systems and Broadcasting (BMSB), 2025. DOI: `10.1109/BMSB65076.2025.11165560`.

Raw file: `raw/Yan 等 - 2025 - Radio-Frequency-Based Unmanned-Aerial-Vehicle Identification Using Cyclic-Paw-Print.pdf`

## Core View

论文把 cyclic-paw-print (CPP) 从 modulation classification 扩展到 RF-based UAV identification。核心观点是：UAV 的 TT&C 和 digital data-transmission (DDT) RF signals 可通过 ST-ESER 选帧，再把选中片段的 cyclic spectrum 转换为 CPP tensor，输入 lightweight ResNet-18 识别 UAV 类型。

## Method

系统包含三部分：RF signal acquisition and segmentation、CPP extraction、lightweight DL classification。接收 RF waveform 被划分为 image-transmission intervals (ITIs)、silent intervals (SIs) 和 frequency-hopping intervals (FHIs)，只有 ITIs 和 FHIs 用于识别。

分帧后计算 short-time energy-to-spectral-entropy ratio (ST-ESER)，用于选择有效 signal subsequences。对选中帧做 cyclic-spectrum analysis，构造 normalized spectral correlation magnitude surface (NSCMS)，再取 top view 得到 CPP。CPP 被转换为 `224 x 224 x 3` tensor，输入 ResNet-18。

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
