#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试计划文档 第7章（需求的可追踪性）的追踪表
使用 tabularray (longtblr) 生成完整的表格代码
修复问题：
1. 移除 SetCell 和 Chunking 逻辑，允许表格自然分页，彻底解决页码被覆盖问题
2. 移除全局 hlines，使用 \cline{3-6} 仅在右侧画线，左侧 Metric/序号列无横线，实现“连续表”视觉效果
3. 采用 valign=t (顶部对齐)，确保长文本显示自然
4. 参照 Chapter 1 Table 1 的逻辑，对 Test Items 进行分组，而不是强制切分 Metric 文本。
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


def generate_table_rows(items, table_type="forward"):
    """
    Generate table rows using "Item Chunking" strategy similar to Chapter 1.2 Table 1.
    table_type: "forward" or "reverse"
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
        
        # New "Slot-based" Strategy:
        # 1. Calculate required slots for Text.
        # 2. Extend Item list to match Text slots (Visual Merge).
        # 3. Chunk the extended lists for pagination.
        # 4. Control borders to create "Same Box" illusion.
        
        # Calibration: How many chars fit in one Item's height?
        # Metric col width 3cm ~= 12 chars/line.
        # Avg Item height ~= 3-4 lines.
        # So 1 Item Slot ~= 40 chars.
        CHARS_PER_SLOT = 40
        BLOCK_SIZE = 4 # Max rows per physical block (safe for page break)
        
        total_text_len = len(metric_content)
        n_items = len(group)
        n_text_slots = math.ceil(total_text_len / CHARS_PER_SLOT)
        
        # The grid must be at least as long as items, and long enough for text
        total_slots = max(n_items, n_text_slots)
        
        # Prepare Text Parts
        # We split text evenly across all slots to maintain consistent spacing
        text_parts = []
        if total_slots > 0:
            # Distribute text evenly? Or fill linearly?
            # Filling linearly is safer for reading order.
            # But evenly is better for alignment?
            # Let's use linear filling based on the calculated capacity, 
            # but allow the last slot to take the rest.
            # Actually, split_text_by_length is fine, but we need exactly total_slots parts.
            
            # Better: Linear split
            avg_chunk_len = math.ceil(total_text_len / total_slots)
            # Ensure avg_chunk_len is at least 1
            if avg_chunk_len < 1: avg_chunk_len = 1
            
            for k in range(total_slots):
                start = k * avg_chunk_len
                end = min((k + 1) * avg_chunk_len, total_text_len)
                if start < total_text_len:
                    text_parts.append(metric_content[start:end])
                else:
                    text_parts.append("")
        else:
            text_parts = [""]

        # Prepare Extended Items
        extended_items = []
        for k in range(total_slots):
            if k < n_items:
                extended_items.append(group[k])
            else:
                # Clone the last item
                extended_items.append(group[-1])
        
        # Chunking
        # We process `total_slots` in blocks of `BLOCK_SIZE`
        
        current_slot = 0
        while current_slot < total_slots:
            # Determine block size
            this_block_size = min(BLOCK_SIZE, total_slots - current_slot)
            
            # Collect data for this block
            block_text_parts = text_parts[current_slot : current_slot + this_block_size]
            block_items = extended_items[current_slot : current_slot + this_block_size]
            
            # Join text parts for this block (Metric Cell Content)
            # We join them because in this block they are one merged cell
            block_metric_text = "".join(block_text_parts)
            block_metric_text_esc = utils.escape_latex(block_metric_text)
            
            # Generate Rows
            for k in range(this_block_size):
                global_idx = current_slot + k
                item = block_items[k]
                
                # Check if this item is a continuation of the previous one (Visual Merge)
                # Logic: If global_idx > 0 and item == extended_items[global_idx - 1]
                # But we need to compare content or ID.
                # Since we cloned the object, identity comparison might work, 
                # but safer to compare unique ID if available, or just index logic.
                
                is_continuation = False
                if global_idx > 0:
                    prev_item = extended_items[global_idx - 1]
                    # We can assume if it's the SAME object reference, it's a continuation.
                    # In our loop above: `extended_items.append(group[-1])` uses same ref.
                    # For `group[k]`, they are distinct objects.
                    if item is prev_item:
                        is_continuation = True
                
                # Check if next item is same (for border logic)
                is_next_same = False
                if global_idx < total_slots - 1:
                    next_item = extended_items[global_idx + 1]
                    if next_item is item:
                        is_next_same = True
                
                # Content Generation
                if is_continuation:
                    # Empty content for continued item
                    req = ""
                    srs = ""
                    test_item = ""
                    sec = ""
                else:
                    # New Item
                    req = utils.escape_latex(item["requirement"])
                    srs = utils.escape_latex(item["srs_chapter"])
                    n_tex = utils.escape_latex(item["test_item_name"])
                    i_tex = utils.escape_latex(item["test_item_ident"])
                    test_item = f"{n_tex}（{i_tex}）"
                    sec = utils.escape_latex(item["section"])
                
                # Row Commands
                row_cmd = r"\\"
                
                # Col 1: Seq (Only first row of first block)
                if k == 0 and current_slot == 0:
                    c1 = f"\\SetCell[r={this_block_size}]{{c,t}} {{{seq}}}"
                elif k == 0:
                     # First row of subsequent blocks: Empty placeholder for merged cell?
                     # No, we can't merge Seq across blocks (pages).
                     # So subsequent blocks have empty Seq cell.
                     # But we want visual continuity.
                     # We will Merge vertically within block, content empty.
                     c1 = f"\\SetCell[r={this_block_size}]{{c,t}} {{}}"
                else:
                    c1 = ""
                
                # Col 2: Metric (Merged per block)
                if k == 0:
                    c2 = f"\\SetCell[r={this_block_size}]{{l,t}} {{{block_metric_text_esc}}}"
                else:
                    c2 = ""
                
                # Line Assembly
                line = f"{c1} & {c2} & {req} & {srs} & {test_item} & {sec} {row_cmd}"
                
                # Horizontal Lines Logic
                # 1. Metric Col (2) & Seq Col (1):
                #    - Only draw bottom line if this is the VERY LAST row of the Metric Group.
                #    - i.e. global_idx == total_slots - 1.
                # 2. Item Cols (3-6):
                #    - Draw bottom line if `not is_next_same`.
                #    - i.e. End of an Item's scope.
                #    - Also draw if End of Table (implied by End of Metric Group).
                
                is_last_row_of_metric = (global_idx == total_slots - 1)
                
                if is_last_row_of_metric:
                    # End of everything -> Full Line
                    line += r" \hline"
                else:
                    # Not end of Metric Group.
                    # Metric/Seq cols get NO line (to look continuous).
                    # Check Item cols:
                    if not is_next_same:
                        # Item changed (or real item ended) -> Draw partial line
                        line += r" \cline{3-6}"
                    else:
                        # Item continues to next row -> NO line
                        pass
                
                rows_tex.append(line)

            current_slot += this_block_size
        
        i = j
        seq += 1
        
    return "\n".join(rows_tex)


def generate_forward_table(items):
    body = generate_table_rows(items, "forward")
    latex = f"""
{{\\settablespacing
\\begin{{longtblr}}[
  theme=gjb,
  caption={{xxxxxxxxxx与需求规格说明以及测试项的追踪关系}},
  label={{tbl:plan-trace}},
]{{
  colspec={{|Q[c,t,0.8cm]|Q[l,t,3.0cm]|Q[l,t,2.4cm]|Q[c,t,1.8cm]|Q[l,t,5.0cm]|Q[c,t,1.4cm]|}},
  rowhead=2,
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
    body = generate_table_rows(items, "reverse")
    latex = f"""
{{\\settablespacing
\\begin{{longtblr}}[
  theme=gjb,
  caption={{xxxxxxxxxx与需求规格说明以及测试项的逆向追踪关系}},
  label={{tbl:plan-trace-rev}},
]{{
  colspec={{|Q[c,t,0.8cm]|Q[l,t,3.0cm]|Q[l,t,5.2cm]|Q[c,t,1.4cm]|Q[l,t,2.0cm]|Q[c,t,1.6cm]|}},
  rowhead=2,
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
