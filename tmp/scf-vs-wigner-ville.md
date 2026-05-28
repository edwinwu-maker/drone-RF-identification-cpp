# 二阶循环谱与 Wigner-Ville 分布的关系

二阶循环谱（second-order cyclic spectrum / SCF）和 Wigner-Ville 分布（WVD）都来自同一个二阶时频相关核：

$$
R_x(t,\tau)=x(t+\tau/2)x^*(t-\tau/2)
$$

其中，$t$ 表示时间，$\tau$ 表示时延，$x^*(\cdot)$ 表示复共轭。

## Wigner-Ville 分布

Wigner-Ville 分布对时延 $\tau$ 做傅里叶变换：

$$
W_x(t,f)=\int x(t+\tau/2)x^*(t-\tau/2)e^{-j2\pi f\tau}d\tau
$$

它描述信号能量如何分布在时间-频率平面上，因此变量是：

- 时间 $t$
- 频率 $f$

直观地说，WVD 关心的是信号的瞬时时频结构。

## WVD 从连续到离散的推导

连续 WVD 定义为：

$$
W_x(t,f)=\int_{-\infty}^{\infty}
x(t+\tau/2)x^*(t-\tau/2)e^{-j2\pi f\tau}d\tau
$$

令连续时间信号以采样周期 $T_s$ 采样：

$$
x[n]=x(nT_s)
$$

时间变量离散化为：

$$
t=nT_s
$$

若直接令时延 $\tau=mT_s$，则核函数中会出现：

$$
x\left((n+m/2)T_s\right)x^*\left((n-m/2)T_s\right)
$$

当 $m$ 为奇数时，$n+m/2$ 与 $n-m/2$ 不是整数采样点，会产生半采样索引。为了避免这一点，离散 WVD 通常令连续时延取偶数个采样间隔：

$$
\tau=2mT_s
$$

代入连续 WVD：

$$
W_x(nT_s,f)=\int x(nT_s+\tau/2)x^*(nT_s-\tau/2)e^{-j2\pi f\tau}d\tau
$$

用离散求和近似积分，并令 $\tau=2mT_s$：

$$
W_x[n,f]\approx
\sum_m x[(n+m)]x^*[(n-m)]e^{-j2\pi f(2mT_s)}
$$

若使用归一化数字频率 $\nu=fT_s$，则：

$$
W_x[n,\nu]=
\sum_m x[n+m]x^*[n-m]e^{-j4\pi \nu m}
$$

这里 $\nu$ 的单位是 cycles/sample，取值通常在 $[-1/2,1/2)$。

## WVD 的离散表达式

对有限长离散信号，WVD 常写为：

$$
W_x[n,k]=\sum_{m=-M}^{M}
x[n+m]x^*[n-m]e^{-j\frac{4\pi}{N}km}
$$

其中：

- $n$ 是时间索引。
- $m$ 是离散时延索引的一半。
- $k$ 是离散频率索引。
- $N$ 是频率方向 DFT 点数。
- $M$ 由信号边界和所选窗口长度决定。

若令：

$$
r_x[n,m]=x[n+m]x^*[n-m]
$$

则离散 WVD 可以看成对局部时延积 $r_x[n,m]$ 沿 $m$ 方向做傅里叶变换：

$$
W_x[n,k]=\sum_m r_x[n,m]e^{-j\frac{4\pi}{N}km}
$$

注意指数里是 $4\pi$ 而不是普通 DFT 常见的 $2\pi$，这是因为离散推导中使用了对称采样点 $n+m$ 与 $n-m$，两点间实际时延为 $2m$ 个采样间隔。

为了写成标准 DFT 形式，也可以定义偶时延变量：

$$
\ell=2m
$$

此时连续定义中的 $\tau$ 对应离散时延 $\ell$，核函数形式为：

$$
x[n+\ell/2]x^*[n-\ell/2]
$$

但只有当 $\ell$ 为偶数时索引才是整数。因此实际实现中常使用 $m$ 表示半时延，并写成 $x[n+m]x^*[n-m]$。

## 离散实现中的边界处理

有限长信号 $x[n]$ 只在 $0\le n<L$ 范围内有定义，因此 $x[n+m]$ 和 $x[n-m]$ 必须同时落在有效范围内：

$$
0\le n+m < L
$$

$$
0\le n-m < L
$$

