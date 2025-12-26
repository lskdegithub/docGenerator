# LaTeX 文档转换项目

## 项目概述

这是一个专门用于技术文档转换和处理的 LaTeX 项目，主要用于将 Word 文档转换为 LaTeX 格式并生成符合标准的 PDF 文档。

## 项目结构

```
latex-test/
├── src/                      # 源代码目录
│   └── doc2tex-template/     # 文档转 LaTeX 模板
│       └── str-captain-1.tex # LaTeX 模板文件
├── templates/                # 模板文件目录
│   └── *.docx               # Word 模板文档
├── tools/                    # 工具脚本目录
│   ├── README.md            # 工具使用说明
│   ├── extract_word_structure.py  # Word章节结构提取工具
│   ├── extract_docx.py      # DOCX文档解析工具
│   └── extract_structure.py # 结构提取工具
├── output/                   # 输出目录
│   └── *.pdf               # 生成的 PDF 文件
├── build.sh                 # LaTeX 编译脚本
├── .claude/                 # Claude Code 配置
│   └── skills/             # Claude Code Skills
└── README.md               # 项目说明文档
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

## 使用方法

### 编译 LaTeX 文件
```bash
xelatex -output-directory=output src/doc2tex-template/str-captain-1.tex
```

### 生成的文件
- `output/str-captain-1.pdf` - 主要 PDF 文档
- `output/str-captain-1.log` - 编译日志
- `output/str-captain-1.aux` - LaTeX 辅助文件

## 配置权限

项目配置了以下工具的使用权限：
- 文件操作命令
- Python 脚本执行
- Pandoc 文档转换
- LaTeX 编译（XeLaTeX）
- 字体列表查询

## 注意事项

- **所有生成的 TEX 文件必须严格遵守上述格式标准**
- 编译时需要系统中文字体支持
- 输出文件将保存到 `output/` 目录

**创建日期**: 2025-12-22
**版本**: 1.0