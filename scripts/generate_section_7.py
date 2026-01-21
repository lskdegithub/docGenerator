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


def split_into_n_chunks(text: str, n: int):
    text = str(text or "")
    if n <= 1:
        return [text]
    if not text:
        return [""] * n

    candidates = [m.end() for m in re.finditer(r"[。！？；;!?]\s*", text)]
    if not candidates:
        avg = max(1, len(text) // n)
        out = [text[i * avg : (i + 1) * avg] for i in range(n - 1)]
        out.append(text[(n - 1) * avg :])
        return out

    targets = [round(len(text) * k / n) for k in range(1, n)]
    cuts = []
    start = 0
    for t in targets:
        best = None
        best_dist = None
        for c in candidates:
            if c <= start:
                continue
            dist = abs(c - t)
            if best is None or dist < best_dist:
                best = c
                best_dist = dist
        if best is None:
            break
        cuts.append(best)
        start = best

    if len(cuts) < n - 1:
        avg = max(1, len(text) // n)
        out = [text[i * avg : (i + 1) * avg] for i in range(n - 1)]
        out.append(text[(n - 1) * avg :])
        return out

    parts = []
    s = 0
    for c in cuts:
        parts.append(text[s:c])
        s = c
    parts.append(text[s:])
    while len(parts) < n:
        parts.append("")
    return parts[:n]


def split_front_small_rest_last(text: str, n: int, head_max_chars: int = 240):
    text = str(text or "")
    if n <= 1:
        return [text]
    if not text:
        return [""] * n

    parts = []
    s = 0
    for _ in range(n - 1):
        remaining = text[s:]
        if not remaining:
            parts.append("")
            continue
        if len(remaining) <= head_max_chars:
            parts.append(remaining)
            s = len(text)
            continue
        window = remaining[: head_max_chars + 60]
        m = re.search(r".*([。！？；;!?])\s*", window)
        if m:
            cut = s + m.end()
        else:
            cut = s + head_max_chars
        parts.append(text[s:cut])
        s = cut

    parts.append(text[s:])
    while len(parts) < n:
        parts.append("")
    return parts[:n]


def split_by_max_chars(text: str, max_chars: int):
    text = str(text or "")
    if not text:
        return [""]
    if max_chars <= 0:
        return [text]
    parts = []
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


def build_rows_forward(items):
    out = []
    i = 0
    while i < len(items):
        j = i
        metric_index = items[i]["metric_index"]
        while j < len(items) and items[j]["metric_index"] == metric_index:
            j += 1
        group = items[i:j]
        metric_content = group[0].get("metric_content") or group[0].get("metric_cell") or ""
        
        # Split content to distribute across rows
        head_parts = split_front_small_rest_last(metric_content, len(group), head_max_chars=60)
        tail_chunks = split_by_max_chars(head_parts[-1], max_chars=200)

        for row_idx, it in enumerate(group):
            if row_idx == len(group) - 1:
                content_piece = tail_chunks[0]
            else:
                content_piece = head_parts[row_idx]

            content_tex = escape_latex(content_piece)
            
            # Seq only in first row
            if row_idx == 0:
                c1 = r"\Seq"
            else:
                c1 = ""
            
            c2 = content_tex
            
            req = escape_latex(it["requirement"])
            srs = escape_latex(it["srs_chapter"])
            test_item_name = escape_latex(it["test_item_name"])
            test_item_ident = escape_latex(it["test_item_ident"])
            test_item = test_item_name + "（" + test_item_ident + "）"
            sec = escape_latex(it["section"])
            
            # Columns: Seq, Metric, Req, SRS, TestItem, Section
            line = f"{c1} & {c2} & {req} & {srs} & {test_item} & {sec} \\\\"
            
            if row_idx == len(group) - 1:
                # If there are more tail chunks, add extra rows
                if len(tail_chunks) > 1:
                     line += r" \cline{3-6}" # Close item part
                else:
                     if j < len(items):
                         line += r" \hline"
            else:
                line += r" \cline{3-6}"
            
            out.append(line)

        # Append extra rows for remaining text
        for extra_idx, extra in enumerate(tail_chunks[1:]):
            content_tex = escape_latex(extra)
            # Empty cells for other columns
            out.append(f" & {content_tex} &  &  &  &  \\\\")
            if extra_idx == len(tail_chunks[1:]) - 1:
                if j < len(items):
                    out[-1] += r" \hline"

        i = j
    if out:
        while out and out[-1].strip() in {r"\hline", r"\cline{3-6}"}:
            out.pop()
        if out:
            out[-1] = re.sub(r"\s*\\\\\s*$", "", out[-1]).rstrip()
            out[-1] = re.sub(r"\s*(\\cline\{3-6\}|\\hline)\s*$", "", out[-1]).rstrip()
    return "\n".join(out)


def build_rows_reverse(items):
    out = []
    i = 0
    while i < len(items):
        j = i
        metric_index = items[i]["metric_index"]
        while j < len(items) and items[j]["metric_index"] == metric_index:
            j += 1
        group = items[i:j]
        metric_content = group[0].get("metric_content") or group[0].get("metric_cell") or ""
        
        head_parts = split_front_small_rest_last(metric_content, len(group), head_max_chars=60)
        tail_chunks = split_by_max_chars(head_parts[-1], max_chars=200)

        for row_idx, it in enumerate(group):
            if row_idx == len(group) - 1:
                content_piece = tail_chunks[0]
            else:
                content_piece = head_parts[row_idx]

            content_tex = escape_latex(content_piece)
            
            if row_idx == 0:
                c1 = r"\Seq"
            else:
                c1 = ""
            c2 = content_tex

            req = escape_latex(it["requirement"])
            srs = escape_latex(it["srs_chapter"])
            test_item_name = escape_latex(it["test_item_name"])
            test_item_ident = escape_latex(it["test_item_ident"])
            test_item = test_item_name + "（" + test_item_ident + "）"
            sec = escape_latex(it["section"])
            
            # Columns: Seq, Metric, TestItem, Section, Req, SRS
            line = f"{c1} & {c2} & {test_item} & {sec} & {req} & {srs} \\\\"
            
            if row_idx == len(group) - 1:
                if len(tail_chunks) > 1:
                     line += r" \cline{3-6}"
                else:
                     if j < len(items):
                         line += r" \hline"
            else:
                line += r" \cline{3-6}"
                
            out.append(line)

        for extra_idx, extra in enumerate(tail_chunks[1:]):
            content_tex = escape_latex(extra)
            out.append(f" & {content_tex} &  &  &  &  \\\\")
            if extra_idx == len(tail_chunks[1:]) - 1:
                if j < len(items):
                    out[-1] += r" \hline"

        i = j
    if out:
        while out and out[-1].strip() in {r"\hline", r"\cline{3-6}"}:
            out.pop()
        if out:
            out[-1] = re.sub(r"\s*\\\\\s*$", "", out[-1]).rstrip()
            out[-1] = re.sub(r"\s*(\\cline\{3-6\}|\\hline)\s*$", "", out[-1]).rstrip()
    return "\n".join(out)


def write_output(forward_rows: str, reverse_rows: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    # Write without trailing newline to avoid longtable empty row issue
    # Ensure strict stripping
    forward_rows = forward_rows.strip()
    reverse_rows = reverse_rows.strip()
    
    (out_dir / "chapter7_trace_rows.tex").write_text(forward_rows, encoding="utf-8")
    (out_dir / "chapter7_trace_rev_rows.tex").write_text(reverse_rows, encoding="utf-8")


def main():
    repo = Path(__file__).resolve().parents[1]
    data_dir = repo / "data"
    out_dir = repo / "output" / "test_plan" / "chapters"

    items = collect_plan_items(data_dir)
    forward = build_rows_forward(items)
    reverse = build_rows_reverse(items)
    write_output(forward, reverse, out_dir)

    print(f"✅ 第七章追踪表行已生成到: {out_dir}")


if __name__ == "__main__":
    main()