所以每个时间点 $n$ 允许的最大 $|m|$ 为：

$$
|m|\le \min(n,L-1-n)
$$

实际计算时常见做法包括：

- 只对有效 $m$ 求和。
- 对信号两端补零。
- 使用滑动窗口限制 $m$ 的范围，得到平滑伪 Wigner-Ville 分布。

窗口化后的形式可写为：

$$
W_x[n,k]=\sum_m h[m]x[n+m]x^*[n-m]e^{-j\frac{4\pi}{N}km}
$$

其中 $h[m]$ 是时延方向窗口，用于控制交叉项与频率分辨率之间的权衡。

## 二阶循环谱

循环自相关函数（CAF）先对时间 $t$ 做傅里叶分析：

$$
R_x^\alpha(\tau)=\lim_{T\to\infty}\frac{1}{T}\int_{-T/2}^{T/2}
x(t+\tau/2)x^*(t-\tau/2)e^{-j2\pi \alpha t}dt
$$

再对时延 $\tau$ 做傅里叶变换，得到二阶循环谱：

$$
S_x^\alpha(f)=\int R_x^\alpha(\tau)e^{-j2\pi f\tau}d\tau
$$

因此二阶循环谱也可以写成 WVD 在时间方向上的傅里叶分量：

$$
S_x^\alpha(f)
=
\lim_{T\to\infty}\frac{1}{T}\int_{-T/2}^{T/2}
W_x(t,f)e^{-j2\pi \alpha t}dt
$$

这里的 $\alpha$ 是循环频率，表示信号二阶统计特性随时间周期变化的频率。

## 二阶循环谱从连续到离散的推导

连续时间 CAF 定义为：

$$
R_x^\alpha(\tau)=
\lim_{T\to\infty}\frac{1}{T}
\int_{-T/2}^{T/2}
x(t+\tau/2)x^*(t-\tau/2)e^{-j2\pi\alpha t}dt
$$

令：

$$
t=nT_s
$$

并为了避免半采样索引，令：

$$
\tau=2mT_s
$$

其中 $m$ 是半时延索引。代入后：

$$
x(t+\tau/2)=x((n+m)T_s)=x[n+m]
$$

$$
x^*(t-\tau/2)=x^*((n-m)T_s)=x^*[n-m]
$$

时间积分用离散平均近似：

$$
\frac{1}{T}\int_{-T/2}^{T/2}(\cdot)dt
\rightarrow
\frac{1}{N}\sum_{n=0}^{N-1}(\cdot)
$$

循环频率使用归一化数字循环频率：

$$
\alpha_d=\alpha T_s
$$

于是离散 CAF 的中心时延形式为：

$$
R_x^{\alpha_d}[m]=
\lim_{N\to\infty}\frac{1}{N}
\sum_{n=0}^{N-1}
x[n+m]x^*[n-m]e^{-j2\pi\alpha_d n}
$$

再对时延变量做傅里叶变换，即得到离散二阶循环谱：

$$
S_x^{\alpha_d}[\nu]=
\sum_m R_x^{\alpha_d}[m]e^{-j4\pi\nu m}
$$

其中 $\nu=fT_s$ 是归一化频率，单位是 cycles/sample。指数中出现 $4\pi$ 的原因与离散 WVD 相同：$x[n+m]$ 与 $x[n-m]$ 的实际间隔是 $2m$ 个采样点。

若频率离散化为 $N_f$ 个 DFT bin：

$$
\nu_k=\frac{k}{N_f}
$$

则：

$$
S_x^{\alpha_d}[k]=
\sum_m R_x^{\alpha_d}[m]e^{-j\frac{4\pi}{N_f}km}
$$

这就是二阶循环谱的离散中心时延表达式。

## 二阶循环谱的单边移位实现形式

实际代码中也常使用单边移位形式：

$$
\tilde{R}_x^{\alpha_d}[\ell]=
\lim_{N\to\infty}\frac{1}{N}
\sum_{n=0}^{N-1}
x[n]x^*[n-\ell]e^{-j2\pi\alpha_d n}
$$

对应的循环谱为：

$$
\tilde{S}_x^{\alpha_d}[\nu]=
\sum_\ell \tilde{R}_x^{\alpha_d}[\ell]e^{-j2\pi\nu\ell}
$$

这与中心时延形式只差一个由变量替换带来的相位因子。因为：

