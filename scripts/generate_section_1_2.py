#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试计划文档 1.2 章节（系统概述）的覆盖性对照表
从 data 目录读取测试指标和测试项信息
"""

import os
import re
import yaml
from pathlib import Path


def load_yaml(file_path):
    """加载YAML文件，处理中文编码和中文冒号"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 将中文冒号替换为英文冒号
        content = content.replace('：', ':')
        return yaml.safe_load(content)
    except Exception as e:
        print(f"错误：无法读取文件 {file_path}: {e}")
        return None


def parse_plan_yaml(file_path):
    """解析plan.yaml文件，提取测试项名称"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取测试项名称
        match = re.search(r'测试项名称[：:]\s*(.+?)(?:\n|$)', content)
        if match:
            return match.group(1).strip()
        return ""
    except Exception as e:
        print(f"错误：解析文件 {file_path} 失败: {e}")
        return None


def generate_coverage_table(data_dir):
    """生成覆盖性对照表的LaTeX代码"""
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"错误：数据目录 {data_dir} 不存在")
        return ""

    latex_lines = []
    table_number = 1
    global_row_number = 1

    # 获取所有test-metric目录并排序
    metric_dirs = sorted([d for d in data_path.iterdir() if d.is_dir() and d.name.endswith('-test-metric')])

    for metric_dir in metric_dirs:
        # 查找metric.yaml文件
        metric_files = list(metric_dir.glob("*metric.yaml"))
        if not metric_files:
            print(f"警告：在 {metric_dir} 中未找到metric.yaml文件")
            continue

        metric_file = metric_files[0]
        metric_data = load_yaml(metric_file)
        if not metric_data or 'content' not in metric_data:
            print(f"警告：{metric_file} 中缺少content字段")
            continue

        metric_content = metric_data.get('content', '')

        # 收集该指标下的所有测试项
        test_items = []
        module_dirs = sorted([d for d in metric_dir.iterdir() if d.is_dir() and d.name.endswith('-module')])

        for module_dir in module_dirs:
            # 获取该module下的所有item目录并排序
            item_dirs = sorted([d for d in module_dir.iterdir() if d.is_dir() and 'item' in d.name])

            for item_dir in item_dirs:
                # 读取plan.yaml
                plan_file = item_dir / "plan.yaml"
                if not plan_file.exists():
                    continue

                test_item_name = parse_plan_yaml(plan_file)
                if test_item_name:
                    test_items.append(test_item_name)

        # 如果没有测试项，跳过
        if not test_items:
            print(f"警告：指标 {metric_dir.name} 没有测试项")
            continue

        # 生成表格行：第一行使用 \multirow 合并单元格
        num_items = len(test_items)
        for idx, test_item in enumerate(test_items):
            if idx == 0:
                # 第一行：使用 \multirow 合并单元格
                latex_lines.append(f"\\multicolumn{{1}}{{|c|}}{{{{\\xiaowu {global_row_number}}}}} & \\multirow{{{num_items}}}{{7cm}}{{{{\\xiaowu {metric_content}}}}} & {{\\xiaowu {test_item}}} \\\\")
            else:
                # 后续行：第二列为空
                latex_lines.append(f"\\multicolumn{{1}}{{|c|}}{{{{\\xiaowu {global_row_number}}}}} &  & {{\\xiaowu {test_item}}} \\\\")

            latex_lines.append("\\hline")
            global_row_number += 1

    return "\n".join(latex_lines)


def generate_section_1_2(data_dir):
    """生成完整的1.2章节LaTeX代码"""
    # 生成表格行内容
    table_rows = generate_coverage_table(data_dir)

    # 如果没有数据，返回空字符串
    if not table_rows:
        print("警告：没有生成任何表格内容")
        return ""

    # 构建完整表格
    full_table = f"""% 表格使用[H]参数强制在当前位置，防止标题与内容分离
\\begin{{table}}[H]
\\centering
\\vspace{{6pt}}
{{\\wuhaohei 表 1 主要要求和技术指标与测试项覆盖性对照表}}

\\vspace{{6pt}}
{{\\settablespacing
\\begin{{tabular}}{{|p{{0.5cm}}|p{{7cm}}|p{{7cm}}|}}
\\hline
\\rowcolor{{gray!20}}
\\multicolumn{{1}}{{|c|}}{{{{\\xiaowuhei 序号}}}} & \\multicolumn{{1}}{{c|}}{{{{\\xiaowuhei 主要要求和技术指标}}}} & \\multicolumn{{1}}{{c|}}{{{{\\xiaowuhei 测试项}}}} \\\\
\\hline
{table_rows}
\\end{{tabular}}
}}
\\end{{table}}
\\vspace{{6pt}}  % 表格后为正文，总间距18pt"""

    # 构建1.2章节内容
    latex = f"""\\subsection*{{1.2 系统概述}}

{{\\normalsize
系统用途部分内容敏感，不在此处列出。详见xxxxxx系统合同（xxxxxx）。

xxxxxxx规定的本阶段主要要求和技术指标为：

{full_table}

xxxxxxxxxx系统软件的需方是"M"项目管理办公室，开发方是xxxxx。

标识当前和计划运行的现场，测试地点为"xxxxxx"，测试环境包括1台国产ARM架构服务器，其搭载国产处理器（飞腾）和国产操作系统（银河麒麟服务器版）以及2台国产X86台式机，其中服务器部署xxxxxxxxxxreleaseV0.7.1版，两台台式机为客户端。
}}

"""

    return latex


def main():
    """主函数"""
    data_dir = "data"
    output_file = "output/test_plan/chapters/chapter1_2_generated.tex"

    # 确保输出目录存在
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # 生成1.2章节内容
    latex_content = generate_section_1_2(data_dir)

    if not latex_content:
        print("❌ 未能生成内容")
        return

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    print(f"✅ 1.2章节LaTeX代码已生成到: {output_file}")
    print(f"✓ 接下来运行构建脚本将内容插入到chapter1.tex中")


if __name__ == "__main__":
    main()
