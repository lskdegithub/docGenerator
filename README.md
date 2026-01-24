# LaTeX 技术文档项目

## 项目概述

基于 LaTeX 的军用软件测试文档生成系统，严格遵循 GJB 438C-2021 标准，支持生成测试大纲、测试细则、测试报告等文档。

**核心特性**：
- ✅ **样式与内容分离**：统一样式文件，格式修改一处生效
- ✅ **章节拆分管理**：每个文档按章节独立成多个文件
- ✅ **多人协作友好**：不同人员可同时编辑不同章节
- ✅ **一键编译**：支持编译全部或指定文档
- ✅ **数据驱动生成**：自动从数据生成表格和章节内容
- ✅ **跨页表格支持**：使用 tabularray 的 longtblr 支持大表格跨页显示

## 技术栈

### LaTeX（排版与标准样式）
- **编译引擎**：XeLaTeX（推荐 TeX Live 2025+）
- **中文与字体**：`ctex` + `fontspec`
- **表格系统**：`tabularray`（`tblr/longtblr`），用于长表跨页与主题化样式
- **版式控制**：`geometry`（页边距）、`titlesec`（标题）、`setspace`（行距）、`needspace`（防止表格被拆到页底）
- **统一样式入口**：[gjb438c-style.sty](file:///d:/workspace/claude/app/latex-test/src/doc2tex-template/gjb438c-style.sty)

### Python（数据驱动生成）
- **解释器**：Python 3（建议 3.8+；兼容旧版时避免使用 `list[str]` 语法）
- **依赖**：PyYAML（解析 `*.yaml`）、标准库（`re/json/pathlib` 等）
- **职责**：从 `data/` 读取指标/模块/测试项/用例数据，生成章节片段与追踪表 tex

### Shell（构建编排）
- **脚本语言**：bash
- **职责**：复制模板到 `output/`、调用 Python 生成、运行 XeLaTeX、多轮编译/日志解析/分页收敛
- **Windows 建议**：在 WSL 中执行 `*.sh`（减少路径与依赖差异）

## 工作原理（两条主流程）

### 1) 编译模板（不读 data）
- 输入：`src/doc2tex-template/<doc>/`
- 脚本：`./build.sh [test_plan|test_detail|test_report]`
- 输出：`output/template/<doc>.pdf`

### 2) 数据驱动生成（推荐）
- 输入：模板 `src/doc2tex-template/<doc>/` + 数据 `data/`
- 脚本：`./scripts/build_test_plan.sh`、`./scripts/build_test_detail.sh`
- 输出：
  - `output/generated/<doc>.pdf`（最终 PDF）
  - `output/<doc>/`（合成后的可编译 LaTeX 源码目录，用于排查/二次加工）

## 环境准备

### 必备软件
- **TeX Live**：建议 2025+，并确保 `xelatex` 可用
- **Python3**：用于运行 `scripts/*.py`
- **bash**：Linux/macOS/WSL 均可

### 字体依赖（默认样式）
样式文件默认使用：
- 中文：`Noto Serif CJK SC`、`Noto Sans CJK SC`
- 西文：`DejaVu Serif`

如果目标环境未安装这些字体，请先安装或调整 [gjb438c-style.sty](file:///d:/workspace/claude/app/latex-test/src/doc2tex-template/gjb438c-style.sty) 的字体配置。

## 项目结构

```
latex-test/
├── src/doc2tex-template/      # LaTeX 文档源码
│   ├── gjb438c-style.sty     # 📌 统一样式文件
│   ├── README.md             # 详细使用说明
│   │
│   ├── test_plan/            # 测试大纲（8章）
│   │   ├── main.tex          # 主文件
│   │   └── chapters/         # 章节文件夹
│   │       ├── chapter1.tex  # 范围
│   │       ├── chapter2.tex  # 引用文档
│   │       └── ...
│   │
│   ├── test_detail/          # 测试细则（5章+附录）
│   │   ├── main.tex
│   │   └── chapters/
│   │
│   └── test_report/          # 测试报告（4章+附录）
│       ├── main.tex
│       └── chapters/
│
├── data/                     # 测试数据目录
│   ├── 001-test-metric/      # 测试指标1
│   │   ├── 001-metric.yaml   # 指标定义
│   │   ├── 001-module/       # 模块1
│   │   │   ├── metadata.yaml # 模块元数据
│   │   │   ├── 001-item1/    # 测试项1
│   │   │   │   ├── plan.yaml # 测试计划
│   │   │   │   └── test_case/ # 测试用例
│   │   │   └── 002-item2/
│   │   └── 002-module/
│   └── README.md             # 数据目录使用说明
│
├── scripts/                  # 构建脚本
│   ├── build_test_plan.sh    # 测试计划构建脚本
│   ├── build_test_detail.sh  # 测试细则构建脚本
│   ├── parse_trace_pages.py  # 解析编译日志中的分页段信息（追踪表切分用）
│   ├── generate_section_1_2.py  # 1.2章节表格自动生成
│   ├── generate_section_4_2.py  # 4.2章节生成脚本
│   ├── generate_section_7.py    # 第7章追踪表生成（测试大纲）
│   ├── generate_test_detail.py  # 测试细则章节/追踪表生成
│   └── audit_tables.py          # LaTeX 表格一致性审计（可选）
│
├── output/                   # 编译输出目录
│   ├── test_plan.pdf         # 数据驱动构建脚本生成的 PDF（便捷拷贝）
│   ├── test_detail.pdf        # 数据驱动构建脚本生成的 PDF（便捷拷贝）
│   ├── test_plan/            # 完整的测试计划源码（从模板+数据生成）
│   └── log/                 # 编译日志
│
├── templates/                # Word 模板文档
├── build.sh                  # 一键编译脚本（编译模板）
├── .claude/skills/           # Claude Code 技能
└── README.md                 # 本文件
```

## 快速开始

### 方式1：从数据生成文档（推荐）

使用 `data/` 目录的测试数据自动生成文档内容（章节/表格），再编译生成 PDF。

```bash
# 构建测试计划（从 data 目录读取数据）
./scripts/build_test_plan.sh

# 构建测试细则（从 data 目录读取数据）
./scripts/build_test_detail.sh

# 输出文件
# - output/generated/test_plan.pdf    (PDF 文档)
# - output/generated/test_detail.pdf  (PDF 文档)
# - output/test_plan/                 (完整的 LaTeX 源码：模板 + 数据生成)
# - output/test_detail/               (完整的 LaTeX 源码：模板 + 数据生成)
```

**数据驱动的文档生成**：
- 从 `data/` 目录读取测试指标、模块、测试项数据
- **自动生成1.2章节**：系统概述表格（主要要求和技术指标与测试项覆盖性对照表）
- **自动生成4.2章节**：计划执行的测试（详细测试项信息）
- 支持三层结构：测试指标 → 模块 → 测试项
- 详细说明请查看 [data/README.md](data/README.md)

### 方式2：编译模板文档

直接编译 LaTeX 模板（不使用 data 目录的数据）。

```bash
# 编译所有文档
./build.sh

# 编译指定文档
./build.sh test_plan     # 只编译测试大纲
./build.sh test_detail   # 只编译测试细则
./build.sh test_report   # 只编译测试报告
```

### 输出文件

模板编译（`./build.sh`）完成后，PDF 文件位于 `output/template/`，日志位于 `output/log/`：
- `output/template/test_plan.pdf`
- `output/template/test_detail.pdf`
- `output/template/test_report.pdf`

数据驱动生成（`./scripts/build_test_*.sh`）完成后，PDF 文件位于 `output/generated/`：
- `output/generated/test_plan.pdf`
- `output/generated/test_detail.pdf`

## 多人协作流程

1. **分配章节**
   ```bash
   # 例如：A负责第1章，B负责第2章
   A: src/doc2tex-template/test_plan/chapters/chapter1.tex
   B: src/doc2tex-template/test_plan/chapters/chapter2.tex
   ```

2. **独立编辑**
   - 各人在自己的 Git 分支上编辑对应章节
   - 只需关心自己负责的章节文件

3. **合并代码**
   - 通过 Pull Request 合并修改
   - 章节独立，减少合并冲突

4. **编译验证**
   ```bash
   ./build.sh test_plan  # 编译验证
   ```

## 数据驱动文档生成

### 数据组织结构

项目支持通过 `data/` 目录的测试数据自动生成测试计划文档。采用**指标-模块-测试项**的三层结构：

```
data/
├── 001-test-metric/              # 测试指标
│   ├── 001-metric.yaml          # 指标定义 → 4.2.1 三级标题
│   ├── 001-module/              # 模块1
│   │   ├── metadata.yaml        # 模块元数据 → 4.2.1.1 四级标题
│   │   ├── 001-item1/           # 测试项1
│   │   │   └── plan.yaml        # 测试计划 → 4.2.1.1.1 五级标题 + 表格
│   │   └── 002-item2/           # 测试项2
│   └── 002-module/              # 模块2
└── 002-test-metric/             # 测试指标2
```

### 文档生成流程

```
data/ 目录数据
    ↓
scripts/generate_section_4_2.py  # 解析数据，生成 LaTeX 代码
    ↓
output/test_plan/chapters/chapter4.tex  # 插入到第4章
    ↓
output/test_plan.pdf             # 编译生成 PDF
```

**生成的章节结构**：
```
4.2 计划执行的测试
├─ 4.2.1 大规模数据存储           ← metric.yaml 的 content 字段
│   ├─ 4.2.1.1 模块1             ← metadata.yaml 的 MODULE_NAME 字段
│   │   ├─ 4.2.1.1.1 测试项1（标识）  ← plan.yaml 的测试项名称(标识)
│   │   │   └─ 表11: 测试项详细信息
│   │   └─ 4.2.1.1.2 测试项2（标识）
│   └─ 4.2.1.2 模块2
└─ 4.2.2 小规模数据存储
```

详细说明请查看：[data/README.md](data/README.md)

## 技术文件格式规范

### 字号与间距
- **正文**：五号宋体 (10.5pt)，行间距 18磅
- **标题**：五号宋体加粗，段前段后 6pt
- **表题**：五号黑体居中
- **表头/内容**：小五号宋体（由表格主题统一控制）

### 表格格式
- **表格引擎**：使用 `tabularray`（`tblr/longtblr/talltblr`）
- **跨页表格**：使用 `longtblr`，跨页自动重复表头（设置 `rowhead=1`）
- **统一主题**：普通表使用 `theme=gjb`；4.2 字段表使用 `theme=gjbNoHead`（无表头样式）
- **横纵线条**：有竖线 `|` 的表，需显式配置 `hlines=...` 以生成横线
- **内容留白**：通过主题内 `colsep` 统一控制文字与竖线的间距
- **字体约束**：主题内 `cells={font=\\xiaowu}` 统一保证表内容为小五宋体；表头为 `\\xiaowuhei`
- **表格编号**：全局递增（表1、表2、表11、表12...）

### 页面设置
- **页边距**：上下左右各 2.5cm
- **段落首行缩进**：1.5em
- **页码**：小五号新罗马体，版心下居中

## 一致性检查（推荐）

为避免模板、Python 生成内容与最终插入章节出现格式不一致，提供了一个审计脚本用于检查：
- 是否在表格环境内使用了 `\\ttfamily/\\texttt` 等非宋体字体
- 是否出现 `\\normalsize/\\wuhao/\\Large` 等显式字号覆盖（会破坏“小五宋体”统一约束）
- 对 `theme=gjb` 表格是否遗漏 `hlines`（在使用 `|` 竖线时）

```bash
# 注意：Windows 下建议在 WSL/bash 环境使用 python3
python3 scripts/audit_tables.py
```

## Claude Code Skills

项目配置了以下自动化技能：

- `latex-format-checker` - 检查 LaTeX 文件格式合规性
- `latex-table-formatter` - 表格格式化工具
- `latex-special-table-generator` - 生成专用技术表格
- `latex-chapter-creator` - 章节结构生成
- `latex-document-updater` - 文档批量更新
- `latex-word-converter` - Word 到 LaTeX 转换

## 注意事项

- ⚠️ 所有文档必须严格遵守 GJB 438C-2021 格式标准
- ⚠️ 修改格式只需编辑 `gjb438c-style.sty`，所有文档自动生效
- ⚠️ 不要直接手工修改 `output/` 下的生成结果（会被脚本覆盖），应修改 `src/doc2tex-template/` 或 `data/` 或 `scripts/`
- ✅ 数据驱动生成的 LaTeX 源码会写入 `output/test_plan/`、`output/test_detail/`
- ✅ 编译产物自动输出到 `output/` 目录
- ✅ 使用 `scripts/build_test_plan.sh` 生成数据驱动的文档

## 追踪表跨页切分（box 切分）

当追踪表使用 `\SetCell[r=...]` 合并多行时，如果单元格跨页，分页会变得不可控。项目对部分追踪表采用“按页切分 box”的实现：
- **probe**：生成逐行探测版表格，并在每行注入 `\GjbTraceMark{tbl}{seq}{row}`（编译日志记录页码）
- **解析日志**：用 [parse_trace_pages.py](file:///d:/workspace/claude/app/latex-test/scripts/parse_trace_pages.py) 生成 `(tbl, seq) -> segs=[len1,len2,...]` 的 JSON
- **final**：按 `segs` 把一个大合并单元格拆成多个 `\SetCell[r=seg_len]` 段，从而做到“跨页处切断 box，但视觉仍像合并”

对应实现入口：
- 测试细则第5/6章：[generate_test_detail.py](file:///d:/workspace/claude/app/latex-test/scripts/generate_test_detail.py)
- 测试大纲第7章：[generate_section_7.py](file:///d:/workspace/claude/app/latex-test/scripts/generate_section_7.py)

## 常见问题（FAQ）

### Python 报错：`TypeError: 'type' object is not subscriptable`
通常是因为运行环境 Python 版本较老，无法解析 `list[str]` 这种类型注解。项目脚本已改为 `typing.List/Dict/Optional` 写法；若你本地仍出现类似问题，请确认使用的是 `python3` 并升级到 Python 3。

### 字体找不到/中文乱码
请安装 README「字体依赖」中列出的字体，或修改 [gjb438c-style.sty](file:///d:/workspace/claude/app/latex-test/src/doc2tex-template/gjb438c-style.sty) 的字体配置为你系统已安装的字体。

## 目录结构优势

### 模板与数据分离
- **模板不变**：`src/doc2tex-template/` 保持为标准模板
- **数据驱动**：`data/` 目录存放测试数据
- **自动生成**：脚本自动合并模板和数据，生成最终文档

### 数据组织优势
- 📁 **层次清晰**：指标 → 模块 → 测试项，层次分明
- 🔍 **易于管理**：测试数据与文档模板分离，便于维护
- 📦 **可扩展性**：添加测试数据即可自动生成新章节
- 🎯 **数据复用**：同一套数据可用于生成不同文档
- 🤝 **协作友好**：测试人员维护数据，文档人员维护模板

### 文档组织优势
- 📁 **组织清晰**：章节文件统一放在 `chapters/` 文件夹中
- 🔍 **查找快速**：需要哪个章节直接进入对应文件夹
- 📦 **易于扩展**：新增章节只需在 `chapters/` 中添加新文件
- 🎯 **职责分明**：`main.tex` 负责组织，`chapters/` 负责内容
- 🤝 **协作友好**：多人可同时编辑不同章节文件

## 相关文档

- [data/README.md](data/README.md) - 测试数据目录使用说明
- [src/doc2tex-template/README.md](src/doc2tex-template/README.md) - LaTeX 模板详细说明
- [scripts/README.md](scripts/README.md) - 构建脚本使用说明（待创建）

---

**创建日期**: 2025-12-22
**最后更新**: 2026-01-23
**版本**: 3.3
**标准**: GJB 438C-2021

**v3.3 更新内容**：
- ✨ 新增：第7章表格长文本自动换行功能
- ✨ 优化：表格列宽限制，适应不同内容长度
- ✨ 新增：28个测试用例数据内容丰富
- ✨ 新增：需求追踪关系唯一序号（SRS-01 ~ SRS-14）
- ✨ 改进：generate_section_7.py 支持正向/反向表格差异化配置
- 📝 更新：测试用例数据包含详细的综述、步骤和判定准则
