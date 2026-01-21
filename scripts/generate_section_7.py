#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试计划文档 第7章（需求的可追踪性）的追踪表
使用 tabularray (longtblr) 生成完整的表格代码
修复问题：
1. 移除 SetCell 和 Chunking 逻辑，允许表格自然分页，彻底解决页码被覆盖问题
2. 移除全局 hlines，使用 \cline{3-6} 仅在右侧画线，左侧 Metric/序号列无横线，实现“连续表”视觉效果
3. 采用 valign=t (顶部对齐)，确保长文本显示自然
"""

import math
from pathlib import Path
import utils


def split_text_by_length(text, length=50):
    """
    Split text into chunks of specified length.
    Returns a list of strings.
    """
    if not text:
        return []
    return [text[i:i+length] for i in range(0, len(text), length)]


def collect_plan_items(data_dir: Path):
    rows = []

    metric_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir() and d.name.endswith("-test-metric")])
    for metric_dir in metric_dirs:
        metric_files = list(metric_dir.glob("*metric.yaml"))
        if not metric_files:
            continue

        metric_data = utils.load_yaml(metric_files[0]) or {}
        metric_index = str(metric_data.get("index") or metric_dir.name.split("-")[0]).strip()
        metric_title = (metric_data.get("title") or "").strip()
        metric_content = (metric_data.get("content") or "").strip()
        metric_cell = metric_content or metric_index

        module_dirs = sorted([d for d in metric_dir.iterdir() if d.is_dir() and d.name.endswith("-module")])
        for module_idx, module_dir in enumerate(module_dirs, start=1):
            item_dirs = sorted([d for d in module_dir.iterdir() if d.is_dir() and "item" in d.name])
            for item_idx, item_dir in enumerate(item_dirs, start=1):
                plan_file = item_dir / "plan.yaml"
                if not plan_file.exists():
                    continue
                plan_data = utils.parse_plan_yaml(plan_file)
                if not plan_data:
                    continue
                section = f"4.2.{metric_index}.{module_idx}.{item_idx}"
                rows.append(
                    {
                        "metric_index": metric_index,
                        "metric_cell": metric_cell,
                        "metric_title": metric_title,
                        "metric_content": metric_content,
                        "requirement": plan_data.get("需求追踪关系", ""),
                        "srs_chapter": plan_data.get("需规章节", ""),
                        "test_item_name": plan_data.get("测试项名称", ""),
                        "test_item_ident": plan_data.get("标识", ""),
                        "section": section,
                    }
                )
    return rows


def generate_forward_table(items):
    """
    生成表1：xxxxxxxxxx与需求规格说明以及测试项的追踪关系
    Columns:
    1. 序号 (Seq)
    2. xxxxx (Metric Content)
    3. 需求名称/标识 (Req)
    4. 需求规格说明章节号 (SRS)
    5. 测试项名称/标识 (Test Item)
    6. 本文档的章节号 (Section)
    """
    
    rows_tex = []
    
    # Process items grouping by Metric
    i = 0
    seq = 1
    
    while i < len(items):
        j = i
        metric_index = items[i]["metric_index"]
        while j < len(items) and items[j]["metric_index"] == metric_index:
            j += 1
        
        group = items[i:j]
        metric_content = group[0].get("metric_content") or group[0].get("metric_cell") or ""
        
        # Split metric content into chunks
        metric_chunks = split_text_by_length(metric_content, 60)
        
        num_rows = max(len(metric_chunks), len(group))
        if num_rows == 0:
            num_rows = 1
            
        for k in range(num_rows):
            if k == 0:
                seq_str = str(seq)
            else:
                seq_str = ""
            
            if k < len(metric_chunks):
                metric_tex = utils.escape_latex(metric_chunks[k])
            else:
                metric_tex = ""
            
            if k < len(group):
                item = group[k]
                req = utils.escape_latex(item["requirement"])
                srs = utils.escape_latex(item["srs_chapter"])
                test_item_name = utils.escape_latex(item["test_item_name"])
                test_item_ident = utils.escape_latex(item["test_item_ident"])
                test_item = f"{test_item_name}（{test_item_ident}）"
                sec = utils.escape_latex(item["section"])
            else:
                req = ""
                srs = ""
                test_item = ""
                sec = ""
            
            # Row construction
            if k == 0:
                c1 = f"{{{seq_str}}}"
            else:
                c1 = ""
            
            c2 = f"{{{metric_tex}}}"
            
            line = f"{c1} & {c2} & {req} & {srs} & {test_item} & {sec} \\\\"
            
            if k == num_rows - 1:
                line += r" \hline"
            elif k < len(group) - 1:
                line += r" \cline{3-6}"
            elif k == len(group) - 1:
                line += r" \cline{3-6}"
            else:
                pass
            
            rows_tex.append(line)
        
        i = j
        seq += 1

    body = "\n".join(rows_tex)

    latex = f"""
{{\\settablespacing
\\begin{{longtblr}}[
  theme=gjb,
  caption={{xxxxxxxxxx与需求规格说明以及测试项的追踪关系}},
  label={{tbl:plan-trace}},
]{{
  colspec={{|Q[c,t,0.8cm]|Q[l,t,3.0cm]|Q[l,t,2.4cm]|Q[c,t,1.8cm]|Q[l,t,5.0cm]|Q[c,t,1.4cm]|}},
  rowhead=2,
  % Remove global hlines to avoid lines crossing the Metric column
  % hlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},
  row{{1,2}}={{font=\\xiaowuhei}},
}}
\\hline
\\SetCell[r=2]{{c}} 序号 & \\SetCell[r=2]{{c}} xxxxx & \\SetCell[c=2]{{c}} 需求规格说明 & & \\SetCell[c=2]{{c}} 测试大纲 & \\\\
\\hline
 & & 需求名称/标识 & 需求规格说明章节号 & 测试项名称/标识 & 本文档的章节号 \\\\
\\hline
{body}
\\end{{longtblr}}
}}
"""
    return latex


def generate_reverse_table(items):
    """
    生成表2：xxxxxxxxxx与需求规格说明以及测试项的逆向追踪关系
    Columns:
    1. 序号 (Seq)
    2. xxxxx (Metric Content)
    3. 测试项名称/标识 (Test Item)
    4. 本文档的章节号 (Section)
    5. 需求名称/标识 (Req)
    6. 需求规格说明章节号 (SRS)
    """
    
    rows_tex = []
    
    i = 0
    seq = 1
    
    while i < len(items):
        j = i
        metric_index = items[i]["metric_index"]
        while j < len(items) and items[j]["metric_index"] == metric_index:
            j += 1
        
        group = items[i:j]
        metric_content = group[0].get("metric_content") or group[0].get("metric_cell") or ""
        
        # Split metric content into chunks
        metric_chunks = split_text_by_length(metric_content, 60)
        
        num_rows = max(len(metric_chunks), len(group))
        if num_rows == 0:
            num_rows = 1
            
        for k in range(num_rows):
            if k == 0:
                seq_str = str(seq)
            else:
                seq_str = ""
            
            if k < len(metric_chunks):
                metric_tex = utils.escape_latex(metric_chunks[k])
            else:
                metric_tex = ""
            
            if k < len(group):
                item = group[k]
                req = utils.escape_latex(item["requirement"])
                srs = utils.escape_latex(item["srs_chapter"])
                test_item_name = utils.escape_latex(item["test_item_name"])
                test_item_ident = utils.escape_latex(item["test_item_ident"])
                test_item = f"{test_item_name}（{test_item_ident}）"
                sec = utils.escape_latex(item["section"])
            else:
                req = ""
                srs = ""
                test_item = ""
                sec = ""
            
            if k == 0:
                c1 = f"{{{seq_str}}}"
            else:
                c1 = "" # Seq only on first row
            
            # Metric chunk on every row (if available)
            c2 = f"{{{metric_tex}}}"
            
            line = f"{c1} & {c2} & {test_item} & {sec} & {req} & {srs} \\\\"
            
            if k == num_rows - 1:
                line += r" \hline"
            elif k < len(group) - 1:
                line += r" \cline{3-6}"
            elif k == len(group) - 1:
                line += r" \cline{3-6}"
            else:
                pass
            
            rows_tex.append(line)
        
        i = j
        seq += 1

    body = "\n".join(rows_tex)

    latex = f"""
{{\\settablespacing
\\begin{{longtblr}}[
  theme=gjb,
  caption={{xxxxxxxxxx与需求规格说明以及测试项的逆向追踪关系}},
  label={{tbl:plan-trace-rev}},
]{{
  colspec={{|Q[c,t,0.8cm]|Q[l,t,3.0cm]|Q[l,t,5.2cm]|Q[c,t,1.4cm]|Q[l,t,2.0cm]|Q[c,t,1.6cm]|}},
  rowhead=2,
  % Remove global hlines
  row{{1,2}}={{font=\\xiaowuhei}},
}}
\\hline
\\SetCell[r=2]{{c}} 序号 & \\SetCell[r=2]{{c}} xxxxx & \\SetCell[c=2]{{c}} 测试大纲 & & \\SetCell[c=2]{{c}} 需求规格说明 & \\\\
\\hline
 & & 测试项名称/标识 & 本文档的章节号 & 需求名称/标识 & 需求规格说明章节号 \\\\
\\hline
{body}
\\end{{longtblr}}
}}
"""
    return latex


def main():
    repo_root = utils.get_project_root()
    data_dir = repo_root / "data"
    out_dir = repo_root / "output" / "test_plan" / "chapters"

    items = collect_plan_items(data_dir)
    
    forward_table = generate_forward_table(items)
    reverse_table = generate_reverse_table(items)
    
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "chapter7_forward_table.tex").write_text(forward_table, encoding="utf-8")
    (out_dir / "chapter7_reverse_table.tex").write_text(reverse_table, encoding="utf-8")

    print(f"✅ 第七章追踪表已生成到: {out_dir}")
    print("  - chapter7_forward_table.tex")
    print("  - chapter7_reverse_table.tex")


if __name__ == "__main__":
    main()
