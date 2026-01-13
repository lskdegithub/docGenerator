import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Issue:
    file: str
    kind: str


TABLE_BEGIN_RE = re.compile(r"\\begin\{(longtblr|talltblr|tblr)\}\[(.*?)\]\{", re.DOTALL)
TABLE_END_RE = re.compile(r"\\end\{(longtblr|talltblr|tblr)\}")
COLSPEC_RE = re.compile(r"colspec\s*=\s*\{([^}]*)\}", re.DOTALL)

FORBIDDEN_TT_RE = re.compile(r"\\ttfamily|\\texttt|\\tt\b")
FORBIDDEN_SIZE_RE = re.compile(r"\\normalsize|\\wuhao(?!hei)|\\large|\\Large|\\LARGE|\\huge|\\Huge")


def scan_tex_tree(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for fp in sorted(root.rglob("*.tex")):
        text = fp.read_text(encoding="utf-8", errors="ignore")

        for m in TABLE_BEGIN_RE.finditer(text):
            opt = m.group(2)
            if "theme=gjb" not in opt and "theme=gjbNoHead" not in opt:
                continue

            spec_start = m.end()
            spec_end = text.find("}", spec_start)
            if spec_end == -1:
                issues.append(Issue(str(fp), "table_spec_not_closed"))
                continue

            spec = text[spec_start:spec_end]
            colspec_m = COLSPEC_RE.search(spec)
            if colspec_m and "|" in colspec_m.group(1):
                if "hlines=" not in spec and "hline{" not in spec:
                    issues.append(Issue(str(fp), "missing_hlines_for_bar_colspec"))

            if "theme=gjbNoHead" in opt and "row{1}" in spec:
                issues.append(Issue(str(fp), "gjbNoHead_has_row1_style"))

            end_m = TABLE_END_RE.search(text, pos=spec_end)
            if end_m:
                body = text[m.start() : end_m.end()]
                if FORBIDDEN_TT_RE.search(body):
                    issues.append(Issue(str(fp), "contains_ttfamily_or_texttt_in_table"))
                if FORBIDDEN_SIZE_RE.search(body):
                    issues.append(Issue(str(fp), "contains_size_override_in_table"))

    return issues


def scan_py_tree(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for fp in sorted(root.rglob("*.py")):
        if fp.name == "audit_tables.py":
            continue
        text = fp.read_text(encoding="utf-8", errors="ignore")
        if FORBIDDEN_TT_RE.search(text):
            issues.append(Issue(str(fp), "script_contains_ttfamily_or_texttt"))
        if FORBIDDEN_SIZE_RE.search(text):
            issues.append(Issue(str(fp), "script_contains_explicit_size"))
    return issues


def print_report(title: str, issues: list[Issue]) -> None:
    counts: dict[str, int] = {}
    for it in issues:
        counts[it.kind] = counts.get(it.kind, 0) + 1

    print(f"{title}: {len(issues)} issues")
    for k in sorted(counts):
        print(f"  - {k}: {counts[k]}")

    shown = 0
    for it in issues:
        if shown >= 30:
            break
        print(f"    {it.kind}: {it.file}")
        shown += 1


def main() -> None:
    repo = Path(__file__).resolve().parents[1]

    tpl = repo / "src" / "doc2tex-template"
    out_tp = repo / "output" / "test_plan" / "chapters"
    scripts = repo / "scripts"

    print_report("TEMPLATE_TEX", scan_tex_tree(tpl))
    if out_tp.exists():
        print_report("GENERATED_TEST_PLAN_TEX", scan_tex_tree(out_tp))
    else:
        print("GENERATED_TEST_PLAN_TEX: output/test_plan/chapters not found")
    print_report("SCRIPTS_PY", scan_py_tree(scripts))


if __name__ == "__main__":
    main()