$$
\ell=2m
$$

中心时延形式更贴近理论定义，单边移位形式更方便离散实现。许多 Python 代码使用 `np.roll(samples, tau)` 时，本质上就是这种单边移位写法；若需要与中心时延定义严格对齐，通常会补偿一个与 $\alpha$ 和时延有关的相位项。

## 二阶循环谱的频域定义

二阶循环谱也可以从频域直接理解。需要注意的是，局部 Fourier transform 的窗口长度和后续时间平均的观测长度应区分开。令 $L$ 表示短时分析窗长度，$T$ 表示用于长期平均的观测长度。对信号做短时 Fourier transform：

$$
X_L(t,f)=\int x(u)a_L(u-t)e^{-j2\pi fu}du
$$

其中 $a_L(\cdot)$ 是长度约为 $L$ 的分析窗。则循环谱可以由两个频移谱分量的短时谱相关做时间平均来近似：

$$
S_x^\alpha(f)=
\lim_{T\to\infty}\frac{1}{T}
\int_{-T/2}^{T/2}
X_L(t,f+\alpha/2)X_L^*(t,f-\alpha/2)dt
$$

这个写法中，$L$ 控制短时谱估计的时间-频率分辨率，$T$ 控制谱相关的长期平均长度。原理上，二阶循环谱描述的是频率间隔为 $\alpha$ 的两个谱分量 $f+\alpha/2$ 与 $f-\alpha/2$ 之间的相关性。

这个形式非常重要，因为 FSM、TSM 和 FAM 都可以看作对上式思想的不同离散近似：

- FSM：先做大 FFT，再在频率方向平滑。
- TSM：分块做短时 FFT，再在时间方向平均。
- FAM：分块做短时 FFT，再对时间方向的谱乘积做第二次 FFT，一次性得到多个循环频率。

## FAM 的推导

FAM（FFT Accumulation Method）的目标是高效估计：

$$
S_x^\alpha(f)
$$

它从短时谱相关形式出发：

$$
X_L(t,f+\alpha/2)X_L^*(t,f-\alpha/2)
$$

更一般地，令两个短时频率通道为 $f_1$ 和 $f_2$，可以先构造连续时间上的短时谱乘积：

$$
Y_{f_1,f_2}(t)=X_L(t,f_1)X_L^*(t,f_2)
$$

其中频率中心和粗循环频率分别为：

$$
f=\frac{f_1+f_2}{2}
$$

$$
\alpha_0=f_1-f_2
$$

FAM 的思想不是只对 $Y_{f_1,f_2}(t)$ 做时间平均，而是沿短时时间轴 $t$ 做 Fourier 分析：

$$
Z_{f_1,f_2}(\beta)
=
\lim_{T\to\infty}\frac{1}{T}
\int_{-T/2}^{T/2}
Y_{f_1,f_2}(t)e^{-j2\pi\beta t}dt
$$

其中 $\beta$ 是由时间轴 Fourier 分析得到的细循环频率分量。因此连续形式下可以写成：

$$
\hat{S}_x^\alpha(f)\approx Z_{f_1,f_2}(\beta)
$$

其中：

$$
f=\frac{f_1+f_2}{2}
$$

$$
\alpha=(f_1-f_2)+\beta
$$

离散实现时，先把信号切成 $P$ 个重叠窗口。第 $r$ 个窗口从样本 $rL$ 开始，窗口长度为 $N_p$，hop size 为 $L$。注意这里的 $L$ 表示窗口步长，与前文边界处理中用作信号长度的 $L$ 不是同一个量：

$$
x_r[n]=x[rL+n]a[n], \quad 0\le n<N_p
$$

其中 $a[n]$ 是分析窗，例如 Hanning 窗。对每个窗口做第一阶段 FFT：

$$
X[r,k]=
\sum_{n=0}^{N_p-1}
x[rL+n]a[n]e^{-j2\pi kn/N_p}
$$

这里 $k$ 是第一个 FFT 的频率 bin，对应归一化频率：

$$
f_k=\frac{k}{N_p}
$$

由于每个短时 FFT 的时间原点随窗口位置 $rL$ 移动，需要做相位校正：

$$
\tilde{X}[r,k]=X[r,k]e^{-j2\pi f_k rL}
$$

然后取两个频率通道 $k$ 和 $l$ 的乘积：

