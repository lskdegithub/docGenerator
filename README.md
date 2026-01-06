# LaTeX 技术文档项目

## 项目概述

基于 LaTeX 的军用软件测试文档生成系统，严格遵循 GJB 438C-2021 标准，支持生成测试大纲、测试细则、测试报告等文档。

**核心特性**：
- ✅ **样式与内容分离**：统一样式文件，格式修改一处生效
- ✅ **章节拆分管理**：每个文档按章节独立成多个文件
- ✅ **多人协作友好**：不同人员可同时编辑不同章节
- ✅ **一键编译**：支持编译全部或指定文档

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
│   └── generate_section_4_2.py  # 4.2章节生成脚本
│
├── output/                   # 编译输出目录
│   ├── test_plan.pdf         # 生成的 PDF 文档
│   ├── test_detail.pdf
│   ├── test_report.pdf
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

使用 `data/` 目录的测试数据自动生成测试计划文档。

```bash
# 构建测试计划（从 data 目录读取数据）
./scripts/build_test_plan.sh

# 输出文件
# - output/test_plan.pdf              (PDF 文档)
# - output/test_plan/                 (完整的 LaTeX 源码)
```

**数据驱动的文档生成**：
- 从 `data/` 目录读取测试指标、模块、测试项数据
- 自动生成测试计划文档的第 4.2 章节
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

编译完成后，PDF 文件位于 `output/` 目录：
- `output/test_plan.pdf` (221KB)
- `output/test_detail.pdf` (119KB)
- `output/test_report.pdf` (109KB)

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
- **表头/内容**：小五号宋体

### 表格格式
- 表题与表格不分页：使用 `table[H]` + `\vspace{-6pt}`
- 表头灰色背景：`\rowcolor{gray!20}`
- 统一宽度：14.5cm（A4纸张，页边距2.5cm）
- 表格编号全局递增（表11、表12、表13...）

### 页面设置
- **页边距**：上下左右各 2.5cm
- **段落首行缩进**：1.5em
- **页码**：小五号新罗马体，版心下居中

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
- ⚠️ 不要修改 `src/doc2tex-template/` 下的模板文件
- ✅ 数据驱动的文档会生成到 `output/test_plan/` 目录
- ✅ 编译产物自动输出到 `output/` 目录
- ✅ 使用 `scripts/build_test_plan.sh` 生成数据驱动的文档

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
**最后更新**: 2025-01-06
**版本**: 3.1
**标准**: GJB 438C-2021
