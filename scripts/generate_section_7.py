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
    text = text.replace("_", "\\_")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    text = text.replace("~", "\\textasciitilde ")
    text = text.replace("^", "\\textasciicircum ")
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
        metric_cell = metric_data.get("content") or metric_data.get("title") or metric_index

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
        metric_cell = items[i]["metric_cell"]
        metric_index = items[i]["metric_index"]
        while j < len(items) and items[j]["metric_index"] == metric_index:
            j += 1
        span = j - i

        for k in range(i, j):
            it = items[k]
            metric_tex = ""
            if k == i:
                metric_tex = f"\\SetCell[r={span}]{{valign=t}}{{{escape_latex(metric_cell)}}}"
            req = escape_latex(it["requirement"])
            srs = escape_latex(it["srs_chapter"])
            test_item = escape_latex(it['test_item_name']) + "（" + escape_latex(it["test_item_ident"]) + "）"
            sec = escape_latex(it["section"])
            out.append(f"\\Seq & {metric_tex} & {req} & {srs} & {test_item} & {sec} \\\\")
        i = j
    return "\n".join(out)


def build_rows_reverse(items):
    out = []
    i = 0
    while i < len(items):
        j = i
        metric_cell = items[i]["metric_cell"]
        metric_index = items[i]["metric_index"]
        while j < len(items) and items[j]["metric_index"] == metric_index:
            j += 1
        span = j - i

        for k in range(i, j):
            it = items[k]
            metric_tex = ""
            if k == i:
                metric_tex = f"\\SetCell[r={span}]{{valign=t}}{{{escape_latex(metric_cell)}}}"
            test_item = escape_latex(it['test_item_name']) + "（" + escape_latex(it["test_item_ident"]) + "）"
            sec = escape_latex(it["section"])
            req = escape_latex(it["requirement"])
            srs = escape_latex(it["srs_chapter"])
            out.append(f"\\Seq & {metric_tex} & {test_item} & {sec} & {req} & {srs} \\\\")
        i = j
    return "\n".join(out)


def write_output(forward_rows: str, reverse_rows: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "chapter7_trace_rows.tex").write_text(forward_rows + "\n", encoding="utf-8")
    (out_dir / "chapter7_trace_rev_rows.tex").write_text(reverse_rows + "\n", encoding="utf-8")


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

