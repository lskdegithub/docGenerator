#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import yaml
from pathlib import Path

def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).resolve().parents[1]

def load_yaml(file_path: Path):
    """加载YAML文件，处理中文编码和中文冒号"""
    try:
        content = file_path.read_text(encoding="utf-8")
        content = content.replace("：", ":")
        return yaml.safe_load(content)
    except Exception as e:
        print(f"错误：无法读取文件 {file_path}: {e}")
        return None

def escape_latex(text: str) -> str:
    """转义LaTeX特殊字符，并处理长单词断行"""
    text = str(text or "")
    text = text.replace("\\", "\\textbackslash ")
    text = text.replace("&", "\\&")
    text = text.replace("%", "\\%")
    text = text.replace("$", "\\$")
    text = text.replace("#", "\\#")
    text = text.replace("_", "\\_\\allowbreak ")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    text = text.replace("~", "\\textasciitilde ")
    text = text.replace("^", "\\textasciicircum ")
    
    def break_long(match: re.Match) -> str:
        s = match.group(0)
        chunk = 10
        return r"\allowbreak ".join([s[i:i + chunk] for i in range(0, len(s), chunk)])

    # 对长单词进行断行处理 (排除已经被转义的命令)
    text = re.sub(r"(?<!\\)[A-Za-z0-9]{20,}", break_long, text)
    return " ".join(text.split())


def parse_plan_yaml(file_path: Path):
    """解析plan.yaml文件，返回结构化数据"""
    try:
        content = file_path.read_text(encoding='utf-8')

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
            '需规章节': '',
        }

        def pick(pattern: str, flags=0):
            m = re.search(pattern, content, flags)
            return m.group(1).strip() if m else ""

        data['测试项名称'] = pick(r'测试项名称[：:]\s*(.+?)(?:\n|$)')
        data['标识'] = pick(r'标识[：:]\s*(.+?)(?:\n|$)')
        data['测试要求'] = pick(r'测试要求[：:]\s*(.+?)(?:\n\w+\s*[：:]|$)', re.DOTALL)
        
        # 策略和方法
        strategy_match = re.search(
            r'测试策略与方法[：:]\s*\n\s*-[ ]*测试策略[：:]\s*(.+?)\n\s*-[ ]*测试方法[：:]\s*(.+?)(?=\n\n|\n\w+\s*[：:]|$)',
            content, re.DOTALL
        )
        if strategy_match:
            data['测试策略'] = strategy_match.group(1).strip()
            data['测试方法'] = strategy_match.group(2).strip()

        # 假设和约束
        constraint_match = re.search(
            r'假设与约束[：:]\s*\n\s*-[ ]*假设[：:]\s*(.+?)\n\s*-[ ]*约束[：:]\s*(.+?)(?=\n\n|\n\w+\s*[：:]|$)',
            content, re.DOTALL
        )
        if constraint_match:
            data['假设'] = constraint_match.group(1).strip()
            data['约束'] = constraint_match.group(2).strip()

        data['优先级'] = pick(r'优先级[：:]\s*(.+?)(?:\n|$)')
        data['测试终止条件'] = pick(r'测试终止条件[：:]\s*(.+?)(?:\n\w+\s*[：:]|$)', re.DOTALL)
        data['需求追踪关系'] = pick(r'(?:需求追踪关系|需求的追踪关系)[：:]\s*(.+?)(?:\n|$)')
        data['需规章节'] = pick(r'需规章节[：:]\s*(.+?)(?:\n|$)')

        return data
    except Exception as e:
        print(f"错误：解析文件 {file_path} 失败: {e}")
        return None
