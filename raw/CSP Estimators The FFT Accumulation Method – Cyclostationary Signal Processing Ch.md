---
title: "CSP Estimators: The FFT Accumulation Method - Cyclostationary Signal Processing 中文译文"
source: "https://cyclostationary.blog/2018/06/01/csp-estimators-the-fft-accumulation-method/"
author:
  - "[[View all posts by Chad Spooner]]"
published: 2001-07-14
created: 2026-05-25
description: "An alternative to the strip spectral correlation analyzer."
tags:
  - "clippings"
  - "translation"
---

我们来看另一种 [spectral correlation function](http://cyclostationary.blog/2015/09/28/the-spectral-correlation-function/) 估计器：`FFT Accumulation Method (FAM)`。这个估计器属于 time-smoothing 类方法。它是 exhaustive 的，因为它被设计用来在 spectral correlation function 的整个主定义域内计算估计值；同时它也很高效，因此可以作为 [Strip Spectral Correlation Analyzer](http://cyclostationary.blog/2016/03/22/csp-estimators-the-strip-spectral-correlation-analyzer/) (`SSCA`) 方法的竞争方案。作者基于 Roberts *et al* 的论文实现了自己的 FAM 版本（见 [The Literature](http://cyclostationary.blog/the-literature/) \[R4\]）。如果仔细跟随公式，就能成功实现该论文中的估计器。和 SSCA 一样，棘手之处在于：要把代码公式的输出正确关联到对应的 $(f, \alpha)$ 值。

本文还会在 FAM 中实现 [coherence](http://cyclostationary.blog/2016/01/08/the-spectral-coherence-function/) 计算，并像使用 SSCA 时一样，用它自动检测显著 cycle frequencies。最后，本文会比较 SSCA 与 FAM 的 spectral-correlation 和 spectral-coherence 估计输出。算法实现并非没有问题和未解之处，文章也会指出这些问题。欢迎在评论区留下修正、评论和澄清。

### FFT Accumulation Method 的定义

该方法会产生大量 cross spectral correlation function 的点估计。在 \[R4\] 中，点估计给为：

$$
S_{xy_T}^{\alpha_i + q\Delta\alpha} (nL, f_j)_{\Delta\!t} = \sum_{r}X_T(rL, f_k) Y_T^* (rL, f_l) g_c(n-r) e^{-i2\pi r q /P} \tag{1}
$$

其中 complex demodulates 定义为：

$$
X_T(n,f) = \sum_{r=-N^{\prime}/2}^{N^{\prime}/2} a(r) x(n-r) e^{-i 2 \pi f(n-r)T_s} \tag{2}
$$

这里的公式 (2) 对应 \[R4\] 中的公式 (2)。作者认为这里的求和应该覆盖 $N^{\prime}$ 个采样点，而不是 $N^{\prime}+1$ 个采样点：

$$
X_T(n,f) = \sum_{r=-N^{\prime}/2}^{N^{\prime}/2-1} a(r) x(n-r) e^{-i 2 \pi f(n-r)T_s} \tag{3}
$$

在公式 (1) 中，函数 $g_c(n)$ 是一个 [data-tapering window](https://en.wikipedia.org/wiki/Window_function)，通常取为单位高度矩形窗，因此不需要实际乘法。在公式 (2) 中，函数 $a(r)$ 是另一个 tapering window，通常取为 Hamming window，可用 MATLAB 的 [hamming.m](https://www.mathworks.com/help/signal/ref/hamming.html) 生成。

采样率为 $f_s = 1/T_s$。在公式 (2) 和 (3) 中，$T = N^{\prime} T_s$。channelizer 中短时跳步 Fourier transform 的 tapering window $a(r)$ 宽度为 $T_s N^{\prime}$，输出端 long-time Fourier transform 的 tapering window $g_c(r)$ 宽度为 $NT_s$，也就是被处理 data-block 的长度。

因此，FAM 用长度为 $N^{\prime}$ 的短 Fourier transform 对输入数据进行 channelization，并以 $L$ 个采样点作为时间 hop。这样得到的 transform 序列长度为：

$$
P = N/L \tag{4}
$$

这里假设 $N$ 和 $L$ 都是 dyadic integers，并且 $L \ll N$。因此，输出 Fourier transform 的长度为 $P$。

对公式 (1)，\[R4\] 将 cycle-frequency resolution 定义为：

$$
\Delta\alpha = 1/N \tag{5}
$$

单位为 normalized-frequency units。最后，点估计与 cycle frequency $\alpha_i$ 和 spectral frequency $f_j$ 关联，而这两个量由输出 transform 涉及的谱分量定义：

$$
\alpha_i = f_k - f_l \tag{6}
$$

以及：

$$
f_j = (f_k + f_l)/2 \tag{7}
$$

### 在软件中实现 FAM 的基本步骤

#### Step 1: 查找并排列 $N^{\prime}$ 点数据子块

从 MATLAB 编码角度看，我们希望尽可能多地执行向量或矩阵操作，尽可能少地使用 for-loop。因此，当我们以 $L$ 个采样点为步长滑动并提取 $N^{\prime}$ 点 block 时，可以把每个 block 放入矩阵的一列：

![fam_data_blocks](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/05/fam_data_blocks.jpg?resize=381%2C121&ssl=1)

注意，为了得到完整的 $P$ 个 block，需要在输入 $x(t)$ 末尾补几个零。这样就得到一个具有 $N^{\prime}$ 行和 $P$ 列的矩阵。

#### Step 2: 对子块施加 data-tapering window

我们将对 Step 1 中 data-block 矩阵的每一列做 [Fourier transform](https://en.wikipedia.org/wiki/Fourier_transform)。在此之前，需要施加上面所说的 channelizer data-tapering window $a(\cdot)$。这里选择 Hamming window，它在 MATLAB 中可通过 m-file 函数 hamming.m 获得。把这个特定选择记为 $h(\cdot)$。data-block 矩阵的每一列都需要乘以长度为 $N^{\prime}$ 的 Hamming window：

![fam_data_blocks_window](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/05/fam_data_blocks_window.jpg?resize=529%2C121&ssl=1)

#### Step 3: 对加窗后的子块施加 Fourier transform

接下来，对每一列施加 Fourier transform。在 MATLAB 中用 fft.m 很容易做到，但这里有一个复杂点。对矩阵的每一列使用 fft.m 后，各 block 之间存在的相对延迟会丢失。也就是说，公式 (2) 并没有被精确计算；由于使用 fft.m 以获得计算效率，transform 之间的相位关系被修改了。

![fam_channelized](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/05/fam_channelized.jpg?resize=327%2C122&ssl=1)

因此，在对 data blocks 做 FFT 后，需要对它们进行 phase-shift。某个元素的相移取决于频率 $f_j$ 和时间索引 $rL$。这与 spectral correlation estimation 的 time-smoothing method 中所做的处理类似；详见 [this post](http://cyclostationary.blog/2015/12/18/csp-estimators-the-time-smoothing-method/)。

对输入 $y(t)$ 做同样的事情。如果 $x(t) == y(t)$，则不需要重复计算；否则需要执行相同流程：

![fam_channelized_Y](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/05/fam_channelized_y.jpg?fit=327%2C122&ssl=1)

#### Step 4: 将 channelized subblocks 相乘并做 Fourier transform

回看公式 (1)，现在需要将 $X$ 矩阵中的一行与 $Y$ 矩阵中的一行逐元素相乘，并对后者取共轭。这会得到一个长度为 $P$ 的复数向量，然后可以对该向量使用 FFT。例如，下图中框出了 $f_k = f_1$ 对应的 $X$ 值和 $f_l = f_2$ 对应的 $Y$ 值。

![fam_channelized_boxed](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/05/fam_channelized_boxed.jpg?fit=340%2C122&ssl=1)

![fam_channels_Y_boxed](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/05/fam_channels_y_boxed.jpg?fit=338%2C122&ssl=1)

#### Step 5: 将每个 Fourier transform 输出关联到正确的 $(f, \alpha)$

根据公式 (1)，来自 channelizer product vector 的 Fourier transform 的 $P$ 个值，对应 $P$ 个 cycle frequencies：

$$
\alpha_i + q\Delta \alpha \tag{8}
$$

其中 $\Delta\alpha$ 和 $\alpha_i$ 分别由公式 (5) 和 (6) 定义，$q$ 遍历 $P$ 个整数。这个对应关系会产生 spectral correlation function 熟悉的 [diamond-shaped principal domain](https://cyclostationary.blog/2021/10/30/the-principal-domain-for-the-spectral-correlation-function/) 中的值；任何不在该区域内的值都可以丢弃。到这里，我们就得到了大量 spectral correlation function 的点估计：spectral frequency 位于 normalized range $[-0.5, 0.5)$，cycle frequency 位于 $[-1.0, 1.0)$。

### 扩展到 Conjugate Spectral Correlation Function

如果 $x(t) = y(t)$，则 $Y_T(t,f) = X_T(t,f)$，公式 (1) 产生的估计对应 auto [non-conjugate](http://cyclostationary.blog/2016/02/29/conjugation-configurations/) spectral correlation function。如果 $y(t) = x^*(t)$，则该估计对应 [conjugate](http://cyclostationary.blog/2016/02/29/conjugation-configurations/) spectral correlation function。否则，它就是一般的 cross spectral correlation function。扩展到 conjugate spectral correlation function 就这么简单。把 conjugate spectral correlation function 进一步扩展到 conjugate coherence，只比 non-conjugate spectral correlation 扩展到 non-conjugate coherence 稍微复杂一点。

### 扩展到 Coherence

回顾一下，[spectral coherence function](http://cyclostationary.blog/2016/01/08/the-spectral-coherence-function/) 或简称 coherence，对 non-conjugate spectral correlation function 的定义为：

$$
C_x^\alpha(f) = \frac{S_x^\alpha(f)}{\left[ S_x^0(f+\alpha/2)S_x^0(f-\alpha/2) \right]^{1/2}} \tag{9}
$$

conjugate coherence 给为：

$$
C_{x^*}^\alpha(f) = \frac{S_{x^*}^\alpha(f)}{\left[ S_x^0(f+\alpha/2) S_x^0(\alpha/2 - f) \right]^{1/2}} \tag{10}
$$

因此，要计算 coherence 估计，需要逐个遍历 spectral correlation estimates，根据 Step 5 找到对应的 spectral frequency $f$ 和 cycle frequency $\alpha$，然后使用 PSD 估计找到构成归一化因子的两个 PSD 值。作者通常使用一个高度 oversampled 的 PSD 辅助估计，这样对任何有效的 spectral frequency $f$ 与 cycle-frequency shift $\pm\alpha/2$ 组合，都能容易地找到所需 PSD 值。[frequency-smoothing method](http://cyclostationary.blog/2015/11/20/csp-estimators-the-frequency-smoothing-method/) 是生成这类 PSD 估计的一个好选择。

coherence 对自动检测显著 cycle frequencies 尤其有用，因为它对信号功率和噪声功率水平具有不变性，相关说明可见 SSCA 文章的评论部分。

### 示例

下面来看作者实现的 FAM 输出，并将其与 strip spectral correlation analyzer 对比；当然也会和一个经典 rectangular-pulse BPSK 信号的已知 spectral correlation surface 对比。

#### Rectangular-Pulse BPSK（教科书信号）

首先，回顾一下 [theoretical spectral correlation function](http://cyclostationary.blog/2015/09/28/the-spectral-correlation-function-for-rectangular-pulse-bpsk/)：这是一个 rectangular-pulse BPSK 信号，bits 独立同分布，每 bit 十个采样点，carrier offset 为 $0.05$：

![ww_ideal_scf_BPSK_fs_1](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/ww_ideal_scf_bpsk_fs_1.jpg?fit=771%2C1024&ssl=1)

Figure 1. rectangular-pulse BPSK 的理论 spectral correlation surfaces。这些曲面来自对 BPSK 已知 spectral correlation 公式的数值计算。

该信号表现出 non-conjugate cycle frequencies，它们是 bit rate 的整数倍，即 $\alpha = kf_{bit}, k = 0, \pm 1, \pm 2, \ldots$。当 $f_{bit} = 0.1$ 时，该集合为 $\{0, \pm 0.1, \pm 0.2, \ldots\}$。由于 [symmetry considerations](https://cyclostationary.blog/2019/12/12/symmetries-of-second-order-probabilistic-parameters-in-csp/)，绘图时忽略负的 non-conjugate cycle frequencies。

它还表现出 conjugate cycle frequencies，这些频率等于 non-conjugate cycle frequencies 加上 doubled carrier $2f_c = 2(0.05) = 0.1$。当 $\alpha = 2f_c$ 时，conjugate spectral correlation function 的形状与 $\alpha = 0$ 时 non-conjugate spectral correlation function，也就是 PSD 的形状相同。

先从 rectangular-pulse BPSK 的 FAM power spectrum estimate 开始，并将其与 TSM-based PSD estimate 对比：

![fam_tsm_psd_plot_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_tsm_psd_plot_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 2. 两种 power spectral density 估计的比较：FAM 与 time-smoothing method (`TSM`)。

两个 PSD 估计都符合我们对该信号的预期，但可以看到 FAM 估计中存在一个小的规则 ripple，而 TSM 估计中没有。我们知道这个 ripple 不是该信号 PSD 的真实特征，因此这是作者尚未解决的一个疑点。不过后面会看到，从 cycle frequencies、spectral correlation magnitudes 和 spectral coherence magnitudes 角度看，作者创建的 FAM 实现整体上与 SSCA 输出相当一致。

接下来展示 FAM-based non-conjugate 和 conjugate spectral correlation surfaces。先说明处理参数：

后一个参数会与 $N$ 和 $N^{\prime}$ 一起用于计算 coherence function 的 threshold。只有那些 coherence magnitude 超过 threshold 的点估计，才会被包含在下面的 FAM spectral correlation surface 图中：

![fam_surf_nonconj_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_surf_nonconj_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 3. FAM 生成的 non-conjugate spectral correlation function estimates。

![fam_surf_conj_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_surf_conj_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 4. FAM 生成的 conjugate spectral correlation function estimates。

因此，FAM surfaces 在已知 cycle frequency values 以及每个 coherence-detected $\alpha$ 上随 spectral frequency $f$ 的变化方面，都与 ideal surfaces 一致。换句话说，它是有效的。

下面的图展示 FAM 与 SSCA 的 cyclic domain profiles 对比：

![fam_ssca_cdp_scf_nc_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_scf_nc_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 5. rectangular-pulse BPSK 的 FAM 与 SSCA non-conjugate spectral-correlation cyclic-domain profile 结果。

![fam_ssca_cdp_scf_c_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_scf_c_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 6. FAM 与 SSCA 生成的 conjugate spectral-correlation cyclic-domain profile estimates。

![fam_ssca_cdp_coh_nc_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_coh_nc_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 7. rectangular-pulse BPSK 的 FAM 与 SSCA non-conjugate spectral-coherence cyclic-domain profile 结果。

![fam_ssca_cdp_coh_c_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_coh_c_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 8. rectangular-pulse BPSK 的 FAM 与 SSCA conjugate spectral-coherence cyclic-domain profile 结果。

最后，下面只绘制 coherence-threshold 检测到的 cycle frequencies，这是 CSP 实践中常见的期望输出：

![fam_ssca_cfs_scf_nc_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_scf_nc_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 9. rectangular-pulse BPSK 的 FAM 与 SSCA non-conjugate spectral-correlation cyclic-domain profile 结果，仅显示 coherence magnitudes 超过 threshold 的 cycle frequencies。

![fam_ssca_cfs_coh_nc_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_coh_nc_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 10. rectangular-pulse BPSK 的 FAM 与 SSCA non-conjugate spectral-coherence cyclic-domain profile 结果，仅显示 coherence magnitudes 超过 threshold 的 cycle frequencies。

![fam_ssca_cfs_scf_c_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_scf_c_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 11. rectangular-pulse BPSK 的 FAM 与 SSCA conjugate spectral-correlation cyclic-domain profile 结果，仅显示 coherence magnitudes 超过 threshold 的 cycle frequencies。

![fam_ssca_cfs_coh_c_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_coh_c_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 12. rectangular-pulse BPSK 的 FAM 与 SSCA conjugate spectral-coherence cyclic-domain profile 结果，仅显示 coherence magnitudes 超过 threshold 的 cycle frequencies。

两个算法都只检测到了真实的 cycle frequencies。对于所有其他 cycle frequencies，spectral correlation 和 coherence 的平均值在 FAM 与 SSCA 之间大致相同。这里有两个异常值得提到。第一个异常是：SSCA 在 doubled-carrier conjugate cycle frequency $0.1$ 上产生了显著大于 1 的 coherence。第二个异常是：FAM 在 spectral correlation function 中产生了一些 false peaks，位置接近 $0.6, 0.7,$ 和 $0.8$。这些 false peaks 的 coherence magnitudes 都没有超过 threshold，因此最终不会被检测出来，也不会出现在后面的图中。作者尚不知道这些 spurious spectral correlation peaks 的来源。

#### Captured DSSS BPSK

最后，用一个非教科书信号，即 captured DSSS BPSK 信号，展示 FAM 与 SSCA 结果。DSSS BPSK 具有许多 cycle frequencies，既包括 non-conjugate，也包括 conjugate；并且随着 processing gain 增大，cycle frequencies 的数量也会增加。更多细节和示例可参考 [DSSS post](http://cyclostationary.blog/2017/03/28/cyclostationarity-of-direct-sequence-spread-spectrum-signals/) 和 [SCF Gallery](http://cyclostationary.blog/2016/01/28/a-gallery-of-spectral-correlation/)。

在这个示例中，采样率任意设为 $5$ MHz，处理的采样点数为 $N = 65536$。

![fam_tsm_psd_plot_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_tsm_psd_plot_dsss.jpg?fit=840%2C473&ssl=1)

Figure 13. captured DSSS BPSK 信号的 FAM 与 TSM power spectrum estimates。

![fam_surf_nonconj_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_surf_nonconj_dsss.jpg?fit=840%2C473&ssl=1)

Figure 14. captured DSSS BPSK 信号的 FAM-produced non-conjugate spectral correlation surface。

![fam_surf_conj_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_surf_conj_dsss.jpg?fit=840%2C473&ssl=1)

Figure 15. captured DSSS BPSK 信号的 FAM-produced conjugate spectral correlation surface。

![fam_ssca_cdp_scf_nc_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_scf_nc_dsss.jpg?fit=840%2C473&ssl=1)

Figure 16. captured DSSS BPSK 信号的 FAM 与 SSCA non-conjugate spectral correlation cyclic-domain profile。

![fam_ssca_cdp_scf_c_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_scf_c_dsss.jpg?fit=840%2C473&ssl=1)

Figure 17. captured DSSS BPSK 信号的 FAM 与 SSCA conjugate spectral correlation cyclic-domain profile。

![fam_ssca_cdp_coh_nc_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_coh_nc_dsss.jpg?fit=840%2C473&ssl=1)

Figure 18. captured DSSS BPSK 信号的 FAM 与 SSCA non-conjugate spectral coherence cyclic-domain profile。

![fam_ssca_cdp_coh_c_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_coh_c_dsss.jpg?fit=840%2C473&ssl=1)

Figure 19. captured DSSS BPSK 信号的 FAM 与 SSCA conjugate spectral coherence cyclic-domain profile。

![fam_ssca_cfs_scf_nc_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_scf_nc_dsss.jpg?fit=840%2C473&ssl=1)

Figure 20. captured DSSS BPSK 信号的 FAM 与 SSCA non-conjugate spectral correlation cyclic-domain profile，仅使用 coherence magnitudes 超过 threshold 的 cycle frequencies。

![fam_ssca_cfs_scf_c_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_scf_c_dsss.jpg?fit=840%2C473&ssl=1)

Figure 21. captured DSSS BPSK 信号的 FAM 与 SSCA conjugate spectral correlation cyclic-domain profile，仅使用 coherence magnitudes 超过 threshold 的 cycle frequencies。

![fam_ssca_cfs_coh_nc_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_coh_nc_dsss.jpg?fit=840%2C473&ssl=1)

Figure 22. captured DSSS BPSK 信号的 FAM 与 SSCA non-conjugate spectral coherence cyclic-domain profile，仅使用 coherence magnitudes 超过 threshold 的 cycle frequencies。

![fam_ssca_cfs_coh_c_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_coh_c_dsss.jpg?fit=840%2C473&ssl=1)

Figure 23. captured DSSS BPSK 信号的 FAM 与 SSCA conjugate spectral coherence cyclic-domain profile，仅使用 coherence magnitudes 超过 threshold 的 cycle frequencies。

[Support the CSP Blog here.](https://cyclostationary.blog/2019/07/14/sponsoring-the-csp-blog/)
