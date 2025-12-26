---
name: latex-word-converter
description: Convert Word documents (.docx) to LaTeX format following technical document standards. Extracts structure, content, and tables while maintaining formatting compliance. Use when user has Word source documents that need to be converted to LaTeX.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# LaTeX Word Converter

将 Word 文档转换为符合技术文档标准的 LaTeX 格式。

## 功能概述

该 Skill 用于将 Word 文档（.docx）转换为 LaTeX 格式，包括：
- 提取文档结构（章节标题）
- 转换表格格式
- 保留文本内容
- 应用标准格式（字体、间距）
- 清理 Word 特有格式

## 转换流程

### 步骤1：Word 文档分析

**工具**: pandoc

```bash
# 转换为 markdown 以分析结构
pandoc templates/9月节点-测试大纲-0928.docx -o output/temp.md

# 查看转换结果
cat output/temp.md
```

**输出示例**:
```markdown
# 1. 范围

## 1.1 标识

（1）文档标识号：xxxx；
...
```

### 步骤2：结构提取

**提取章节标题**:

```bash
# 提取所有标题
grep -E "^#{1,3}" output/temp.md
```

**输出示例**:
```
# 1. 范围
## 1.1 标识
## 1.2 系统概述
## 1.3 文档概述
## 1.4 与其他计划的关系
## 1.5 引用文档
# 2. 软件测试环境
## 2.1 测试现场
## 2.2 测试环境概述
...
```

### 步骤3：内容提取

**提取表格**:

```bash
# 查找表格（在 markdown 中）
grep -A 20 "^|.*|" output/temp.md
```

**提取纯文本段落**:

```bash
# 提取正文内容
grep -v "^#" output/temp.md | grep -v "^|" | grep -v "^$"
```

### 步骤4：格式转换

将 Word/Markdown 格式转换为 LaTeX 标准格式：

| Word/Markdown | LaTeX 标准格式 |
|--------------|----------------|
| `# 1. 标题` | `\section*{1. 标题}` |
| `## 1.1 子标题` | `\subsection*{1.1 子标题}` |
| 普通文本 | `{\normalsize 文本}` |
| 表格 | 标准表格格式（见模板） |
| 列表 | `（1）...；` |

### 步骤5：格式标准化

应用技术文档标准：

```latex
% 章节标题
\noindent\section*{N. 章节标题}

% 子节标题
\subsection*{N.X 子节标题}

% 正文
{\normalsize
正文内容，使用五号宋体，行间距18磅，首行缩进1.5em。
}

% 表格
\vspace{-12pt}
\begin{center}
{\wuhaohei 表 X 表格标题}

{\settablespacing
\begin{tabular}{|列格式|}
...
\end{tabular}
}
\end{center}
\vspace{6pt}
```

## 转换模板

### 章节转换模板

**Word 格式**:
```
1. 范围
```

**LaTeX 格式**:
```latex
\noindent\section*{1. 范围}
```

### 子节转换模板

**Word 格式**:
```
1.1 标识
```

**LaTeX 格式**:
```latex
{\normalsize
\subsection*{1.1 标识}

{\normalsize
正文内容...
}
}
```

### 段落转换模板

**Word 格式**:
```
（1）文档标识号：xxxx；
（2）系统标识：xxxx，测试文档简称为xxxx；
```

**LaTeX 格式**:
```latex
{\normalsize
（1）文档标识号：xxxx；

（2）系统标识：xxxx，测试文档简称为xxxx；
}
```

### 表格转换模板

**Word/Markdown 表格**:
```markdown
| 序号 | 项目A | 项目B |
|---|---|---|
| 1 | 内容A | 内容B |
| 2 | 内容C | 内容D |
```

**LaTeX 格式**:
```latex
\vspace{-12pt}
\begin{center}
{\wuhaohei 表 X 表格标题}

{\settablespacing
\begin{tabular}{|p{0.5cm}|p{7cm}|p{7cm}|}
\hline
\rowcolor{gray!20}
\multicolumn{1}{|c|}{{\xiaowuhei 序号}} & \multicolumn{1}{c|}{{\xiaowuhei 项目A}} & \multicolumn{1}{c|}{{\xiaowuhei 项目B}} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 1}} & {\xiaowu 内容A} & {\xiaowu 内容B} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 2}} & {\xiaowu 内容C} & {\xiaowu 内容D} \\
\hline
\end{tabular}
}
\end{center}
\vspace{6pt}
```

## 使用方法

### 场景1：完整文档转换

**用户请求**: "把 templates/9月节点-测试大纲-0928.docx 转换为 LaTeX"

**执行步骤**:

1. **使用 pandoc 初步转换**
   ```bash
   pandoc templates/9月节点-测试大纲-0928.docx -o output/converted.tex
   ```

2. **分析转换结果**
   - 读取 output/converted.tex
   - 识别结构问题

3. **手动优化格式**
   - 调整章节标题格式
   - 修正表格格式
   - 应用标准字体和间距

4. **集成到主文档**
   - 将转换后的内容插入到 str-captain-1.tex
   - 编译验证

### 场景2：逐章转换

**用户请求**: "只转换第2章内容"

**执行步骤**:

