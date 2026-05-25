---
title: "CSP Estimators: The FFT Accumulation Method – Cyclostationary Signal Processing"
source: "https://cyclostationary.blog/2018/06/01/csp-estimators-the-fft-accumulation-method/"
author:
  - "[[View all posts by Chad Spooner]]"
published: 2001-07-14
created: 2026-05-25
description: "An alternative to the strip spectral correlation analyzer."
tags:
  - "clippings"
---
Let’s look at another [spectral correlation function](http://cyclostationary.blog/2015/09/28/the-spectral-correlation-function/) estimator: the FFT Accumulation Method (FAM). This estimator is in the time-smoothing category, is exhaustive in that it is designed to compute estimates of the spectral correlation function over its entire principal domain, and is efficient, so that it is a competitor to the [Strip Spectral Correlation Analyzer](http://cyclostationary.blog/2016/03/22/csp-estimators-the-strip-spectral-correlation-analyzer/) (SSCA) method. I implemented my version of the FAM by using the paper by Roberts *et al* ([The Literature](http://cyclostationary.blog/the-literature/) \[R4\]). If you follow the equations closely, you can successfully implement the estimator from that paper. The tricky part, as with the SSCA, is correctly associating the outputs of the coded equations to their proper $(f, \alpha)$ values.

We’ll also implement a [coherence](http://cyclostationary.blog/2016/01/08/the-spectral-coherence-function/) computation in our FAM, and use it to automatically detect the significant cycle frequencies, just as we like to do with the SSCA. Finally, we’ll compare outputs between the SSCA and FAM spectral-correlation and spectral-coherence estimation methods. The algorithms’ implementations are not without issues and mysteries, and we’ll point them out too. Please leave corrections, comments, and clarifications in the comment section.

### Definition of the FFT Accumulation Method

The method produces a large number of point estimates of the cross spectral correlation function. In \[R4\], the point estimates are given by

$$
S_{xy_T}^{\alpha_i + q\Delta\alpha} (nL, f_j)_{\Delta\!t} = \sum_{r}X_T(rL, f_k) Y_T^* (rL, f_l) g_c(n-r) e^{-i2\pi r q /P} \tag{1}
$$

where the complex demodulates are given by

$$
X_T(n,f) = \sum_{r=-N^{\prime}/2}^{N^{\prime}/2} a(r) x(n-r) e^{-i 2 \pi f(n-r)T_s} \tag{2}
$$

Equation (2) here is Equation (2) in \[R4\]. I think it should have a sum over $N^{\prime}$ samples, rather than $N^{\prime}+1$,

$$
X_T(n,f) = \sum_{r=-N^{\prime}/2}^{N^{\prime}/2-1} a(r) x(n-r) e^{-i 2 \pi f(n-r)T_s} \tag{3}
$$

In (1), the function $g_c(n)$ is a [data-tapering window](https://en.wikipedia.org/wiki/Window_function), which is commonly taken to be a unit-height rectangle (and therefore no actual multiplications are needed), and in (2), the function $a(r)$ is another tapering window, which is often taken to be a Hamming window (can be generated using MATLAB’s [hamming.m](https://www.mathworks.com/help/signal/ref/hamming.html)).

The sampling rate is $f_s = 1/T_s$. In (2) and (3), $T = N^{\prime} T_s$. The channelizer (short-time hopped) Fourier transforms’ tapering window $a(r)$ has width $T_s N^{\prime}$, and the output (long-time) Fourier transforms’ tapering window $g_c(r)$ has width $NT_s$, which is the length of the data-block that is processed.

So the FAM channelizes the input data using short Fourier transforms of length $N^{\prime}$, which are hopped in time by $L$ samples. This results in a sequence of transforms that has length

$$
P = N/L \tag{4}
$$

where here I am assuming that both $N$ and $L$ are dyadic integers, with $L \ll N$. Therefore, the length of the output Fourier transforms is $P$.

For (1), \[R4\] defines the cycle-frequency resolution as

$$
\Delta\alpha = 1/N \tag{5}
$$

in normalized-frequency units. Finally, the point estimate is associated with the cycle frequency $\alpha_i$ and the spectral frequency $f_j$, which are defined in terms of the spectral components involved in the output transform:

$$
\alpha_i = f_k - f_l \tag{6}
$$

and

$$
f_j = (f_k + f_l)/2 \tag{7}
$$

### Basic Steps in Implementing the FAM in Software

#### Step 1: Find and Arrange the $N^{\prime}$-Point Data Subblocks

Thinking in terms of MATLAB coding, we’d like to perform as many vector or matrix operations as possible, and as few for-loop operations as possible. So when we extract our blocks of $N^{\prime}$ samples, sliding along by $L$ samples, we can place each one in a column of a matrix:

![fam_data_blocks](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/05/fam_data_blocks.jpg?resize=381%2C121&ssl=1)

Note that to achieve the full set of $P$ blocks, we’ll need to add a few zeroes to the end of the input $x(t)$. So now we have a matrix with $N^{\prime}$ rows and $P$ columns.

#### Step 2: Apply Data-Tapering Window to Subblocks

We will be [Fourier transforming](https://en.wikipedia.org/wiki/Fourier_transform) each column of the data-block matrix from Step 1, but before that we’ll apply the channelizer data-tapering window called $a(\cdot)$ above. Let’s pick the Hamming window, available in MATLAB as the m-file function hamming.m. Let’s denote this particular choice for $a(\cdot)$ by $h(\cdot)$. Each column of our data-block matrix needs to be multiplied by a Hamming window with length $N^{\prime}$:

![fam_data_blocks_window](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/05/fam_data_blocks_window.jpg?resize=529%2C121&ssl=1)

#### Step 3: Apply Fourier Transform to Windowed Subblocks

Next, apply the Fourier transform to each column. This is easy in MATLAB with fft.m, but there is a complication. The relative delay that exists between each of the blocks in the matrix is lost when fft.m is applied to each column. That is, (2) above is not exactly computed; the phase relationship between the transforms is modified through the use of fft.m, which we want to use for computational efficiency.

![fam_channelized](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/05/fam_channelized.jpg?resize=327%2C122&ssl=1)

So after the FFT is applied to the data blocks, they need to be phase-shifted. The phase shift for a particular element depends on the frequency $f_j$ and the time index $rL$. This is similar to what we do in the time-smoothing method of spectral correlation estimation; see [this post](http://cyclostationary.blog/2015/12/18/csp-estimators-the-time-smoothing-method/) for details.

Do the same thing for the input $y(t)$. If $x(t) == y(t)$, then don’t bother repeating the computation, otherwise, do so:

![fam_channelized_Y](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/05/fam_channelized_y.jpg?fit=327%2C122&ssl=1)

#### Step 4: Multiply Channelized Subblocks Together and Fourier Transform

Looking back at (1), we now need to multiply (elementwise) one row from the $X$ matrix by one row from the $Y$ matrix, conjugating the latter. This will result in a vector of $P$ complex values, which can then be transformed using the FFT. For example, below I’ve boxed the $X$ values for $f_k = f_1$ and the $Y$ values for $f_l = f_2$.

![fam_channelized_boxed](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/05/fam_channelized_boxed.jpg?fit=340%2C122&ssl=1)

![fam_channels_Y_boxed](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/05/fam_channels_y_boxed.jpg?fit=338%2C122&ssl=1)

#### Step 5: Associate Each Fourier Transform Output with the Correct \(f, \\alpha)

According to (1), the $P$ values that arise from the Fourier transform of the channelizer product vector correspond to the $P$ cycle frequencies

$$
\alpha_i + q\Delta \alpha \tag{8}
$$

where $\Delta\alpha$ and $\alpha_i$ are defined in (5) and (6), and $q$ ranges over $P$ integers. This association leads to values in the familiar [diamond-shaped principal domain](https://cyclostationary.blog/2021/10/30/the-principal-domain-for-the-spectral-correlation-function/) of the spectral correlation function; any values that do not lie in that region can be discarded. So at this point, we have a large number of spectral correlation function point estimates for frequencies in the (normalized) range $[-0.5, 0.5)$ and cycle frequencies in the range $[-1.0, 1.0)$.

### Extension to the Conjugate Spectral Correlation Function

If $x(t) = y(t)$, then $Y_T(t,f) = X_T(t,f)$, and the estimate produced by (1) corresponds to the (auto) [non-conjugate](http://cyclostationary.blog/2016/02/29/conjugation-configurations/) spectral correlation function. If $y(t) = x^*(t)$, then the estimate corresponds to the [conjugate](http://cyclostationary.blog/2016/02/29/conjugation-configurations/) spectral correlation function. Otherwise, it is a generic cross spectral correlation function. The extension to the conjugate spectral correlation function is that easy! It’s only a little more complicated to extend the conjugate spectral correlation function to the conjugate coherence than it is to extend the non-conjugate spectral correlation to the non-conjugate coherence.

### Extension to Coherence

Recall that the [spectral coherence function](http://cyclostationary.blog/2016/01/08/the-spectral-coherence-function/), or just coherence, is defined for the non-conjugate spectral correlation function by

$$
C_x^\alpha(f) = \frac{S_x^\alpha(f)}{\left[ S_x^0(f+\alpha/2)S_x^0(f-\alpha/2) \right]^{1/2}} \tag{9}
$$

The conjugate coherence is given by

$$
C_{x^*}^\alpha(f) = \frac{S_{x^*}^\alpha(f)}{\left[ S_x^0(f+\alpha/2) S_x^0(\alpha/2 - f) \right]^{1/2}} \tag{10}
$$

To compute estimates of the coherence, then, go through the spectral correlation estimates one by one, find the associated spectral frequency $f$ and cycle frequency $\alpha$ from Step 5, and then use a PSD estimate to find the corresponding two PSD values that form the normalization factor. I typically use a side estimate of the PSD that is highly oversampled so it is easy to find the required PSD values for any valid combination of spectral frequency $f$ and cycle-frequency shift $\pm\alpha/2$. The [frequency-smoothing method](http://cyclostationary.blog/2015/11/20/csp-estimators-the-frequency-smoothing-method/) is a good choice for creating such PSD estimates.

The coherence is especially useful for automatic detection of significant cycle frequencies in a way that is invariant to signal and noise power levels, as described in the comments of the SSCA post.

### Examples

Let’s look at the output of the FAM I’ve implemented with an eye toward comparing to the strip spectral correlation analyzer and (of course!) to the known spectral correlation surface for our old friend the [rectangular-pulse BPSK signal](http://cyclostationary.blog/2015/09/28/creating-a-simple-cs-signal-rectangular-pulse-bpsk/).

#### Rectangular-Pulse BPSK (Textbook Signal)

First, let’s review the [theoretical spectral correlation function](http://cyclostationary.blog/2015/09/28/the-spectral-correlation-function-for-rectangular-pulse-bpsk/) for a rectangular-pulse BPSK signal with independent and identically distributed bits, ten samples per bit, and a carrier offset of $0.05$:

![ww_ideal_scf_BPSK_fs_1](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/ww_ideal_scf_bpsk_fs_1.jpg?fit=771%2C1024&ssl=1)

Figure 1. Theoretical spectral correlation surfaces for rectangular-pulse BPSK. These arise from numerical evaluation of the known spectral correlation formula for BPSK.

The signal exhibits non-conjugate cycle frequencies that are multiples of the bit rate, or $\alpha = kf_{bit}, k = 0, \pm 1, \pm 2, \ldots$, which for $f_{bit} = 0.1$ is the set $\{0, \pm 0.1, \pm 0.2, \ldots\}$. Due to [symmetry considerations,](https://cyclostationary.blog/2019/12/12/symmetries-of-second-order-probabilistic-parameters-in-csp/) we ignore the negative non-conjugate cycle frequencies in our plots.

It also exhibits the conjugate cycle frequencies that are the non-conjugate cycle frequencies plus the doubled carrier $2f_c = 2(0.05) = 0.1$. The shape of the conjugate spectral correlation function for $\alpha = 2f_c$ is the same as that for the non-conjugate spectral correlation function for $\alpha = 0$ (the PSD).

Let’s start the progression of FAM results for rectangular-pulse BPSK with the FAM power spectrum estimate together with a TSM-based PSD estimate for comparison:

![fam_tsm_psd_plot_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_tsm_psd_plot_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 2. Comparison of two power spectral density estimates: The FAM and the time-smoothing method (TSM).

Both PSD estimates look like what we expect for the signal, but you can see a small regular ripple in the FAM estimate, which is not in the TSM estimate, and which we know is not a true feature of the PSD for the signal. So that is a mystery I’ve not yet solved. We’ll see, though, that overall the FAM implementation I’ve created compares well to the SSCA outputs in terms of cycle frequencies, spectral correlation magnitudes, and spectral coherence magnitudes.

Next, I want to show the FAM-based non-conjugate and conjugate spectral correlation surfaces. Let’s first mention the processing parameters:

The latter parameter is used, together with $N$ and $N^{\prime}$, to compute a threshold for the coherence function. Only those point estimates that correspond to a coherence magnitude that exceeds the threshold are included in the following FAM spectral correlation surface plots:

![fam_surf_nonconj_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_surf_nonconj_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 3. FAM-produced non-conjugate spectral correlation function estimates.

![fam_surf_conj_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_surf_conj_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 4. FAM-produced conjugate spectral correlation function estimates.

So the FAM surfaces agree with the ideal surfaces in terms of the known cycle frequency values and the variation over spectral frequency $f$ for each coherence-detected $\alpha$. In other words, it works.

In the following graphs, I show the cyclic domain profiles for the FAM and for the SSCA for comparison:

![fam_ssca_cdp_scf_nc_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_scf_nc_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 5. FAM-produced and SSCA-produced non-conjugate spectral-correlation cyclic-domain profile results for rectangular-pulse BPSK.

![fam_ssca_cdp_scf_c_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_scf_c_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 6. FAM-produced and SSCA-produced conjugate spectral-correlation cyclic-domain profile estimates.

![fam_ssca_cdp_coh_nc_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_coh_nc_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 7. FAM-produced and SSCA-produced non-conjugate spectral-coherence cyclic-domain profile results for rectangular-pulse BPSK.

![fam_ssca_cdp_coh_c_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_coh_c_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 8. FAM-produced and SSCA-produced conjugate spectral-coherence cyclic-domain profile results for rectangular-pulse BPSK.

Finally, here are plots of only the coherence-threshold detected cycle frequencies, which is a typical desired output in CSP practice:

![fam_ssca_cfs_scf_nc_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_scf_nc_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 9. FAM-produced and SSCA-produced non-conjugate spectral-correlation cyclic-domain profile results for rectangular-pulse BPSK showing only those cycle frequencies with coherence magnitudes that cross a threshold.

![fam_ssca_cfs_coh_nc_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_coh_nc_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 10. FAM-produced and SSCA-produced non-conjugate spectral-coherence cyclic-domain profile results for rectangular-pulse BPSK showing only those cycle frequencies with coherence magnitudes that cross a threshold.

![fam_ssca_cfs_scf_c_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_scf_c_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 11. FAM-produced and SSCA-produced conjugate spectral-correlation cyclic-domain profile results for rectangular-pulse BPSK showing only those cycle frequencies with coherence magnitudes that cross a threshold.

![fam_ssca_cfs_coh_c_bpsk](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_coh_c_bpsk.jpg?fit=840%2C473&ssl=1)

Figure 12. FAM-produced and SSCA-produced conjugate spectral-coherence cyclic-domain profile results for rectangular-pulse BPSK showing only those cycle frequencies with coherence magnitudes that cross a threshold.

Only true cycle frequencies are detected by both algorithms. The average values for spectral correlation and coherence for all the other cycle frequencies are about the same between the FAM and the SSCA. Two anomalies are worth mentioning. The first is that the SSCA produces a coherence significantly greater than one for the doubled-carrier conjugate cycle frequency of $0.1$. The second is that the FAM produces a few false peaks in the spectral correlation function (near $0.6, 0.7,$ and $0.8$). These all have coherence magnitudes that do not exceed threshold, so they don’t end up getting detected and don’t appear in the later plots. I don’t yet know the origin of these spurious spectral correlation peaks, and if you have an idea about it, feel free to leave a comment below.

#### Captured DSSS BPSK

Let’s end this post by showing FAM and SSCA results for a non-textbook signal, a captured DSSS BPSK signal. Recall that DSSS BPSK has many cycle frequencies, both non-conjugate and conjugate, and that the number of cycle frequencies increases as the processing gain increases. See the [DSSS post](http://cyclostationary.blog/2017/03/28/cyclostationarity-of-direct-sequence-spread-spectrum-signals/) and the [SCF Gallery](http://cyclostationary.blog/2016/01/28/a-gallery-of-spectral-correlation/) post for more details and examples.

In this example, the sampling rate is arbitrarily set to $5$ MHz, and the number of processed samples is $N = 65536$.

![fam_tsm_psd_plot_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_tsm_psd_plot_dsss.jpg?fit=840%2C473&ssl=1)

Figure 13. FAM-produced and TSM-produced power spectrum estimates for a captured DSSS BPSK signal.

![fam_surf_nonconj_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_surf_nonconj_dsss.jpg?fit=840%2C473&ssl=1)

Figure 14. FAM-produced non-conjugate spectral correlation surface for a captured DSSS BPSK signal.

![fam_surf_conj_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_surf_conj_dsss.jpg?fit=840%2C473&ssl=1)

Figure 15. FAM-produced conjugate spectral correlation surface for a captured DSSS BPSK signal.

![fam_ssca_cdp_scf_nc_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_scf_nc_dsss.jpg?fit=840%2C473&ssl=1)

Figure 16. FAM-produced and SSCA-produced non-conjugate spectral correlation cyclic-domain profile for a captured DSSS BPSK signal.

![fam_ssca_cdp_scf_c_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_scf_c_dsss.jpg?fit=840%2C473&ssl=1)

Figure 17. FAM-produced and SSCA-produced conjugate spectral correlation cyclic-domain profile for a captured DSSS BPSK signal.

![fam_ssca_cdp_coh_nc_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_coh_nc_dsss.jpg?fit=840%2C473&ssl=1)

Figure 18. FAM-produced and SSCA-produced non-conjugate spectral coherence cyclic-domain profile for a captured DSSS BPSK signal.

![fam_ssca_cdp_coh_c_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cdp_coh_c_dsss.jpg?fit=840%2C473&ssl=1)

Figure 19. FAM-produced and SSCA-produced conjugate spectral coherence cyclic-domain profile for a captured DSSS BPSK signal.

![fam_ssca_cfs_scf_nc_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_scf_nc_dsss.jpg?fit=840%2C473&ssl=1)

Figure 20. FAM-produced and SSCA-produced non-conjugate spectral correlation cyclic-domain profile for a captured DSSS BPSK signal using only those cycle frequencies that have coherence magnitudes that exceed a threshold.

![fam_ssca_cfs_scf_c_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_scf_c_dsss.jpg?fit=840%2C473&ssl=1)

Figure 21. FAM-produced and SSCA-produced conjugate spectral correlation cyclic-domain profile for a captured DSSS BPSK signal using only those cycle frequencies that have coherence magnitudes that exceed a threshold.

![fam_ssca_cfs_coh_nc_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_coh_nc_dsss.jpg?fit=840%2C473&ssl=1)

Figure 22. FAM-produced and SSCA-produced non-conjugate spectral coherence cyclic-domain profile for a captured DSSS BPSK signal using only those cycle frequencies that have coherence magnitudes that exceed a threshold.

![fam_ssca_cfs_coh_c_dsss](https://i0.wp.com/cyclostationary.blog/wp-content/uploads/2018/06/fam_ssca_cfs_coh_c_dsss.jpg?fit=840%2C473&ssl=1)

Figure 23. FAM-produced and SSCA-produced conjugate spectral coherence cyclic-domain profile for a captured DSSS BPSK signal using only those cycle frequencies that have coherence magnitudes that exceed a threshold.

[Support the CSP Blog here.](https://cyclostationary.blog/2019/07/14/sponsoring-the-csp-blog/)