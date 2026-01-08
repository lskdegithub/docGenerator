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

        # 返回格式化后的字符串：测试项名称\newline（标识）- 使用换行
        if test_item_id:
            return f"{test_item_name}\\newline（{test_item_id}）"
        else:
            return test_item_name
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
                    # 转义LaTeX特殊字符（如下划线）
                    test_item_name_escaped = test_item_name.replace('_', '\\_')
                    test_items.append(test_item_name_escaped)

        # 如果没有测试项，跳过
        if not test_items:
            print(f"警告：指标 {metric_dir.name} 没有测试项")
            continue

        # 生成表格行：第一列和第二列用multirow合并，第三列拆分
        num_items = len(test_items)

        # 根据第二列内容长度估算需要的总高度（以正常行为单位）
        # 假设每行约35个中文字符，根据字符数估算需要的行数
        content_chars = len(metric_content)
        estimated_rows = max(1, int(content_chars / 35) + 1)

        # 计算最后一个测试项需要的行高
        # 总需要高度 = (num_items - 1) 个正常行 + 最后一个超高行
        # 最后一个超高行 = estimated_rows - (num_items - 1)
        # 如果estimated_rows <= num_items，则最后一个行保持正常
        base_spacing = 12  # 正常行高（可以调整这个值来改变最后一行高度）
        if estimated_rows > num_items:
            # 需要增加最后一个测试项的行高
            extra_height = (estimated_rows - num_items + 1) * base_spacing
            last_line_spacing = base_spacing + extra_height
        else:
            last_line_spacing = base_spacing

        def calculate_line_spacing(item_text, row_index=0, num_items_in_group=1, is_last_row=False):
            """根据内容高度动态计算行间距"""
            # 如果是最后一行且需要增加行高来容纳第二列parbox
            if is_last_row and estimated_rows > num_items:
                return last_line_spacing

            # 检测是否有换行符（\newline表示两行内容）
            has_newline = "\\newline" in item_text

            # 基础行间距
            base_spacing = 6

            # 如果有换行，需要额外间距
            if has_newline:
                base_spacing += 12  # 换行时的基础额外间距（从6改为12）

            # 对于测试项数量>=4的情况，第3行（索引为2）需要更多空间避免穿模
            if num_items_in_group >= 4 and row_index == 2:
                base_spacing += 10  # 第三行增加10pt

            # 最后一行适当增加（但不是通过这个逻辑，而是通过is_last_row参数）
            if is_last_row and num_items_in_group >= 4:
                base_spacing += 4  # 最后一行增加4pt

            return int(base_spacing)

        for idx, test_item in enumerate(test_items):
            # 判断是否为最后一行
            is_last = (idx == num_items - 1)

            # 计算当前行的行间距（传入行索引、测试项数量、是否最后一行）
            line_spacing = calculate_line_spacing(test_item, idx, num_items, is_last)

            if idx == 0:
                # 第一行：第一列和第二列都使用multirow
                # 使用实际的测试项数量作为multirow行数
                col1 = "\\multirow{" + str(num_items) + "}{*}{\\xiaowu " + str(metric_number) + "}"
                col2 = "\\multirow{" + str(num_items) + "}{*}{\\parbox[t]{7.6cm}{\\xiaowu " + metric_content + "}}"
                line = col1 + " & " + col2 + " & {\\xiaowu " + test_item + "} \\\\[" + str(line_spacing) + "pt]"
                latex_lines.append(line)
                # 根据是否为最后一行决定画线类型
                if is_last:
                    latex_lines.append("\\hline")
                else:
                    latex_lines.append("\\cline{3-3}")
            else:
                # 后续行：第一列和第二列为空（被multirow合并）
                line = " &  & {\\xiaowu " + test_item + "} \\\\[" + str(line_spacing) + "pt]"
                latex_lines.append(line)
                # 根据是否为最后一行决定画线类型
                if is_last:
                    latex_lines.append("\\hline")
                else:
                    latex_lines.append("\\cline{3-3}")

        # 指标编号递增
        metric_number += 1

    return "\n".join(latex_lines)


def generate_section_1_2(data_dir):
    """生成完整的1.2章节LaTeX代码"""
    # 生成表格行内容
    table_rows = generate_coverage_table(data_dir)

    # 如果没有数据，返回空字符串
    if not table_rows:
        print("警告：没有生成任何表格内容")
        return ""

    # 构建完整表格（使用longtable支持跨页）
    full_table = f"""% 使用longtable支持跨页，同时保留multirow
\\begin{{longtable}}{{|p{{0.8cm}}|p{{8cm}}|p{{5.7cm}}|}}
% 第一页表头
\\hline
\\rowcolor{{gray!20}}
\\multicolumn{{1}}{{|c|}}{{{{\\xiaowuhei 序号}}}} & \\multicolumn{{1}}{{c|}}{{{{\\xiaowuhei 主要要求和技术指标}}}} & \\multicolumn{{1}}{{c|}}{{{{\\xiaowuhei 测试项}}}} \\\\
\\hline
\\endfirsthead

% 后续页表头（每页重复）
\\hline
\\rowcolor{{gray!20}}
\\multicolumn{{1}}{{|c|}}{{{{\\xiaowuhei 序号}}}} & \\multicolumn{{1}}{{c|}}{{{{\\xiaowuhei 主要要求和技术指标}}}} & \\multicolumn{{1}}{{c|}}{{{{\\xiaowuhei 测试项}}}} \\\\
\\hline
\\endhead

% 每页底部横线
\\hline
\\vspace{{-6pt}}  % 减少底部间距，避免跨页时内容压线
\\endfoot

% 最后一页底部
\\hline
\\endlastfoot

% 表格内容
{table_rows}
\\end{{longtable}}
\\vspace{{-6pt}}  % 表格后间距调整"""

    # 构建1.2章节内容
    latex = f"""\\subsection*{{1.2 系统概述}}

{{\\normalsize
系统用途部分内容敏感，不在此处列出。详见xxxxxx系统合同（xxxxxx）。

xxxxxxx规定的本阶段主要要求和技术指标为：

\\vspace{{6pt}}
\\centerline{{\\wuhaohei 表 1 主要要求和技术指标与测试项覆盖性对照表}}
\\vspace{{6pt}}

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
