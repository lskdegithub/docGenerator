#!/usr/bin/env python3
"""
增强版：精确分析Word文档的标题层级结构，支持1-6级标题
通过分析段落的编号级别(numId, ilvl)和样式来确定层级关系

支持的LaTeX层级：
- \section* (1级)
- \subsection* (2级)
- \subsubsection* (3级)
- \paragraph* (4级)
- \subparagraph* (5级)
- 自定义命令 (6级+)
"""

import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

def analyze_docx_structure(docx_path):
    """分析Word文档的完整结构，支持任意深度层级"""

    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        xml_content = zip_ref.read('word/document.xml')

    tree = ET.fromstring(xml_content)
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }

    # 存储所有段落信息
    paragraphs = []

    for para in tree.findall('.//w:p', namespaces):
        # 获取样式
        style_elem = para.find('.//w:pStyle', namespaces)
        style_val = style_elem.get(f'{{{namespaces["w"]}}}val') if style_elem is not None else ''

        # 获取编号信息
        numbering_elem = para.find('.//w:numPr', namespaces)
        num_id = ''
        ilvl = ''

        if numbering_elem is not None:
            num_id_elem = numbering_elem.find('.//w:numId', namespaces)
            ilvl_elem = numbering_elem.find('.//w:ilvl', namespaces)

            if num_id_elem is not None:
                num_id = num_id_elem.get(f'{{{namespaces["w"]}}}val', '')
            if ilvl_elem is not None:
                ilvl = ilvl_elem.get(f'{{{namespaces["w"]}}}val', '')

        # 获取文本内容
        text_elems = para.findall('.//w:t', namespaces)
        text = ''.join([t.text for t in text_elems if t.text]).strip()

        # 保存所有标题段落（包括所有可能的样式）
        if text and style_val in ['198', '43', '44', '46', '215', '']:
            paragraphs.append({
                'style': style_val,
                'numId': num_id,
                'ilvl': ilvl,
                'text': text,
                'has_numbering': bool(numbering_elem)
            })

    # 打印详细分析
    print("=" * 120)
    print("Word文档标题结构详细分析（支持1-6级）")
    print("=" * 120)
    print(f"{'样式':<10} {'编号ID':<10} {'ilvl':<8} {'推断层级':<10} {'LaTeX命令':<20} {'文本内容'}")
    print("-" * 120)

    style_names = {
        '198': '1级',
        '43': '2级',
        '44': '2级',
        '46': '3级',
        '215': '表格',
        '': '其他'
    }

    # LaTeX命令映射
    latex_commands = {
        1: ('\\section*', '一级'),
        2: ('\\subsection*', '二级'),
        3: ('\\subsubsection*', '三级'),
        4: ('\\paragraph*', '四级'),
        5: ('\\subparagraph*', '五级'),
        6: ('\\subsubparagraph*', '六级(自定义)'),
        7: ('\\customlevel{}*', '七级+(自定义)')
    }

    max_ilvl_found = 0
    for p in paragraphs:
        if p['has_numbering'] and p['ilvl'].isdigit():
            ilvl_num = int(p['ilvl']) + 1  # ilvl从0开始，层级从1开始
            max_ilvl_found = max(max_ilvl_found, ilvl_num)

    # 分析每个段落
    analyzed_structure = []
    for p in paragraphs:
        if not p['has_numbering'] and p['style'] == '215':
            continue  # 跳过表格内容

        # 推断层级
        if p['style'] == '198':
            level = 1
        elif p['has_numbering'] and p['ilvl'].isdigit():
            level = int(p['ilvl']) + 1  # ilvl=0 → 1级, ilvl=1 → 2级, etc.
        elif p['style'] in ['43', '44']:
            level = 2
        elif p['style'] == '46':
            level = 3
        else:
            continue

        cmd_info = latex_commands.get(level, ('\\customlevel*', '自定义'))
        style_name = style_names.get(p['style'], p['style'])
        ilvl_display = p['ilvl'] if p['ilvl'] else '-'

        print(f"{style_name:<10} {p['numId']:<10} {ilvl_display:<8} {level:<10} {cmd_info[0]:<20} {p['text'][:50]}")

        analyzed_structure.append({
            'level': level,
            'text': p['text'],
            'ilvl': p['ilvl']
        })

    print(f"\n发现的最大层级深度: {max_ilvl_found}级")

    # 生成层级结构
    print("\n" + "=" * 120)
    print("层级结构推断（Markdown格式）")
    print("=" * 120)

    level_marks = {
        1: '#',
        2: '##',
        3: '###',
        4: '####',
        5: '#####',
        6: '######',
        7: '#######'
    }

    for item in analyzed_structure:
        level = item['level']
        indent = "  " * (level - 1)
        mark = level_marks.get(level, '#' * level)
        print(f"{indent}{mark} {item['text']}")

    # 生成LaTeX代码建议
    print("\n" + "=" * 120)
    print("LaTeX代码建议（带层级编号）")
    print("=" * 120)

    # 跟踪当前编号
    current_numbers = [0] * 10  # 支持最多10级

    for item in analyzed_structure:
        level = item['level']
        current_numbers[level - 1] += 1

        # 重置下级编号
        for i in range(level, 10):
            current_numbers[i] = 0

        # 生成编号
        if level == 1:
            number = f"{current_numbers[0]}."
        elif level == 2:
            number = f"{current_numbers[0]}.{current_numbers[1]}."
        elif level == 3:
            number = f"{current_numbers[0]}.{current_numbers[1]}.{current_numbers[2]}."
        elif level == 4:
            number = f"{current_numbers[0]}.{current_numbers[1]}.{current_numbers[2]}.{current_numbers[3]}."
        elif level == 5:
            number = f"{current_numbers[0]}.{current_numbers[1]}.{current_numbers[2]}.{current_numbers[3]}.{current_numbers[4]}."
        elif level == 6:
            number = f"{current_numbers[0]}.{current_numbers[1]}.{current_numbers[2]}.{current_numbers[3]}.{current_numbers[4]}.{current_numbers[5]}."
        else:
            number = f"{current_numbers[0]}.{current_numbers[1]}.{current_numbers[2]}.{current_numbers[3]}.{current_numbers[4]}.{current_numbers[5]}.{current_numbers[6]}."

        # 生成LaTeX命令
        if level == 1:
            print(f'\\section*{{{number} {item["text"]}}}')
        elif level == 2:
            print(f'\\subsection*{{{number} {item["text"]}}}')
        elif level == 3:
            print(f'\\subsubsection*{{{number} {item["text"]}}}')
        elif level == 4:
            print(f'\\paragraph*{{{number} {item["text"]}}}')
        elif level == 5:
            print(f'\\subparagraph*{{{number} {item["text"]}}}')
        elif level == 6:
            print('% 六级标题需要自定义命令:')
            print('% 在导言区添加: \\newcommand{\\subsubparagraph}[1]{\\noindent\\textbf{#1}\\par}')
            print(f'\\subsubparagraph*{{{number} {item["text"]}}}')
        else:
            print(f'% {level}级标题需要自定义命令')
            print(f'% {item["text"]}')

    # 打印统计信息
    print("\n" + "=" * 120)
    print("统计信息")
    print("=" * 120)

    from collections import Counter
    level_count = Counter([item['level'] for item in analyzed_structure])

    for level in sorted(level_count.keys()):
        cmd_info = latex_commands.get(level, ('未知', '未知'))
        print(f"{cmd_info[1]}标题: {level_count[level]}个")

    # 如果需要六级以上标题，给出建议
    if max_ilvl_found >= 6:
        print("\n" + "=" * 120)
        print("⚠️  警告：文档包含6级或更深层的标题")
        print("=" * 120)
        print("LaTeX标准article文档类只支持到5级标题（\\subparagraph）")
        print("如需使用6级标题，请在文档导言区添加以下自定义命令：")
        print()
        print(r"\usepackage{titlesec}")
        print()
        print(r"% 定义六级标题")
        print(r"\titleformat{\\paragraph}")
        print(r"  {\\normalsize\\bfseries}")
        print(r"  {\\theparagraph}")
        print(r"  {1em}")
        print(r"  {}")
        print()
        print(r"\newcounter{subsubparagraph}")
        print(r"\newcommand{\\subsubparagraph}[1]{\\noindent\\textbf{#1}\\par}")
        print()
        print("或者考虑重构文档结构，减少层级深度。")

    return analyzed_structure


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 analyze_docx_structure_full.py <docx文件路径>")
        print("\n示例:")
        print("  python3 analyze_docx_structure_full.py templates/document.docx")
        sys.exit(1)

    docx_path = sys.argv[1]
    analyze_docx_structure(docx_path)
