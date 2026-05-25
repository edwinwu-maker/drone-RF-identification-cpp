# Automatic Composite-Modulation Classification Using ULWNet Based on CPP

## Source

Yan, Xiao; Yang, Pengfei; Zhong, Xunuo; Wang, Qian; Wu, Hsiao-Chun; He, Ling. "Automatic Composite-Modulation Classification Using Ultra Lightweight Deep-Learning Network Based on Cyclic-Paw-Print." IEEE Transactions on Cognitive Communications and Networking (TCCN), Vol. 10, No. 3, pp. 866–879, June 2024. DOI: `10.1109/TCCN.2024.3357850`.

Raw file: `raw/Yan 等 - 2024 - Automatic Composite-Modulation Classification Using Ultra Lightweight Deep-Learning Network Based on.pdf`

## Core View

论文提出了一种端到端的 DL-based ACMC 方案：将 CM 信号的 cyclic spectrum 转换为 CPP pseudo-color RGB tensor，直接输入专门设计的 ultra lightweight network (ULWNet) 完成复合调制识别。与已有 2024 会议论文的 FB 路线（DCT/DWT + SMO-SVM）不同，本文用 DL 替代手工特征提取与分类器，同时通过极简网络架构控制计算开销，面向资源受限的认知通信场景。

## Method

系统流程分三阶段：

1. **Cyclic Spectrum Analysis**：接收 CM 信号经 FAM 计算 second-order cyclic periodogram，得到 three-dimensional SCS $R_r^{\alpha}(f)$，再归一化为 NSCS $\bar{R}_r^{\alpha}(f)$，离散化后得到 DNSCS $\bar{R}_r^{\alpha_u}(f_v)$，矩阵尺寸 $(2N+1)\times(N'+1)$。

2. **CPP Extraction**：DNSCS 幅值矩阵经 b-bit quantizer（$b=16$）量化 → 行插值/列抽取 reshaped 为 $\Lambda\times\Lambda$ 方阵 → parula colormap 映射为 pseudo-color RGB image → 得到三阶 tensor $\mathbf{R}^{\text{RGB}} = \{\widetilde{\mathbf{R}}^R, \widetilde{\mathbf{R}}^G, \widetilde{\mathbf{R}}^B\}$（每通道 $224\times224$）。

3. **ULWNet Classification**：CPP tensor 输入 ULWNet，网络由 5 个 E-unit（每个含 conv + BN + eLU）、max-pooling、flatten、fully-connected + softmax 组成。第一层 E-unit 使用 64 个 $7\times7$ filter（stride=2），后续 E-unit 使用 $3\times3$ filter。

## Data & Experiments

候选集 K 包含 10 类 CCSDS CM 方案：PCM/BPSK/PM、PCM/QPSK/PM、PCM/(BPSK1+BPSK2)/PM、PCM/(QPSK1+QPSK2)/PM、PCM/(BPSK1+QPSK2)/PM、PCM/(BPSK1+BPSK2)/FM、PCM/(QPSK1+QPSK2)/FM、PCM/(BPSK1+QPSK2)/FM、PCM/BPSK/FM、PCM/QPSK/FM。参数设置：$K_p=K_f=1.2$，FAM FFT window $N'=64$，sample size $N=1024$，CPP 输出 $224\times224\times3$。

每类每 SNR/MSNR 500 次 Monte Carlo trial，每次 2048 samples，训练/测试比 7:3。信道覆盖 AWGN、Rayleigh、$\alpha$-stable distributed noise（$\alpha=1.5$），SNR/MSNR 范围 `-20` 到 `20 dB`（间隔 5 dB）。额外鲁棒性测试：residual timing error（2.5%~10% $T_s$）、carrier frequency offset（0.025~0.1 $f_c$）、phase offset（$\pi/16$~$\pi/4$）。

关键结果：
- AWGN 下 SNR $\ge 0$ dB 时 Pcc 达 `100%`，显著优于 HOS-based 方法（所有 SNR 下 Pcc $\le 70\%$）。
- CPP 特征优于 I/Q、cyclostationary、FBREWT 特征（同用 ULWNet）。
- Rayleigh 信道下 SNR $\ge 10$ dB 时 Pcc 达 `100%`；$\alpha$-stable 噪声下性能与 AWGN 接近。
- 对 timing error、frequency offset、phase offset 均鲁棒，SNR $\ge 10$ dB 时 Pcc 恢复至 `100%`。
- 计算效率：ULWNet 的 FLOPs（0.01G）、参数量（0.01M）、训练/测试时间均远小于 MobileNetV2、ResNet、ConvNeXt。

## Conclusion

该论文给出了 CPP + ULWNet 的完整 DL-ACMC pipeline，在 10 类 CCSDS CM 方案上达到高精度，且计算开销极低。证明了 CPP 作为一种通用循环域图像特征可适配轻量 DL 网络，为资源受限的星载/认知通信场景提供可行方案。

## Related Pages

- [Summary: Cyclic Features for RF Signal Identification](../summary.md)
- [Citation Order](../citation-order.md)

## Terms

- [ACMC](../concepts/acmc.md): automatic composite-modulation classification
- [CPP](../concepts/cpp.md): cyclic-paw-print
- [ULWNet](../concepts/ulwnet.md): ultra lightweight deep-learning network
- [Cyclic Spectrum](../concepts/cyclic-spectrum.md): 包含 DNSCS 与 FAM 估计
- CM: composite modulation
- DNSCS: discrete normalized second-order cyclic spectrum
- NSCS: normalized spectral correlation surface
- E-unit: ULWNet 的基本卷积组块（conv + BN + eLU）
- CCSDS: Consultative Committee for Space Data Systems
