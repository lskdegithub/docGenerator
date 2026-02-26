#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试计划文档 第7章（需求的可追踪性）的追踪表
使用 tabularray (longtblr) 生成完整的表格代码
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import utils


def split_by_max_chars(text: str, max_chars: int) -> List[str]:
    text = str(text or "")
    if not text:
        return [""]
    max_chars = int(max_chars or 0)
    if max_chars <= 0:
        return [text]
    parts: List[str] = []
    s = 0
    while s < len(text):
        end = min(len(text), s + max_chars)
        window = text[s : min(len(text), end + 80)]
        m = re.search(r".*([。！？；;!?])\s*", window)
        if m and s + m.end() > s:
            end = s + m.end()
        parts.append(text[s:end])
        s = end
    return parts


def split_to_fixed_row_parts(text: str, max_chars: int, row_count: int) -> List[str]:
    row_count = max(1, int(row_count or 0))
    parts = split_by_max_chars(text, max_chars=max_chars)
    if len(parts) >= row_count:
        return parts[: row_count - 1] + ["".join(parts[row_count - 1 :])]
    return parts + [""] * (row_count - len(parts))


def escape_with_breaks(text: str, max_chars: int) -> str:
    parts = split_by_max_chars(text, max_chars=max_chars)
    escaped = [utils.escape_latex(p) for p in parts if str(p).strip()]
    return r"\GjbCellBreak ".join(escaped).strip()


def load_trace_segments(path: Optional[str]) -> Dict[str, Dict[str, List[int]]]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    segs = data.get("segments") or {}
    if not isinstance(segs, dict):
        return {}
    out: Dict[str, Dict[str, List[int]]] = {}
    for tbl, tbl_map in segs.items():
        if isinstance(tbl, int):
            tbl = str(tbl)
        if not isinstance(tbl, str) or not isinstance(tbl_map, dict):
            continue
        cleaned_tbl: Dict[str, List[int]] = {}
        for k, v in tbl_map.items():
            if isinstance(k, int):
                k = str(k)
            if not isinstance(k, str) or not isinstance(v, list):
                continue
            cleaned = [int(x) for x in v if int(x) > 0]
            if cleaned:
                cleaned_tbl[k] = cleaned
        if cleaned_tbl:
            out[tbl] = cleaned_tbl
    return out


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


def generate_table_rows(
    items,
    trace_pass: str,
    probe_piece_chars: int,
    segments_by_seq: Optional[Dict[str, List[int]]],
    enable_trace_mark: bool,
    tbl_tag: str,
    table_kind: str,
):
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

        metric_total_rows = len(group)
        metric_parts = split_to_fixed_row_parts(metric_content, max_chars=int(probe_piece_chars), row_count=metric_total_rows)

        segs = (segments_by_seq or {}).get(str(seq), [])
        if trace_pass == "final":
            if not segs:
                segs = [metric_total_rows]
            if sum(segs) != metric_total_rows:
                segs = [metric_total_rows]
        else:
            segs = []
        seg_idx = 0
        seg_row_start = 0
        seg_row_len = segs[0] if segs else metric_total_rows

        for global_row in range(metric_total_rows):
            is_real = global_row < len(group)
            item = group[global_row] if is_real else {}

            mark = ""
            if enable_trace_mark:
                mark = f"\\GjbTraceMark{{{tbl_tag}}}{{{seq}}}{{{global_row + 1}}}"
            if global_row == 0:
                c1 = f"{mark}\\SetCell[r={metric_total_rows}]{{c,t}} {{{seq}}}"
            else:
                c1 = mark

            if trace_pass == "final":
                while global_row >= seg_row_start + seg_row_len and seg_idx + 1 < len(segs):
                    seg_row_start += seg_row_len
                    seg_idx += 1
                    seg_row_len = segs[seg_idx]

                is_segment_start = global_row == seg_row_start
                if is_segment_start:
                    seg_start = seg_row_start
                    seg_end = seg_row_start + seg_row_len
                    seg_pieces = []
                    for p in range(seg_start, seg_end):
                        seg_pieces.append(utils.escape_latex(metric_parts[p] if p < len(metric_parts) else ""))
                    seg_pieces = [p for p in seg_pieces if p.strip()]
                    seg_text = r"\GjbCellBreak ".join(seg_pieces).strip()
                    c2 = f"\\SetCell[r={seg_row_len}]{{l,t}} {{{seg_text}}}"
                else:
                    c2 = ""
            else:
                piece = metric_parts[global_row] if global_row < len(metric_parts) else ""
                c2 = utils.escape_latex(piece)

            if is_real:
                raw_req = str(item.get("requirement") or "")
                raw_srs = str(item.get("srs_chapter") or "")
                raw_name = str(item.get("test_item_name") or "")
                raw_ident = str(item.get("test_item_ident") or "")
                raw_sec = str(item.get("section") or "")

                if table_kind == "reverse":
                    req = escape_with_breaks(raw_req, max_chars=26)
                    srs = escape_with_breaks(raw_srs, max_chars=18)
                    test_item = escape_with_breaks(f"{raw_name}（{raw_ident}）", max_chars=48)
                    sec = escape_with_breaks(raw_sec, max_chars=18)
                else:
                    req = escape_with_breaks(raw_req, max_chars=34)
                    srs = escape_with_breaks(raw_srs, max_chars=18)
                    test_item = escape_with_breaks(f"{raw_name}（{raw_ident}）", max_chars=52)
                    sec = escape_with_breaks(raw_sec, max_chars=18)
            else:
                req = ""
                srs = ""
                test_item = ""
                sec = ""

            row_cmd = r"\\"
            if table_kind == "reverse":
                c3, c4, c5, c6 = test_item, sec, req, srs
            else:
                c3, c4, c5, c6 = req, srs, test_item, sec
            line = f"{c1} & {c2} & {c3} & {c4} & {c5} & {c6} {row_cmd}"

            rows_tex.append(line)
            if global_row == metric_total_rows - 1:
                rows_tex.append(r"\hline")
            else:
                rows_tex.append(r"\cline{2-6}")

        i = j
        seq += 1
        
    return "\n".join(rows_tex)


