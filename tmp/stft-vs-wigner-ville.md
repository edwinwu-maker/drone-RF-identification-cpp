# STFT 与 Wigner-Ville 分布的区别和联系

本文基于 `tmp/scf-vs-wigner-ville.md` 中关于二阶时频相关核、Wigner-Ville 分布以及短时 Fourier 变换形式的内容，整理 STFT 与 Wigner-Ville 分布之间的区别和联系。

## 基本定义

STFT（Short-Time Fourier Transform）通过在信号上滑动一个分析窗，对每个局部时间片段做 Fourier transform：

$$
X(t,f)=\int x(u)g^*(u-t)e^{-j2\pi fu}du
$$

其中，$g(\cdot)$ 是分析窗，$t$ 是窗口中心时间，$f$ 是频率。

Wigner-Ville 分布（WVD）从二阶时频相关核出发：

$$
R_x(t,\tau)=x(t+\tau/2)x^*(t-\tau/2)
$$

然后对时延 $\tau$ 做 Fourier transform：

$$
W_x(t,f)=\int x(t+\tau/2)x^*(t-\tau/2)e^{-j2\pi f\tau}d\tau
$$

因此，STFT 和 WVD 都输出时间-频率平面上的表示，但它们的构造方式不同。

## 核心区别

| 方面 | STFT | Wigner-Ville 分布 |
|---|---|---|
| 基本思想 | 对信号加窗后做 Fourier transform | 对二阶相关核沿时延 $\tau$ 做 Fourier transform |
| 数学对象 | 线性时频表示 | 二次型时频表示 |
| 输出变量 | 时间 $t$、频率 $f$ | 时间 $t$、频率 $f$ |
| 分辨率 | 受窗口长度限制，时间/频率分辨率存在固定折中 | 理论上时频聚集性更高 |
| 交叉项 | 通常没有严重 cross-term | 多分量信号会产生明显 cross-term |
| 稳定性 | 更平滑、更易解释 | 更锐利，但可能有伪影 |
| 工程使用 | spectrogram、FAM、TSM 等短时谱方法的基础 | 高分辨时频分析、SCF 理论推导的基础 |

## 直观理解

STFT 可以理解为：

> **先截取一小段信号，再观察这一小段中有哪些频率成分。**  

窗口越短，时间定位越好，但频率分辨率越差；窗口越长，频率分辨率越好，但时间定位越差。因此 STFT 的时频分辨率由分析窗决定。

WVD 可以理解为：

> **在某个中心时刻 $t$，比较 $t+\tau/2$ 和 $t-\tau/2$ 两侧样本的相关性，再对时延 $\tau$ 做 Fourier transform。**  

WVD 不依赖普通 STFT 那样的分析窗，因此时频能量通常更集中。但由于它是二次型表示，多分量信号中不同分量之间会相互作用，产生 cross-term。

## 二者的联系

STFT 的能量谱通常称为 spectrogram：

$$
|X(t,f)|^2
$$

Spectrogram 和 WVD 都属于二次型时频表示。二者不是同一个量，但可以在 Cohen class 时频分布框架下建立联系：spectrogram 可以理解为对 WVD 做了由分析窗决定的二维平滑。

因此：

- WVD 的时频聚集性更高，但 cross-term 更强。
- STFT/spectrogram 更平滑，cross-term 更少，但分辨率受窗口限制。

## 与循环谱估计的关系

`tmp/scf-vs-wigner-ville.md` 中指出，二阶循环谱可以理解为 WVD 沿时间轴的 Fourier 分析结果：

$$
S_x^\alpha(f)
=
\lim_{T\to\infty}\frac{1}{T}\int_{-T/2}^{T/2}
W_x(t,f)e^{-j2\pi \alpha t}dt
$$

另一方面，FAM、TSM 等循环谱估计算法常从短时谱相关形式出发：

$$
S_x^\alpha(f)=
\lim_{T\to\infty}\frac{1}{T}
\int
X_T(t,f+\alpha/2)X_T^*(t,f-\alpha/2)dt
$$

这里的 $X_T(t,f)$ 可以看作局部 Fourier transform，也就是 STFT 思路下的短时谱。因此：

- WVD 更适合作为理解 SCF 与二阶相关结构关系的理论桥梁。
- STFT 更适合作为 FAM、TSM 等工程算法的实现入口。

## 总结

STFT 和 Wigner-Ville 分布都描述信号的时频结构，但侧重点不同：

- STFT 是加窗后的局部频谱分析，优点是稳定、平滑、工程实现简单。
- WVD 是基于二阶相关核的时频能量分布，优点是分辨率高、理论结构清晰。
- STFT 的 spectrogram 可看作平滑后的 WVD，因此牺牲部分分辨率来换取更少的 cross-term。
- 在循环谱分析中，WVD 更偏理论解释，STFT 更偏实际估计方法。
