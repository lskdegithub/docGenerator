#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 plan.yaml 文件中的标识添加测试类型后缀
- functional (功能测试) → _GN
- performance (性能测试) → _XN
- interface (接口测试) → _JK
- reliability (可靠性测试) → _KKX
"""

import re
from pathlib import Path


# 测试类型到后缀的映射
TYPE_SUFFIX_MAP = {
    'functional': '_GN',
    'performance': '_XN',
    'interface': '_JK',
    'reliability': '_KKX',
}


def update_plan_yaml(file_path):
    """更新单个 plan.yaml 文件的标识"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取类型
    type_match = re.search(r'^type:\s*(\S+)', content, re.MULTILINE)
    if not type_match:
        print(f"  跳过：未找到 type 字段")
        return False

    test_type = type_match.group(1)
    suffix = TYPE_SUFFIX_MAP.get(test_type)

    if not suffix:
        print(f"  跳过：未知类型 {test_type}")
        return False

    # 提取当前标识
    id_match = re.search(r'标识[：:]\s*(\S+)', content)
    if not id_match:
        print(f"  跳过：未找到标识字段")
        return False

    current_id = id_match.group(1)

    # 检查是否已经有后缀
    for existing_suffix in TYPE_SUFFIX_MAP.values():
        if current_id.endswith(existing_suffix):
            print(f"  跳过：标识已有后缀 {current_id}")
            return False

    # 添加后缀
    new_id = current_id + suffix
    new_content = content.replace(f'标识： {current_id}', f'标识： {new_id}', 1)

    if new_content == content:
        # 尝试英文冒号
        new_content = content.replace(f'标识: {current_id}', f'标识: {new_id}', 1)

    if new_content == content:
        print(f"  警告：未能更新标识 {current_id}")
        return False

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  ✓ {current_id} → {new_id} ({test_type} → {suffix})")
    return True


def main():
    data_dir = Path('data')

    if not data_dir.exists():
        print(f"错误：data 目录不存在")
        return

    print(f"开始更新 plan.yaml 文件...")
    print(f"数据目录: {data_dir}")
    print(f"后缀规则: {TYPE_SUFFIX_MAP}")
    print()

    updated_count = 0
    skipped_count = 0

    # 查找所有 plan.yaml 文件
    for plan_file in sorted(data_dir.rglob('plan.yaml')):
        print(f"处理: {plan_file.relative_to(data_dir)}")
        if update_plan_yaml(plan_file):
            updated_count += 1
        else:
            skipped_count += 1
        print()

    print(f"======================================")
    print(f"完成！")
    print(f"  更新: {updated_count} 个文件")
    print(f"  跳过: {skipped_count} 个文件")


if __name__ == '__main__':
    main()
