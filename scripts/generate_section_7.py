#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path
import yaml


def load_yaml(file_path: Path):
    try:
        content = file_path.read_text(encoding="utf-8")
        content = content.replace("：", ":")
        return yaml.safe_load(content)
    except Exception as e:
        print(f"错误：无法读取文件 {file_path}: {e}")
        return None


def parse_plan_yaml(file_path: Path):
    try:
        content = file_path.read_text(encoding="utf-8")

        data = {
            "测试项名称": "",
            "标识": "",
            "需求追踪关系": "",
            "需规章节": "",
        }

        def pick(pattern: str):
            m = re.search(pattern, content)
            return m.group(1).strip() if m else ""

        data["测试项名称"] = pick(r"测试项名称[：:]\s*(.+?)(?:\n|$)")
        data["标识"] = pick(r"标识[：:]\s*(.+?)(?:\n|$)")
        data["需求追踪关系"] = pick(r"(?:需求追踪关系|需求的追踪关系)[：:]\s*(.+?)(?:\n|$)")
        data["需规章节"] = pick(r"需规章节[：:]\s*(.+?)(?:\n|$)")

        return data
    except Exception as e:
        print(f"错误：解析文件 {file_path} 失败: {e}")
        return None


def escape_latex(text: str) -> str:
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

    text = re.sub(r"(?<!\\)[A-Za-z0-9]{20,}", break_long, text)
    return " ".join(text.split())


def collect_plan_items(data_dir: Path):
    rows = []

    metric_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir() and d.name.endswith("-test-metric")])
    for metric_dir in metric_dirs:
        metric_files = list(metric_dir.glob("*metric.yaml"))
        if not metric_files:
            continue

        metric_data = load_yaml(metric_files[0]) or {}
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
                plan_data = parse_plan_yaml(plan_file)
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


def split_text_smart(text, max_chars=300):
    text = str(text or "")
    if not text:
        return [""]
    
    # Simple chunking by length, respecting some punctuation could be better but length is primary constraint
    chunks = []
    current_pos = 0
    text_len = len(text)
    
    while current_pos < text_len:
        # If remaining text fits, take it all
        if text_len - current_pos <= max_chars:
            chunks.append(text[current_pos:])
            break
            
        # Try to find a split point
        end_pos = min(current_pos + max_chars, text_len)
        
        # Look for punctuation near the end
        search_window = text[max(current_pos, end_pos - 50):end_pos]
        # Punctuation: 。！？；，、
        match = re.search(r'[。！？；，、\.\!\?\;\,]\s*$', search_window)
        
        if match:
            # Split after punctuation
            real_end = max(current_pos, end_pos - 50) + match.end()
        else:
            # Hard split
            real_end = end_pos
            
        chunks.append(text[current_pos:real_end])
        current_pos = real_end
        
    return chunks

def build_rows_generic(items, is_reverse=False):
    out = []
    i = 0
    seq_counter = 1
    
    while i < len(items):
        j = i
        metric_index_str = items[i]["metric_index"]
        while j < len(items) and items[j]["metric_index"] == metric_index_str:
            j += 1
        group = items[i:j]
        
        metric_content = group[0].get("metric_content") or group[0].get("metric_cell") or ""
        
        # Split metric content into manageable chunks
        text_chunks = split_text_smart(metric_content, max_chars=300)
        
        # We need to map test items (group) to text chunks.
        # Case 1: More text chunks than items (or equal)
        # We need to create extra rows for the extra text chunks.
        
        # Case 2: More items than text chunks
        # We need to distribute items among text chunks.
        
        mapped_rows = [] # List of (text_chunk, list_of_items)
        
        if len(text_chunks) >= len(group):
            # One item per chunk for the first N chunks
            for k, item in enumerate(group):
                mapped_rows.append((text_chunks[k], [item]))
            # Remaining chunks get empty items
            for k in range(len(group), len(text_chunks)):
                mapped_rows.append((text_chunks[k], []))
        else:
            # More items than chunks. Distribute items evenly.
            # E.g. 5 items, 2 chunks -> [3, 2]
            n_items = len(group)
            n_chunks = len(text_chunks)
            base_size = n_items // n_chunks
            remainder = n_items % n_chunks
            
            current_item_idx = 0
            for k in range(n_chunks):
                size = base_size + (1 if k < remainder else 0)
                chunk_items = group[current_item_idx : current_item_idx + size]
                mapped_rows.append((text_chunks[k], chunk_items))
                current_item_idx += size

        # Now generate LaTeX rows
        try:
            display_seq = str(int(metric_index_str))
        except:
            display_seq = metric_index_str
            
        for chunk_idx, (txt, sub_items) in enumerate(mapped_rows):
            # Determine row span for this chunk
            # If sub_items is empty, it's an extra row -> r=1
            # If sub_items has M items, r=M
            r_span = max(1, len(sub_items))
            
            c_tex = escape_latex(txt)
            if chunk_idx > 0 and not txt.startswith("（续）"):
                 c_tex = r"（续）" + c_tex
            
            # Generate rows for this chunk
            if not sub_items:
                # Extra row with empty test item slots
                # Only left side has content
                seq_cell = f"\\SetCell[r=1]{{c,m}} " # Empty seq cell unless it's the very first row of the whole metric?
                # Actually, "Seq" column should span ALL rows of this metric.
                # But longtblr doesn't support spanning across pages easily if we define it once at top.
                # However, if we split into multiple chunks, visual continuity is better if we repeat Seq or leave empty.
                # Standard practice: First chunk has Seq, others empty.
                
                if chunk_idx == 0:
                    seq_str = display_seq
                else:
                    seq_str = "" 
                    
                # Wait, if we use separate \SetCell for each chunk, the vertical alignment of Seq number might be off 
                # if we want it centered across ALL chunks.
                # But since we are splitting the metric content physically, 
                # it's better to treat each chunk as a "sub-row" group.
                # Let's just put Seq num in the first chunk's first row.
                
                cols_empty = ["", "", "", ""]
                line = f"{seq_str} & {c_tex} & " + " & ".join(cols_empty) + " \\\\"
                out.append(line)
            else:
                # We have items
                for sub_idx, it in enumerate(sub_items):
                    req = escape_latex(it["requirement"])
                    srs = escape_latex(it["srs_chapter"])
                    test_item_name = escape_latex(it["test_item_name"])
                    test_item_ident = escape_latex(it["test_item_ident"])
                    test_item = f"{test_item_name}（{test_item_ident}）"
                    sec = escape_latex(it["section"])
                    
                    if is_reverse:
                        cols = [test_item, sec, req, srs]
                    else:
                        cols = [req, srs, test_item, sec]
                        
                    line = ""
                    if sub_idx == 0:
                        # First row of this chunk
                        if chunk_idx == 0:
                             seq_cell = f"\\SetCell[r={r_span}]{{c,m}} {display_seq}"
                        else:
                             # For subsequent chunks, we don't merge with previous. 
                             # We just leave Seq column empty (but merge it for this chunk's rows?)
                             # If we merge r=r_span with empty content, it looks clean.
                             seq_cell = f"\\SetCell[r={r_span}]{{c,m}} "
                        
                        metric_cell = f"\\SetCell[r={r_span}]{{l,t}} {c_tex}"
                        line = f"{seq_cell} & {metric_cell} & " + " & ".join(cols) + " \\\\"
                    else:
                        line = "& & " + " & ".join(cols) + " \\\\"
                    out.append(line)
                    
        i = j
        seq_counter += 1
        
    return "\n".join(out)


