---
name: latex-chapter-creator
description: Automatically generate chapter structures for LaTeX technical documents following GJB 438C-2021 standards. Creates sections, subsections, and content frameworks. Use when implementing new chapters or adding document sections.
allowed-tools: Read, Write, Edit, Grep, Glob
---

# LaTeX Chapter Creator

按照 GJB 438C-2021 标准自动生成 LaTeX 文档章节结构。

## 功能概述

该 Skill 用于快速创建符合技术文档标准的章节框架，包括：
- 自动生成章节标题（支持1-6级标题）
- 设置正确的字体和间距
- 预留内容占位符
- 插入标准表格模板
- **正确处理层级编号继承关系**

## 层级编号规则（重要）

### 标准层级对应关系

| 层级 | LaTeX命令 | Word ilvl | 编号示例 | 说明 |
|------|-----------|-----------|----------|------|
| 1级 | `\section*` | ilvl=0 | `1.`, `4.` | 章标题 |
| 2级 | `\subsection*` | ilvl=1 | `1.1`, `4.1` | 节标题 |
| 3级 | `\subsubsection*` | ilvl=2 | `1.1.1`, `4.1.1` | 小节标题 |
| 4级 | `\paragraph*` | ilvl=3 | `4.1.1.1` | 段落标题 |
| 5级 | `\subparagraph*` | ilvl=4 | `4.1.1.1.1` | 小段落标题 |
| 6级 | 自定义命令 | ilvl=5 | `4.1.1.1.1.1` | 需自定义 |

### 编号继承规则（关键）

**重要**：子级标题必须继承父级编号，而不是使用独立编号。

**错误示例**：
```latex
\subsection*{4.1 一般信息}
\subsubsection*{4.2 测试级别}  ❌ 错误！应该是4.1.1
```

**正确示例**：
```latex
\subsection*{4.1 一般信息}
\subsubsection*{4.1.1 测试级别}  ✅ 正确！
\subsubsection*{4.1.2 测试方法}
\subsubsection*{4.1.3 测试类别}

\subsection*{4.2 计划执行的测试}
\subsubsection*{4.2.1 xxxxx语言功能测试}
\paragraph*{4.2.1.1 xxxxx功能测试}
```

## 章节结构模板

### 标准章节格式

```latex
\noindent\section*{N. 章节标题}

{\normalsize
\subsection*{N.1 二级标题}

{\normalsize
这里是正文内容。正文使用五号宋体，行间距18磅，首行缩进1.5em。
}

\subsection*{N.2 二级标题}

{\normalsize
正文内容...
}

\subsection*{N.3 二级标题}

{\normalsize
正文内容...
}
}
```

### 含表格的章节格式（推荐）⭐

```latex
% 导言区需要添加
\usepackage{float}    % 浮动体控制，用于[H]参数

\subsection*{N.X 表格型章节}

{\normalsize
前置说明文字。

% 表格使用[H]参数强制在当前位置，防止标题与内容分离
\begin{table}[H]
\centering
\vspace{6pt}
{\wuhaohei 表 X 表格标题}

\vspace{6pt}
{\settablespacing
\begin{tabular}{|列格式|}
\hline
\rowcolor{gray!20}
表头内容 \\
\hline
表格内容 \\
\hline
\end{tabular}
}
\end{table}
\vspace{6pt}  % 或 \vspace{-6pt}，根据后续内容类型调整（见表格最佳实践）

后续说明文字。
}
```

## 常用章节类型

### 第1章：范围

包含以下子节：
- 1.1 标识
- 1.2 系统概述
- 1.3 文档概述
- 1.4 与其他计划的关系
- 1.5 引用文档

### 第2章：软件测试环境

包含以下子节：
- 2.1 测试现场
- 2.2 测试环境概述
- 2.3 软件项（含表格：测试环境被测软件）
- 2.4 硬件和固件项（含表格：测试环境硬件项）
- 2.5 其他材料
- 2.6 所有者的特性、需方权利和许可证
- 2.7 安装、测试和控制

