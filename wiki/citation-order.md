# Citation Order

## 正确的论文引用顺序

在笔记、总结页或 slides 中引用当前论文时，统一使用以下顺序：

1. [Yan et al. 2020 - Robust Modulation Classification Over Alpha-Stable Noise](sources/2020-robust-modulation-classification-alpha-stable-noise.md)
2. [Yan et al. 2024 - Automatic Composite-Modulation Classification Using CPP (FB: DCT/DWT + SMO-SVM)](sources/2024-automatic-composite-modulation-classification-cpp.md)
3. [Yan et al. 2024 - Automatic Composite-Modulation Classification Using ULWNet Based on CPP (DL: ULWNet)](sources/2024-acmc-ulwnet-cpp.md)
4. [Yan et al. 2025 - RF-Based UAV Identification Using CPP](sources/2025-rf-based-uav-identification-cpp.md)

## 顺序依据

该顺序同时满足时间线与方法演进逻辑：

- `2020`：在 impulsive noise 场景下引入 `FLOCS + graph representation`，用于鲁棒 `AMC`。
- `2024 (FB)`：将 `cyclic spectrum` 发展为图像化 `CPP` 表示，用 `DCT/DWT + SMO-SVM` 完成 FB 路线 ACMC。
- `2024 (DL)`：在 CPP 基础上提出 `ULWNet` 端到端 DL-ACMC，强调计算效率与资源受限部署。
- `2025`：在 `UAV RF identification` 中结合 `ST-ESER` 与 `ResNet-18`，完成工程化识别流程。

## Graph 规则

除非论文原文明确存在直接引用或依赖关系，否则 `sources` 下论文页面不互相直连。论文关系优先通过 [Summary](summary.md)、[Concepts](index.md#concepts) 与本页维护。
