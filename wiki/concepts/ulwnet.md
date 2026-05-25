---
type: concept
tags: [concept, method, deep-learning]
---

# ULWNet

`ULWNet (ultra lightweight deep-learning network)` 是专为 CPP-based ACMC 设计的极轻量 CNN，以 5 个 E-unit 为核心，旨在资源受限场景下替代 ResNet/MobileNetV2 等重型网络。

## 关键点

- 输入为 CPP pseudo-color RGB tensor（$224\times224\times3$）。
- 架构：5 个 E-unit → max-pooling → flatten → FC → softmax。
- 每个 E-unit 由 conv + BN + eLU 组成；首层 64 个 $7\times7$ filter（stride=2），后续层 $3\times3$ filter。
- FLOPs 约 0.01G，参数量约 0.01M，训练/测试时间远低于 MobileNetV2、ResNet、ConvNeXt。
- 5 个 E-unit 达到性能饱和，超过 7 个后轻微下降。

## Related Papers

- [Automatic Composite-Modulation Classification Using ULWNet Based on CPP](../sources/2024-acmc-ulwnet-cpp.md)
