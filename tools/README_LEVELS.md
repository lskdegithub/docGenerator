# 文档层级支持测试

## LaTeX标准标题层级

| 层级 | LaTeX命令 | ilvl值 | 编号示例 | 说明 |
|------|-----------|--------|----------|------|
| 1级 | `\section*` | ilvl=0 | 1. | 章标题 |
| 2级 | `\subsection*` | ilvl=1 | 1.1 | 节标题 |
| 3级 | `\subsubsection*` | ilvl=2 | 1.1.1 | 小节标题 |
| 4级 | `\paragraph*` | ilvl=3 | 1.1.1.1 | 段落标题 |
| 5级 | `\subparagraph*` | ilvl=4 | 1.1.1.1.1 | 小段落标题 |
| 6级 | 自定义命令 | ilvl=5 | 1.1.1.1.1.1 | 需要自定义 |

## 使用说明

### 1-5级标题（标准支持）

LaTeX的article文档类原生支持1-5级标题，无需额外配置。

### 6级标题（需要自定义）

如果文档包含6级标题，需要在导言区添加自定义命令：

```latex
\usepackage{titlesec}

% 定义六级标题计数器
\newcounter{subsubparagraph}[subparagraph]

% 定义六级标题命令
\newcommand{\subsubparagraph}[1]{%
  \noindent\textbf{#1}\par
}

% 或者使用titlesec定义格式化的六级标题
\titleformat{\subsubparagraph}
  {\normalsize\bfseries}
  {\thesubsubparagraph}
  {1em}
  {}
```

### 7级及以上标题

建议重构文档结构，减少层级深度。如果确实需要，可以继续定义更多级别的自定义命令。

## 工具对比

| 工具 | 支持层级 | 自动编号 | LaTeX代码生成 | 推荐场景 |
|------|----------|----------|---------------|----------|
| `extract_word_structure.py` | 3级 | ❌ | ✅ | 简单文档 |
| `analyze_docx_structure.py` | 4级 | ❌ | ✅ | 中等复杂度 |
| `analyze_docx_structure_full.py` | 1-7级 | ✅ | ✅ | 复杂文档（推荐） |

## 使用示例

```bash
# 分析包含深层级的Word文档
python3 tools/analyze_docx_structure_full.py templates/document.docx

# 输出包括：
# 1. 详细的标题结构分析
# 2. Markdown格式的层级结构
# 3. 完整的LaTeX代码（带自动编号）
# 4. 层级统计信息
# 5. 如果超过5级，会给出自定义命令建议
```

## 注意事项

1. **编号层级对应关系**：
   - Word的ilvl=0 → LaTeX的1级标题
   - Word的ilvl=1 → LaTeX的2级标题
   - Word的ilvl=N → LaTeX的(N+1)级标题

2. **样式代码识别**：
   - 样式198 → 1级标题
   - 样式43/44 → 2级标题
   - 样式46 → 3级标题
   - 其他样式 → 根据ilvl推断

3. **最佳实践**：
   - 尽量保持文档层级在3-4级以内
   - 超过5级应考虑重构文档结构
   - 使用语义化的标题，而非仅依赖编号
