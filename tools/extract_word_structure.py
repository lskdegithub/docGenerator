#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word文档章节结构提取工具

用途：从Word文档中准确提取章节层级结构，避免pandoc转换导致的编号错乱问题

使用方法：
    python3 extract_word_structure.py <word文件路径>

输出：
    - 章节层级结构
    - 样式代码
    - LaTeX结构建议
"""

import zipfile
import xml.etree.ElementTree as ET
import sys
import json

def extract_word_structure(docx_path):
    """提取Word文档的章节结构"""

    # 打开docx文件
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        # 读取document.xml
        xml_content = zip_ref.read('word/document.xml')

    # 解析XML
    tree = ET.fromstring(xml_content)

    # 定义命名空间
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }

    # 提取所有段落
    paragraphs = []
    for para in tree.findall('.//w:p', namespaces):
        # 获取段落样式
        style_elem = para.find('.//w:pStyle', namespaces)
        style = style_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if style_elem is not None else ''

        # 获取段落文本
        text_elems = para.findall('.//w:t', namespaces)
        text = ''.join([t.text for t in text_elems if t.text]).strip()

        if text and style in ['198', '43', '44', '46', '215', '221']:
            paragraphs.append({
                'style': style,
                'text': text,
                'level': determine_level(style)
            })

    return paragraphs

def determine_level(style):
    """根据样式代码确定层级"""
    level_map = {
        '198': 1,  # 1级标题
        '43': 2,   # 2级标题
        '44': 2,   # 2级标题
        '46': 3,   # 3级标题
        '215': 9,  # 表格内容（忽略）
        '221': 3,  # 3级标题
    }
    return level_map.get(style, 0)

def print_structure(paragraphs):
    """打印结构化输出"""

    print("=" * 80)
    print("Word文档章节结构")
    print("=" * 80)

    for para in paragraphs:
        if para['level'] < 9:  # 不显示表格内容
            indent = "  " * (para['level'] - 1)
            level_marker = f"L{para['level']}"
            print(f"{indent}[{level_marker}] [{para['style']}] {para['text']}")

    print("\n" + "=" * 80)
    print("LaTeX结构建议")
    print("=" * 80)

    current_section = 0
    current_subsection = 0
    current_subsubsection = 0

    for para in paragraphs:
        if para['level'] == 1:
            current_section += 1
            print(f"\\section*{{{current_section}. {para['text']}}}")
        elif para['level'] == 2:
            current_subsection += 1
            print(f"  \\subsection*{{{current_section}.{current_subsection} {para['text']}}}")
        elif para['level'] == 3:
            current_subsubsection += 1
            print(f"    \\subsubsection*{{{current_section}.{current_subsection}.{current_subsubsection} {para['text']}}}")

def export_json(paragraphs, output_path):
    """导出为JSON格式"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(paragraphs, f, ensure_ascii=False, indent=2)
    print(f"\n结构已导出到: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 extract_word_structure.py <word文件路径>")
        print("示例: python3 extract_word_structure.py templates/document.docx")
        sys.exit(1)

    docx_path = sys.argv[1]

    try:
        paragraphs = extract_word_structure(docx_path)
        print_structure(paragraphs)

        # 可选：导出为JSON
        # export_json(paragraphs, 'word_structure.json')

    except FileNotFoundError:
        print(f"错误：文件不存在 - {docx_path}")
        sys.exit(1)
    except Exception as e:
        print(f"错误：{str(e)}")
        sys.exit(1)