### 第3章：测试进度安排

包含时间表、里程碑等。

### 第4章：测试项

包含测试项列表、测试范围等。

## 使用方法

### 场景1：创建全新章节

**用户请求**: "帮我创建第2章：软件测试环境"

**执行步骤**:

1. **读取当前文档结构**
   ```bash
   grep -n "\\section" str-captain-1.tex
   ```

2. **确定插入位置**
   - 在第1章结束后、`\end{document}` 之前

3. **生成章节内容**
   - 创建所有子节框架
   - 添加标准表格模板
   - 预留内容占位符

4. **插入到文档**
   - 使用 Edit 工具在正确位置插入

### 场景2：添加子节

**用户请求**: "在2.3节后面添加一个表格"

**执行步骤**:

1. **定位插入点**
   ```bash
   grep -n "2.3" str-captain-1.tex
   ```

2. **生成表格代码**
   - 根据表格类型选择模板
   - 设置合适的列宽和格式

3. **插入表格**
   - 保持原有格式不变

### 场景3：从Word文档创建章节（推荐方法）⭐

**用户请求**: "根据Word文档创建第3章的完整结构"

**执行步骤**:

1. **使用增强版分析工具**
   ```bash
   # 推荐使用：支持1-7级标题，自动编号
   python3 tools/analyze_docx_structure_full.py templates/document.docx

   # 或使用快速版：仅支持1-3级标题
   python3 tools/extract_word_structure.py templates/document.docx
   ```

2. **分析工具输出**
   - 查看每个标题的ilvl值（编号级别）
   - ilvl=0 → 1级标题（`\section*`）
   - ilvl=1 → 2级标题（`\subsection*`）
   - ilvl=2 → 3级标题（`\subsubsection*`）
   - ilvl=3 → 4级标题（`\paragraph*`）
   - ilvl=4 → 5级标题（`\subparagraph*`）
   - ilvl=5+ → 需自定义

3. **根据ilvl生成正确的层级编号**
   - **关键**：使用继承编号，而非独立编号
   - 例如：ilvl=2的标题应编号为 `4.1.1` 而非 `4.2`

4. **生成LaTeX章节结构**
   ```latex
   # 根据ilvl选择正确的LaTeX命令
   ilvl=0: \section*{1. 标题}
   ilvl=1: \subsection*{1.1 标题}
   ilvl=2: \subsubsection*{1.1.1 标题}
   ilvl=3: \paragraph*{1.1.1.1 标题}
   ilvl=4: \subparagraph*{1.1.1.1.1 标题}
   ```

5. **插入到文档**
   - 保持正确的嵌套关系
   - 使用正确的层级编号继承

**工具输出示例**：
```
====================================================================================================
Word文档标题结构详细分析
====================================================================================================
样式       编号ID     ilvl     推断层级    LaTeX命令          文本内容
----------------------------------------------------------------------------------------------------
1级                  -        1          \section*          测试说明
2级       16         1        2          \subsection*       一般信息
2级       16         2        3          \subsubsection*    测试级别    ← ilvl=2，应该是4.1.1
2级       16         1        2          \subsection*       计划执行的测试
2级       16         2        3          \subsubsection*    xxxxx语言功能测试
3级       16         3        4          \paragraph*        xxxxx功能测试

====================================================================================================
LaTeX代码建议（带层级编号）
====================================================================================================
\section*{4. 测试说明}
\subsection*{4.1 一般信息}
\subsubsection*{4.1.1 测试级别}      ← 注意：继承父级4.1
\subsubsection*{4.1.2 测试方法}
\subsection*{4.2 计划执行的测试}
\subsubsection*{4.2.1 xxxxx语言功能测试}
\paragraph*{4.2.1.1 xxxxx功能测试}   ← 4级标题
```

