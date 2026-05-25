---
type: concept
tags: [concept, task]
---

# UAV RF Identification

`UAV RF identification` 指通过接收端无线电信号识别无人机/遥控器类型。当前主线方法为 `ST-ESER` 选帧、`CPP` 提取、`ResNet-18` 分类。

## 关键点

- 不依赖视觉传感器，适合远距离与遮挡场景。
- 在低信噪比条件下，循环域特征通常优于纯时频图特征。

## Related Papers

- [RF-Based UAV Identification Using CPP](../sources/2025-rf-based-uav-identification-cpp.md)

