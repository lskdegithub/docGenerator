from __future__ import annotations

import re
import argparse
from pathlib import Path
import yaml
from typing import Optional

PT_TO_CM = 2.54 / 72.27
_DETAIL_CASE_LAYOUT = None
_DETAIL_TRACE_LAYOUT = None


def parse_latex_dim_to_cm(value: str) -> float:
    raw = str(value or "").strip()
    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]+)\s*$", raw)
    if not m:
        raise ValueError(f"Unsupported dimension: {raw}")
    num = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "cm":
        return num
    if unit == "mm":
        return num / 10.0
    if unit == "pt":
        return num * PT_TO_CM
    if unit == "in":
        return num * 2.54
    raise ValueError(f"Unsupported unit: {unit}")


def parse_style_macros(style_path: Path) -> dict:
    text = style_path.read_text(encoding="utf-8")
    macros = {}
    for m in re.finditer(r"\\newcommand\{\\([A-Za-z@]+)\}(?:\[[0-9]+\])?\{([^}]*)\}", text):
        macros[m.group(1)] = m.group(2).strip()
    for m in re.finditer(r"\\def\\([A-Za-z@]+)\{([^}]*)\}", text):
        macros[m.group(1)] = m.group(2).strip()
    return macros


def load_detail_case_layout(repo: Path) -> dict:
    style_path = repo / "src" / "doc2tex-template" / "gjb438c-style.sty"
    macros = parse_style_macros(style_path)
    col_keys = [
        "GjbDetailCaseColA",
        "GjbDetailCaseColB",
        "GjbDetailCaseColC",
        "GjbDetailCaseColD",
        "GjbDetailCaseColE",
        "GjbDetailCaseColF",
        "GjbDetailCaseColG",
        "GjbDetailCaseColH",
    ]
    if not all(k in macros for k in col_keys):
        raise ValueError("Missing GjbDetailCaseCol* macros in gjb438c-style.sty")
    col_widths_cm = [parse_latex_dim_to_cm(macros[k]) for k in col_keys]
    colsep_cm = parse_latex_dim_to_cm(macros.get("GjbDetailCaseColSep", "2.5pt"))

    def span_cm(start_1: int, span: int) -> float:
        i0 = start_1 - 1
        return sum(col_widths_cm[i0 : i0 + span]) + colsep_cm * max(0, span - 1)

    return {
        "col_widths_cm": col_widths_cm,
        "colsep_cm": colsep_cm,
        "case_name_value_cm": span_cm(3, 3),
        "case_ident_value_cm": span_cm(7, 2),
        "span6_value_cm": span_cm(3, 6),
        "steps_action_cm": span_cm(2, 3),
        "steps_expect_cm": span_cm(5, 2),
        "steps_result_cm": span_cm(7, 2),
        "designer_cm": span_cm(3, 3),
        "operator_cm": span_cm(7, 2),
        "tester_cm": span_cm(3, 3),
        "test_time_cm": span_cm(7, 2),
    }


def load_detail_trace_layout(repo: Path) -> dict:
    style_path = repo / "src" / "doc2tex-template" / "gjb438c-style.sty"
    macros = parse_style_macros(style_path)
    col_keys = [
        "GjbDetailTraceColA",
        "GjbDetailTraceColB",
        "GjbDetailTraceColC",
        "GjbDetailTraceColD",
        "GjbDetailTraceColE",
        "GjbDetailTraceColF",
        "GjbDetailTraceColG",
        "GjbDetailTraceColH",
    ]
    if not all(k in macros for k in col_keys):
        raise ValueError("Missing GjbDetailTraceCol* macros in gjb438c-style.sty")
    col_widths_cm = [parse_latex_dim_to_cm(macros[k]) for k in col_keys]
    colsep_cm = parse_latex_dim_to_cm(macros.get("GjbDetailTraceColSep", "2pt"))
    return {"col_widths_cm": col_widths_cm, "colsep_cm": colsep_cm}


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
    token = "GJBALLOWBREAKTOKEN"
    def break_alnum(match: re.Match) -> str:
        s = match.group(0)
        chunk = 6
        return token.join([s[i:i + chunk] for i in range(0, len(s), chunk)])
    text = re.sub(r"[A-Za-z0-9]{8,}", break_alnum, text)
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
    text = re.sub(r"(?<=\d)\.(?=\d)", r".\\allowbreak ", text)
    text = re.sub(r"([\u4E00-\u9FFF])([A-Za-z0-9])", r"\1\\allowbreak \2", text)
    text = re.sub(r"([A-Za-z0-9])([\u4E00-\u9FFF])", r"\1\\allowbreak \2", text)
    text = text.replace(token, r"\allowbreak ")
    return " ".join(text.split())


