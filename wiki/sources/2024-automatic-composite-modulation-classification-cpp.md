# Automatic Composite-Modulation Classification Using CPP

## Source

Yan, Xiao; Zhong, Xunuo; Wu, Hsiao-Chun; Yang, PengFei; Wang, Qian; Chen, Yiyun. "Automatic Composite-Modulation Classification Using Cyclic-Paw-Print Features for Cognitive Aerospace Communications." IEEE Transactions on Communications, 72(9), 2024. DOI: `10.1109/TCOMM.2024.3388509`.

Raw file: `raw/Yan 等 - 2024 - Automatic Composite-Modulation Classification Using Cyclic-Paw-Print Features for Cognitive Aerospac.pdf`

## Core View

论文面向 cognitive aerospace communications、TT&C 和 space surveillance 中的 automatic composite-modulation classification (ACMC)。核心观点是：composite-modulation (CM) 信号的 normalized cyclic spectrum 可以转换成 cyclic-paw-print (CPP) gray-scale image matrix，再通过 DCT/DWT 提取 compact hybrid features，用 SMO-SVM 完成 CM scheme 识别。

## Method

方法包含四个机制：cyclic spectrum analysis、CPP mapping、hybrid feature vector extraction、SMO-SVM classification。接收 CM signal 先经过同步和增强处理，再生成 three-dimensional normalized second-order cyclic spectrum。其 top view 被映射为 CPP。随后同时使用 two-dimensional discrete cosine transform (DCT) 和 Haar discrete wavelet transform (DWT)，从低频 DCT components 与主要 DWT components 构造 hybrid feature vector。

分类器使用 sequential minimal optimized support vector machine (SMO-SVM)。论文强调该特征比 high-order-statistics (HOS) 特征更稳定，计算复杂度也更低。

## Data & Experiments

候选集包含 `10` 种 CM schemes：PCM/BPSK/PM、PCM/QPSK/PM、PCM/BPSK/FM、三类双子载波 PM、三类双子载波 FM，以及 PCM/QPSK/FM。primary modulation index `KPM` 或 `KFM` 设为 `1.2`。FAM 的 FFT window size 为 `64`，CPP size 为 `65 x 2049`。

仿真使用 AWGN channel，SNR 范围 `-20 dB` 到 `20 dB`。每个 CM scheme 生成 `350` 个 noise-free training signals；每次 trial 生成 `2048` samples，training/testing ratio 为 `4:1`，通常每个 SNR 做 `500` 次 Monte Carlo trials，Fig. 7 使用 `1000` 次。

结果显示，多数 CM schemes 在 SNR `>=5 dB` 时 CRP 接近 `100%`；较难的 PCM/BPSK1+BPSK2/FM 与 PCM/QPSK/PM 在 `5 dB` 附近约 `90%`，到 `8 dB` 接近 `100%`。论文还搭建 vector signal generator、wideband digital receiver、spectrum analyzer 的硬件平台验证真实 CM signal。

## Conclusion

CPP 将 cyclic spectrum 的结构转换为图像型特征，DCT/DWT hybrid vector 保留判别信息并压缩维度，SMO-SVM 完成多类识别。Monte Carlo simulation 与 real experiment 均支持该方法优于既有 ACMC 方法，适合下一代 intelligent TT&C 与 cognitive space communications。

## Related Pages

- [Summary: Cyclic Features for RF Signal Identification](../summary.md)
- [Citation Order](../citation-order.md)

## Terms

- [ACMC](../concepts/acmc.md): automatic composite-modulation classification
- CM: composite modulation
- [CPP](../concepts/cpp.md): cyclic-paw-print
- [DCT](../concepts/dct.md): discrete cosine transform
- [DWT](../concepts/dwt.md): discrete wavelet transform
- [SMO-SVM](../concepts/smo-svm.md): sequential minimal optimized support vector machine
- [TT&C](../concepts/ttc.md): telemetry, tracking, and command
- HOS: high-order statistics
