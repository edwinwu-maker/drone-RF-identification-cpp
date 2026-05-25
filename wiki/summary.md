# Summary: Cyclic Features for RF Signal Identification

## Overview

当前 `raw/` 中的三篇论文形成了一条清晰研究主线：从 robust modulation classification，到 composite-modulation classification，再到 RF-based UAV identification。共同核心是利用信号的 cyclostationary structure，把 cyclic spectrum 或 FLOCS 转换成更稳定、更可分类的特征表示。

## Research Thread

2020 年论文关注 impulsive alpha-stable noise 下的 automatic modulation classification (AMC)。它用 fractional lower-order cyclic spectrum (FLOCS) 替代传统二阶或高阶统计特征，再映射为 graph representation，通过 graph-domain classifier 识别 BPSK、QPSK、OQPSK、2FSK、4FSK、MSK 等调制类型。

2024 年首篇论文将 cyclic spectrum 转换为 cyclic-paw-print (CPP) gray-scale image matrix，用 DCT/DWT 提取 hybrid feature vector，并通过 SMO-SVM 完成 automatic composite-modulation classification (ACMC)。同年第二篇论文（TCCN 期刊）进一步提出 ULWNet——一种 ultra lightweight DL 网络，直接用 CPP pseudo-color RGB tensor 做端到端分类，强调资源受限场景下的计算效率。

2025 年论文进一步把 CPP 用于 RF-based UAV identification。它先用 ST-ESER 筛选 UAV RF signal 的有效帧，再提取 CPP tensor，输入 ResNet-18，在 DroneRFa dataset 上识别 UAV RF 类型。

## Key Methods

- `FLOCS`: 面向 alpha-stable impulsive noise，避免传统 higher-order statistics 失效。
- `CPP`: 将 cyclic spectrum 的 top-view 结构转为图像型特征。
- `DCT/DWT`: 压缩 CPP 并保留主要判别信息（2024 FB 路线）。
- `SMO-SVM`: 用于 2024 FB-ACMC 的多类分类。
- `ULWNet`: 5 个 E-unit 的 ultra lightweight CNN，用于 2024 DL-ACMC，FLOPs 与参数量远低于 ResNet/MobileNetV2。
- `ST-ESER`: 用于 2025 UAV RF signal segmentation 和有效帧选择。
- `ResNet-18`: 用于 CPP tensor 输入下的 UAV RF identification。

## Key Results

2020 论文中，FLOCS graph method 在 MSNR 约 `4 dB` 时可达到 `Pcc=100%`，明显优于 conventional cyclic spectrum baseline。

2024 FB 论文中，多数 CM schemes 在 SNR `>=5 dB` 时 CRP 接近 `100%`，较难类别在约 `8 dB` 时接近 `100%`，并通过真实硬件平台验证。2024 DL 论文中，ULWNet 在 AWGN 下 SNR `>=0 dB` 时 Pcc 达 `100%`，且在 Rayleigh 和 $\alpha$-stable 噪声下性能鲁棒，计算开销远优于 MobileNetV2、ResNet、ConvNeXt。

2025 论文中，CPP-based ResNet-18 在 DroneRFa 上的 noise-free `Pcc=98.7%`，加入 AWGN 后整体不低于 STFT baseline；SNR `>=10 dB` 时达到约 `98%`。

## Open Questions

- CPP 是否可统一用于 modulation classification、UAV identification 和 RF fingerprinting？
- ULWNet 的轻量架构在 UAV RF identification 场景是否同样适用（对比 ResNet-18）？
- ST-ESER 是否适合替代或补充其他 burst detection / frame selection 方法？
- ResNet-18 在 CPP 上优于 ShuffleNet-V2 和 Vision Transformer 的原因是否来自 CPP 的局部纹理结构？
- DroneRFa 上的结果能否迁移到真实低 SNR、multi-path、co-channel interference 场景？

## Source Pages

- [CSP Estimators: The FFT Accumulation Method](sources/2018-csp-estimators-fam.md)
- [Robust Modulation Classification Over Alpha-Stable Noise](sources/2020-robust-modulation-classification-alpha-stable-noise.md)
- [Automatic Composite-Modulation Classification Using CPP](sources/2024-automatic-composite-modulation-classification-cpp.md)
- [Automatic Composite-Modulation Classification Using ULWNet Based on CPP](sources/2024-acmc-ulwnet-cpp.md)
- [RF-Based UAV Identification Using CPP](sources/2025-rf-based-uav-identification-cpp.md)

## Citation Order

Use [Citation Order](citation-order.md) as the canonical paper sequence: 2020 FLOCS graph method, then 2024 CPP-based ACMC, then 2025 CPP-based UAV RF identification.
