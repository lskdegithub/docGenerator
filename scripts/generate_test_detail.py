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
    text = re.sub(r"([/-])", r"\1\\allowbreak ", text)
    def break_long(match: re.Match) -> str:
        s = match.group(0)
        chunk = 16
        return r"\allowbreak ".join([s[i:i + chunk] for i in range(0, len(s), chunk)])
    text = re.sub(r"(?<!\\)[A-Za-z0-9]{20,}", break_long, text)
    return " ".join(text.split())


def escape_latex_no_wordbreak(text: str) -> str:
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
    text = re.sub(r"([/-])", r"\1\\allowbreak ", text)
    return " ".join(text.split())


def wrap_alnum_runs_by_chars(text: str, chars_per_line: int) -> str:
    if not text:
        return ""
    chars_per_line = int(chars_per_line or 0)
    if chars_per_line <= 0:
        return text

    def repl(match: re.Match) -> str:
        s = match.group(0)
        if len(s) <= chars_per_line:
            return s
        parts = [s[i:i + chars_per_line] for i in range(0, len(s), chars_per_line)]
        return r" \allowbreak ".join(parts)

    pattern = rf"(?<!\\)[A-Za-z0-9]{{{chars_per_line + 1},}}"
    return re.sub(pattern, repl, text)


def escape_latex_table_cell(text: str, chars_per_line: int) -> str:
    return wrap_alnum_runs_by_chars(escape_latex_no_wordbreak(text), chars_per_line)


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
        action = escape_latex_table_cell(step.get("输入及操作", ""), chars_per_line=30)
        expect = escape_latex_table_cell(step.get("期望结果", ""), chars_per_line=30)
        rows.append(
            f"{seq} & \\SetCell[c=3]{{valign=t}}{{{action}}} &  &  & \\SetCell[c=2]{{valign=t}}{{{expect}}} &  & \\SetCell[c=2]{{valign=t}}{{}} &  \\\\"
        )
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
\\begin{{longtblr}}[theme=gjbNoHead,caption={{{caption}}},label={{{label}}}]{{\n  colspec={{|p{{0.8cm}}|p{{1.5cm}}|p{{2.25cm}}|p{{2.25cm}}|p{{2.4cm}}|p{{2.4cm}}|p{{1.45cm}}|p{{1.45cm}}|}},\n  hlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},\n  vlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},\n  column{{1}}={{halign=c}},\n}}
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试用例名称}}}} & & \\SetCell[c=3]{{valign=t}}{{{case_name}}} &  &  & \\TableKeyCell{{标识}} & \\SetCell[c=2]{{valign=t}}{{\\TableIdentifier{{{case_ident}}}}} & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{追踪关系}}}} & & \\SetCell[c=6]{{valign=t}}{{{test_item_label}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试用例综述}}}} & & \\SetCell[c=6]{{valign=t}}{{{summary}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{用例初始化}}}} & & \\SetCell[c=6]{{valign=t}}{{{init}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{前提和约束}}}} & & \\SetCell[c=6]{{valign=t}}{{{prereq}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试用例类型}}}} & & \\SetCell[c=6]{{valign=t}}{{{case_type}}} &  &  &  &  & \\\\
\\SetCell[c=8]{{halign=c,font=\\xiaowuhei}}{{测试步骤}} &  &  &  &  &  &  & \\\\
\\SetCell{{font=\\xiaowuhei,halign=c,valign=m}}{{序号}} & \\SetCell[c=3]{{font=\\xiaowuhei,halign=c,valign=m}}{{输入及操作}} &  &  & \\SetCell[c=2]{{font=\\xiaowuhei,halign=c,valign=m}}{{期望结果}} &  & \\SetCell[c=2]{{font=\\xiaowuhei,halign=c,valign=m}}{{测试结果}} &  \\\\
{steps_rows}
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试用例终止条件}}}} & & \\SetCell[c=6]{{valign=t}}{{{term}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试结果评估标准}}}} & & \\SetCell[c=6]{{valign=t}}{{{criteria}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试用例执行结果}}}} & & \\SetCell[c=6]{{valign=t}}{{{result}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{设计人员}}}} & & \\SetCell[c=3]{{valign=t}}{{{designer}}} &  &  & \\TableKeyCell{{操作人员}} & \\SetCell[c=2]{{valign=t}}{{{operator}}} & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试人员}}}} & & \\SetCell[c=3]{{valign=t}}{{{tester}}} &  &  & \\TableKeyCell{{测试时间}} & \\SetCell[c=2]{{valign=t}}{{{test_time}}} & \\\\
\\end{{longtblr}}
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
    content = f"""\\subsection{{计划执行的测试}}

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
                    label_suffix = f"m{metric['order']}-mo{module['order']}-i{item['order']}-c{case['order']}"
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
    rows.sort(
        key=lambda r: (
            r.get("metric_content", ""),
            r.get("requirement", ""),
            r.get("srs_chapter", ""),
            r.get("test_item", ""),
            r.get("item_section", ""),
            r.get("case_name", ""),
            r.get("case_section", ""),
        )
    )
    out = []
    mi = 0
    while mi < len(rows):
        mj = mi
        metric_content = rows[mi].get("metric_content") or ""
        while mj < len(rows) and (rows[mj].get("metric_content") or "") == metric_content:
            mj += 1
        metric_group = rows[mi:mj]
        head_parts = split_front_small_rest_last(metric_content, len(metric_group), head_max_chars=60)
        tail_chunks = split_by_max_chars(head_parts[-1], max_chars=200)
        metric_row_idx = 0

        ri = 0
        while ri < len(metric_group):
            rj = ri
            req_key = (metric_group[ri].get("requirement") or "", metric_group[ri].get("srs_chapter") or "")
            while rj < len(metric_group) and (
                (metric_group[rj].get("requirement") or "", metric_group[rj].get("srs_chapter") or "") == req_key
            ):
                rj += 1
            req_group = metric_group[ri:rj]
            req_cell = escape_latex_table_cell(req_key[0], chars_per_line=14)
            srs_cell = escape_latex_table_cell(req_key[1], chars_per_line=12)

            ii = 0
            while ii < len(req_group):
                ij = ii
                item_key = (req_group[ii].get("test_item") or "", req_group[ii].get("item_section") or "")
                while ij < len(req_group) and (
                    (req_group[ij].get("test_item") or "", req_group[ij].get("item_section") or "") == item_key
                ):
                    ij += 1
                item_group = req_group[ii:ij]
                item_cell = escape_latex_table_cell(item_key[0], chars_per_line=22)
                item_sec_cell = escape_latex(item_key[1])

                for ci, row in enumerate(item_group):
                    is_first_metric_row = metric_row_idx == 0
                    is_first_req_row = (ii == 0 and ci == 0)
                    is_first_item_row = (ci == 0)
                    is_last_case_in_item = (ci == len(item_group) - 1)
                    is_last_item_in_req = (ij == len(req_group))
                    is_last_req_in_metric = (rj == len(metric_group))
                    is_last_row_in_metric = is_last_case_in_item and is_last_item_in_req and is_last_req_in_metric

                    if metric_row_idx == len(metric_group) - 1:
                        metric_piece = tail_chunks[0]
                    else:
                        metric_piece = head_parts[metric_row_idx]
                    metric_row_idx += 1

                    c1 = r"\Seq" if is_first_metric_row else ""
                    c2 = escape_latex_table_cell(metric_piece, chars_per_line=18)
                    c3 = req_cell if is_first_req_row else ""
                    c4 = srs_cell if is_first_req_row else ""
                    c5 = item_cell if is_first_item_row else ""
                    c6 = item_sec_cell if is_first_item_row else ""
                    c7 = escape_latex_table_cell(row.get("case_name") or "", chars_per_line=22)
                    c8 = escape_latex(row.get("case_section") or "")

                    line = f"{c1} & {c2} & {c3} & {c4} & {c5} & {c6} & {c7} & {c8} \\\\"
                    if is_last_row_in_metric:
                        line += r" \cline{3-8}" if len(tail_chunks) > 1 else r" \hline"
                    elif not is_last_case_in_item:
                        line += r" \cline{7-8}"
                    elif not is_last_item_in_req:
                        line += r" \cline{5-8}"
                    else:
                        line += r" \cline{3-8}"

                    out.append(line)

                ii = ij
            ri = rj

        for extra_idx, extra in enumerate(tail_chunks[1:]):
            content_tex = escape_latex_table_cell(extra, chars_per_line=18)
            out.append(f" & {content_tex} &  &  &  &  &  &  \\\\")
            if extra_idx == len(tail_chunks[1:]) - 1:
                out.append(r" \hline")
        mi = mj

    return "\n".join(out).strip()


def build_trace_longtable_rows_reverse(metrics):
    rows = build_trace_rows(metrics)
    rows.sort(
        key=lambda r: (
            r.get("metric_content", ""),
            r.get("case_name", ""),
            r.get("case_section", ""),
            r.get("test_item", ""),
            r.get("item_section", ""),
            r.get("requirement", ""),
            r.get("srs_chapter", ""),
        )
    )
    out = []
    mi = 0
    while mi < len(rows):
        mj = mi
        metric_content = rows[mi].get("metric_content") or ""
        while mj < len(rows) and (rows[mj].get("metric_content") or "") == metric_content:
            mj += 1
        metric_group = rows[mi:mj]
        head_parts = split_front_small_rest_last(metric_content, len(metric_group), head_max_chars=60)
        tail_chunks = split_by_max_chars(head_parts[-1], max_chars=200)
        metric_row_idx = 0

        ci0 = 0
        while ci0 < len(metric_group):
            cj0 = ci0
            case_key = (metric_group[ci0].get("case_name") or "", metric_group[ci0].get("case_section") or "")
            while cj0 < len(metric_group) and (
                (metric_group[cj0].get("case_name") or "", metric_group[cj0].get("case_section") or "") == case_key
            ):
                cj0 += 1
            case_group = metric_group[ci0:cj0]
            case_cell = escape_latex_table_cell(case_key[0], chars_per_line=22)
            case_sec_cell = escape_latex(case_key[1])

            ii = 0
            while ii < len(case_group):
                ij = ii
                item_key = (case_group[ii].get("test_item") or "", case_group[ii].get("item_section") or "")
                while ij < len(case_group) and (
                    (case_group[ij].get("test_item") or "", case_group[ij].get("item_section") or "") == item_key
                ):
                    ij += 1
                item_group = case_group[ii:ij]
                item_cell = escape_latex_table_cell(item_key[0], chars_per_line=22)
                item_sec_cell = escape_latex(item_key[1])

                for ri, row in enumerate(item_group):
                    is_first_metric_row = metric_row_idx == 0
                    is_first_case_row = (ii == 0 and ri == 0)
                    is_first_item_row = (ri == 0)
                    is_last_req_in_item = (ri == len(item_group) - 1)
                    is_last_item_in_case = (ij == len(case_group))
                    is_last_case_in_metric = (cj0 == len(metric_group))
                    is_last_row_in_metric = is_last_req_in_item and is_last_item_in_case and is_last_case_in_metric

                    if metric_row_idx == len(metric_group) - 1:
                        metric_piece = tail_chunks[0]
                    else:
                        metric_piece = head_parts[metric_row_idx]
                    metric_row_idx += 1

                    c1 = r"\Seq" if is_first_metric_row else ""
                    c2 = escape_latex_table_cell(metric_piece, chars_per_line=18)
                    c3 = case_cell if is_first_case_row else ""
                    c4 = case_sec_cell if is_first_case_row else ""
                    c5 = item_cell if is_first_item_row else ""
                    c6 = item_sec_cell if is_first_item_row else ""
                    c7 = escape_latex_table_cell(row.get("requirement") or "", chars_per_line=14)
                    c8 = escape_latex_table_cell(row.get("srs_chapter") or "", chars_per_line=12)

                    line = f"{c1} & {c2} & {c3} & {c4} & {c5} & {c6} & {c7} & {c8} \\\\"
                    if is_last_row_in_metric:
                        line += r" \cline{3-8}" if len(tail_chunks) > 1 else r" \hline"
                    elif not is_last_req_in_item:
                        line += r" \cline{7-8}"
                    elif not is_last_item_in_case:
                        line += r" \cline{5-8}"
                    else:
                        line += r" \cline{3-8}"

                    out.append(line)

                ii = ij
            ci0 = cj0

        for extra_idx, extra in enumerate(tail_chunks[1:]):
            content_tex = escape_latex_table_cell(extra, chars_per_line=18)
            out.append(f" & {content_tex} &  &  &  &  &  &  \\\\")
            if extra_idx == len(tail_chunks[1:]) - 1:
                out.append(r" \hline")
        mi = mj

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
    (chapters_dir / "chapter4_generated.tex").write_text(build_chapter4(metrics), encoding="utf-8")
    forward_rows = build_trace_longtable_rows_forward(metrics)
    reverse_rows = build_trace_longtable_rows_reverse(metrics)
    (chapters_dir / "chapter5_trace_rows.tex").write_text(forward_rows, encoding="utf-8")
    (chapters_dir / "chapter6_trace_rows.tex").write_text(reverse_rows, encoding="utf-8")


if __name__ == "__main__":
    main()