**重要概念**：

- **ilvl（编号级别）**：Word文档中的编号级别，从0开始
  - ilvl=0 → 1级标题
  - ilvl=1 → 2级标题
  - ilvl=2 → 3级标题
  - 以此类推...

- **样式代码**：Word中定义的段落样式
  - 198 → 1级标题
  - 43/44 → 2级标题
  - 46 → 3级标题
  - **但样式代码不如ilvl可靠，应优先使用ilvl判断层级**

- **编号继承**：子级标题必须包含父级编号
  - ✅ 正确：4.1.1, 4.1.2, 4.2.1
  - ❌ 错误：4.2, 4.3, 4.10（这些应该是4.1.1, 4.1.2, 4.2.1）

**关键提示**：
- ⚠️ **不要使用pandoc直接转换**：会导致章节编号错乱
- ✅ **优先使用ilvl判断层级**：比样式代码更可靠
- ✅ **使用编号继承规则**：子级必须包含父级编号
- ✅ **使用增强版工具**：`analyze_docx_structure_full.py`支持1-7级
- ⚠️ **6级+标题需要自定义**：工具会自动提示

### 场景4：批量创建章节

**用户请求**: "帮我创建第2-5章的框架"

**执行步骤**:

1. **分析 Word 文档结构**
   - 使用 pandoc 转换为 markdown
   - 提取章节标题和层级

2. **逐章生成**
   - 按照标准格式创建
   - 自动编号

3. **插入到文档**
   - 保持顺序
   - 添加占位符内容

## 内容占位符规范

### 文本占位符
```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 表格占位符
```latex
\multicolumn{1}{|c|}{{\xiaowu 1}} & {\xiaowu } & {\xiaowu } \\
```

### 日期占位符
```
xxxx年xx月
```

### 编号占位符
```
xxxx-xxxx
```

## 快速模板

### 纯文本章节

```latex
\subsection*{N.X 子节标题}

{\normalsize
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx。
}
```

### 含列表的章节

```latex
\subsection*{N.X 带列表的子节}

{\normalsize
（1）xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx；

（2）xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx；

（3）xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx。
}
```

### 含表格的章节

```latex
\subsection*{N.X 带表格的子节}

{\normalsize
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx如表 X 所示。

% 表格使用[H]参数强制在当前位置，防止标题与内容分离
\begin{table}[H]
\centering
\vspace{6pt}
{\wuhaohei 表 X 表格标题}

\vspace{6pt}
{\settablespacing
\begin{tabular}{|p{0.5cm}|p{7cm}|p{7cm}|}
\hline
\rowcolor{gray!20}
\multicolumn{1}{|c|}{{\xiaowuhei 序号}} & \multicolumn{1}{c|}{{\xiaowuhei 项目A}} & \multicolumn{1}{c|}{{\xiaowuhei 项目B}} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 1}} & {\xiaowu } & {\xiaowu } \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 2}} & {\xiaowu } & {\xiaowu } \\
\hline
\end{tabular}
}
\end{table}
\vspace{6pt}  % 根据后续内容类型调整（见表格最佳实践）

xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx。
}
```

## 注意事项

### 1. 层级编号规则（最重要）

**❌ 常见错误**：
```latex
\subsection*{4.1 一般信息}
\subsubsection*{4.2 测试级别}      # 错误！独立编号
\subsubsection*{4.3 测试方法}
```

**✅ 正确做法**：
```latex
\subsection*{4.1 一般信息}
\subsubsection*{4.1.1 测试级别}   # 正确！继承父级
\subsubsection*{4.1.2 测试方法}
```

**判断原则**：
- 子级标题必须包含完整的父级编号路径
- 3级标题格式：`章.节.小节`（如4.1.1）
- 4级标题格式：`章.节.小节.段落`（如4.1.1.1）

### 2. Word文档层级识别

**优先级顺序**：
1. **ilvl（编号级别）** - 最可靠 ⭐⭐⭐⭐⭐
   - ilvl=0 → 1级
   - ilvl=1 → 2级
   - ilvl=2 → 3级
   - ilvl=3 → 4级
   - ...

2. **样式代码** - 次可靠 ⭐⭐⭐
   - 样式198 → 1级
   - 样式43/44 → 2级
   - 样式46 → 3级

3. **文本内容** - 辅助参考 ⭐⭐
   - 查看Word文档中的实际编号

**工具推荐**：
```bash
# 完整分析（推荐）
python3 tools/analyze_docx_structure_full.py templates/document.docx

