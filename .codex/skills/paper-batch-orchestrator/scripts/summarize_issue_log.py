#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a batch issue log JSONL file.")
    parser.add_argument("--issues", required=True, help="Path to issues JSONL file")
    parser.add_argument("--top", type=int, default=20, help="How many issue types to show")
    args = parser.parse_args()

    issues_path = Path(args.issues).resolve()
    rows: list[dict[str, Any]] = []
    for raw in issues_path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        rows.append(json.loads(raw))

    counts = Counter()
    papers_by_type: dict[str, set[str]] = defaultdict(set)
    examples: dict[str, dict[str, Any]] = {}
    for row in rows:
        issue_type = str(row.get("issue_type") or row.get("type") or "UNKNOWN")
        counts[issue_type] += 1
        paper_id = row.get("paper_id")
        if paper_id:
            papers_by_type[issue_type].add(str(paper_id))
        examples.setdefault(issue_type, row)

    result = {
        "issues_log": str(issues_path),
        "total_rows": len(rows),
        "top_issue_types": [
            {
                "issue_type": issue_type,
                "count": count,
                "example_papers": sorted(papers_by_type.get(issue_type, set()))[:10],
                "example_message": examples[issue_type].get("message", ""),
            }
            for issue_type, count in counts.most_common(args.top)
        ],
    }

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
