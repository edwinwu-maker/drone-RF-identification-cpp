# FAM Step 5 的总体理解思路

Step 5 的核心问题是：**FAM 算完一堆 FFT 输出以后，这些数值本身还不是“循环谱图”；必须把每个输出点放回正确的 $(f,\alpha)$ 坐标上。**

也就是说，Step 5 解决的是 **坐标解释问题**，不是新的计算步骤。

## 1. 前面步骤到底算出了什么

在 Step 4 中，FAM 选取两个频率通道 $f_k$ 和 $f_l$，做共轭乘积：

$$
X_T(rL,f_k)Y_T^*(rL,f_l)
$$

这里 $rL$ 是时间位置。对固定的频率对 $(f_k,f_l)$ 来说，这个乘积序列描述的是：

> 两个谱分量 $f_k$ 和 $f_l$ 在时间方向上的相关性如何变化。

然后对这个时间序列再做一次 FFT，就会得到一组关于 cycle frequency 的输出。

所以 Step 4 的输出不是单个点，而是一串：

$$
q = 0,1,\dots,P-1
$$

对应 $P$ 个 cycle-frequency bins。

## 2. 为什么频率对会对应一个 $(f,\alpha)$

循环谱关心的是两个谱分量之间的相关：

$$
S_x^\alpha(f)
\sim
X\left(f+\frac{\alpha}{2}\right)
X^*\left(f-\frac{\alpha}{2}\right)
$$

其中两个谱分量分别是：

$$
f+\frac{\alpha}{2}
$$

和：

$$
f-\frac{\alpha}{2}
$$

如果把它们对应到 FAM 中的两个 channel：

$$
f_k = f+\frac{\alpha}{2}
$$

$$
f_l = f-\frac{\alpha}{2}
$$

那么可以反解出：

$$
\alpha = f_k-f_l
$$

$$
f = \frac{f_k+f_l}{2}
$$

这就是文中的公式：

$$
\alpha_i=f_k-f_l
$$

$$
f_j=\frac{f_k+f_l}{2}
$$

直观理解：

- $\alpha$ 是两个频率分量的“间隔”。
- $f$ 是两个频率分量的“中心频率”。

所以一个频率通道对 $(f_k,f_l)$ 并不是随便对应到某个点，而是天然对应到循环谱平面上的一个中心频率 $f$ 和一个基础循环频率 $\alpha_i$。

## 3. $q\Delta\alpha$ 的由来：慢时间 Fourier transform

如果只看频率通道对本身，它给出一个基础 cycle frequency：

$$
\alpha_i=f_k-f_l
$$

但 Step 4 中还对时间方向的乘积序列做了长度为 $P$ 的 FFT。这个 FFT 不是沿原始采样点 $n$ 做的，而是沿短时 FFT block 的索引 $r$ 做的。这个索引可以称为 **慢时间 slow time**：

$$
t_r = rL T_s,\quad r=0,1,\dots,P-1
$$

其中 $L$ 是 hop size，$T_s$ 是采样周期，$P$ 是短时 FFT block 数量。FAM 的核心就是：先在每个慢时间位置 $rL$ 上得到短时频率通道，再看两个频率通道的乘积序列是否随慢时间呈现周期性变化。

对固定频率通道对 $(f_k,f_l)$，定义慢时间乘积序列：

$$
z_{k,l}[r]
=
X_T(rL,f_k)Y_T^*(rL,f_l)
$$

如果信号在 cycle frequency $\alpha$ 上存在循环相关，那么该乘积序列中会包含形如：

$$
z_{k,l}[r]\propto e^{j2\pi(\alpha-\alpha_i)rL T_s}
$$

的慢时间复指数成分。这里 $\alpha_i=f_k-f_l$ 是由频率通道对本身带来的基础频率差，剩余的 $\alpha-\alpha_i$ 需要通过慢时间 Fourier transform 来分辨。

因此，对 $z_{k,l}[r]$ 沿 $r$ 做离散 Fourier transform：

$$
Z_{k,l}[q]
=
\sum_{r=0}^{P-1}
z_{k,l}[r]e^{-j2\pi rq/P}
$$

长度为 $P$ 的 DFT 第 $q$ 个 bin 对应的慢时间 normalized frequency 为：

$$
\nu_q=\frac{q}{P}
$$

因为慢时间采样间隔是 $L T_s$，所以它对应的物理频率间隔为：

$$
\Delta \alpha_{\mathrm{slow}}
=
\frac{1}{P L T_s}
$$

又因为 FAM 处理的数据块长度为：

$$
N = PL
$$

所以：

$$
\Delta \alpha_{\mathrm{slow}}
=
\frac{1}{N T_s}
$$

如果使用 normalized frequency，即把采样率归一化为 $1/T_s=1$，则：

$$
\Delta\alpha=\frac{1}{N}
$$

于是第 $q$ 个慢时间 DFT bin 对应的 cycle-frequency offset 为：

$$
q\Delta\alpha
$$

这就得到 FAM Step 5 中的坐标关系：

$$
\alpha=\alpha_i+q\Delta\alpha
$$

也就是：

$$
\alpha=f_k-f_l+q\Delta\alpha
$$

这里的 $q\Delta\alpha$ 不是人为附加项，而是 **对慢时间乘积序列做长度为 $P$ 的 Fourier transform 后自然产生的循环频率网格偏移**。

## 4. 从理想循环相关到 $q\Delta\alpha$ 的证明

从循环谱的频域定义出发：

$$
S_x^\alpha(f)
\sim
X\left(f+\frac{\alpha}{2}\right)
X^*\left(f-\frac{\alpha}{2}\right)
$$

