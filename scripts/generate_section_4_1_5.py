#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试计划文档 4.1.5 章节（测试进展）的表格行数据
从 data 目录读取 plan.yaml 文件，替换模板中的表格行数据
注意：表格结构在 chapter4.tex 模板中定义，本脚本只替换数据行
"""

import os
import sys
import re
import argparse
from pathlib import Path

# 添加 scripts 目录到路径以导入 utils
sys.path.insert(0, str(Path(__file__).parent))
import utils


def parse_plan_yaml(file_path):
    """解析plan.yaml文件，提取测试项信息"""
    data = utils.parse_plan_yaml(file_path)
    if not data:
        return None

    return {
        'name': data.get('测试项名称', ''),
        'id': data.get('标识', ''),
        'priority': data.get('优先级', '中'),
        'path': str(file_path)
    }


def collect_test_items(data_dir):
    """从data目录收集所有测试项信息"""
    test_items = []
    data_path = Path(data_dir)

    # 遍历所有 test-metric 目录下的 plan.yaml 文件
    for metric_dir in sorted(data_path.glob('*-test-metric')):
        if not metric_dir.is_dir():
            continue

        for module_dir in sorted(metric_dir.glob('*-module')):
            if not module_dir.is_dir():
                continue

            for item_dir in sorted(module_dir.glob('*-item*')):
                plan_file = item_dir / 'plan.yaml'
                if plan_file.exists():
                    item_info = parse_plan_yaml(plan_file)
                    if item_info and item_info['name']:
                        test_items.append(item_info)

    return test_items


def generate_rows(test_items):
    """生成LaTeX表格行代码"""

    # 按优先级排序：高 > 中 > 低
    priority_order = {'高': 0, '中': 1, '低': 2}

    def sort_key(item):
        priority = item.get('priority', '中')
        return (priority_order.get(priority, 1), item['name'])

    sorted_items = sorted(test_items, key=sort_key)

    rows = []
    for i, item in enumerate(sorted_items, 1):
        name = utils.escape_latex(item['name'])
        item_id = utils.escape_latex(item['id'])
        priority = utils.escape_latex(item.get('priority', '中'))

        # 格式：测试项名称（标识）
        display_name = f"{name}（{item_id}）"

        # 时间变量直接使用
        rows.append(f"{{\\xiaowu {i}}} & {{\\xiaowu {display_name}}} & {{\\xiaowu {priority}}} & \\GjbTestStartDate & \\GjbTestEndDate \\\\")

    return "\n".join(rows)


def replace_rows_in_template(chapter_file, test_items):
    """在模板文件中替换标记之间的行数据"""

    with open(chapter_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 生成新的行数据
    if test_items:
        new_rows = generate_rows(test_items)
    else:
        new_rows = "% 无测试项数据"

    # 查找标记并替换
    start_marker = '% MAGIC-ROWS-START'
    end_marker = '% MAGIC-ROWS-END'

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        print(f"警告：未找到行数据标记 {start_marker} / {end_marker}")
        return False

    # 替换标记之间的内容
    new_content = (
        content[:start_idx + len(start_marker)] +
        '\n' + new_rows + '\n' +
        content[end_idx:]
    )

    with open(chapter_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ 已更新 {chapter_file} 中的表格行数据")
    print(f"✓ 共找到 {len(test_items)} 个测试项")
    return True


def main():
    parser = argparse.ArgumentParser(description='生成4.1.5章节表格行数据')
    parser.add_argument('--data-dir', default='data', help='数据目录路径')
    parser.add_argument('--template-dir', default='output/test_plan/chapters',
                        help='模板章节目录')

    args = parser.parse_args()

    # 收集测试项数据
    test_items = collect_test_items(args.data_dir)

    # 替换模板文件中的行数据
    chapter_file = Path(args.template_dir) / 'chapter4.tex'
    replace_rows_in_template(chapter_file, test_items)


if __name__ == '__main__':
    main()