1. **提取第2章内容**
   ```bash
   # 从 Word 文档中提取第2章
   pandoc templates/9月节点-测试大纲-0928.docx -t markdown | \
   sed -n '/# 2. 软件测试环境/,/# 3./p' > output/chapter2.md
   ```

2. **转换为 LaTeX 格式**
   - 手动或使用脚本转换
   - 应用标准格式

3. **插入到文档**
   - 定位到第1章后
   - 使用 Edit 工具插入

### 场景3：表格提取和转换

**用户请求**: "从 Word 文档中提取表格并转换为 LaTeX 格式"

**执行步骤**:

1. **提取表格内容**
   ```bash
   # 使用 pandoc 提取表格
   pandoc templates/9月节点-测试大纲-0928.docx -t markdown | \
   grep -A 30 "^|"
   ```

2. **分析表格结构**
   - 确定列数
   - 识别表头
   - 提取表格标题

3. **转换为标准格式**
   - 选择合适的表格模板
   - 设置列宽
   - 应用表头和内容格式

4. **插入到文档**
   - 确定表格编号
   - 插入到对应章节

## 批量转换脚本

创建批量转换脚本：

```bash
#!/bin/bash
# word-to-latex.sh

INPUT_FILE="$1"
OUTPUT_FILE="$2"

echo "正在转换 $INPUT_FILE 为 LaTeX 格式..."

# 步骤1：转换为 markdown
pandoc "$INPUT_FILE" -o /tmp/temp.md

# 步骤2：转换为 LaTeX
pandoc /tmp/temp.md -o /tmp/temp.tex

# 步骤3：提取内容
echo "转换完成，请手动调整格式："
echo "1. 调整章节标题格式"
echo "2. 修正表格格式"
echo "3. 应用标准字体和间距"

cp /tmp/temp.tex "$OUTPUT_FILE"
echo "文件已保存到: $OUTPUT_FILE"
```

使用示例：
```bash
chmod +x word-to-latex.sh
./word-to-latex.sh templates/9月节点-测试大纲-0928.docx output/converted.tex
```

## 转换检查清单

转换完成后，检查以下项目：

- [ ] 章节标题使用 `\section*` 或 `\subsection*`
- [ ] 正文包裹在 `{\normalsize ... }` 中
- [ ] 表格使用标准格式（`\settablespacing`、`\rowcolor{gray!20}`）
- [ ] 表题使用 `\wuhaohei` 和居中
- [ ] 表头使用 `\xiaowuhei`
- [ ] 表格内容使用 `\xiaowu`
- [ ] 所有特殊字符已转义（% # $ & ~ _ ^ \ { }）
- [ ] 中文字符正常显示（ctex 宏包已加载）
- [ ] 行间距设置为 18磅
- [ ] 标题间距设置为 6pt

## 常见问题和解决方法

### 问题1：中文字符乱码

**原因**: 编码问题或未使用 ctex 宏包

**解决方法**:
```latex
\usepackage{ctex}  % 确保加载此宏包
```

### 问题2：表格格式错误

**原因**: Word 表格与 LaTeX 表格格式不兼容

**解决方法**:
- 手动重建表格结构
- 使用标准表格模板
- 检查列数和行数

### 问题3：特殊字符编译错误

**原因**: LaTeX 特殊字符未转义

**解决方法**:
| 字符 | 转义 |
|------|------|
| % | `\%` |
| # | `\#` |
| $ | `\$` |
| & | `\&` |
| ~ | `\~{}` |
| _ | `\_` |
| ^ | `\^` |
| \ | `\textbackslash` |

### 问题4：段落缩进不一致

**原因**: Word 格式转换时丢失缩进设置

**解决方法**:
```latex
% 确保在导言区设置
\setlength{\parindent}{1.5em}
\setlength{\parskip}{0pt}
```

### 问题5：表格内容溢出

**原因**: 列宽设置不合理

**解决方法**:
- 调整列宽值
- 减少列数
- 使用更小的字体

## 优化建议

### 1. 分步转换
不要一次性转换整个文档，建议：
- 先转换结构（章节）
- 再转换内容（文本）
- 最后转换表格

### 2. 保留原始格式
在转换过程中：
- 保留原始 Word 文档
- 保存中间转换文件
- 记录转换日志

### 3. 质量检查
转换完成后：
- 编译 LaTeX 文件
- 对比 Word 原文
- 检查格式一致性
- 验证内容完整性

### 4. 建立转换库
对于重复文档：
- 创建转换模板
- 积累常用表格格式
- 建立术语对照表

## 示例对话

**用户**: "帮我将 Word 文档转换为 LaTeX 格式"

**执行流程**:
1. 询问 Word 文档路径
2. 使用 pandoc 初步转换
3. 分析转换结果
4. 手动优化格式
5. 编译验证
6. 提供优化建议

**用户**: "只转换第3章的表格"

**执行流程**:
1. 从 Word 文档中提取第3章
2. 定位表格内容
3. 转换为标准 LaTeX 格式
4. 插入到文档中
5. 验证编译

**用户**: "批量转换所有章节"

**执行流程**:
1. 分析文档结构
2. 逐章转换
3. 应用标准格式
4. 集成到主文档
5. 全面检查
6. 编译验证
7. 生成转换报告