$$
Y_{k,l}[r]=
\tilde{X}[r,k]\tilde{X}^*[r,l]
$$

这个乘积对应频率中心：

$$
f=\frac{f_k+f_l}{2}
$$

并对应一个粗循环频率：

$$
\alpha_0=f_k-f_l
$$

如果只对 $Y_{k,l}[r]$ 在 $r$ 上求平均，就类似 TSM，只能得到固定的 $\alpha_0$。FAM 的关键是：对 $Y_{k,l}[r]$ 沿窗口序号 $r$ 再做一次 FFT：

$$
Z_{k,l}[q]=
\sum_{r=0}^{P-1}
Y_{k,l}[r]e^{-j2\pi qr/P}
$$

若使用 `fftshift` 后的中心化索引，可记为：

$$
q_c=q-P/2
$$

第二次 FFT 提供了循环频率的细分量。由于相邻窗口间隔为 $L$ 个采样点，第二次 FFT 的循环频率分辨率为：

$$
\Delta\alpha=\frac{1}{PL}
$$

因此最终循环频率近似为：

$$
\alpha=\alpha_0+\frac{q_c}{PL}
=
(f_k-f_l)+\frac{q_c}{PL}
$$

而对应的谱频率仍为：

$$
f=\frac{f_k+f_l}{2}
$$

所以 FAM 的离散估计可以概括为：

$$
\hat{S}_x^\alpha(f)
\approx
Z_{k,l}[q]
$$

其中：

$$
f=\frac{f_k+f_l}{2}
$$

$$
\alpha=(f_k-f_l)+\frac{q_c}{PL}
$$

实际实现通常会取幅度或幅度平方：

$$
|\hat{S}_x^\alpha(f)|
\quad \text{or} \quad
|\hat{S}_x^\alpha(f)|^2
$$

## FAM 的算法步骤

FAM 可以按以下步骤理解：

1. 将输入信号分成重叠窗口。
2. 对每个窗口加分析窗 $a[n]$。
3. 对每个窗口做第一阶段 FFT，得到 $X[r,k]$。
4. 对 $X[r,k]$ 做相位校正，得到 $\tilde{X}[r,k]$。
5. 对所有频率通道对 $(k,l)$ 计算 $\tilde{X}[r,k]\tilde{X}^*[r,l]$。
6. 对窗口序号 $r$ 做第二阶段 FFT。
7. 将结果映射到 $(f,\alpha)$ 平面。

FAM 的优势是可以一次性估计大量循环频率；代价是会生成较大的二维谱相关矩阵，且需要处理 $(k,l)$ 通道对带来的计算量与存储量。

## FAM 与 TSM 的关系

TSM 对短时谱乘积做时间平均：

$$
\frac{1}{P}\sum_{r=0}^{P-1}
\tilde{X}[r,k]\tilde{X}^*[r,l]
$$

这相当于只取第二次 FFT 的零频分量：

$$
Z_{k,l}[0]
$$

FAM 则保留第二次 FFT 的所有 $q$ 分量，因此能够在同一次计算中得到一组循环频率：

$$
\alpha=(f_k-f_l)+\frac{q_c}{PL}
$$

所以可以把 FAM 理解为：把 TSM 的“时间平均”升级为“沿时间窗口序列做 FFT”，从而把时间周期性显式展开到循环频率轴上。

## 核心区别

| 对象 | 关注点 | 变量 | 直观含义 |
|---|---|---|---|
| Wigner-Ville 分布 | 瞬时时频能量 | $t, f$ | 信号能量在时间和频率上的分布 |
| 二阶循环谱 | 时频结构的周期性 | $\alpha, f$ | 信号二阶统计特性在哪些循环频率上重复 |

## 关系总结

二阶循环谱可以理解为 Wigner-Ville 分布沿时间轴的傅里叶分析结果。

换句话说：

- WVD 看的是“某一时刻有哪些频率成分”。
- SCF 看的是“这些频率结构是否随时间周期性重复”。
- 当 $\alpha=0$ 时，二阶循环谱退化为普通功率谱密度（PSD）。
- 当 $\alpha\neq0$ 时，二阶循环谱揭示调制、符号率、循环前缀、载频偏等造成的循环平稳结构。

因此，WVD 更偏向时频表示，而二阶循环谱更偏向循环平稳特征提取。
