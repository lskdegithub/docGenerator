# 公共章节差异矩阵（范围/引用文档）

本文件用于说明：测试大纲（test_plan）、测试细则（test_detail）、测试报告（test_report）在“范围/引用文档”章节中哪些内容是公共的、哪些是差异点，以及差异如何通过参数（宏）消解。

## 第1章 范围 → 1.1 标识（公共正文）

公共正文文件：
- `common/chapters/chapter1_ident_body.tex`

由各文档提供的参数（在各自 `chapters/doc_vars.tex` 中定义）：

| 语义字段 | 参数宏 |
|---|---|
| 项目标识 | `\\GjbProjectIdent` |
| 文档类型代号（STP/STD/STR） | `\\GjbDocIdType` |
| 系统标识 | `\\GjbSystemIdent` |
| 测试文档简称 | `\\GjbSystemDocAbbr` |
| 项目名称 | `\\GjbProjectName` |
| 软件版本号 | `\\GjbSoftwareVersion` |
| 文档名称（基础名） | `\\GjbDocName` |
| 文档类型名称（测试大纲/细则/报告） | `\\GjbDocKind` |
| 文档标识号（派生） | `\\GjbDocId` |
| 文档名称（派生） | `\\GjbDocTitle` |
| 适用范围/适用过程 | `\\GjbDocApplicableText` |

差异点（由 wrapper 保留在各自 chapter1.tex 中，不进入公共片段）：
- 章节命令：`\\section` vs `\\section*`、是否 `\\addcontentsline` 写入目录
- 小节命令：`\\subsection` vs `\\subsection*`、是否 `\\addcontentsline`

## 第1章 范围 → 1.2 系统概述（公共正文）

公共正文文件：
- `common/chapters/chapter1_system_overview_body.tex`

由各文档提供的参数：

| 语义字段 | 参数宏 |
|---|---|
| 合同/用途描述（第一句） | `\\GjbSystemPurposeText` |
| 合同引用（第二句） | `\\GjbSystemContractText` |
| “主要要求与技术指标”引导句 | `\\GjbSystemReqText` |
| “主要要求与技术指标”内容段 | `\\GjbSystemReqListText` |
| 覆盖性表引导句 | `\\GjbSystemCoverageIntroText` |
| 覆盖性表标题 | `\\GjbCoverageTableCaption` |
| 覆盖性表 label | `\\GjbCoverageTableLabel` |
| 覆盖性表第2列列名 | `\\GjbCoverageTableColBTitle` |
| 覆盖性表列宽（A/B/C） | `\\GjbCoverageColAWidth` / `\\GjbCoverageColBWidth` / `\\GjbCoverageColCWidth` |
| 需方/开发方描述 | `\\GjbSystemCustomerDevText` |
| 测试地点/环境描述 | `\\GjbSystemEnvironmentText` |

## 第2章 引用文档（公共正文）

公共正文文件：
- `common/chapters/chapter2_ref_docs_body.tex`

由各文档提供的参数：

| 语义字段 | 参数宏 |
|---|---|
| 引用表引导句 | `\\GjbRefDocsIntroText` |
| 引用表标题 | `\\GjbRefDocsTableCaption` |
| 引用表 label | `\\GjbRefDocsTableLabel` |
| 引用表列宽（A-F） | `\\GjbRefDocsColAWidth` ... `\\GjbRefDocsColFWidth` |

说明：
- 为减少重复，引用表统一使用 `longtblr` 结构；若你希望细则继续使用 `talltblr`，可将表环境拆回 wrapper，公共片段仅保留“行数据”。 

## 第1章 范围 → 1.3 文档概述（公共骨架 + 可配置话术）

公共正文文件：
- `common/chapters/chapter1_doc_overview_body.tex`

由各文档提供的参数：

| 语义字段 | 参数宏 |
|---|---|
| 文档概述第一段（模板话术） | `\\GjbDocOverviewText` |
| 标准覆盖性说明（模板话术） | `\\GjbDocStdCoverageText` |
| 密级/分发说明（模板话术） | `\\GjbDocSecurityText` |

## 第3章 软件测试环境 → 3.1-3.3（公共正文）

公共正文文件：
- `common/chapters/chapter3_1_site_body.tex`
- `common/chapters/chapter3_2_env_overview_body.tex`
- `common/chapters/chapter3_3_env_components_intro_body.tex`

说明：
- 测试大纲与测试细则在 3.1/3.2/3.3 复用公共正文；各自的更细层级（如 3.3.x）在各自 chapter3.tex 中维护。

## 第4章（细则/报告）→ 公共表模板

公共表模板文件：
- `common/chapters/chapter4_testitems_table.tex`（测试项列表表）
- `common/chapters/chapter4_testcase_table_sample.tex`（测试用例表样例）

由各文档提供的参数：

| 语义字段 | 参数宏 |
|---|---|
| 测试项列表表标题 | `\\GjbTestItemsTableCaption` |
| 测试项列表表 label | `\\GjbTestItemsTableLabel` |
| 测试用例表标题 | `\\GjbSampleTestCaseTableCaption` |
| 测试用例表 label | `\\GjbSampleTestCaseTableLabel` |
