#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试计划文档 4.2 章节（计划执行的测试）
从 data 目录读取测试指标、模块和测试项信息
"""

import os
import re
import yaml
from pathlib import Path
from collections import OrderedDict


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
    """解析plan.yaml文件，返回结构化数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析各个字段
        data = {
            '测试项名称': '',
            '标识': '',
            '测试要求': '',
            '测试策略': '',
            '测试方法': '',
            '假设': '',
            '约束': '',
            '优先级': '',
            '测试终止条件': '',
            '需求追踪关系': '',
        }

        # 提取测试项名称
        match = re.search(r'测试项名称[：:]\s*(.+?)(?:\n|$)', content)
        if match:
            data['测试项名称'] = match.group(1).strip()

        # 提取标识
        match = re.search(r'标识[：:]\s*(.+?)(?:\n|$)', content)
        if match:
            data['标识'] = match.group(1).strip()

        # 提取测试要求
        match = re.search(r'测试要求[：:]\s*(.+?)(?:\n\w+\s*[：:]|$)', content, re.DOTALL)
        if match:
            data['测试要求'] = match.group(1).strip()

        # 提取测试策略与方法
        strategy_match = re.search(
            r'测试策略与方法[：:]\s*\n\s*-[ ]*测试策略[：:]\s*(.+?)\n\s*-[ ]*测试方法[：:]\s*(.+?)(?=\n\n|\n\w+\s*[：:]|$)',
            content, re.DOTALL
        )
        if strategy_match:
            data['测试策略'] = strategy_match.group(1).strip()
            data['测试方法'] = strategy_match.group(2).strip()

        # 提取假设与约束
        constraint_match = re.search(
            r'假设与约束[：:]\s*\n\s*-[ ]*假设[：:]\s*(.+?)\n\s*-[ ]*约束[：:]\s*(.+?)(?=\n\n|\n\w+\s*[：:]|$)',
            content, re.DOTALL
        )
        if constraint_match:
            data['假设'] = constraint_match.group(1).strip()
            data['约束'] = constraint_match.group(2).strip()

        # 提取优先级
        match = re.search(r'优先级[：:]\s*(.+?)(?:\n|$)', content)
        if match:
            data['优先级'] = match.group(1).strip()

        # 提取测试终止条件
        match = re.search(r'测试终止条件[：:]\s*(.+?)(?:\n\w+\s*[：:]|$)', content, re.DOTALL)
        if match:
            data['测试终止条件'] = match.group(1).strip()

        # 提取需求追踪关系
        match = re.search(r'需求追踪关系[：:]\s*(.+?)(?:\n|$)', content)
        if match:
            data['需求追踪关系'] = match.group(1).strip()

        return data
    except Exception as e:
        print(f"错误：解析文件 {file_path} 失败: {e}")
        return None


def wrap_identifier_by_width(identifier, col_width_cm=5.3):
    """
    根据列宽自动计算换行点（纯按字符数，不改变字体大小）
    - col_width_cm: 列宽（厘米）
    返回：添加了换行符的字符串
    """
    # 转义下划线
    identifier = identifier.replace('_', '\\_')

    # 计算每行能容纳的字符数
    # 5.3cm ≈ 150pt，等宽字体每个字符约7pt（在正常大小下）
    # 保守估计每行约20个字符
    chars_per_line = 20

    # 如果字符串长度不超过每行字符数，直接返回
    if len(identifier) <= chars_per_line:
        return identifier

    # 按固定字符数换行
    result = []
    for i in range(0, len(identifier), chars_per_line):
        result.append(identifier[i:i+chars_per_line])

    # 使用LaTeX的换行符连接
    return ' \\newline '.join(result)


def generate_table_latex(plan_data, table_number, table_title):
    """生成测试项表格的LaTeX代码"""
    # 转义LaTeX特殊字符（如下划线）
    test_item_name = plan_data['测试项名称'].replace('_', '\\_')
    requirement = plan_data['测试要求'].replace('_', '\\_')
    strategy = plan_data['测试策略'].replace('_', '\\_')
    method = plan_data['测试方法'].replace('_', '\\_')
    assumption = plan_data['假设'].replace('_', '\\_')
    constraint = plan_data['约束'].replace('_', '\\_')
    priority = plan_data['优先级'].replace('_', '\\_')
    termination = plan_data['测试终止条件'].replace('_', '\\_')
    traceability = plan_data['需求追踪关系'].replace('_', '\\_')

    # 对标识字段进行智能换行处理
    identifier = wrap_identifier_by_width(plan_data['标识'])

    latex = "\\begin{table}[H]\n"
    latex += "\\centering\n"
    latex += "\\vspace{6pt}\n"
    # 表格标题：不使用固定宽度的parbox，让内容自然居中
    latex += "{\\wuhaohei 表 " + str(table_number) + " {\\xiaowuhei " + table_title.replace('_', '\\_') + "}}\n\n"
    latex += "\\vspace{6pt}\n"
    latex += "{\\settablespacing\n"
    latex += "\\begin{tabular}{|p{2.3cm}|p{6cm}|p{0.7cm}|p{5.5cm}|}\n"
    latex += "\\hline\n"
    # 第一行：标识列使用自动换行的标识（不改变字体大小）
    latex += "\\xiaowuhei 测试项名称 & \\xiaowu " + test_item_name + " & \\xiaowuhei 标识 & \\parbox[t]{5.3cm}{{\\xiaowu \\ttfamily " + identifier + "}} \\\\\n"
    latex += "\\hline\n"
    latex += "\\xiaowuhei 测试要求 & \\multicolumn{3}{p{11.6cm}|}{{ \\xiaowu " + requirement + "}} \\\\\n"
    latex += "\\hline\n"
    latex += "\\xiaowuhei 测试策略与方法 & \\multicolumn{3}{p{11.6cm}|}{{ \\xiaowu 测试策略：" + strategy + "\\newline 测试方法：" + method + "}} \\\\\n"
    latex += "\\hline\n"
    latex += "\\xiaowuhei 假设与约束 & \\multicolumn{3}{p{11.6cm}|}{{\\xiaowu 假设：" + assumption + "\\newline 约束：" + constraint + "}} \\\\\n"
    latex += "\\hline\n"
    latex += "\\xiaowuhei 优先级 & \\multicolumn{3}{p{11.6cm}|}{{\\xiaowu " + priority + "}} \\\\\n"
    latex += "\\hline\n"
    latex += "\\xiaowuhei 测试终止条件 & \\multicolumn{3}{p{11.6cm}|}{{\\xiaowu " + termination + "}} \\\\\n"
    latex += "\\hline\n"
    latex += "\\xiaowuhei 追踪关系 & \\multicolumn{3}{p{11.6cm}|}{{\\xiaowu " + traceability + "}} \\\\\n"
    latex += "\\hline\n"
    latex += "\\end{tabular}\n"
    latex += "}\n"
    latex += "\\end{table}\n"
    latex += "\\vspace{-6pt}  % 表格后为标题，总间距6pt\n"
    return latex


