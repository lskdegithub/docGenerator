#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 plan.yaml 文件分配测试类型并添加对应后缀
分配比例：
- functional (功能测试): 50%
- interface (接口测试): 25%
- reliability (可靠性测试): 15%
- performance (性能测试): 10%
"""

import re
import random
from pathlib import Path

# 设置随机种子，确保每次运行结果一致
random.seed(42)


# 测试类型到后缀的映射
TYPE_INFO = {
    'functional': {'suffix': '_GN', 'name': '功能测试', 'ratio': 0.50},
    'interface': {'suffix': '_JK', 'name': '接口测试', 'ratio': 0.25},
    'reliability': {'suffix': '_KKX', 'name': '可靠性测试', 'ratio': 0.15},
    'performance': {'suffix': '_XN', 'name': '性能测试', 'ratio': 0.10},
}


def get_all_plan_files(data_dir):
    """获取所有 plan.yaml 文件，按路径排序"""
    files = list(sorted(data_dir.rglob('plan.yaml')))
    return files


def update_plan_yaml(file_path, test_type):
    """更新单个 plan.yaml 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 更新 type 字段
    type_match = re.search(r'^type:\s*\S+', content, re.MULTILINE)
    if type_match:
        content = re.sub(r'^type:\s*\S+', f'type: {test_type}', content, count=1, flags=re.MULTILINE)
    else:
        # 在文件末尾添加 type 字段
        content = content.rstrip() + f'\ntype: {test_type}\n'

    # 提取当前标识
    id_match = re.search(r'标识[：:]\s*(\S+)', content)
    if not id_match:
        print(f"  警告：未找到标识字段")
        return False, None

    current_id = id_match.group(1)
    base_id = current_id

    # 移除旧的后缀
    for suffix_info in TYPE_INFO.values():
        old_suffix = suffix_info['suffix']
        if base_id.endswith(old_suffix):
            base_id = base_id[:-len(old_suffix)]
            break

    new_id = base_id + TYPE_INFO[test_type]['suffix']

    # 更新标识
    content = re.sub(
        r'标识[：:]\s*' + re.escape(current_id),
        f'标识： {new_id}',
        content,
        count=1
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True, (base_id, new_id, test_type)


def main():
    data_dir = Path('data')

    if not data_dir.exists():
        print(f"错误：data 目录不存在")
        return

    files = get_all_plan_files(data_dir)
    total = len(files)

    if total == 0:
        print(f"错误：未找到 plan.yaml 文件")
        return

    # 计算每种类型的数量
    counts = {}
    remaining = total

    for ttype, info in TYPE_INFO.items():
        count = int(total * info['ratio'])
        counts[ttype] = count
        remaining -= count

    # 分配剩余的项给第一个类型
    if remaining > 0:
        counts['functional'] += remaining

    print(f"测试类型分配方案 (共{total}项):")
    for ttype, count in counts.items():
        info = TYPE_INFO[ttype]
        print(f"  {info['name']} ({ttype}): {count}项 → {info['suffix']}")
    print()

    # 按顺序分配类型
    type_sequence = []
    for ttype, count in counts.items():
        type_sequence.extend([ttype] * count)

    # 打乱顺序
    random.shuffle(type_sequence)

    print(f"开始更新 plan.yaml 文件...")
    print()

    results = {'functional': [], 'interface': [], 'reliability': [], 'performance': []}

    for i, (file_path, ttype) in enumerate(zip(files, type_sequence), 1):
        rel_path = str(file_path.relative_to(data_dir))
        print(f"[{i}/{total}] {rel_path}")

        success, data = update_plan_yaml(file_path, ttype)
        if success:
            base_id, new_id, actual_type = data
            results[actual_type].append(file_path)
            print(f"  ✓ {base_id} → {new_id} ({TYPE_INFO[ttype]['name']})")
        else:
            print(f"  ✗ 更新失败")
        print()

    # 打印汇总
    print(f"======================================")
    print(f"完成！")
    for ttype, info in TYPE_INFO.items():
        count = len(results[ttype])
        print(f"  {info['name']} ({ttype}): {count}项")


if __name__ == '__main__':
    main()
