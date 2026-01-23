from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


TRACE_RE = re.compile(r"GJBTRACE\s+tbl=([A-Za-z]+)\s+seq=(\d+)\s+row=(\d+)\s+page=(\d+)")


def parse_segments(log_text: str) -> dict[str, dict[str, list[int]]]:
    by_key: dict[tuple[str, str], dict[int, int]] = {}
    for m in TRACE_RE.finditer(log_text):
        tbl = m.group(1)
        seq = m.group(2)
        row = int(m.group(3))
        page = int(m.group(4))
        by_key.setdefault((tbl, seq), {})[row] = page

    segments: dict[str, dict[str, list[int]]] = {}
    for (tbl, seq), row_pages in by_key.items():
        items = sorted(row_pages.items(), key=lambda t: t[0])

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
