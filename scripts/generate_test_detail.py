import re
import argparse
from pathlib import Path
import yaml


def load_yaml(file_path: Path):
    content = file_path.read_text(encoding="utf-8")
    content = content.replace("：", ":")
    content = re.sub(r"(^\s*[^:\n]+):(?!\s)", r"\1: ", content, flags=re.MULTILINE)
    return yaml.safe_load(content) or {}


def parse_plan_yaml(file_path: Path):
    content = file_path.read_text(encoding="utf-8")
    content = content.replace("：", ":")
    def pick(pattern: str):
        m = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        return m.group(1).strip() if m else ""
    return {
        "测试项名称": pick(r"测试项名称:\s*(.+?)(?:\n|$)"),
        "标识": pick(r"标识:\s*(.+?)(?:\n|$)"),
        "需求追踪关系": pick(r"(?:需求追踪关系|需求的追踪关系):\s*(.+?)(?:\n|$)"),
        "需规章节": pick(r"需规章节:\s*(.+?)(?:\n|$)"),
        "type": pick(r"^type:\s*(.+?)(?:\n|$)"),
    }


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
        chunk = 16
        return r"\allowbreak ".join([s[i:i + chunk] for i in range(0, len(s), chunk)])
    text = re.sub(r"(?<!\\)[A-Za-z0-9]{20,}", break_long, text)
    return " ".join(text.split())


def normalize_index(value: str) -> str:
    value = str(value or "").strip()
    if value.isdigit():
        return str(int(value))
    return value or "1"


def sanitize_label(value: str) -> str:
    value = str(value or "").strip().lower()
    value = re.sub(r"[^0-9a-z]+", "-", value).strip("-")
    return value or "item"


def map_test_type(value: str) -> str:
    key = str(value or "").strip().lower()
    if key in {"functional", "function", "func"}:
        return "功能测试"
    if key in {"interface", "api"}:
        return "接口测试"
    if key in {"reliability", "stable"}:
        return "可靠性测试"
    return str(value or "").strip() or "—"


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


def collect_data(data_dir: Path):
    metrics = []
    metric_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir() and d.name.endswith("-test-metric")])
    for metric_order, metric_dir in enumerate(metric_dirs, start=1):
        metric_files = list(metric_dir.glob("*metric.yaml"))
        if not metric_files:
            continue
        metric_data = load_yaml(metric_files[0])
        metric_index = normalize_index(metric_data.get("index", metric_dir.name.split("-")[0]))
        metric_title = str(metric_data.get("title", "")).strip()
        metric_content = str(metric_data.get("content", "")).strip()
        metric_title = metric_title or metric_content or metric_index
        modules = []
        module_dirs = sorted([d for d in metric_dir.iterdir() if d.is_dir() and d.name.endswith("-module")])
        for module_order, module_dir in enumerate(module_dirs, start=1):
            metadata_file = module_dir / "metadata.yaml"
            metadata = load_yaml(metadata_file) if metadata_file.exists() else {}
            module_name = str(metadata.get("MODULE_NAME", "")).strip()
            module_id = str(metadata.get("MODULE_ID", "")).strip()
            items = []
            item_dirs = sorted([d for d in module_dir.iterdir() if d.is_dir() and "item" in d.name])
            for item_order, item_dir in enumerate(item_dirs, start=1):
                plan_file = item_dir / "plan.yaml"
                if not plan_file.exists():
                    continue
                plan_data = parse_plan_yaml(plan_file)
                test_item_name = str(plan_data.get("测试项名称", "")).strip()
                test_item_ident = str(plan_data.get("标识", "")).strip()
                test_item_type = map_test_type(plan_data.get("type", ""))
                requirement = str(plan_data.get("需求追踪关系", "")).strip()
                srs_chapter = str(plan_data.get("需规章节", "")).strip()
                cases = []
                case_dir = item_dir / "test_case"
                case_files = sorted(case_dir.glob("*.yaml")) if case_dir.exists() else []
                for case_order, case_file in enumerate(case_files, start=1):
                    case_data = load_yaml(case_file)
                    cases.append(
                        {
                            "order": case_order,
                            "data": case_data,
                        }
                    )
                items.append(
                    {
                        "order": item_order,
                        "name": test_item_name,
                        "ident": test_item_ident,
                        "type": test_item_type,
                        "requirement": requirement,
                        "srs_chapter": srs_chapter,
                        "cases": cases,
                    }
                )
            modules.append(
                {
                    "order": module_order,
                    "name": module_name,
                    "ident": module_id,
                    "items": items,
                }
            )
        metrics.append(
            {
                "order": metric_order,
                "index": metric_index,
                "title": metric_title,
                "content": metric_content,
                "modules": modules,
            }
        )
    return metrics


