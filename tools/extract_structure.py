#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取Word文档的章节结构，保留正确的章节编号
"""

from docx import Document
import re

def is_heading(paragraph):
    """判断是否为标题"""
    if paragraph.style.name.startswith('Heading'):
        return True
    return False

def get_heading_level(paragraph):
    """获取标题级别"""
    match = re.search(r'Heading (\d+)', paragraph.style.name)
    if match:
        return int(match.group(1))
    return 0

def extract_structure(docx_path):
    """提取文档结构"""
    doc = Document(docx_path)

    structure = []
    for para in doc.paragraphs:
        if is_heading(para):
            level = get_heading_level(para)
            text = para.text.strip()
            if text:
                structure.append({
                    'level': level,
                    'text': text
                })

    return structure

def print_structure(structure):
    """打印结构"""
    print("=" * 80)
    print("Word文档章节结构：")
    print("=" * 80)

    for item in structure:
        indent = "  " * (item['level'] - 1)
        level_marker = f"L{item['level']}"
        print(f"{indent}[{level_marker}] {item['text']}")

    print("\n" + "=" * 80)
    print("章节编号列表（纯文本）：")
    print("=" * 80)

    for item in structure:
        print(item['text'])

if __name__ == "__main__":
    docx_path = "templates/9月节点-测试大纲-0928.docx"
    structure = extract_structure(docx_path)
    print_structure(structure)
