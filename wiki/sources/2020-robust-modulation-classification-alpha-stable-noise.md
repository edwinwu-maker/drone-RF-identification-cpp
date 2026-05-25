# Robust Modulation Classification Over Alpha-Stable Noise

## Source

Yan, Xiao; Liu, Guannan; Wu, Hsiao-Chun; Zhang, Guoyu; Wang, Qian; Wu, Yiyan. "Robust Modulation Classification Over alpha-Stable Noise Using Graph-Based Fractional Lower-Order Cyclic Spectrum Analysis." IEEE Transactions on Vehicular Technology, 69(3), 2020. DOI: `10.1109/TVT.2020.2965137`.

Raw file: `raw/Yan 等 - 2020 - Robust Modulation Classification Over α-Stable Noise Using Graph-Based Fractional Lower-Order Cyclic.pdf`

## Core View

传统 automatic modulation classification (AMC) 多假设 Gaussian noise，但实际无线环境常出现 impulsive noise，可用 alpha-stable distribution 描述。该噪声会使二阶或高阶统计量失效。论文提出用 fractional lower-order cyclic spectrum (FLOCS) 加 graph-based feature extraction，在 alpha-stable noise 下保持调制识别能力。

## Method

流程包含三步：先对接收信号做 FLOCS analysis，得到可在 alpha-stable noise 下存在的 fractional lower-order polyspectra；再把 FLOCS 映射为 graph representation 和 adjacency matrix；最后用 graph-domain classifier 比较 training 与 test graph features 的差异完成分类。分类判据涉及 Kullback-Leibler divergence、Hamming distance，并推导了 correct classification probability `Pcc`。

关键参数包括 nonlinear transform order `b=0.1`、FFT window size `32`、quantization levels `16`。

## Data & Experiments

候选调制集为 BPSK、QPSK、OQPSK、2FSK、4FSK、MSK。仿真在 alpha-stable noise 下进行，characteristic exponent `alpha=1.5`，MSNR 从 `-10 dB` 到 `20 dB`。每个 MSNR 条件做 `1000` 次 Monte Carlo trials，每种调制每次生成 `8192` samples。

结果显示，proposed FLOCS graph method 在 MSNR 约 `4 dB` 时可达到 `Pcc=100%`；基于 conventional cyclic spectrum 的 SCS/AMCG 方法在 alpha-stable noise 下表现明显退化。与 human-selected FLOCS features 相比，系统化 graph feature selection 更稳健。

## Conclusion

该方法的主要贡献是把 FLOCS 与 graph representation 结合，解决 impulsive alpha-stable noise 中传统 AMC 特征失效的问题。理论上给出 `Pcc` 计算和 candidate set 变化时的 iterative update rule，实验上验证了低 MSNR 下的鲁棒性。

## Related Pages

- [Summary: Cyclic Features for RF Signal Identification](../summary.md)
- [Citation Order](../citation-order.md)

## Terms

- [AMC](../concepts/amc.md): automatic modulation classification
- [alpha-stable noise](../concepts/alpha-stable-noise.md): impulsive, heavy-tailed noise model
- [FLOCS](../concepts/flocs.md): fractional lower-order cyclic spectrum
- [graph representation](../concepts/graph-representation.md) / adjacency matrix
- Kullback-Leibler divergence
- Hamming distance
- [Pcc](../concepts/pcc.md): probability of correct classification