def build_steps_table(steps):
    rows = []
    if not isinstance(steps, list):
        steps = []
    if not steps:
        steps = [{"序号": 1, "输入及操作": "", "期望结果": ""}]
    for idx, step in enumerate(steps, start=1):
        seq = step.get("序号", idx)
        action = escape_latex(step.get("输入及操作", ""))
        expect = escape_latex(step.get("期望结果", ""))
        rows.append(f"{seq} & {action} & {expect} &  \\\\")
    return "\n".join(rows)


def build_case_table(case_data, test_item_label, label_suffix):
    case_name = escape_latex(case_data.get("测试用例名称", ""))
    case_ident = escape_latex(case_data.get("标识", ""))
    summary = escape_latex(case_data.get("测试用例综述", ""))
    init = escape_latex(case_data.get("用例初始化", ""))
    prereq = escape_latex(case_data.get("前提与约束", ""))
    case_type = escape_latex(case_data.get("测试用例类型", ""))
    term = escape_latex(case_data.get("测试用例终止条件", ""))
    criteria = escape_latex(case_data.get("测试结果判定准则", ""))
    result = escape_latex(case_data.get("测试用例执行结果", ""))
    designer = escape_latex(case_data.get("设计人员", ""))
    operator = escape_latex(case_data.get("操作人员", ""))
    tester = escape_latex(case_data.get("测试人员", ""))
    test_time = escape_latex(case_data.get("测试时间", ""))
    steps_rows = build_steps_table(case_data.get("测试步骤", []))
    label = f"tbl:detail-tc-{sanitize_label(label_suffix)}"
    caption = case_name or "测试用例"
    table = f"""{{\\settablespacing
\\begin{{tblr}}[theme=gjbNoHead,caption={{{caption}}},label={{{label}}}]{{\n  colsep=2pt,\n  colspec={{|p{{2.3cm}}|p{{7.3cm}}|p{{2.3cm}}|p{{2.6cm}}|}},\n  hlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},\n  vlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},\n  column{{1}}={{halign=c}},\n  column{{3}}={{halign=c}},\n  column{{4}}={{halign=c}},\n}}
\\TableKeyCell{{测试用例名称}} & {case_name} & \\SetCell{{halign=c}}{{\\TableKeyCell{{标识}}}} & \\TableIdentifier{{{case_ident}}} \\\\
\\TableKeyCell{{追踪关系}} & \\SetCell[c=3]{{valign=t}}{{{test_item_label}}} && \\\\
\\TableKeyCell{{测试用例综述}} & \\SetCell[c=3]{{valign=t}}{{{summary}}} && \\\\
\\TableKeyCell{{用例初始化}} & \\SetCell[c=3]{{valign=t}}{{{init}}} && \\\\
\\TableKeyCell{{前提和约束}} & \\SetCell[c=3]{{valign=t}}{{{prereq}}} && \\\\
\\TableKeyCell{{测试用例类型}} & \\SetCell[c=3]{{valign=t}}{{{case_type}}} && \\\\
\\SetCell[c=4]{{halign=c,font=\\xiaowuhei}}{{测试步骤}} &&& \\\\
\\end{{tblr}}
\\vspace*{{-6pt}}
\\begin{{longtblr}}[theme=gjbNoHead]{{\n  colsep=2pt,\n  colspec={{|p{{0.8cm}}|p{{6.0cm}}|p{{4.8cm}}|p{{2.9cm}}|}},\n  hlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},\n  vlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},\n  column{{1,4}}={{halign=c}},\n  rowhead=1,\n  row{{1}}={{font=\\xiaowuhei,halign=c,valign=m}},\n}}
序号 & 输入及操作 & 期望结果 & 测试结果 \\\\\n{steps_rows}
\\end{{longtblr}}
\\vspace*{{-6pt}}
\\begin{{tblr}}[theme=gjbNoHead]{{\n  colsep=2pt,\n  colspec={{|p{{2.3cm}}|p{{7.3cm}}|p{{2.3cm}}|p{{2.6cm}}|}},\n  hlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},\n  vlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},\n  column{{1}}={{halign=c}},\n  column{{3}}={{halign=c}},\n  column{{4}}={{halign=c}},\n}}
\\TableKeyCell{{测试用例终止条件}} & \\SetCell[c=3]{{valign=t}}{{{term}}} && \\\\
\\TableKeyCell{{测试结果评估标准}} & \\SetCell[c=3]{{valign=t}}{{{criteria}}} && \\\\
\\TableKeyCell{{测试用例执行结果}} & \\SetCell[c=3]{{valign=t}}{{{result}}} && \\\\
\\TableKeyCell{{设计人员}} & {designer} & \\SetCell{{halign=c}}{{\\TableKeyCell{{操作人员}}}} & {operator} \\\\
\\TableKeyCell{{测试人员}} & {tester} & \\SetCell{{halign=c}}{{\\TableKeyCell{{测试时间}}}} & {test_time} \\\\
\\end{{tblr}}
}}
\\vspace{{-6pt}}"""
    return table


