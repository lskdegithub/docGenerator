#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接提取Word文档的文本和段落结构
不依赖外部库，直接解析XML
"""

import zipfile
import xml.etree.ElementTree as ET
import re

def extract_text_from_docx(docx_path):
    """从docx文件中提取所有段落文本"""
    # 打开docx文件（它是一个zip文件）
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
        text = ''.join([t.text for t in text_elems if t.text])

        if text.strip():
            paragraphs.append({
                'style': style,
                'text': text.strip()
            })

    return paragraphs

def analyze_structure(paragraphs):
    """分析文档结构，识别标题"""
    print("=" * 80)
    print("Word文档段落分析")
    print("=" * 80)

    # 常见的标题样式模式
    heading_patterns = [
        (r'^1$', '1级标题'),
        (r'^2$', '2级标题'),
        (r'^\d+\.', '编号标题'),
        (r'Heading', '内置标题'),
    ]

    for i, para in enumerate(paragraphs[:100]):  # 只看前100个段落
        text = para['text']
        style = para['style']

        # 判断是否可能是标题
        is_likely_title = False

        # 检查是否以数字开头（如"1. "、"1.1 "等）
        if re.match(r'^\d+\.\d*\s+', text):
            is_likely_title = True

        # 检查是否是关键标题词
        title_keywords = ['范围', '标识', '系统概述', '文档概述', '引用文档',
                         '软件测试环境', '测试现场', '测试环境概述', '软件项',
                         '硬件和固件项', '其他材料', '安装', '测试', '控制']

        if any(keyword in text for keyword in title_keywords):
            is_likely_title = True

        if is_likely_title or style.startswith('Heading'):
            marker = "★ " if is_likely_title else "  "
            print(f"{marker}[{style}] {text}")

    print("\n" + "=" * 80)
    print("完整的标题列表（手动分析）")
    print("=" * 80)

    # 只打印看起来像标题的行
    for para in paragraphs:
        text = para['text']
        # 匹配 "数字. 标题" 或 "数字.数字. 标题" 格式
        if re.match(r'^\d+(\.\d+)*\s+', text):
            print(text)

if __name__ == "__main__":
    docx_path = "templates/9月节点-测试大纲-0928.docx"
    paragraphs = extract_text_from_docx(docx_path)
    analyze_structure(paragraphs)