def generate_forward_table(items, trace_pass: str, probe_piece_chars: int, segments_by_seq: Optional[Dict[str, List[int]]], enable_trace_mark: bool):
    body = generate_table_rows(items, trace_pass, probe_piece_chars, segments_by_seq, enable_trace_mark, "PF", "forward")
    latex = f"""
{{\\settablespacing
\\begin{{longtblr}}[
  theme=gjb,
  caption={{xxxxxxxxxx与需求规格说明以及测试项的追踪关系}},
  label={{tbl:plan-trace}},
]{{
  colspec={{|Q[c,t,0.8cm]|Q[l,t,3.0cm]|Q[c,t,2.4cm]|Q[c,t,1.8cm]|Q[c,t,5.0cm]|Q[c,t,1.4cm]|}},
  rowhead=2,
  row{{1,2}}={{font=\\xiaowuhei}},
  vlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},
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


def generate_reverse_table(items, trace_pass: str, probe_piece_chars: int, segments_by_seq: Optional[Dict[str, List[int]]], enable_trace_mark: bool):
    body = generate_table_rows(items, trace_pass, probe_piece_chars, segments_by_seq, enable_trace_mark, "PR", "reverse")
    latex = f"""
{{\\settablespacing
\\begin{{longtblr}}[
  theme=gjb,
  caption={{xxxxxxxxxx与需求规格说明以及测试项的逆向追踪关系}},
  label={{tbl:plan-trace-rev}},
]{{
  colspec={{|Q[c,t,0.8cm]|Q[l,t,3.0cm]|Q[c,t,5.2cm]|Q[c,t,1.4cm]|Q[c,t,2.0cm]|Q[c,t,1.6cm]|}},
  rowhead=2,
  row{{1,2}}={{font=\\xiaowuhei}},
  vlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},
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
    parser = argparse.ArgumentParser(description="生成测试计划第七章追踪表")
    parser.add_argument("--data", default=None, help="数据目录（默认使用仓库 data/）")
    parser.add_argument("--out", default=None, help="输出目录（默认 output/test_plan/chapters/）")
    parser.add_argument("--trace-pass", default="final", choices=["probe", "final"], help="追踪表生成阶段")
    parser.add_argument("--trace-probe-piece-chars", default=60, type=int, help="探测阶段切分长度")
    parser.add_argument("--trace-page-map", default=None, help="分页段信息 JSON（parse_trace_pages.py 输出）")
    parser.add_argument("--trace-enable-mark", action="store_true", help="输出分页探测标记到编译日志")
    args = parser.parse_args()

    repo_root = utils.get_project_root()
    data_dir = Path(args.data).resolve() if args.data else (repo_root / "data")
    out_dir = Path(args.out).resolve() if args.out else (repo_root / "output" / "test_plan" / "chapters")

    items = collect_plan_items(data_dir)
    
    segs = load_trace_segments(args.trace_page_map)
    forward_table = generate_forward_table(
        items,
        args.trace_pass,
        args.trace_probe_piece_chars,
        segs.get("PF", {}),
        bool(args.trace_enable_mark),
    )
    reverse_table = generate_reverse_table(
        items,
        args.trace_pass,
        args.trace_probe_piece_chars,
        segs.get("PR", {}),
        bool(args.trace_enable_mark),
    )
    
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "chapter7_forward_table.tex").write_text(forward_table, encoding="utf-8")
    (out_dir / "chapter7_reverse_table.tex").write_text(reverse_table, encoding="utf-8")

    print(f"✅ 第七章追踪表已生成到: {out_dir}")
    print("  - chapter7_forward_table.tex")
    print("  - chapter7_reverse_table.tex")


if __name__ == "__main__":
    main()
