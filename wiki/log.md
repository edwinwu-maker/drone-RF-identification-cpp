# Log

## [2026-05-25] ingest | FAM method reference

- 处理新增 raw clipping：Chad Spooner "CSP Estimators: The FFT Accumulation Method"。
- 新增 `wiki/sources/2018-csp-estimators-fam.md`。
- 更新 `wiki/concepts/cyclic-spectrum.md`、`wiki/index.md`、`wiki/summary.md`，补充 FAM 方法参考入口。

## [2026-05-25] ingest | 2024 CPP-ULWNet ACMC paper

- 处理新 PDF：Yan et al. 2024 TCCN "ACMC Using Ultra Lightweight DL Network Based on CPP"。
- 新建 `wiki/sources/2024-acmc-ulwnet-cpp.md`。
- 新建 `wiki/concepts/ulwnet.md`。
- 更新 `wiki/concepts/cpp.md`、`acmc.md`、`cyclic-spectrum.md` 补充 ULWNet 论文引用。
- 更新 `wiki/index.md`、`wiki/citation-order.md`、`wiki/summary.md`。

## [2026-05-20] fix | paper citation order

- 移除了 `sources` 页面 `Related Pages` 中的论文互链，避免 Obsidian 图谱出现误导性边。
- 新增 `wiki/citation-order.md`，统一标准顺序：2020 FLOCS 方法 → 2024 CPP-ACMC → 2025 CPP-UAV RF identification。

## [2026-05-20] structure | concept pages

- 新增 `wiki/concepts/`，覆盖关键方法、任务、数据集、指标与应用术语。
- 将 `sources` 页面 `Terms` 区改为链接到 concept pages，支持 Obsidian 的论文-关键词图谱过滤。

## [2026-05-20] lint | cross-reference check

- 校验 `wiki/` 下 Markdown 链接，未发现 broken links。
- 为三篇 source summary 补充 `Related Pages` 区块（后续已按引用规则收敛）。

## [2026-05-20] synthesize | cyclic features summary

- 新增 `wiki/summary.md`，汇总三篇 PDF 论文的研究脉络与核心结论。
- 更新 `wiki/index.md`，加入 summary 入口。

## [2026-05-20] ingest | raw PDF papers on cyclic-paw-print and RF identification

- 通过本地 PDF MCP 流程（`PyMuPDF`）处理 `raw/` 下三篇论文。
- 在 `wiki/sources/` 新增三篇 source summary 页面。
- 更新 `wiki/index.md` 索引入口。