def escape_latex_no_wordbreak(text: str) -> str:
    text = str(text or "")
    token = "GJBALLOWBREAKTOKEN"
    def break_alnum(match: re.Match) -> str:
        s = match.group(0)
        chunk = 6
        return token.join([s[i:i + chunk] for i in range(0, len(s), chunk)])
    text = re.sub(r"[A-Za-z0-9]{8,}", break_alnum, text)
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
    text = re.sub(r"([,.;:])", r"\1\\allowbreak ", text)
    text = re.sub(r"(?<=\d)\.(?=\d)", r".\\allowbreak ", text)
    text = re.sub(r"([\u4E00-\u9FFF])([A-Za-z0-9])", r"\1\\allowbreak \2", text)
    text = re.sub(r"([A-Za-z0-9])([\u4E00-\u9FFF])", r"\1\\allowbreak \2", text)
    text = text.replace(token, r"\allowbreak ")
    return " ".join(text.split())


def escape_latex_table_cell_soft(text: str) -> str:
    return escape_latex_no_wordbreak(text)


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


def format_name_ident_multiline(name: str, ident: str, width_cm: Optional[float] = None) -> str:
    name = str(name or "").strip()
    ident = str(ident or "").strip()
    global _DETAIL_CASE_LAYOUT
    if width_cm is None:
        width_cm = (_DETAIL_CASE_LAYOUT or {}).get("span6_value_cm", 11.6)
    if not ident:
        return escape_latex_table_cell_soft(name)

    combined = f"{name}（{ident}）"
    wrapped = escape_latex_table_cell_multiline(combined, width_cm=float(width_cm), dont_split_english=True)
    if r"\GjbCellBreak" not in wrapped:
        return wrapped

    name_wrapped = escape_latex_table_cell_multiline(name, width_cm=float(width_cm), dont_split_english=True)
    escaped_ident = escape_latex(ident)
    return f"{name_wrapped}\\GjbCellBreak （{escaped_ident}）"


def escape_latex_table_cell_multiline(
    text: str,
    width_cm: float,
    dont_split_english: bool = True,
    cjk_chars_per_cm: float = 3.2,
    ascii_units: float = 0.55,
    punct_units: float = 0.6,
) -> str:
    text = str(text or "")
    width_cm = float(width_cm or 0)
    if width_cm <= 0:
        return escape_latex_no_wordbreak(text)

    max_units = max(1, int(width_cm * float(cjk_chars_per_cm)))

    def is_cjk(ch: str) -> bool:
        code = ord(ch)
        return (
            0x4E00 <= code <= 0x9FFF
            or 0x3400 <= code <= 0x4DBF
            or 0x20000 <= code <= 0x2A6DF
            or 0x2A700 <= code <= 0x2B73F
            or 0x2B740 <= code <= 0x2B81F
            or 0x2B820 <= code <= 0x2CEAF
            or 0xF900 <= code <= 0xFAFF
        )

    def token_units(token: str) -> float:
        if not token:
            return 0.0
        if token.isspace():
            return 0.0
        total = 0.0
        for ch in token:
            if is_cjk(ch):
                total += 1.0
            elif ch.isalnum():
                total += float(ascii_units)
            else:
                total += float(punct_units)
        return total

    break_after = set("，。、；;：:,.!?！？)）")

    def split_preserving_words(paragraph: str):
        paragraph = " ".join(str(paragraph or "").split())
        if not paragraph:
            return []
        tokens = []
        ascii_buf = []
        for ch in paragraph:
            if ch == " ":
                if ascii_buf:
                    tokens.append("".join(ascii_buf))
                    ascii_buf = []
                continue
            if is_cjk(ch):
                if ascii_buf:
                    tokens.append("".join(ascii_buf))
                    ascii_buf = []
                tokens.append(ch)
                continue
            if ch.isascii() and (ch.isalnum() or ch in {"-", "_"}):
                ascii_buf.append(ch)
                continue
            if ascii_buf:
                tokens.append("".join(ascii_buf))
                ascii_buf = []
            tokens.append(ch)
        if ascii_buf:
            tokens.append("".join(ascii_buf))

        merged = []
        for tok in tokens:
            if tok in break_after and merged:
                merged[-1] = merged[-1] + tok
            else:
                merged.append(tok)
        return merged

    def wrap_tokens(tokens):
        lines = []
        current = []
        used = 0.0
        for tok in tokens:
            if tok == " ":
                continue
            units = token_units(tok)
            if not current:
                current.append(tok)
                used = units
                continue
            if used + units <= max_units:
                current.append(tok)
                used += units
                continue
            if dont_split_english and tok.isascii() and tok.replace("-", "").isalpha():
                lines.append("".join(current))
                current = [tok]
                used = units
                continue
            lines.append("".join(current))
            current = [tok]
            used = units
        if current:
            lines.append("".join(current))
        return lines

    def escape_for_table_keep_words(s: str) -> str:
        s = escape_latex_no_wordbreak(s)
        def break_long_id(m: re.Match) -> str:
            t = m.group(0)
            if t.isalpha():
                return t
            chunk = 16
            return r"\allowbreak ".join([t[i:i + chunk] for i in range(0, len(t), chunk)])
        return re.sub(r"(?<!\\)[A-Za-z0-9]{24,}", break_long_id, s)

    paragraphs = [p for p in re.split(r"\n+", text) if p.strip()]
    if not paragraphs:
        return ""

    out_lines = []
    for para in paragraphs:
        tokens = split_preserving_words(para)
        for line in wrap_tokens(tokens):
            out_lines.append(escape_for_table_keep_words(line))
    return r"\GjbCellBreak ".join(out_lines)


