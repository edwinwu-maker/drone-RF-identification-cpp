# Wiki Index

## 总览

- [Summary: Cyclic Features for RF Signal Identification](summary.md)：对当前 `raw/` 论文集合的综合分析页。
- [Citation Order](citation-order.md)：当前论文的标准引用顺序。

## Sources（论文页）

- [CSP Estimators: The FFT Accumulation Method](sources/2018-csp-estimators-fam.md)：`FAM` 作为高效 `SCF/SCS` 估计器的方法参考，可用于理解 `CPP` 提取前的循环谱估计步骤。
- [Robust Modulation Classification Over Alpha-Stable Noise](sources/2020-robust-modulation-classification-alpha-stable-noise.md)：基于 `FLOCS` 的图表示方法，用于 impulsive `alpha-stable noise` 下的 `AMC`。
- [Automatic Composite-Modulation Classification Using CPP](sources/2024-automatic-composite-modulation-classification-cpp.md)：`CPP + DCT/DWT + SMO-SVM` 的 FB 复合调制识别流程。
- [Automatic Composite-Modulation Classification Using ULWNet Based on CPP](sources/2024-acmc-ulwnet-cpp.md)：`CPP + ULWNet` 的端到端 DL 复合调制识别，面向资源受限场景。
- [RF-Based UAV Identification Using CPP](sources/2025-rf-based-uav-identification-cpp.md)：`ST-ESER` 分帧、`CPP` 提取与 `ResNet-18` 分类的 UAV 射频识别方法。

## Concepts（关键词页）

- [Cyclic Spectrum](concepts/cyclic-spectrum.md)：`CPP` 等循环域特征的基础表示。
- [CPP](concepts/cpp.md)：循环谱图像化后的关键特征表示。
- [FLOCS](concepts/flocs.md)：面向冲击噪声的分数低阶循环谱。
- [ST-ESER](concepts/st-eser.md)：用于有效信号帧筛选的比值特征。
- [ULWNet](concepts/ulwnet.md)：用于 `CPP` 的 ultra lightweight DL 分类器。
- [ResNet-18](concepts/resnet-18.md)：用于 `CPP tensor` 的 `CNN` 分类器。
- [Alpha-Stable Noise](concepts/alpha-stable-noise.md)：重尾冲击噪声模型。
- [AMC](concepts/amc.md)：automatic modulation classification 任务。
- [ACMC](concepts/acmc.md)：automatic composite-modulation classification 任务。
- [UAV RF Identification](concepts/uav-rf-identification.md)：无人机遥控射频信号识别任务。
- [DCT](concepts/dct.md)、[DWT](concepts/dwt.md)、[SMO-SVM](concepts/smo-svm.md)：特征提取与分类组件。
- [TT&C](concepts/ttc.md)、[DroneRFa Dataset](concepts/drone-rfa.md)：应用背景与数据集。
