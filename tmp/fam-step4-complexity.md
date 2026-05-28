# FAM Step 4 的计算复杂度分析

## Step 4 的核心计算

在 FAM（FFT Accumulation Method）的 Step 4 中，需要从 channelized subblocks 中选取两个频率通道 $k$ 和 $l$，构造短时谱乘积：

$$
Y_{k,l}[r]=X[r,k]Y^*[r,l]
$$

然后对窗口序号 $r$ 做长度为 $P$ 的 FFT：

$$
Z_{k,l}[q]=
\sum_{r=0}^{P-1}
Y_{k,l}[r]e^{-j2\pi rq/P}
$$

其中：

- $N^{\prime}$ 是每个短时 FFT 的长度，也就是 channelizer 的频率通道数。
- $P=N/L$ 是短时 block 的数量，也是第二次 FFT 的长度。
- $(k,l)$ 表示两个频率通道组合。

## 单个通道对的复杂度

对固定的 $(k,l)$：

1. 逐元素乘积 $X[r,k]Y^*[r,l]$，长度为 $P$：

$$
O(P)
$$

2. 对该长度为 $P$ 的向量做 FFT：

$$
O(P\log P)
$$

所以单个 $(k,l)$ 通道对的复杂度为：

$$
O(P+P\log P)
\approx
O(P\log P)
$$

## 所有通道对的复杂度

如果 exhaustive FAM 对所有频率通道对 $(k,l)$ 都计算，那么通道对数量为：

$$
N^{\prime}\times N^{\prime}=N^{\prime 2}
$$

因此 Step 4 的总复杂度为：

$$
O(N^{\prime 2}P\log P)
$$

其中逐元素乘积部分为：

$$
O(N^{\prime 2}P)
$$

第二次 FFT 部分为：

$$
O(N^{\prime 2}P\log P)
$$

通常第二次 FFT 部分主导计算量。

## 与直接计算的对比

如果不用 FFT，而是对每个 $(k,l)$ 直接计算所有 $q$：

$$
Z_{k,l}[q]=
\sum_{r=0}^{P-1}
Y_{k,l}[r]e^{-j2\pi rq/P}
$$

那么每个通道对需要：

$$
O(P^2)
$$

所有通道对的复杂度会变成：

$$
O(N^{\prime 2}P^2)
$$

FAM 的效率优势就在于将这一步从：

$$
O(N^{\prime 2}P^2)
$$

降低为：

$$
O(N^{\prime 2}P\log P)
$$

## 空间复杂度

如果一次性保存所有通道对的乘积矩阵：

$$
Y_{k,l}[r]
$$

其形状相当于：

$$
N^{\prime}\times N^{\prime}\times P
$$

因此空间复杂度为：

$$
O(N^{\prime 2}P)
$$

这在实际工程中通常很大。

更常见的实现方式是逐个或分批处理 $(k,l)$，这样工作内存可以降低为：

$$
O(P)
$$

或分批情况下：

$$
O(BP)
$$

其中 $B$ 是一次处理的通道对数量。

## 工程优化方向

Step 4 是 FAM 中计算量较重的一步。实际实现时可以考虑：

- 只计算 principal domain 内有效的 $(f,\alpha)$ 点。
- 只计算感兴趣的循环频率或频率区域。
- 分批处理通道对 $(k,l)$，避免构造完整的 $N^{\prime}\times N^{\prime}\times P$ 张量。
- 利用 SCF 的对称性减少重复计算。
- 在 GPU 或向量化后端上批量执行长度为 $P$ 的 FFT。

## 总结

若计算全部频率通道对，FAM Step 4 的主要复杂度为：

$$
O(N^{\prime 2}P\log P)
$$

其中：

- $N^{\prime 2}$ 来自所有频率通道对。
- $P\log P$ 来自每个通道对沿时间窗口序列做第二次 FFT。

Step 4 的空间复杂度在完整存储所有通道对时为：

$$
O(N^{\prime 2}P)
$$

因此，实际实现中通常需要 principal domain 剪枝、分批计算或只计算感兴趣的 $(f,\alpha)$ 区域来降低计算量和内存压力。