def chunk_text_for_table(text: str, max_chars: int) -> list[str]:
    text = str(text or "").strip()
    if not text:
        return [""]
    max_chars = int(max_chars or 0)
    if max_chars <= 0:
        return [text]
    breaks = set("。！？；;!?，、")
    chunks = []
    buf = []
    last_break_pos = -1
    for ch in text:
        buf.append(ch)
        if ch in breaks:
            last_break_pos = len(buf)
        if len(buf) >= max_chars:
            if last_break_pos > 0 and last_break_pos < len(buf):
                chunks.append("".join(buf[:last_break_pos]).strip())
                buf = buf[last_break_pos:]
            else:
                chunks.append("".join(buf).strip())
                buf = []
            last_break_pos = -1
    if buf:
        chunks.append("".join(buf).strip())
    return [c for c in chunks if c]


def estimate_table_lines(text: str, width_cm: float, cjk_chars_per_cm: float = 3.2, ascii_units: float = 0.55, punct_units: float = 0.6) -> int:
    text = str(text or "")
    width_cm = float(width_cm or 0)
    if not text or width_cm <= 0:
        return 1
    cjk = len(re.findall(r"[\u4E00-\u9FFF]", text))
    ascii_alnum = len(re.findall(r"[A-Za-z0-9]", text))
    space = len(re.findall(r"\s", text))
    punct = max(0, len(text) - cjk - ascii_alnum - space)
    units = float(cjk) + float(ascii_units) * float(ascii_alnum) + float(punct_units) * float(punct)
    per_line = max(1.0, float(width_cm) * float(cjk_chars_per_cm))
    return max(1, int((units + per_line - 1) // per_line))


def _strip_latex_commands_for_estimate(s: str) -> str:
    s = str(s or "")
    s = re.sub(r"\\[A-Za-z@]+(\s*\[[^\]]*\])?(\s*\{[^}]*\})?", "", s)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("\\", "")
    s = s.replace("_", "_")
    return s


def estimate_case_table_height_cm(case_data: dict, test_item_label: str, layout: dict) -> float:
    line_height_cm = 11.0 * PT_TO_CM
    row_padding_cm = 0.20

    def row_height_by_lines(lines: int) -> float:
        return float(lines) * line_height_cm + row_padding_cm

    wd_case_name = float(layout.get("case_name_value_cm", 6.56))
    wd_case_ident = float(layout.get("case_ident_value_cm", 2.76))
    wd_span6 = float(layout.get("span6_value_cm", 11.6))
    wd_designer = float(layout.get("designer_cm", 6.56))
    wd_operator = float(layout.get("operator_cm", 2.76))
    wd_tester = float(layout.get("tester_cm", 6.56))
    wd_test_time = float(layout.get("test_time_cm", 2.76))
    wd_steps_action = float(layout.get("steps_action_cm", 5.7))
    wd_steps_expect = float(layout.get("steps_expect_cm", 4.56))

    total = 0.0

    lines_case_name = estimate_table_lines(case_data.get("测试用例名称", ""), width_cm=wd_case_name)
    lines_case_ident = estimate_table_lines(case_data.get("标识", ""), width_cm=wd_case_ident)
    total += row_height_by_lines(max(lines_case_name, lines_case_ident, 1))

    lines_trace = estimate_table_lines(_strip_latex_commands_for_estimate(test_item_label), width_cm=wd_span6)
    total += row_height_by_lines(max(lines_trace, 1))

    for k in ["测试用例综述", "用例初始化", "前提与约束", "测试用例类型"]:
        total += row_height_by_lines(estimate_table_lines(case_data.get(k, ""), width_cm=wd_span6))

    total += row_height_by_lines(1)
    total += row_height_by_lines(1)

    steps = case_data.get("测试步骤", [])
    if not isinstance(steps, list):
        steps = []
    if not steps:
        steps = [{"序号": 1, "输入及操作": "", "期望结果": ""}]
    for step in steps:
        lines_action = estimate_table_lines(step.get("输入及操作", ""), width_cm=wd_steps_action)
        lines_expect = estimate_table_lines(step.get("期望结果", ""), width_cm=wd_steps_expect)
        total += row_height_by_lines(max(lines_action, lines_expect, 1))

    for k in ["测试用例终止条件", "测试结果判定准则", "测试用例执行结果"]:
        total += row_height_by_lines(estimate_table_lines(case_data.get(k, ""), width_cm=wd_span6))

    lines_designer = estimate_table_lines(case_data.get("设计人员", ""), width_cm=wd_designer)
    lines_operator = estimate_table_lines(case_data.get("操作人员", ""), width_cm=wd_operator)
    total += row_height_by_lines(max(lines_designer, lines_operator, 1))

    lines_tester = estimate_table_lines(case_data.get("测试人员", ""), width_cm=wd_tester)
    lines_test_time = estimate_table_lines(case_data.get("测试时间", ""), width_cm=wd_test_time)
    total += row_height_by_lines(max(lines_tester, lines_test_time, 1))

    total *= 1.10
    return total


def split_text_to_fit_lines(text: str, width_cm: float, max_lines: int) -> tuple[str, str]:
    text = str(text or "")
    if not text:
        return "", ""
    width_cm = float(width_cm or 0)
    if width_cm <= 0 or max_lines <= 0:
        return "", text
    per_line = max(1.0, float(width_cm) * 3.2)
    max_units = float(max_lines) * per_line
    breaks = set("。！？；;!?，、,.")
    head_chars = []
    used = 0.0
    last_break_at = -1
    for i, ch in enumerate(text):
        if re.match(r"[\u4E00-\u9FFF]", ch):
            u = 1.0
        elif ch.isalnum():
            u = 0.55
        elif ch.isspace():
            u = 0.0
        else:
            u = 0.6
        if used + u > max_units:
            cut = last_break_at + 1 if last_break_at >= 0 else i
            head = text[:cut].strip()
            tail = text[cut:].strip()
            return head, tail
        head_chars.append(ch)
        used += u
        if ch in breaks:
            last_break_at = i
    return text.strip(), ""


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
    global _DETAIL_CASE_LAYOUT
    layout = _DETAIL_CASE_LAYOUT or {"steps_action_cm": 5.7, "steps_expect_cm": 4.56, "steps_result_cm": 2.76}
    wd_action = f"{float(layout.get('steps_action_cm', 5.7)):.3f}cm"
    wd_expect = f"{float(layout.get('steps_expect_cm', 4.56)):.3f}cm"
    wd_result = f"{float(layout.get('steps_result_cm', 2.76)):.3f}cm"
    for idx, step in enumerate(steps, start=1):
        seq = step.get("序号", idx)
        action_raw = str(step.get("输入及操作", "") or "")
        expect_raw = str(step.get("期望结果", "") or "")
        action = escape_latex_table_cell_soft(action_raw)
        expect = escape_latex_table_cell_soft(expect_raw)
        rows.append(
            f"{seq} & \\SetCell[c=3]{{wd={wd_action},valign=t}}{{{action}}} &  &  & \\SetCell[c=2]{{wd={wd_expect},valign=t}}{{{expect}}} &  & \\SetCell[c=2]{{wd={wd_result},valign=t}}{{}} &  \\\\"
        )
    return "\n".join(rows)


def build_case_table(case_data, test_item_label, label_suffix):
    global _DETAIL_CASE_LAYOUT
    layout = _DETAIL_CASE_LAYOUT or {
        "case_name_value_cm": 6.56,
        "case_ident_value_cm": 2.76,
        "span6_value_cm": 11.6,
        "designer_cm": 6.56,
        "operator_cm": 2.76,
        "tester_cm": 6.56,
        "test_time_cm": 2.76,
    }
    wd_case_name = f"{float(layout.get('case_name_value_cm', 6.56)):.3f}cm"
    wd_case_ident = f"{float(layout.get('case_ident_value_cm', 2.76)):.3f}cm"
    wd_span6 = f"{float(layout.get('span6_value_cm', 11.6)):.3f}cm"
    wd_designer = f"{float(layout.get('designer_cm', 6.56)):.3f}cm"
    wd_operator = f"{float(layout.get('operator_cm', 2.76)):.3f}cm"
    wd_tester = f"{float(layout.get('tester_cm', 6.56)):.3f}cm"
    wd_test_time = f"{float(layout.get('test_time_cm', 2.76)):.3f}cm"
    needspace_cm = min(estimate_case_table_height_cm(case_data, test_item_label, layout), 23.0)
    case_name_caption = escape_latex(case_data.get("测试用例名称", ""))
    case_name = escape_latex_table_cell_soft(case_data.get("测试用例名称", ""))
    case_ident = escape_latex(case_data.get("标识", ""))
    summary = escape_latex_table_cell_soft(case_data.get("测试用例综述", ""))
    init = escape_latex_table_cell_soft(case_data.get("用例初始化", ""))
    prereq = escape_latex_table_cell_soft(case_data.get("前提与约束", ""))
    case_type = escape_latex_table_cell_soft(case_data.get("测试用例类型", ""))
    term = escape_latex_table_cell_soft(case_data.get("测试用例终止条件", ""))
    criteria = escape_latex_table_cell_soft(case_data.get("测试结果判定准则", ""))
    result = escape_latex_table_cell_soft(case_data.get("测试用例执行结果", ""))
    designer = escape_latex_table_cell_soft(case_data.get("设计人员", ""))
    operator = escape_latex_table_cell_soft(case_data.get("操作人员", ""))
    tester = escape_latex_table_cell_soft(case_data.get("测试人员", ""))
    test_time = escape_latex_table_cell_soft(case_data.get("测试时间", ""))
    steps_rows = build_steps_table(case_data.get("测试步骤", []))
    label = f"tbl:detail-tc-{sanitize_label(label_suffix)}"
    caption = case_name_caption or "测试用例"
    table = f"""\\Needspace{{{needspace_cm:.2f}cm}}
{{\\settablespacing
\\begin{{longtblr}}[theme=gjbNoHead,caption={{{caption}}},label={{{label}}}]{{
  width=\\GjbDetailCaseTableWidth,
  leftsep=\\GjbDetailCaseLeftSep,
  rightsep=\\GjbDetailCaseRightSep,
  colsep=\\GjbDetailCaseColSep,
  colspec={{|Q[c,\\GjbDetailCaseColA]|Q[\\GjbDetailCaseColB]|Q[\\GjbDetailCaseColC]|Q[\\GjbDetailCaseColD]|Q[\\GjbDetailCaseColE]|Q[\\GjbDetailCaseColF]|Q[\\GjbDetailCaseColG]|Q[\\GjbDetailCaseColH]|}},
  hlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},
  vline{{1,2,3,4,5,6,7,8,Z}}={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},
}}
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试用例名称}}}} & & \\SetCell[c=3]{{wd={wd_case_name},valign=t}}{{{case_name}}} &  &  & \\TableKeyCell{{标识}} & \\SetCell[c=2]{{wd={wd_case_ident},valign=t}}{{\\TableIdentifier{{{case_ident}}}}} & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{追踪关系}}}} & & \\SetCell[c=6]{{wd={wd_span6},valign=t}}{{{test_item_label}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试用例综述}}}} & & \\SetCell[c=6]{{wd={wd_span6},valign=t}}{{{summary}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{用例初始化}}}} & & \\SetCell[c=6]{{wd={wd_span6},valign=t}}{{{init}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{前提和约束}}}} & & \\SetCell[c=6]{{wd={wd_span6},valign=t}}{{{prereq}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试用例类型}}}} & & \\SetCell[c=6]{{wd={wd_span6},valign=t}}{{{case_type}}} &  &  &  &  & \\\\
\\SetCell[c=8]{{halign=c,font=\\xiaowuhei}}{{测试步骤}} &  &  &  &  &  &  & \\\\
\\SetCell{{font=\\xiaowuhei,halign=c,valign=m}}{{序号}} & \\SetCell[c=3]{{font=\\xiaowuhei,halign=c,valign=m}}{{输入及操作}} &  &  & \\SetCell[c=2]{{font=\\xiaowuhei,halign=c,valign=m}}{{期望结果}} &  & \\SetCell[c=2]{{font=\\xiaowuhei,halign=c,valign=m}}{{测试结果}} &  \\\\
{steps_rows}
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试用例终止条件}}}} & & \\SetCell[c=6]{{wd={wd_span6},valign=t}}{{{term}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试结果评估标准}}}} & & \\SetCell[c=6]{{wd={wd_span6},valign=t}}{{{criteria}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试用例执行结果}}}} & & \\SetCell[c=6]{{wd={wd_span6},valign=t}}{{{result}}} &  &  &  &  & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{设计人员}}}} & & \\SetCell[c=3]{{wd={wd_designer},valign=t}}{{{designer}}} &  &  & \\TableKeyCell{{操作人员}} & \\SetCell[c=2]{{wd={wd_operator},valign=t}}{{{operator}}} & \\\\
\\SetCell[c=2]{{halign=c}}{{\\TableKeyCell{{测试人员}}}} & & \\SetCell[c=3]{{wd={wd_tester},valign=t}}{{{tester}}} &  &  & \\TableKeyCell{{测试时间}} & \\SetCell[c=2]{{wd={wd_test_time},valign=t}}{{{test_time}}} & \\\\
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
        label = format_name_ident_multiline(item.get("name"), item.get("ident"), width_cm=12.0)
        item_type = escape_latex(item["type"])
        table_rows.append(f"\\Seq & {{\\xiaowu {item_type}}} & {{\\xiaowu {label}}} \\\\")
    table_rows_text = "\n".join(table_rows)
    content = f"""\\subsection{{计划执行的测试}}

{intro}

计划执行的测试项列表如表 \\ref{{tbl:detail-testitems}}所示。

{{\\settablespacing
\\begin{{longtblr}}[theme=gjb,caption={{测试项列表}},label={{tbl:detail-testitems}}]{{
  colspec={{c p{{4.0cm}} X}},
  rowhead=1,
  hlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},
  vlines={{wd=\\GjbTableRuleWd,fg=\\GjbTableRuleColor}},
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
                test_item_label = format_name_ident_multiline(item.get("name"), item.get("ident"))
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


def generate_trace_table_forward_full(metrics):
    rows = build_trace_rows(metrics)
    body_lines = []
    seq = 1
    i = 0
    while i < len(rows):
        metric_content = rows[i].get("metric_content") or ""
        j = i
        while j < len(rows) and (rows[j].get("metric_content") or "") == metric_content:
            j += 1
        group = rows[i:j]
        contract_parts = split_by_max_chars(metric_content, max_chars=60)
        contract_parts_escaped = [escape_latex_table_cell_soft(p) for p in contract_parts]
        contract_part_idx = 0
        will_need_extra_contract_rows = len(contract_parts_escaped) > len(group)
        k = 0
        while k < len(group):
            req_item_key = (
                group[k].get("requirement") or "",
                group[k].get("srs_chapter") or "",
                group[k].get("test_item") or "",
                group[k].get("item_section") or "",
            )
            m = k
            while m < len(group) and (
                (group[m].get("requirement") or "", group[m].get("srs_chapter") or "", group[m].get("test_item") or "", group[m].get("item_section") or "")
                == req_item_key
            ):
                m += 1
            span = m - k

            for kk in range(k, m):
                row = group[kk]
                is_first_row_in_contract = (kk == 0)
                is_first_row_in_group = (kk == k)
                is_last_row_in_group = (kk == m - 1)
                is_last_row_in_contract = (kk == len(group) - 1)
                is_last_row_in_contract_effective = is_last_row_in_contract and not will_need_extra_contract_rows
                contract_piece = contract_parts_escaped[contract_part_idx] if contract_part_idx < len(contract_parts_escaped) else ""
                contract_part_idx += 1

                c1 = f"{seq}" if is_first_row_in_contract else ""
                c2 = contract_piece

                if is_first_row_in_group:
                    req_cell = escape_latex_table_cell_soft(req_item_key[0])
                    srs_cell = escape_latex(req_item_key[1])
                    item_cell = escape_latex_table_cell_soft(req_item_key[2])
                    item_sec_cell = escape_latex(req_item_key[3])
                    c3 = f"\\SetCell[r={span}]{{l,t}} {{{req_cell}}}"
                    c4 = f"\\SetCell[r={span}]{{c,t}} {{{srs_cell}}}"
                    c5 = f"\\SetCell[r={span}]{{l,t}} {{{item_cell}}}"
                    c6 = f"\\SetCell[r={span}]{{c,t}} {{{item_sec_cell}}}"
                else:
                    c3 = ""
                    c4 = ""
                    c5 = ""
                    c6 = ""

                c7 = escape_latex_table_cell_soft(row.get("case_name") or "")
                c8 = escape_latex(row.get("case_section") or "")

                line = f"{c1} & {c2} & {c3} & {c4} & {c5} & {c6} & {c7} & {c8} \\\\"

                if is_last_row_in_contract_effective:
                    line += r" \hline"
                elif not is_last_row_in_group:
                    line += r" \cline{7-8}"
                else:
                    line += r" \cline{3-8}"

                body_lines.append(line)

            k = m
        while contract_part_idx < len(contract_parts_escaped):
            contract_piece = contract_parts_escaped[contract_part_idx]
            contract_part_idx += 1
            is_last_extra = contract_part_idx >= len(contract_parts_escaped)
            line = f" & {contract_piece} &  &  &  &  &  &  \\\\"
            line += (r" \hline" if is_last_extra else r" \cline{2-2}")
            body_lines.append(line)

        i = j
        seq += 1

    body_text = "\n".join(body_lines)
    head_contract = r"合同/\allowbreak 补充协议/\allowbreak xxxxx/\allowbreak xxxxx"
    latex = f"""\\Needspace{{6cm}}
{{\\settablespacing
\\begin{{longtblr}}[theme=gjb,caption={{需求到测试用例的追踪关系表}},label={{tbl:detail-req-to-case}}]{{
  width=\\GjbDetailTraceTableWidth,
  leftsep=\\GjbDetailTraceLeftSep,
  rightsep=\\GjbDetailTraceRightSep,
  colsep=\\GjbDetailTraceColSep,
  colspec={{|Q[c,t,\\GjbDetailTraceColA]|Q[l,t,\\GjbDetailTraceColB]|Q[l,t,\\GjbDetailTraceColC]|Q[c,t,\\GjbDetailTraceColD]|Q[l,t,\\GjbDetailTraceColE]|Q[c,t,\\GjbDetailTraceColF]|Q[l,t,\\GjbDetailTraceColG]|Q[c,t,\\GjbDetailTraceColH]|}},
  rowhead=2,
  row{{1,2}}={{font=\\xiaowuhei}},
}}
\\hline
\\SetCell[r=2]{{c}} 序号 & \\SetCell[r=2]{{c}} {head_contract} & \\SetCell[c=2]{{c}} 需求规格说明书 & & \\SetCell[c=2]{{c}} 测试项 & & \\SetCell[c=2]{{c}} 测试用例 & \\\\
\\hline
 & & 需求名称/\\allowbreak 标识 & 需规章节号 & 测试项名称/\\allowbreak 标识 & 本文档章节号 & 测试用例名称/\\allowbreak 标识 & 测试章节号 \\\\
\\hline
{body_text}
\\end{{longtblr}}
}}
\\vspace{{0pt}}
"""
    return latex


def generate_trace_table_reverse_full(metrics):
    rows = build_trace_rows(metrics)
    body_lines = []
    seq = 1
    i = 0
    while i < len(rows):
        metric_content = rows[i].get("metric_content") or ""
        j = i
        while j < len(rows) and (rows[j].get("metric_content") or "") == metric_content:
            j += 1
        group = rows[i:j]
        contract_parts = split_by_max_chars(metric_content, max_chars=60)
        contract_parts_escaped = [escape_latex_table_cell_soft(p) for p in contract_parts]
        contract_part_idx = 0
        will_need_extra_contract_rows = len(contract_parts_escaped) > len(group)
        k = 0
        while k < len(group):
            req_item_key = (
                group[k].get("requirement") or "",
                group[k].get("srs_chapter") or "",
                group[k].get("test_item") or "",
                group[k].get("item_section") or "",
            )
            m = k
            while m < len(group) and (
                (group[m].get("requirement") or "", group[m].get("srs_chapter") or "", group[m].get("test_item") or "", group[m].get("item_section") or "")
                == req_item_key
            ):
                m += 1
            span = m - k

            for kk in range(k, m):
                row = group[kk]
                is_first_row_in_contract = (kk == 0)
                is_first_row_in_group = (kk == k)
                is_last_row_in_group = (kk == m - 1)
                is_last_row_in_contract = (kk == len(group) - 1)
                is_last_row_in_contract_effective = is_last_row_in_contract and not will_need_extra_contract_rows
                contract_piece = contract_parts_escaped[contract_part_idx] if contract_part_idx < len(contract_parts_escaped) else ""
                contract_part_idx += 1

                c1 = f"{seq}" if is_first_row_in_contract else ""
                c2 = contract_piece
                c3 = escape_latex_table_cell_soft(row.get("case_name") or "")
                c4 = escape_latex(row.get("case_section") or "")

                if is_first_row_in_group:
                    item_cell = escape_latex_table_cell_soft(req_item_key[2])
                    item_sec_cell = escape_latex(req_item_key[3])
                    req_cell = escape_latex_table_cell_soft(req_item_key[0])
                    srs_cell = escape_latex(req_item_key[1])
                    c5 = f"\\SetCell[r={span}]{{l,t}} {{{item_cell}}}"
                    c6 = f"\\SetCell[r={span}]{{c,t}} {{{item_sec_cell}}}"
                    c7 = f"\\SetCell[r={span}]{{l,t}} {{{req_cell}}}"
                    c8 = f"\\SetCell[r={span}]{{c,t}} {{{srs_cell}}}"
                else:
                    c5 = ""
                    c6 = ""
                    c7 = ""
                    c8 = ""

                line = f"{c1} & {c2} & {c3} & {c4} & {c5} & {c6} & {c7} & {c8} \\\\"

                if is_last_row_in_contract_effective:
                    line += r" \hline"
                elif not is_last_row_in_group:
                    line += r" \cline{3-4}"
                else:
                    line += r" \cline{3-8}"

                body_lines.append(line)

            k = m
        while contract_part_idx < len(contract_parts_escaped):
            contract_piece = contract_parts_escaped[contract_part_idx]
            contract_part_idx += 1
            is_last_extra = contract_part_idx >= len(contract_parts_escaped)
            line = f" & {contract_piece} &  &  &  &  &  &  \\\\"
            line += (r" \hline" if is_last_extra else r" \cline{2-2}")
            body_lines.append(line)

        i = j
        seq += 1

    body_text = "\n".join(body_lines)
    head_contract = r"合同/\allowbreak 补充协议/\allowbreak xxxxx/\allowbreak xxxxx"
    latex = f"""\\Needspace{{6cm}}
{{\\settablespacing
\\begin{{longtblr}}[theme=gjb,caption={{测试用例到需求的追踪关系表}},label={{tbl:detail-case-to-req}}]{{
  width=\\GjbDetailTraceTableWidth,
  leftsep=\\GjbDetailTraceLeftSep,
  rightsep=\\GjbDetailTraceRightSep,
  colsep=\\GjbDetailTraceColSep,
  colspec={{|Q[c,t,\\GjbDetailTraceColA]|Q[l,t,\\GjbDetailTraceColB]|Q[l,t,\\GjbDetailTraceColC]|Q[c,t,\\GjbDetailTraceColD]|Q[l,t,\\GjbDetailTraceColE]|Q[c,t,\\GjbDetailTraceColF]|Q[l,t,\\GjbDetailTraceColG]|Q[c,t,\\GjbDetailTraceColH]|}},
  rowhead=2,
  row{{1,2}}={{font=\\xiaowuhei}},
}}
\\hline
\\SetCell[r=2]{{c}} 序号 & \\SetCell[r=2]{{c}} {head_contract} & \\SetCell[c=2]{{c}} 测试用例 & & \\SetCell[c=2]{{c}} 测试项 & & \\SetCell[c=2]{{c}} 需求规格说明书 & \\\\
\\hline
 & & 测试用例名称/\\allowbreak 标识 & 测试章节号 & 测试项名称/\\allowbreak 标识 & 本文档章节号 & 需求名称/\\allowbreak 标识 & 需规章节号 \\\\
\\hline
{body_text}
\\end{{longtblr}}
}}
\\vspace{{0pt}}
"""
    return latex


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
    global _DETAIL_CASE_LAYOUT
    _DETAIL_CASE_LAYOUT = load_detail_case_layout(repo)
    global _DETAIL_TRACE_LAYOUT
    _DETAIL_TRACE_LAYOUT = load_detail_trace_layout(repo)
    data_dir = (repo / args.data).resolve()
    out_dir = (repo / args.out).resolve()

    chapters_dir = out_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    metrics = collect_data(data_dir)
    (chapters_dir / "chapter4_generated.tex").write_text(build_chapter4(metrics), encoding="utf-8")
    (chapters_dir / "chapter5_generated.tex").write_text(generate_trace_table_forward_full(metrics), encoding="utf-8")
    (chapters_dir / "chapter6_generated.tex").write_text(generate_trace_table_reverse_full(metrics), encoding="utf-8")


if __name__ == "__main__":
    main()
