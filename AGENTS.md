# Repository Guidelines

## Math Rendering Convention

数学公式渲染统一使用 LaTeX 语法：
- 行内公式使用 `$...$`，例如 `$R_x^{\alpha}(\tau)$`。
- 行间公式使用 `$$...$$`。
- 不要使用反引号包裹公式（例如不要写成 `` `R_x^{\alpha}(\tau)` ``）。
- 含 prime 的变量使用 LaTeX 写法，如 `$N^{\prime}$`，不要写 `N'`。

## Language Convention

本仓库文件以中文为主题进行编写与维护，部分关键词保留 English 术语以保证技术准确性与可检索性。
推荐写法为“中文叙述 + 英文关键词”，例如：`cyclic spectrum`、`CPP`、`FLOCS`、`ResNet-18`、`ST-ESER`、`MCP`。
除专有名词外，不建议整段英文替代中文说明。

## Project Structure & Module Organization

本仓库目前是一个以 Markdown 为主的 knowledge-base scaffold。根目录包含 `llm-wiki.md` 和 `llm-wiki-ch.md` 等概念文档。`raw/` 用于保存不可变的 source material，例如剪藏文章、论文、图片、datasets 和 notes。`wiki/` 用于存放整合 raw sources 后形成的 Markdown 页面。`.obsidian/` 保存本地 Obsidian workspace 设置；除非明确修改 vault 行为，否则不要编辑。

当 knowledge base 扩展后，建议维护以下 wiki 文件：

- `wiki/index.md`: 页面目录，每个页面配一行简介。
- `wiki/log.md`: append-only 活动日志，记录 ingests、queries 和 lint passes。
- `raw/assets/`: source files 引用的本地图片或附件。

## Build, Test, and Development Commands

当前没有配置 application build system 或 test runner。常用本地命令：

- `rg "term" wiki raw`: 快速搜索 Markdown 内容。
- `rg --files`: 列出项目文件，包括嵌套 Markdown。
- `git status`: 当目录初始化为 Git repository 后，用于检查 pending changes。

如果后续添加 scripts，请在此记录，并确保命令可从 repository root 运行。

## Local MCP Services

`tools/` 目录下当前可用的 MCP 服务：

- `tools/pdf_mcp_server.py`: 本地 PDF MCP server（`stdio`），用于读取 `raw/` 下论文，支持 `list_pdfs`、`pdf_info`、`extract_text`。
- 启动命令（repository root）: `python tools/pdf_mcp_server.py --root raw`
- 自检命令: `python tools/pdf_mcp_server.py --root raw --self-test`
- 依赖说明见 `tools/requirements-pdf.txt` 与 `tools/pdf_mcp_server.md`。

## Coding Style & Naming Conventions

编写 Markdown 时使用清晰 headings、短段落和描述性文件名。新页面优先使用 lowercase kebab-case，例如 `signal-processing-overview.md` 或 `drone-rf-datasets.md`。ingestion 之后不要改写 raw sources；解释、摘要和 cross-references 应放在 `wiki/`。

wiki 页面之间使用 relative links，例如 `[Dataset Notes](drone-rf-datasets.md)`。如果添加 YAML frontmatter，keys 保持 lowercase 且稳定，例如 `title`、`tags`、`date` 和 `sources`。

## Testing Guidelines

当前没有 automated tests。对 knowledge-base 修改，应在 Obsidian 或 Markdown preview 中阅读受影响页面，检查 links，并用 `rg` 搜索 stale references。添加 code 或 scripts 时，应在代码附近加入 focused tests，并在本文件记录 test command。

## Commit & Pull Request Guidelines

当前 workspace 没有可用 Git history，因此无法推断项目专属 commit convention。在形成约定前，使用简洁的 imperative messages，例如 `Add source ingestion notes` 或 `Update wiki index structure`。

Pull requests 应说明变更的 source material 或 workflow，列出受影响 directories，并记录已执行的 manual verification。面向 Obsidian 的变更，只有在 visual settings 或 rendered Markdown behavior 改变时才需要 screenshots。

## LLM Wiki Workflows