FAM 不是直接连续计算任意 $f+\alpha/2$ 和 $f-\alpha/2$，而是先用短时 FFT 得到离散频率通道 $f_k$ 和 $f_l$。令：

$$
f_j=\frac{f_k+f_l}{2}
$$

$$
\alpha_i=f_k-f_l
$$

如果真实循环频率正好等于 $\alpha_i$，那么频率通道对本身就已经对齐到目标循环频率；此时慢时间乘积序列在理想情况下接近直流成分，对应：

$$
q=0
$$

也就是：

$$
\alpha=\alpha_i
$$

但真实循环频率不一定正好落在通道差 $\alpha_i$ 上。设真实循环频率为：

$$
\alpha=\alpha_i+\delta
$$

其中 $\delta$ 是相对于通道差的剩余偏移。这个剩余偏移会表现为慢时间乘积序列中的相位旋转：

$$
z_{k,l}[r]\propto e^{j2\pi\delta rL T_s}
$$

对 $z_{k,l}[r]$ 做长度为 $P$ 的 DFT 时，DFT 能分辨的慢时间频率为：

$$
\delta_q=\frac{q}{P L T_s}
$$

所以当：

$$
\delta=\delta_q
$$

时，第 $q$ 个 DFT bin 会出现峰值。代入 $N=PL$，得到：

$$
\delta_q=\frac{q}{N T_s}
$$

归一化频率下：

$$
\delta_q=q\Delta\alpha,\quad \Delta\alpha=\frac{1}{N}
$$

因此：

$$
\alpha
=
\alpha_i+\delta_q
=
\alpha_i+q\Delta\alpha
$$

这证明了：FAM 输出的第 $q$ 个慢时间 FFT bin 不只是“第 $q$ 个数组元素”，它对应的是基础循环频率 $\alpha_i$ 之外的一个可分辨 cycle-frequency offset。

## 5. 为什么 $N$ 决定 $\Delta\alpha$

循环频率本质上是“相关性随时间周期变化”的频率。要分辨两个很接近的 cycle frequencies，就需要更长的时间观测窗口。

FAM 中慢时间 FFT 覆盖的总时间长度为：

$$
T_{\mathrm{obs}}=P L T_s=N T_s
$$

Fourier transform 的频率分辨率约为观测时长的倒数：

$$
\Delta\alpha=\frac{1}{T_{\mathrm{obs}}}
=
\frac{1}{N T_s}
$$

归一化后就是：

$$
\Delta\alpha=\frac{1}{N}
$$

所以：

- $N$ 越大，观测时间越长，cycle-frequency resolution 越高。
- $P$ 越大，慢时间 FFT bin 越多。
- $L$ 越小，慢时间采样更密，但在 $N=PL$ 固定时不改变 $\Delta\alpha$，主要影响计算量和慢时间采样结构。

## 6. Step 5 真正在做什么

Step 5 就是在遍历所有这些输出，然后给每个数值贴上坐标：

```text
for each channel pair (f_k, f_l):
    f_j = (f_k + f_l) / 2
    alpha_i = f_k - f_l

    for each output FFT bin q:
        alpha = alpha_i + q * Delta_alpha
        assign output value to S(alpha, f_j)
```

最终得到的是一堆 scattered point estimates：

$$
\hat{S}_x^\alpha(f)
$$

它们分布在 $f-\alpha$ 平面上。

## 7. 为什么要丢弃 principal domain 外的点

SCF 的有效定义域不是完整矩形，而是一个 diamond-shaped principal domain。原因是两个实际频率分量：

$$
f+\frac{\alpha}{2}
$$

和：

$$
f-\frac{\alpha}{2}
$$

必须都落在信号的 normalized frequency 范围内，例如：

$$
[-0.5,0.5)
$$

因此需要满足：

$$
-0.5 \leq f+\frac{\alpha}{2} < 0.5
$$

$$
-0.5 \leq f-\frac{\alpha}{2} < 0.5
$$

这两个约束共同形成 diamond-shaped domain。

如果某个 FAM 输出点对应的 $(f,\alpha)$ 让其中一个谱分量超出有效频率范围，那么这个点虽然是算法产物，但不属于 SCF 的有效主定义域，需要丢弃。

## 8. 总体理解思路

可以把 FAM 理解为三层映射。

第一层：短时 FFT 得到频率通道：

$$
x[n] \rightarrow X_T(rL,f_k)
$$

第二层：频率通道两两相关：

$$
X_T(rL,f_k)Y_T^*(rL,f_l)
$$

这里的频率对决定：

$$
f=\frac{f_k+f_l}{2},\quad \alpha_i=f_k-f_l
$$

第三层：沿慢时间方向 FFT：

$$
\alpha=\alpha_i+q\Delta\alpha
$$

最终得到：

$$
(f_k,f_l,q)
\rightarrow
(f,\alpha)
\rightarrow
\hat{S}_x^\alpha(f)
$$

所以 Step 5 的一句话总结是：

> FAM 的计算输出天然是按“频率通道对 + 慢时间 FFT bin”排列的，而循环谱需要按 $(f,\alpha)$ 排列；Step 5 就是把前者重新映射到后者。

在 CPP 场景中，这一步尤其重要。因为 CPP 最终是 $f-\alpha$ 平面的 top-view 图像，如果 Step 5 的坐标映射错了，生成的 CPP 纹理会错位，后续 `NSCMS`、resize、colormap 和 CNN 分类都会建立在错误的循环谱结构上。
