# Conjugate SCF 与 Non-Conjugate SCF 的区别和联系

non-conjugate SCF 和 conjugate SCF 都是二阶循环谱，但它们检测的是不同类型的二阶周期相关结构。

## Non-Conjugate SCF

non-conjugate cyclic autocorrelation 定义为：

$$
R_x^\alpha(\tau)
=
\lim_{T\to\infty}
\frac{1}{T}
\int_{-T/2}^{T/2}
x(t+\tau/2)x^*(t-\tau/2)
e^{-j2\pi\alpha t}dt
$$

对应的 SCF 为：

$$
S_x^\alpha(f)
=
\int R_x^\alpha(\tau)e^{-j2\pi f\tau}d\tau
$$

它使用的二阶核是：

$$
x(t+\tau/2)x^*(t-\tau/2)
$$

也就是**一个信号和它的复共轭相乘。**  

non-conjugate SCF 描述的是普通功率型二阶结构，例如：

- PSD 是 $\alpha=0$ 的特例。
- 调制符号率造成的循环平稳结构。
- OFDM cyclic prefix、帧周期、码片率等造成的周期相关。
- 频率间隔为 $\alpha$ 的两个谱分量之间的相关性。

频域上可直观理解为：

$$
S_x^\alpha(f)\sim
E\left[
X(f+\alpha/2)X^*(f-\alpha/2)
\right]
$$

## Conjugate SCF

conjugate cyclic autocorrelation 定义为：

$$
R_{x^*}^\alpha(\tau)
=
\lim_{T\to\infty}
\frac{1}{T}
\int_{-T/2}^{T/2}
x(t+\tau/2)x(t-\tau/2)
e^{-j2\pi\alpha t}dt
$$

对应的 conjugate SCF 为：

$$
S_{x^*}^\alpha(f)
=
\int R_{x^*}^\alpha(\tau)e^{-j2\pi f\tau}d\tau
$$

它使用的二阶核是：

$$
x(t+\tau/2)x(t-\tau/2)
$$

注意第二项没有复共轭。

conjugate SCF 描述的是**信号和自身非共轭副本之间的周期相关，** 常用于揭示：

- 载波频率相关结构。
- 非圆复信号 impropriety。
- BPSK、ASK、PAM 等 real-valued 或非圆调制的共轭循环特征。
- 与 doubled carrier frequency 相关的特征。

频域上可直观理解为：

$$
S_{x^*}^\alpha(f)\sim
E\left[
X(f+\alpha/2)X(\alpha/2-f)
\right]
$$

## 核心区别

| 项目 | non-conjugate SCF | conjugate SCF |
|---|---|---|
| 时域核 | $x(t+\tau/2)x^*(t-\tau/2)$ | $x(t+\tau/2)x(t-\tau/2)$ |
| 是否共轭 | 第二项取复共轭 | 第二项不取复共轭 |
| 主要描述 | 功率型周期相关 | 共轭/非圆周期相关 |
| $\alpha=0$ | 退化为 PSD | 不等于普通 PSD |
| 常见特征 | 符号率、帧周期、CP、码片率 | 载波、BPSK/ASK/PAM 的非圆结构 |
| 频域相关 | $X(f+\alpha/2)X^*(f-\alpha/2)$ | $X(f+\alpha/2)X(\alpha/2-f)$ |

## 在 UAV RF 识别中的意义

无人机 RF 信号可能包含：

- 调制符号率
- 跳频周期
- 帧结构
- 遥控链路协议周期
- 载波偏移
- 非圆调制结构

non-conjugate SCF 更偏向提取周期功率谱结构；conjugate SCF 更容易揭示与载波和非圆调制有关的结构。两者可能提供互补特征。

## 总结

一句话概括：

> non-conjugate SCF 看的是 $x$ 与 $x^*$ 的周期相关，偏功率谱结构；conjugate SCF 看的是 $x$ 与 $x$ 的周期相关，偏载波和非圆调制结构。
