# scripts 目录说明

本目录存放文档生成与构建脚本，分为两类：

- 构建脚本：负责复制模板、调用生成脚本、编译 PDF。
- 生成脚本：负责从 `data/` 解析数据并生成章节内容。

## 快速使用

在 WSL/Linux 下执行：

```bash
./scripts/build_test_plan.sh
./scripts/build_test_detail.sh
./scripts/build_test_report.sh
```

Docker 方式：

```bash
./scripts/docker_build_image.sh
./scripts/docker_compile.sh all
```

输出 PDF：

- `output/generated/test_plan.pdf`
- `output/generated/test_detail.pdf`
- `output/generated/test_report.pdf`

## 主要脚本

- `build_test_plan.sh`：测试大纲完整构建
- `build_test_detail.sh`：测试细则完整构建
- `build_test_report.sh`：测试报告完整构建
- `docker_build_image.sh`：构建 Docker 编译镜像（Ubuntu 22.04）
- `docker_compile.sh`：在 Docker 中挂载项目并执行构建
- `generate_section_1_2.py`：生成 1.2 系统概述章节
- `generate_section_4_1_5.py`：生成 4.1.5 测试顺序表
- `generate_section_4_2.py`：生成 test_plan 第 4.2 章节
- `generate_section_7.py`：生成 test_plan 第 7 章追踪表
- `generate_test_detail.py`：生成 test_detail 章节与追踪表
- `generate_test_report.py`：生成 test_report 第 4 章
- `parse_trace_pages.py`：解析日志分页信息
- `utils.py`：通用工具（转义、标题格式、YAML 读取等）

## 维护约定

- 标题“名称（标识）”换行规则统一走 `utils.format_title_name_ident`。
- 不要直接修改 `output/` 结果文件；应修改 `src/`、`scripts/`、`data/`。
- 运行前确保 `xelatex` 与 `python3` 可用。