本仓库遵循 `llm-wiki` 模式：LLM 增量构建与维护一个持久化的 `wiki/`，`raw/` 为不可变 source material，`AGENTS.md` 为 schema。LLM 承担全部 summarize、cross-reference、filing 与 bookkeeping 工作。

### Ingest（摄入新来源）

当用户将新 source 放入 `raw/` 并指示处理时，按以下流程执行：

1. **读取来源**：PDF 通过本地 MCP server（`tools/pdf_mcp_server.py`）提取文本；Markdown 或其他文本文件直接读取。
2. **讨论关键 takeaway**：与用户确认核心发现、方法与结论后再写入，避免方向偏差。
3. **创建 source page**：在 `wiki/sources/` 下新建 `<year>-<topic-slug>.md`，包含以下结构：
   - `## Source`：完整 citation + raw 文件路径
   - `## Core View`：1-2 句概括论文核心观点
   - `## Method`：方法流程的关键步骤
   - `## Data & Experiments`：数据集、参数设置、关键结果数值
   - `## Conclusion`：论文结论与贡献
   - `## Related Pages`：链接到 `../summary.md`、`../citation-order.md`
   - `## Terms`：列出关键技术术语并链接到 `../concepts/<term>.md`（已有则更新，无则新建）
4. **更新 concept pages**：为 source 中出现的每项关键术语检查 `wiki/concepts/`，无页面则新建（含 YAML frontmatter `type: concept`），已有则补充新论文的关联信息。
5. **更新 index.md**：在 `wiki/index.md` 的 Sources 与 Concepts 区新增/更新条目，每条带一句话中文摘要。
6. **追加 log.md**：按格式 `## [YYYY-MM-DD] ingest | <title>` 追加条目，简述操作内容。
7. **考虑 synthesize**：当多篇论文形成清晰研究主线时，更新或新建 `wiki/summary.md`，梳理 research thread、key methods、key results、open questions。

### Query（查询）

当用户针对 wiki 内容提问时：

1. 先读 `wiki/index.md` 定位相关页面。
2. 深入读取相关 source pages 和 concept pages。
3. 综合答案，引用具体页面。
4. 如果答案有长期参考价值，询问用户是否 filed back 为新的 wiki 页面（如对比分析、专题讨论等），而非仅留在聊天记录中。

### Lint（健康检查）

用户请求或定期主动执行时：

- 检查 wiki 页面间的 broken links。
- 检查 contradictions：不同 source page 对同一方法的结论是否冲突。
- 检查 stale claims：新 source 是否已覆盖或修正旧结论。
- 检查孤儿页面：concept page 是否有至少一篇 source page 链接到它。
- 检查缺失概念：source page 中提及但尚未有 concept page 的关键术语。
- 完成后追加 `wiki/log.md`：`## [YYYY-MM-DD] lint | <summary>`。

### Index 与 Log 维护规范

- **index.md** 每次 ingest 后必须更新。新增 source 或 concept 时同步添加条目。每个条目 = `[Title](relative/path.md)：一句话中文描述`。
- **log.md** 为 append-only 时间线。条目前缀格式：`## [YYYY-MM-DD] <type> | <subject>`，其中 type 为 `ingest`、`query`、`lint`、`synthesize`、`fix`、`structure`。
- **source page 互链规则**：sources 之间不互相直连，论文关系通过 `summary.md`、`concepts/`、`citation-order.md` 维护。避免 Obsidian 图谱出现误导性边。

### 文件命名与语言约定

- 新页面使用 lowercase kebab-case，例如 `2025-rf-based-uav-identification-cpp.md`。
- 正文以中文为主，关键技术术语保留英文（`CPP`、`FLOCS`、`cyclic spectrum`、`ResNet-18` 等）。
- 数学公式统一使用 LaTeX：行内 `$...$`，行间 `$$...$$`。

## Agent-Specific Instructions

保持 surgical changes。不要重写 raw sources、重排无关页面，或发明未被要求的 tooling。进行大范围 wiki updates 前，先说明计划修改的 files 和 success checks。上述 workflows 为默认操作指南，具体执行时可根据用户指示灵活调整。