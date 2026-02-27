#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试计划文档 4.2 章节（计划执行的测试）
从 data 目录读取测试指标、模块和测试项信息
"""

import os
import re
import sys
import yaml
from pathlib import Path
from collections import OrderedDict

# 添加 scripts 目录到路径以导入 utils
sys.path.insert(0, str(Path(__file__).parent))
import utils


# 测试类型后缀到名称的映射
SUFFIX_TO_TYPE = {
    '_GN': '功能测试',
    '_JK': '接口测试',
    '_KKX': '可靠性测试',
    '_XN': '性能测试',
}

# 测试类型说明描述
TYPE_DESCRIPTION = {
    '功能测试': '验证软件功能是否满足需求规格说明',
    '接口测试': '测试各模块之间的接口参数传递正确性',
    '可靠性测试': '测试系统在异常情况下的恢复能力',
    '性能测试': '测试系统在负载条件下的性能表现',
}


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


def format_title_name_ident(name: str, ident: str, section_number: str, page_width_cm: float = 15.5) -> str:
    _ = section_number
    _ = page_width_cm
    return utils.format_title_name_ident(name, ident)


def format_toc_name_ident(name: str, ident: str) -> str:
    name = utils.escape_latex(str(name or "").strip())
    ident = utils.escape_latex(str(ident or "").strip())
    if ident:
        return f"{name}（{ident}）"
    return name


def wrap_identifier_by_width(identifier, col_width_cm=5.5):
    """
    根据列宽自动计算换行点（纯按字符数，不改变字体大小）
    - col_width_cm: 列宽（厘米）
    返回：添加了换行符的字符串
    """
    # 转义下划线
    identifier = identifier.replace('_', '\\_')

    # 计算每行能容纳的字符数
    # 5.5cm ≈ 155.9pt，小五号字体(9pt)等宽字体每个字符约5.4pt
    # 精确计算：155.9pt ÷ 5.4pt/字符 ≈ 28.9，取整为28-29个字符
    # 不需要额外留白，parbox充分利用宽度
    chars_per_line = 35

    # 如果字符串长度不超过每行字符数，直接返回
    if len(identifier) <= chars_per_line:
        return identifier

    # 按固定字符数换行
    result = []
    for i in range(0, len(identifier), chars_per_line):
        result.append(identifier[i:i+chars_per_line])

    # 使用LaTeX的换行符连接
    return ' \\newline '.join(result)

def make_table_label(identifier, fallback_number):
    raw = identifier or str(fallback_number)
    raw = str(raw)
    raw = re.sub(r'[^0-9a-zA-Z]+', '-', raw).strip('-').lower()
    if not raw:
        raw = str(fallback_number)
    return f"tbl:plan-item-{raw}"

def generate_table_latex(plan_data, table_number, table_title):
    """生成测试项表格的LaTeX代码（使用tabularray longtblr）"""
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

    table_label = make_table_label(plan_data.get('标识', ''), table_number)
    def compact(s: str) -> str:
        return " ".join(str(s or "").split())

    return (
        "\\GjbPlanItemTable{"
        + "caption={"
        + table_title.replace("_", "\\_")
        + "},"
        + "label={"
        + table_label
        + "},"
        + "name={"
        + compact(test_item_name)
        + "},"
        + "ident={"
        + compact(identifier)
        + "},"
        + "req={"
        + compact(requirement)
        + "},"
        + "strategy={"
        + compact(strategy)
        + "},"
        + "method={"
        + compact(method)
        + "},"
        + "assume={"
        + compact(assumption)
        + "},"
        + "constraint={"
        + compact(constraint)
        + "},"
        + "priority={"
        + compact(priority)
        + "},"
        + "term={"
        + compact(termination)
        + "},"
        + "trace={"
        + compact(traceability)
        + "}"
        + "}\n"
    )


def generate_section_4_2(data_dir):
    """生成4.2章节的LaTeX代码"""
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"错误：数据目录 {data_dir} 不存在")
        return ""

    latex_output = []
    table_number = 11

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

        metric_title = utils.escape_latex(metric_title)
        latex_output.append(f"\\GjbSubsubsection{{4.2.{metric_index} {metric_title}}}")
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

            # 生成四级子标题 (4.2.x.x) - 格式：MODULE_NAME (MODULE_ID)
            module_section = f"4.2.{metric_index}.{module_idx}"
            module_title = format_title_name_ident(module_name, module_id, module_section)
            module_toc_title = format_toc_name_ident(module_name, module_id)
            if r"\begin{minipage}" in module_title:
                latex_output.append(f"\\GjbParagraph[{module_section} {module_toc_title}]{{{module_section} {module_title}}}")
            else:
                latex_output.append(f"\\GjbParagraph{{{module_section} {module_title}}}")

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
                item_section = f"4.2.{metric_index}.{module_idx}.{item_idx}"
                item_title = format_title_name_ident(
                    plan_data['测试项名称'],
                    plan_data['标识'],
                    item_section
                )
                item_toc_title = format_toc_name_ident(plan_data['测试项名称'], plan_data['标识'])
                if r"\begin{minipage}" in item_title:
                    latex_output.append(f"\\GjbSubparagraph[{item_section} {item_toc_title}]{{{item_section} {item_title}}}")
                else:
                    latex_output.append(f"\\GjbSubparagraph{{{item_section} {item_title}}}")

                # 生成表格
                table_title = plan_data['测试项名称']
                table_latex = generate_table_latex(plan_data, table_number, table_title)
                latex_output.append(table_latex)

                table_number += 1

            # 三级标题不包含内容，无需结束标记

        # 三级标题不包含内容，无需结束标记

    return "\n".join(latex_output)


def get_test_type_from_suffix(identifier):
    """根据标识后缀获取测试类型"""
    for suffix, type_name in SUFFIX_TO_TYPE.items():
        if identifier.endswith(suffix):
            return type_name
    return '功能测试'  # 默认


def collect_test_items_for_table(data_dir):
    """收集所有测试项用于4.2表格"""
    test_items = []
    data_path = Path(data_dir)

    for metric_dir in sorted(data_path.glob('*-test-metric')):
        if not metric_dir.is_dir():
            continue

        for module_dir in sorted(metric_dir.glob('*-module')):
            if not module_dir.is_dir():
                continue

            for item_dir in sorted(module_dir.glob('*-item*')):
                plan_file = item_dir / 'plan.yaml'
                if plan_file.exists():
                    plan_data = utils.parse_plan_yaml(plan_file)
                    if plan_data:
                        identifier = plan_data.get('标识', '')
                        test_type = get_test_type_from_suffix(identifier)
                        test_items.append({
                            'name': plan_data.get('测试项名称', ''),
                            'id': identifier,
                            'type': test_type,
                        })
    return test_items


def generate_4_2_table_rows(test_items):
    """生成4.2表格行数据"""
    rows = []
    for i, item in enumerate(test_items, 1):
        name = utils.escape_latex(item['name'])
        item_id = utils.escape_latex(item['id'])
        test_type = item['type']

        # 格式：测试项名称（标识）
        display_name = f"{name}（{item_id}）"

        rows.append(f"  {{\\xiaowu {i}}} & {{\\xiaowu {test_type}}} & {{\\xiaowu {display_name}}} \\\\")
    return "\n".join(rows)


def replace_4_2_table_rows(template_file, test_items):
    """在模板文件中替换4.2表格行数据"""
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 生成新的行数据
    if test_items:
        new_rows = generate_4_2_table_rows(test_items)
    else:
        new_rows = "% 无测试项数据"

    # 查找标记并替换
    start_marker = '% MAGIC-42-ROWS-START'
    end_marker = '% MAGIC-42-ROWS-END'

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        print(f"警告：未找到4.2表格行数据标记")
        return False

    # 替换标记之间的内容
    new_content = (
        content[:start_idx + len(start_marker)] +
        '\n' + new_rows + '\n' +
        content[end_idx:]
    )

    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ 已更新4.2表格行数据，共 {len(test_items)} 个测试项")
    return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='生成4.2章节内容')
    parser.add_argument('--data-dir', default='data', help='数据目录路径')
    parser.add_argument('--out', default='output/test_plan/chapters/chapter4_2_generated.tex',
                        help='输出文件路径')
    parser.add_argument('--template-dir', default='output/test_plan/chapters',
                        help='模板章节目录（用于更新表格）')
    parser.add_argument('--update-table', action='store_true',
                        help='是否更新4.2表格行数据')

    args = parser.parse_args()

    # 确保输出目录存在
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    # 生成4.2章节详细内容
    latex_content = generate_section_4_2(args.data_dir)

    # 写入文件
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    print(f"✅ 4.2章节详细内容已生成到: {args.out}")

    # 如果指定了 --update-table，则更新4.2表格行数据
    if args.update_table:
        test_items = collect_test_items_for_table(args.data_dir)
        template_file = Path(args.template_dir) / 'chapter4.tex'
        replace_4_2_table_rows(template_file, test_items)


if __name__ == "__main__":
    main()

