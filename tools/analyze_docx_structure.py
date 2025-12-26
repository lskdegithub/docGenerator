#!/usr/bin/env python3
"""
精确分析Word文档的标题层级结构
通过分析段落的编号级别(numId, ilvl)和样式来确定层级关系
"""

import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

def analyze_docx_structure(docx_path):
    """分析Word文档的完整结构"""

    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        # 读取文档内容
        xml_content = zip_ref.read('word/document.xml')

    # 解析XML
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

        # 只保存有文本且是标题样式的段落
        if text and style_val in ['198', '43', '44', '46', '215']:
            paragraphs.append({
                'style': style_val,
                'numId': num_id,
                'ilvl': ilvl,
                'text': text
            })

    # 打印分析结果
    print("=" * 100)
    print("Word文档标题结构详细分析")
    print("=" * 100)
    print(f"{'样式':<8} {'编号ID':<10} {'级别':<8} {'文本内容'}")
    print("-" * 100)

    style_names = {
        '198': '1级标题',
        '43': '2级标题',
        '44': '2级标题',
        '46': '3级标题',
        '215': '表格内容'
    }

    for p in paragraphs:
        style_name = style_names.get(p['style'], p['style'])
        ilvl_display = p['ilvl'] if p['ilvl'] else '-'
        print(f"{style_name:<8} {p['numId']:<10} {ilvl_display:<8} {p['text'][:60]}")

    print("\n" + "=" * 100)
    print("层级结构推断")
    print("=" * 100)

    # 按编号级别和样式推断层级
    current_structure = []
    for p in paragraphs:
        if p['style'] == '198':  # 1级标题
            level = 1
        elif p['style'] in ['43', '44']:  # 2级标题
            # 检查是否有ilvl，如果有ilvl=1则是真正的2级
            if p['ilvl'] == '1':
                level = 2
            elif p['ilvl'] == '2':
                level = 3
            else:
                # 根据上下文判断
                level = 2
        elif p['style'] == '46':  # 3级标题
            level = 3
        else:
            continue

        indent = "  " * (level - 1)
        level_mark = {1: '#', 2: '##', 3: '###'}[level]
        print(f"{indent}{level_mark} {p['text']}")

    print("\n" + "=" * 100)
    print("LaTeX代码建议")
    print("=" * 100)

    for p in paragraphs:
        if p['style'] == '198':
            print(f'\\section*{{{p["text"]}}}')
        elif p['style'] in ['43', '44']:
            # 根据ilvl判断是subsection还是subsubsection
            if p['ilvl'] == '2':
                print(f'  \\subsubsection*{{{p["text"]}}}')
            else:
                print(f'\\subsection*{{{p["text"]}}}')
        elif p['style'] == '46':
            print(f'  \\subsubsection*{{{p["text"]}}}')


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 analyze_docx_structure.py <docx文件路径>")
        sys.exit(1)

    docx_path = sys.argv[1]
    analyze_docx_structure(docx_path)