def build_chapter4(metrics):
    items = []
    total_cases = 0
    type_counts = {}
    for metric in metrics:
        for module in metric["modules"]:
            for item in module["items"]:
                items.append(item)
                total_cases += len(item["cases"])
                if item["type"] and item["type"] != "—":
                    type_counts[item["type"]] = type_counts.get(item["type"], 0) + 1
    total_items = len(items)
    type_summary = "，".join([f"{k}{v}个" for k, v in type_counts.items()]) if type_counts else ""
    if type_summary:
        intro = f"围绕《xxxx软件需求规格说明》的要求计划开展的测试共计{total_items}个测试项，其中{type_summary}。"
    else:
        intro = f"围绕《xxxx软件需求规格说明》的要求计划开展的测试共计{total_items}个测试项。"
    metric_count = len(metrics)
    detail_intro = f"针对本次节点要求共设置{total_items}个测试项，包括{total_cases}个测试用例。具体内容参见4.1.1到4.1.{metric_count}章节。"
    table_rows = []
    for item in items:
        name = escape_latex(item["name"])
        ident = escape_latex(item["ident"])
        label = f"{name}（{ident}）" if ident else name
        item_type = escape_latex(item["type"])
        table_rows.append(f"\\Seq & {{\\xiaowu {item_type}}} & {{\\xiaowu {label}}} \\\\")
    table_rows_text = "\n".join(table_rows)
    content = f"""\\section{{测试说明}}

\\subsection{{计划执行的测试}}

{intro}

计划执行的测试项列表如表 \\ref{{tbl:detail-testitems}}所示。

{{\\settablespacing
\\begin{{longtblr}}[theme=gjb,caption={{测试项列表}},label={{tbl:detail-testitems}}]{{
  colspec={{|p{{0.8cm}}|p{{4.0cm}}|p{{9.7cm}}|}},
  rowhead=1,
  hlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},
  column{{1}}={{halign=c}},
}}
序号 & 测试类别 & 测试项名称 \\\\\n{table_rows_text}
\\end{{longtblr}}
}}
\\vspace{{-6pt}}

{detail_intro}
"""
    for metric in metrics:
        metric_title = escape_latex(metric["title"])
        content += f"\n\n\\subsubsection{{{metric_title}}}\n\n"
        for module in metric["modules"]:
            module_name = escape_latex(module["name"])
            module_id = escape_latex(module["ident"])
            module_title = f"{module_name}（{module_id}）" if module_id else module_name
            content += f"\\paragraph{{{module_title}}}\n\n"
            for item in module["items"]:
                item_name = escape_latex(item["name"])
                item_ident = escape_latex(item["ident"])
                item_title = f"{item_name}（{item_ident}）" if item_ident else item_name
                content += f"\\subparagraph{{{item_title}}}\n\n"
                test_item_label = escape_latex(f"{item['name']}（{item['ident']}）" if item["ident"] else item["name"])
                for case in item["cases"]:
                    case_data = case["data"]
                    case_name = escape_latex(case_data.get("测试用例名称", ""))
                    case_ident = escape_latex(case_data.get("标识", ""))
                    case_title = f"{case_name}（{case_ident}）" if case_ident else case_name
                    content += f"\\subsubparagraph{{{case_title}}}\n\n"
                    label_suffix = f"{item.get('ident','')}-{item.get('order','')}-{case.get('order','')}-{case_ident or case_name}"
                    content += build_case_table(case_data, test_item_label, label_suffix)
                    content += "\n\n"
    return content.rstrip() + "\n"


def build_trace_rows(metrics):
    rows = []
    for metric in metrics:
        for module in metric["modules"]:
            for item in module["items"]:
                for case in item["cases"]:
                    case_data = case["data"]
                    rows.append(
                        {
                            "metric_content": metric["content"],
                            "requirement": item["requirement"],
                            "srs_chapter": item["srs_chapter"],
                            "test_item": f"{item['name']}（{item['ident']}）" if item["ident"] else item["name"],
                            "case_name": f"{case_data.get('测试用例名称','')}（{case_data.get('标识','')}）" if case_data.get("标识") else case_data.get("测试用例名称", ""),
                            "item_section": f"4.1.{metric['order']}.{module['order']}.{item['order']}",
                            "case_section": f"4.1.{metric['order']}.{module['order']}.{item['order']}.{case['order']}",
                        }
                    )
    return rows


