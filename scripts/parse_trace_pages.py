from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


TRACE_RE = re.compile(r"GJBTRACE\s+tbl=([A-Za-z]+)\s+seq=(\d+)\s+row=(\d+)\s+page=(\d+)")


def parse_segments(log_text: str) -> dict[str, dict[str, list[int]]]:
    by_key: dict[tuple[str, str], dict[int, list[int]]] = {}
    for m in TRACE_RE.finditer(log_text):
        tbl = m.group(1)
        seq = m.group(2)
        row = int(m.group(3))
        page = int(m.group(4))
        by_key.setdefault((tbl, seq), {}).setdefault(row, []).append(page)

    segments: dict[str, dict[str, list[int]]] = {}
    for (tbl, seq), row_pages in by_key.items():
        rows_sorted = sorted(row_pages.keys())
        items: list[tuple[int, int]] = []
        for r in rows_sorted:
            pages = row_pages.get(r) or []
            counts: dict[int, int] = {}
            for p in pages:
                counts[p] = counts.get(p, 0) + 1
            if not counts:
                continue
            best_count = max(counts.values())
            best_pages = [p for p, c in counts.items() if c == best_count]
            page = min(best_pages)
            items.append((r, page))

        current_page = None
        current_len = 0
        segs: list[int] = []
        for _, page in items:
            if current_page is None:
                current_page = page
                current_len = 1
                continue
            if page == current_page:
                current_len += 1
                continue
            segs.append(current_len)
            current_page = page
            current_len = 1
        if current_page is not None:
            segs.append(current_len)
        segments.setdefault(tbl, {})[seq] = segs

    return segments


def main() -> None:
    parser = argparse.ArgumentParser(description="解析追踪表分页信息（GJBTRACE）")
    parser.add_argument("--log", required=True, help="编译日志路径（compile_test_detail*.log）")
    parser.add_argument("--out", required=True, help="输出 JSON 路径")
    args = parser.parse_args()

    log_path = Path(args.log).resolve()
    out_path = Path(args.out).resolve()
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    segments = parse_segments(text)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"segments": segments}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
