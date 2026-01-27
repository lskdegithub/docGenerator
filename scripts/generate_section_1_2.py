#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试文档 1.2 章节（系统概述）的覆盖性对照表
支持 test_plan 和 test_detail 两种文档类型
从 data 目录读取测试指标和测试项信息
"""

import os
import re
import yaml
import argparse
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


def escape_latex_basic(text):
    if text is None:
        return ""
    text = str(text)
    return (
        text.replace('&', '\\&')
        .replace('%', '\\%')
        .replace('#', '\\#')
        .replace('_', '\\_\\allowbreak ')
    )


def break_long_words(text, length=10):
    if not text:
        return ""

    def replace(match):
        s = match.group(0)
        return r'\allowbreak '.join([s[i:i + length] for i in range(0, len(s), length)])

    return re.sub(r'[a-zA-Z0-9]{' + str(length) + r',}', replace, text)


def parse_plan_yaml(file_path):
    """解析plan.yaml文件，提取测试项名称和标识"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取测试项名称
        name_match = re.search(r'测试项名称[：:]\s*(.+?)(?:\n|$)', content)
        test_item_name = name_match.group(1).strip() if name_match else ""

        # 提取标识
        id_match = re.search(r'标识[：:]\s*(.+?)(?:\n|$)', content)
        test_item_id = id_match.group(1).strip() if id_match else ""

        test_item_name = escape_latex_basic(test_item_name)
        test_item_id = break_long_words(test_item_id)
        test_item_id = escape_latex_basic(test_item_id)

        # 返回格式化后的字符串：测试项名称\newline（标识）- 使用换行
        if test_item_id:
            return f"{test_item_name}\\newline（{test_item_id}）"
        else:
            return test_item_name
    except Exception as e:
        print(f"错误：解析文件 {file_path} 失败: {e}")
        return None


def collect_coverage_data(data_dir):
    """收集覆盖性对照表数据"""
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"错误：数据目录 {data_dir} 不存在")
        return []

    metrics = []
    metric_number = 1  # 指标序号，用于表格显示

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

        raw_metric_content = metric_data.get('content', '')
        metric_content = escape_latex_basic(raw_metric_content)

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

        # 如果没有测试项，跳过
        if not test_items:
            print(f"警告：指标 {metric_dir.name} 没有测试项")
            continue

        metrics.append(
            {
                "metric_number": metric_number,
                "metric_content": metric_content,
                "test_items": test_items,
            }
        )

        # 指标编号递增
        metric_number += 1

    return metrics


def generate_table2_longtblr(metrics):
    rows = []
    for m in metrics:
        metric_number = m["metric_number"]
        metric_content = m["metric_content"]
        test_items = m["test_items"]
        rough_len = len(metric_content) + sum(len(t) for t in test_items)
        should_split = rough_len >= 1200

        def emit_block(block_items, content_text):
            n = len(block_items)
            for idx, test_item in enumerate(block_items):
                row_end = r"\\*" if idx < n - 1 else r"\\"
                if idx == 0:
                    rows.append(
                        f"\\SetCell[r={n}]{{valign=t}}{{{metric_number}}} & "
                        f"\\SetCell[r={n}]{{valign=t}}{{{content_text}}} & "
                        f"{{{test_item}}} {row_end}"
                    )
                else:
                    rows.append(f" &  & {{{test_item}}} {row_end}")

        if should_split and len(test_items) > 2:
            chunk_size = 2
            chunks = [test_items[i:i + chunk_size] for i in range(0, len(test_items), chunk_size)]
            for chunk_idx, chunk in enumerate(chunks):
                content = metric_content if chunk_idx == 0 else f"{metric_content}（续）"
                emit_block(chunk, content)
        else:
            emit_block(test_items, metric_content)
    return "\n".join(rows)


def generate_section_1_2(data_dir, doc_type="test_plan"):
    """生成完整的1.2章节LaTeX代码

    Args:
        data_dir: 数据目录路径
        doc_type: 文档类型，"test_plan" 或 "test_detail"
    """
    metrics = collect_coverage_data(data_dir)

    # 如果没有数据，返回空字符串
    if not metrics:
        print("警告：没有生成任何表格内容")
        return ""

    table2_rows = generate_table2_longtblr(metrics)

    # 根据文档类型设置不同的参数
    if doc_type == "test_detail":
        subsection_cmd = "\\GjbSubsection{1.2 系统概述}"
        table_label = "tbl:detail-coverage"
    else:  # test_plan
        subsection_cmd = "\\GjbSubsection{1.2 系统概述}"
        table_label = "tbl:plan-coverage"

    table1 = f"""{{\\settablespacing
\\begin{{longtblr}}[theme=gjb,caption={{主要要求和技术指标与测试项覆盖性对照表}},label={{{table_label}}}]{{
  colspec={{|p{{0.8cm}}|p{{8cm}}|p{{5.7cm}}|}},
  rowhead=1,
  hlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},
  column{{1}}={{halign=c}},
}}
序号 & 主要要求和技术指标 & 测试项 \\\\
{table2_rows}
\\end{{longtblr}}
}}
\\vspace{{-6pt}}"""

    # 构建1.2章节内容
    latex = f"""{subsection_cmd}

系统用途部分内容敏感，不在此处列出。详见xxxxxx系统合同（xxxxxx）。

xxxxxxx规定的本阶段主要要求和技术指标为：

{table1}

xxxxxxxxxx系统软件的需方是"M"项目管理办公室，开发方是xxxxx。

标识当前和计划运行的现场，测试地点为"xxxxxx"，测试环境包括1台国产ARM架构服务器，其搭载国产处理器（飞腾）和国产操作系统（银河麒麟服务器版）以及2台国产X86台式机，其中服务器部署xxxxxxxxxxreleaseV0.7.1版，两台台式机为客户端。

"""

    return latex


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="生成测试文档1.2章节（系统概述）的覆盖性对照表")
    parser.add_argument("--data", default="data", help="数据目录路径")
    parser.add_argument("--out", default="output/test_plan/chapters/chapter1_2_generated.tex",
                        help="输出文件路径")
    parser.add_argument("--doc-type", default="test_plan", choices=["test_plan", "test_detail"],
                        help="文档类型：test_plan 或 test_detail")
    args = parser.parse_args()

    data_dir = args.data
    output_file = args.out
    doc_type = args.doc_type

    # 确保输出目录存在
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # 生成1.2章节内容
    latex_content = generate_section_1_2(data_dir, doc_type)

    if not latex_content:
        print("❌ 未能生成内容")
        return

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    print(f"✅ 1.2章节LaTeX代码已生成到: {output_file}")
    print(f"✓ 文档类型: {doc_type}")
    print(f"✓ 接下来运行构建脚本将内容插入到chapter1.tex中")


if __name__ == "__main__":
    main()