def build_trace_longtable_rows_forward(metrics):
    rows = build_trace_rows(metrics)
    out = []
    i = 0
    while i < len(rows):
        j = i
        content = rows[i]["metric_content"]
        while j < len(rows) and rows[j]["metric_content"] == content:
            j += 1
        group = rows[i:j]
        metric_content = group[0].get("metric_content") or ""
        head_parts = split_front_small_rest_last(metric_content, len(group), head_max_chars=60)
        tail_chunks = split_by_max_chars(head_parts[-1], max_chars=200)
        for row_idx, row in enumerate(group):
            content_piece = tail_chunks[0] if row_idx == len(group) - 1 else head_parts[row_idx]
            c1 = r"\Seq" if row_idx == 0 else ""
            c2 = escape_latex(content_piece)
            req = escape_latex(row["requirement"])
            srs = escape_latex(row["srs_chapter"])
            test_item = escape_latex(row["test_item"])
            item_sec = escape_latex(row["item_section"])
            case_name = escape_latex(row["case_name"])
            case_sec = escape_latex(row["case_section"])
            line = f"{c1} & {c2} & {req} & {srs} & {test_item} & {item_sec} & {case_name} & {case_sec} \\\\"
            if row_idx == len(group) - 1:
                line += r" \cline{3-8}" if len(tail_chunks) > 1 else r" \hline"
            else:
                line += r" \cline{3-8}"
            out.append(line)
        for extra_idx, extra in enumerate(tail_chunks[1:]):
            content_tex = escape_latex(extra)
            out.append(f" & {content_tex} &  &  &  &  &  &  \\\\")
            if extra_idx == len(tail_chunks[1:]) - 1:
                out.append(r" \hline")
        i = j
    return "\n".join(out).strip()


def build_trace_longtable_rows_reverse(metrics):
    rows = build_trace_rows(metrics)
    out = []
    i = 0
    while i < len(rows):
        j = i
        content = rows[i]["metric_content"]
        while j < len(rows) and rows[j]["metric_content"] == content:
            j += 1
        group = rows[i:j]
        metric_content = group[0].get("metric_content") or ""
        head_parts = split_front_small_rest_last(metric_content, len(group), head_max_chars=60)
        tail_chunks = split_by_max_chars(head_parts[-1], max_chars=200)
        for row_idx, row in enumerate(group):
            content_piece = tail_chunks[0] if row_idx == len(group) - 1 else head_parts[row_idx]
            c1 = r"\Seq" if row_idx == 0 else ""
            c2 = escape_latex(content_piece)
            case_name = escape_latex(row["case_name"])
            case_sec = escape_latex(row["case_section"])
            test_item = escape_latex(row["test_item"])
            item_sec = escape_latex(row["item_section"])
            req = escape_latex(row["requirement"])
            srs = escape_latex(row["srs_chapter"])
            line = f"{c1} & {c2} & {case_name} & {case_sec} & {test_item} & {item_sec} & {req} & {srs} \\\\"
            if row_idx == len(group) - 1:
                line += r" \cline{3-8}" if len(tail_chunks) > 1 else r" \hline"
            else:
                line += r" \cline{3-8}"
            out.append(line)
        for extra_idx, extra in enumerate(tail_chunks[1:]):
            content_tex = escape_latex(extra)
            out.append(f" & {content_tex} &  &  &  &  &  &  \\\\")
            if extra_idx == len(tail_chunks[1:]) - 1:
                out.append(r" \hline")
        i = j
    return "\n".join(out).strip()


def main():
    parser = argparse.ArgumentParser(description="生成测试细则（test_detail）章节与追踪表行")
    parser.add_argument("--data", default="data", help="数据目录（相对仓库根目录）")
    parser.add_argument(
        "--out",
        default="output/test_detail",
        help="输出目录（相对仓库根目录），应包含 main.tex 与 chapters/",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    data_dir = (repo / args.data).resolve()
    out_dir = (repo / args.out).resolve()

    chapters_dir = out_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    metrics = collect_data(data_dir)
    (chapters_dir / "chapter4.tex").write_text(build_chapter4(metrics), encoding="utf-8")
    forward_rows = build_trace_longtable_rows_forward(metrics)
    reverse_rows = build_trace_longtable_rows_reverse(metrics)
    (chapters_dir / "chapter5_trace_rows.tex").write_text(forward_rows, encoding="utf-8")
    (chapters_dir / "chapter6_trace_rows.tex").write_text(reverse_rows, encoding="utf-8")


if __name__ == "__main__":
    main()