def generate_section_4_2(data_dir):
    """生成4.2章节的LaTeX代码"""
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"错误：数据目录 {data_dir} 不存在")
        return ""

    latex_output = []
    table_number = 11  # 从表11开始编号

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
        if not metric_data or 'title' not in metric_data:
            print(f"警告：{metric_file} 中缺少title字段")
            continue

        metric_title = metric_data.get('title', '')
        metric_content = metric_data.get('content', '')
        metric_index = metric_data.get('index', metric_dir.name.split('-')[0])

        # 生成三级子标题 (4.2.x) - 只显示标题，不包含content内容
        latex_output.append(f"\\subsubsection*{{4.2.{metric_index} {metric_title}}}")
        # 三级标题后不添加内容，直接处理下一级

        # 获取该metric下的所有module目录并排序
        module_dirs = sorted([d for d in metric_dir.iterdir() if d.is_dir() and d.name.endswith('-module')])

        for module_idx, module_dir in enumerate(module_dirs, start=1):
            # 读取metadata.yaml
            metadata_file = module_dir / "metadata.yaml"
            if not metadata_file.exists():
                print(f"警告：在 {module_dir} 中未找到metadata.yaml文件")
                continue

            metadata_data = load_yaml(metadata_file)
            if not metadata_data or 'MODULE_NAME' not in metadata_data:
                print(f"警告：{metadata_file} 中缺少MODULE_NAME字段")
                continue

            module_name = metadata_data.get('MODULE_NAME', '')
            module_id = metadata_data.get('MODULE_ID', '')

            # 转义LaTeX特殊字符（如下划线）
            module_id_escaped = module_id.replace('_', '\\_')

            # 生成四级子标题 (4.2.x.x) - 格式：MODULE_NAME (MODULE_ID)
            module_title = f"{module_name}（{module_id_escaped}）" if module_id else module_name
            latex_output.append(f"\\paragraph*{{4.2.{metric_index}.{module_idx} {module_title}}}")
            latex_output.append("\n{\\normalsize")

            # 获取该module下的所有item目录并排序
            item_dirs = sorted([d for d in module_dir.iterdir() if d.is_dir() and 'item' in d.name])

            for item_idx, item_dir in enumerate(item_dirs, start=1):
                # 读取plan.yaml
                plan_file = item_dir / "plan.yaml"
                if not plan_file.exists():
                    print(f"警告：在 {item_dir} 中未找到plan.yaml文件")
                    continue

                plan_data = parse_plan_yaml(plan_file)
                if not plan_data:
                    print(f"警告：无法解析 {plan_file}")
                    continue

                # 生成五级子标题 (4.2.x.x.x) - 使用递增序号，格式：测试项名称(标识)
                # 转义下划线等LaTeX特殊字符
                item_title = plan_data['测试项名称'].replace('_', '\\_') + "（" + plan_data['标识'].replace('_', '\\_') + "）"
                # 五级标题使用parbox实现换行
                latex_output.append("\\subparagraph*{4.2." + str(metric_index) + "." + str(module_idx) + "." + str(item_idx) + " \\parbox[t]{12cm}{{" + item_title + "}}}")
                latex_output.append("\n{\\normalsize")

                # 生成表格
                table_title = plan_data['测试项名称']
                table_latex = generate_table_latex(plan_data, table_number, table_title)
                latex_output.append(table_latex)
                latex_output.append("}")

                table_number += 1

            latex_output.append("}")  # 结束四级section

        # 三级标题不包含内容，无需结束标记

    return "\n".join(latex_output)


def main():
    """主函数"""
    data_dir = "data"
    output_file = "output/test_plan/chapters/chapter4_2_generated.tex"

    # 确保输出目录存在
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # 生成4.2章节内容
    latex_content = generate_section_4_2(data_dir)

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    print(f"✅ 4.2章节LaTeX代码已生成到: {output_file}")
    print(f"✓ 接下来运行构建脚本将内容插入到chapter4.tex中")


if __name__ == "__main__":
    main()
