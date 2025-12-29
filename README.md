# LaTeX 技术文档项目

## 项目概述

基于 LaTeX 的军用软件技术文档生成系统，严格遵循 GJB 438C-2021 标准，支持生成测试大纲、测试细则、测试报告等文档。

## 项目结构

```
latex-test/
├── src/                      # 源文件目录
│   └── doc2tex-template/     # LaTeX 模板
│       └── str-captain-1.tex # 测试大纲模板
├── output/                   # 编译输出目录
│   ├── *.pdf                # 生成的 PDF 文档
│   └── log/                 # 编译日志
│       ├── *.log            # LaTeX 日志文件
│       └── *.aux            # LaTeX 辅助文件
├── templates/                # Word 模板文档
├── tools/                    # 辅助工具
│   ├── extract_word_structure.py
│   └── extract_docx.py
├── build.sh                  # 一键编译脚本
├── .claude/                  # Claude Code 配置
│   └── skills/              # LaTeX 处理技能
└── README.md
```

## 技术文件格式规范标准

### 1. 目次格式
- **目次标题**：第一行"目次"，使用三号黑体加粗
- **目次内容**：使用五号宋体

### 2. 正文格式
- **技术文件正文**：五号宋体，西文使用 Times New Roman
- **页脚注释**：条文注、表注、图注，表头和表内容，使用小五号宋体
- **表题和编号**：五号黑体 + **居中**
- **图题和编号**：五号黑体 + **居中**
- **表注、图注**：小五号宋体 + **居中**

### 3. 附录格式
- **第一行**：附录及其编号和附录性质，使用五号黑体加粗和宋体
- **第二行**：附录名称，使用五号黑体加粗
- **第三行**：附录条文，使用五号宋体

### 4. 版式要求
- **行间距**：固定值18磅
- **标题格式**：1级、2级、3级标题，使用宋体5号加粗
- **标题间距**：段前段后6磅，行间距18磅
- **页码**：版心下面居中，使用小五号新罗马体

## LaTeX 实现要点

```latex
% 基础设置
\documentclass[12pt,a4paper]{article}
\usepackage{ctex}
\usepackage{fontspec}
\usepackage{geometry}
\usepackage{setspace}

% 字体设置
\setCJKmainfont{SimSun}  % 宋体
\setCJKsansfont{SimHei}  % 黑体
\setmainfont{Times New Roman}  % 西文字体

% 字号定义
\newcommand{\wuhao}{\fontsize{10.5pt}{15.75pt}\selectfont}  % 五号
\newcommand{\xiaowu}{\fontsize{9pt}{11pt}\selectfont}  % 小五号
\newcommand{\sanhao}{\fontsize{16pt}{18pt}\selectfont\bfseries}  % 三号

% 行间距设置
\renewcommand{\baselinestretch}{1.5}  % 18磅行距

% 页码设置
\pagestyle{plain}
\renewcommand{\thepage}{\xiaowu\rmfamily\arabic{page}}

% 标题格式设置
\usepackage{titlesec}
\titleformat{\section}{\wuhao\bfseries}{\thesection}{1em}{}
\titlespacing{\section}{0pt}{6pt}{6pt}
```

## 快速开始

### 编译文档

```bash
# 一键编译（推荐）
./build.sh
```

编译脚本会自动：
- 创建 `output/log/` 目录
- 编译 LaTeX 源文件
- 将 PDF 输出到 `output/` 目录
- 将日志文件移到 `output/log/` 目录

### 手动编译

```bash
xelatex -output-directory=output src/doc2tex-template/str-captain-1.tex
```

### 输出文件

- `output/str-captain-1.pdf` - 生成的 PDF 文档
- `output/log/str-captain-1.log` - 编译日志
- `output/log/str-captain-1.aux` - LaTeX 辅助文件

## Claude Code Skills

项目配置了以下自动化技能：

- `latex-format-checker` - 检查 LaTeX 文件格式合规性
- `latex-table-formatter` - 表格格式化工具
- `latex-special-table-generator` - 生成专用技术表格
- `latex-chapter-creator` - 章节结构生成
- `latex-document-updater` - 文档批量更新
- `latex-word-converter` - Word 到 LaTeX 转换

## 技术要点

### 表格防分页处理

```latex
\begin{table}[H]  % 使用 float 包的 [H] 参数
\centering
\caption{表格标题}
\nobreak          % 防止标题与内容分页
\begin{tabular}{|c|c|c|}
...
\end{tabular}
\end{table}
```

### 中文支持

项目使用 `ctex` 宏包和 `fontspec` 配置中文字体：
- 宋体：Noto Serif CJK SC
- 黑体：Noto Sans Mono CJK SC

## 注意事项

- 所有生成的 TEX 文件必须严格遵守 GJB 438C-2021 格式标准
- 源文件目录 `src/` 保持干净，不生成临时文件
- 所有编译产物自动输出到 `output/` 目录
- 编译日志保存在 `output/log/` 目录

---

**创建日期**: 2025-12-22
**最后更新**: 2025-12-29
**版本**: 2.0