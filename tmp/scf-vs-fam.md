# FAM 与二阶循环谱的区别和联系

二阶循环谱（second-order cyclic spectrum / SCF）是理论对象，FAM（FFT Accumulation Method）是估计这个理论对象的一种离散算法。

二者关系可以概括为：

> SCF 定义了要估计的量 $S_x^\alpha(f)$，FAM 提供了一种高效计算 $\hat{S}_x^\alpha(f)$ 的方法。

## 二阶循环谱是什么

二阶循环谱描述信号二阶统计特性在循环频率 $\alpha$ 上的周期结构。它通常由循环自相关函数（CAF）再对时延做 Fourier transform 得到。

CAF 定义为：

$$
R_x^\alpha(\tau)=
\lim_{T\to\infty}\frac{1}{T}
\int_{-T/2}^{T/2}
x(t+\tau/2)x^*(t-\tau/2)e^{-j2\pi\alpha t}dt
$$

二阶循环谱定义为：

$$
S_x^\alpha(f)=
\int R_x^\alpha(\tau)e^{-j2\pi f\tau}d\tau
$$

因此，SCF 的变量是：

$$
(\alpha, f)
$$

其中 $f$ 是谱频率，$\alpha$ 是循环频率。

## FAM 是什么

FAM 是一种用 FFT 高效估计 SCF 的方法。它先对信号分块做短时 FFT，然后计算频率通道对的谱乘积：

$$
Y_{k,l}[r]=\tilde{X}[r,k]\tilde{X}^*[r,l]
$$

其中，$r$ 是短时窗口序号，$k$ 和 $l$ 是两个短时 FFT 频率通道。

然后，FAM 沿窗口序号 $r$ 做第二次 FFT：

$$
Z_{k,l}[q]=
\sum_{r=0}^{P-1}
Y_{k,l}[r]e^{-j2\pi qr/P}
$$

最后将结果映射到循环谱平面：

$$
f=\frac{f_k+f_l}{2}
$$

$$
\alpha=(f_k-f_l)+\frac{q_c}{PL}
$$

其中：

- $P$ 是短时窗口数量。
- $L$ 是 hop size。
- $q_c$ 是 `fftshift` 后的中心化第二阶段 FFT 索引。

所以 FAM 的输出是对 SCF 的估计：

$$
\hat{S}_x^\alpha(f)
$$

## 主要区别

| 对象 | 二阶循环谱 SCF | FAM |
|---|---|---|
| 性质 | 理论定义 | 数值估计算法 |
| 目标 | 描述循环平稳二阶统计特征 | 高效估计 $S_x^\alpha(f)$ |
| 输入 | 理想连续/离散信号模型 | 有限长采样数据 |
| 输出 | $S_x^\alpha(f)$ | $\hat{S}_x^\alpha(f)$ |
| 核心变量 | 循环频率 $\alpha$、谱频率 $f$ | FFT bin、窗口序号、通道对 $(k,l)$，最后映射到 $(\alpha,f)$ |
| 关键操作 | 带 $e^{-j2\pi\alpha t}$ 的时间平均，再对时延 Fourier transform | 短时 FFT、频率通道乘积、沿窗口序号 FFT |
| 是否唯一 | 是目标量，不是算法 | 只是 SCF 的多种估计方法之一 |

## 二者的联系

SCF 可以写成短时谱相关的形式：

$$
S_x^\alpha(f)
\approx
\lim_{T\to\infty}
\frac{1}{T}
\int_{-T/2}^{T/2}
X_L(t,f+\alpha/2)X_L^*(t,f-\alpha/2)dt
$$

其中 $X_L(t,f)$ 是短时 Fourier transform，$L$ 表示短时分析窗长度。

FAM 正是从这个形式出发：

1. 把连续的 $X_L(t,f)$ 离散成短时 FFT。
2. 把两个频移谱分量的乘积离散成频率通道对乘积 $Y_{k,l}[r]$。
3. 把带循环频率解调的时间平均变成沿窗口序号 $r$ 的第二次 FFT。
4. 把离散结果映射回循环谱坐标 $(\alpha,f)$。

因此：

- SCF 是要估计的理论量。
- FAM 是估计 SCF 的快速算法。
- FAM 得到的是有限数据、有限窗长、有限 FFT 网格上的 SCF 近似。
- FAM 的精度受窗口长度、hop size、FFT 点数、平均长度、频率栅格映射影响。

## 总结

可以把二者关系理解为：

> 二阶循环谱是目标坐标系 $(\alpha,f)$ 上的理论谱相关函数，FAM 是把有限采样数据投影到这个坐标系上的一种 FFT-based 快速估计方法。

所以，FAM 不是新的循环谱定义，也不是与 SCF 并列的理论对象。它只是 SCF 的一种工程实现路径。