def main():
    repo = Path(__file__).resolve().parents[1]
    data_dir = repo / "data"
    out_dir = repo / "output" / "test_plan" / "chapters"

    items = collect_plan_items(data_dir)
    # Generate content
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate Forward Table
    forward_rows = build_rows_generic(items, is_reverse=False)
    forward_table = f"""{{\\settablespacing
\\begin{{longtblr}}[theme=gjb,caption={{xxxxxxxxxx与需求规格说明以及测试项的追踪关系表}},label={{tbl:plan-trace}}]{{
  colspec={{|Q[c,0.8cm]|Q[l,2.8cm]|X[l,1]|Q[c,2.0cm]|X[l,1.5]|Q[c,2.0cm]|}},
  rowhead=2,
  hlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},
  cell{{1}}{{1,2}}={{r=2}}{{c,m}},
  cell{{1}}{{3,5}}={{c=2}}{{c,m}},
  cell{{2}}{{3,4,5,6}}={{c,m}},
  row{{2}}={{font=\\xiaowuhei,halign=c,valign=m}},
}}
  序号 & xxxxxx & 需求规格说明 & & 测试大纲 & \\\\
  & & 需求名称/标识 & 需求规格说明章节号 & 测试项名称/标识 & 本文档的章节号 \\\\
{forward_rows}
\\end{{longtblr}}
}}"""

    # Generate Reverse Table
    reverse_rows = build_rows_generic(items, is_reverse=True)
    reverse_table = f"""{{\\settablespacing
\\begin{{longtblr}}[theme=gjb,caption={{xxxxxxxxxx与需求规格说明以及测试项的逆向追踪关系表}},label={{tbl:plan-trace-rev}}]{{
  colspec={{|Q[c,0.8cm]|Q[l,2.8cm]|X[l,1.5]|Q[c,2.0cm]|X[l,1]|Q[c,2.0cm]|}},
  rowhead=2,
  hlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},
  cell{{1}}{{1,2}}={{r=2}}{{c,m}},
  cell{{1}}{{3,5}}={{c=2}}{{c,m}},
  cell{{2}}{{3,4,5,6}}={{c,m}},
  row{{2}}={{font=\\xiaowuhei,halign=c,valign=m}},
}}
  序号 & xxxxxx & 测试大纲 & & 需求规格说明 & \\\\
  & & 测试项名称/标识 & 本文档的章节号 & 需求名称/标识 & 需求规格说明章节号 \\\\
{reverse_rows}
\\end{{longtblr}}
}}"""

    full_content = forward_table + "\n\\vspace{0pt}\n\n" + reverse_table
    (out_dir / "chapter7_content.tex").write_text(full_content, encoding="utf-8")

    print(f"✅ 第七章完整表格内容已生成到: {out_dir / 'chapter7_content.tex'}")


if __name__ == "__main__":
    main()