# 快速查看
python3 tools/extract_word_structure.py templates/document.docx
```

### 3. LaTeX层级支持

| 层级 | 命令 | 支持 | 使用场景 |
|------|------|------|----------|
| 1-3级 | `\section*` ~ `\subsubsection*` | ✅ 原生 | 大部分文档 |
| 4级 | `\paragraph*` | ✅ 原生 | 详细内容 |
| 5级 | `\subparagraph*` | ✅ 原生 | 深层结构 |
| 6级+ | 自定义命令 | ⚠️ 需扩展 | 极少使用 |

**如果需要6级+标题**，在导言区添加：
```latex
\newcommand{\subsubparagraph}[1]{%
  \noindent\textbf{#1}\par
}
```

### 4. 编号规则

- 章节编号使用阿拉伯数字（1、2、3）
- 层级间用点号分隔（4.1.1）
- 保持连续性和一致性
- 子级必须继承父级编号

### 5. 字体规范

- 1-3级标题：五号宋体加粗 `\wuhao\bfseries`
- 正文：五号宋体 `\wuhao` 或 `\normalsize`
- 4-5级标题：继承上级标题格式

### 6. 间距规范

- **标题段前段后**：6pt
- **正文行间距**：18磅（重要，见下方详细说明）
- **段落首行缩进**：1.5em

#### 正文行间距设置（关键）⭐⭐⭐⭐⭐

**问题**：避免双重设置导致实际行间距超过预期。

**正确设置方法**：
```latex
% 导言区设置
\newcommand{\wuhao}{\fontsize{10.5pt}{18pt}\selectfont}  % 五号，行间距18磅
\renewcommand{\baselinestretch}{1.0}  % 不额外倍增
```

**错误示例**（会导致行间距过大）：
```latex
\newcommand{\wuhao}{\fontsize{10.5pt}{15.75pt}\selectfont}
\renewcommand{\baselinestretch}{1.71}
% 实际行间距：15.75pt × 1.71 ≈ 26.9pt ❌ 远超18磅
```

**计算公式**：
```
实际行间距 = \fontsize的第二个参数 × \baselinestretch
```

**推荐设置**：

| 字体大小 | \fontsize参数 | \baselinestretch | 实际行间距 |
|---------|--------------|-----------------|-----------|
| 10.5pt (五号) | 18pt | 1.0 | **18pt** ✅ |
| 9pt (小五号) | 可自定义 | 1.0 | 根据需求 |

**注意事项**：
- ⚠️ 避免双重设置：不要同时设置\fontsize的第二个参数和\baselinestretch
- ⚠️ 如果使用\baselinestretch，应设置为1.0，并在\fontsize中直接指定行间距
- ✅ 推荐：`\fontsize{10.5pt}{18pt}` + `\baselinestretch{1.0}`
- ❌ 不推荐：`\fontsize{10.5pt}{15.75pt}` + `\baselinestretch{1.71}`

### 7. 表格规范

- **表格环境**：使用 `\begin{table}[H]` 替代 `\begin{center}`（重要）
- **表题**：五号黑体居中
- **表头**：小五号黑体，灰色背景
- **表格内容**：小五号宋体
- **统一宽度**：14.5cm（参考表1、表2）

### 8. 表格最佳实践（新增）⭐⭐⭐⭐⭐

#### 防止表格分页

**问题**：表格标题和内容可能被分页符分开到不同页面。

**解决方案**：
```latex
% 必须在导言区添加
\usepackage{float}    % 浮动体控制

% 表格格式
\begin{table}[H]
\centering
\vspace{6pt}
{\wuhaohei 表 X 表格标题}

\vspace{6pt}
{\settablespacing
\begin{tabular}{|...|}
...
\end{tabular}
}
\end{table}
```

**方法对比**：
| 方法 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| `\begin{table}[H]` | 防止分页，效果好 | 需要float包 | ✅ 强烈推荐 |
| `\begin{center}` | 简单 | 标题和内容可能分页 | ❌ 不推荐 |
| `\nopagebreak` | 简单 | 效果弱，可能被忽略 | ⚠️ 不推荐 |

#### 表格后间距精确控制

**问题**：表格与后续内容（正文/标题）的间距需要精确控制。

**技术要点**：LaTeX的table环境有默认的 `\textfloatsep` 间距（约12pt）。

**间距计算公式**：
```
总间距 = LaTeX默认间距(\textfloatsep) + 手动间距(\vspace)
```

**推荐设置**：

| 后续内容 | 目标总间距 | 手动设置 | 说明 |
|---------|-----------|---------|------|
| 标题 | 6pt | `\vspace{-6pt}` | 抵消部分默认间距 |
| 正文 | 18pt | `\vspace{6pt}` | 在默认间距基础上增加 |

**实现示例**：
```latex
\end{table}
% 智能选择间距：
% - 后续是标题：\vspace{-6pt}  % 总间距6pt
% - 后续是正文：\vspace{6pt}   % 总间距18pt
```

**Python自动判断**：
```python
# 检查表格后的内容类型
if '\\section*' in next_content or '\\subsection*' in next_content:
    spacing = '\\vspace{-6pt}  % 表格后为标题'
else:
    spacing = '\\vspace{6pt}   % 表格后为正文'
```

#### 常见问题

**Q: 为什么实际间距比设置的大？**
A: LaTeX的table环境有默认的 `\textfloatsep`（约12pt），需要考虑这个值。

**Q: 可以使用负值间距吗？**
A: 可以。`\vspace{-6pt}` 是安全的，用于抵消部分默认间距。

**Q: 如何批量转换旧表格？**
A: 使用Python脚本逐行处理，将 `\begin{center}` 改为 `\begin{table}[H]`。

**Q: table环境缺少float包怎么办？**
A: 在导言区添加 `\usepackage{float}`。

### 9. 内容填充

- 使用 `xxxx` 作为占位符
- 保持句子结构完整
- 预留足够的填充空间

## 调试技巧

### 章节未正确插入
- 检查插入位置是否在 `\end{document}` 之前
- 确认 `{}` 和 `\normalsize` 配对正确

### 编译错误
- 检查表格列数与表头一致
- 确认所有 `\\` 和 `\hline` 配对
- 验证特殊字符已转义
- **表格环境错误**：确认已加载 `\usepackage{float}`
- **表格结束错误**：检查是否有遗漏的 `\end{center}`

### 格式不一致
- 对比已有章节的格式
- 复制粘贴已有的正确格式代码

## 示例对话

**用户**: "帮我创建第2章软件测试环境"

**执行流程**:
1. 读取当前文档末尾
2. 生成第2章完整框架（7个子节）
3. 在第1章后插入
4. 返回插入位置和内容概要

**用户**: "在2.3节添加一个硬件配置表"

**执行流程**:
1. 定位 2.3 节位置
2. 生成合适的表格（考虑硬件配置的特点）
3. 在正确位置插入
4. 编译验证

**用户**: "帮我生成第3-5章的框架"

**执行流程**:
1. 询问每章大致内容
2. 批量生成章节框架
3. 一次性插入所有章节
4. 提供内容填充指南
