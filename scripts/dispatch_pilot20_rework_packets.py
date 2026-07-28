#!/usr/bin/env python3
"""Create durable owner-worker dispatch packets for pilot-20 rework targets."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PILOT_ROOT = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation" / "pilot20"
PACKET_ROOT = PILOT_ROOT / "source_review_packets"
RESULTS_CSV = PACKET_ROOT / "summary" / "pilot20_true_source_review_results_latest.csv"
TICKETS_JSONL = PACKET_ROOT / "summary" / "pilot20_true_source_review_rework_tickets_latest.jsonl"
OUTDIR = PACKET_ROOT / "owner_rework_dispatch"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except (OSError, RuntimeError, ValueError):
        return str(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                data = json.loads(line)
                if isinstance(data, dict):
                    rows.append(data)
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def owner_for_ticket(ticket: dict[str, Any]) -> str:
    text = json.dumps(ticket, ensure_ascii=False).lower()
    if "mechanism" in text or "ontology" in text or "evidence_class" in text or "direct_assay" in text:
        return "worker-5_mechanism_ontology_extractor"
    if "activity" in text or "toxicity" in text or "mic" in text or "endpoint" in text or "unit" in text:
        return "worker-2_main_text_assay_extractor"
    if "supplement" in text or "ocr" in text or "archive" in text or "missing material" in text:
        return "worker-3_supplementary_methods_extractor"
    if "sequence" in text or "modification" in text or "source_verified" in text or "database" in text:
        return "worker-4_database_record_auditor"
    if "review_report" in text or "adjudicat" in text or "publication_grade" in text:
        return "worker-6_adjudicator_review"
    return "worker-6_adjudicator_review"


def prompt_for_dispatch(dispatch: dict[str, Any]) -> str:
    ticket = dispatch["ticket"]
    owner = dispatch["owner_worker"]
    result_path = dispatch["source_review_result_path"]
    packet_dir = dispatch["review_packet_dir"]
    output_path = dispatch["expected_response_path"]
    return f"""# Pilot20 Owner-Worker Rework Prompt

You are `{owner}` for the AMP Evidence Atlas pilot20 true source-review rework queue.

## Scope

- Work only on this paper and ticket.
- Do not mark publication-grade acceptance yourself unless you are worker-6.
- Preserve conflicts and cautions; do not convert uncertainty into clean source_verified.
- If material is insufficient after best effort, write that explicitly and stop.

## Inputs

- Paper: `{ticket.get('paper_id', '')}`
- Audit record: `{ticket.get('audit_record_id', '')}`
- Ticket id: `{ticket.get('ticket_id', '')}`
- Review packet: `{packet_dir}`
- Source review result: `{result_path}`
- Original ticket source: `{ticket.get('_source_ticket_path', '')}`

Ticket:

```json
{json.dumps(ticket, ensure_ascii=False, indent=2, sort_keys=True)}
```

## Required action

1. Re-open the source review result and the cited packet materials.
2. Repair only the owned layer if local evidence is sufficient.
3. If repair is not safe, write a best-effort blocker with exact missing material or locator.
4. Write `{output_path}` as JSON with:
   - `ticket_id`
   - `paper_id`
   - `owner_worker`
   - `action_taken`: `repair_ready`, `blocked_missing_material`, `needs_upstream_material`, or `defer_to_worker6`
   - `files_to_update_or_review`
   - `source_inputs_checked`
   - `remaining_gaps`
   - `worker6_followup_required`: boolean

Do not edit canonical `papers/<paper_id>/final/` in this dispatch pass unless explicitly running a repair task. This prompt is the durable owner-worker handoff packet.
"""


def main() -> int:
    run_id = stamp()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    results = {row["pilot_sample_id"]: row for row in read_csv(RESULTS_CSV)}
    tickets = read_jsonl(TICKETS_JSONL)
    dispatch_rows: list[dict[str, Any]] = []
    inboxes: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for idx, ticket in enumerate(tickets, 1):
        paper_id = ticket.get("paper_id", "")
        pilot_id = ""
        for candidate, row in results.items():
            if row.get("paper_id") == paper_id and row.get("audit_record_id") == ticket.get("audit_record_id", ""):
                pilot_id = candidate
                break
        if not pilot_id:
            pilot_id = f"UNKNOWN-{idx:03d}"
        owner = owner_for_ticket(ticket)
        dispatch_id = f"dispatch-{idx:03d}-{pilot_id}-{owner.split('_', 1)[0]}"
        dispatch_dir = OUTDIR / dispatch_id
        dispatch_dir.mkdir(parents=True, exist_ok=True)
        review_packet_dir = PACKET_ROOT / f"{pilot_id}__{paper_id}"
        source_result = review_packet_dir / "true_review_result.json"
        response_path = dispatch_dir / "owner_response.json"
        dispatch = {
            "dispatch_schema": "pilot20_owner_worker_rework_dispatch_v1",
            "dispatch_id": dispatch_id,
            "generated_at": now_utc(),
            "pilot_sample_id": pilot_id,
            "paper_id": paper_id,
            "audit_record_id": ticket.get("audit_record_id", ""),
            "owner_worker": owner,
            "target_queue": ticket.get("target_queue", ""),
            "severity": ticket.get("severity", ""),
            "ticket": ticket,
            "review_packet_dir": rel(review_packet_dir),
            "source_review_result_path": rel(source_result),
            "expected_response_path": rel(response_path),
            "completion_claim": "owner_rework_dispatch_packet_ready_not_repaired",
        }
        write_json(dispatch_dir / "dispatch_packet.json", dispatch)
        (dispatch_dir / "OWNER_REWORK_PROMPT.md").write_text(prompt_for_dispatch(dispatch), encoding="utf-8")
        dispatch_row = {
            "dispatch_id": dispatch_id,
            "pilot_sample_id": pilot_id,
            "paper_id": paper_id,
            "audit_record_id": ticket.get("audit_record_id", ""),
            "owner_worker": owner,
            "target_queue": ticket.get("target_queue", ""),
            "severity": ticket.get("severity", ""),
            "ticket_id": ticket.get("ticket_id", ""),
            "dispatch_packet": rel(dispatch_dir / "dispatch_packet.json"),
            "prompt_path": rel(dispatch_dir / "OWNER_REWORK_PROMPT.md"),
            "expected_response_path": rel(response_path),
        }
        dispatch_rows.append(dispatch_row)
        inboxes[owner].append(dispatch)

    fields = [
        "dispatch_id",
        "pilot_sample_id",
        "paper_id",
        "audit_record_id",
        "owner_worker",
        "target_queue",
        "severity",
        "ticket_id",
        "dispatch_packet",
        "prompt_path",
        "expected_response_path",
    ]
    index_path = OUTDIR / f"dispatch_index_{run_id}.csv"
    latest_index = OUTDIR / "dispatch_index_latest.csv"
    write_csv(index_path, dispatch_rows, fields)
    latest_index.write_text(index_path.read_text(encoding="utf-8"), encoding="utf-8")

    for owner, packets in inboxes.items():
        inbox_path = OUTDIR / f"{owner}_inbox.jsonl"
        with inbox_path.open("w", encoding="utf-8") as fh:
            for packet in packets:
                fh.write(json.dumps(packet, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "generated_at": now_utc(),
        "completion_claim": "pilot20_owner_worker_dispatch_ready_not_repaired",
        "source_results_csv": rel(RESULTS_CSV),
        "source_tickets_jsonl": rel(TICKETS_JSONL),
        "dispatch_count": len(dispatch_rows),
        "owner_counts": dict(Counter(row["owner_worker"] for row in dispatch_rows)),
        "severity_counts": dict(Counter(row["severity"] for row in dispatch_rows)),
        "target_queue_counts": dict(Counter(row["target_queue"] for row in dispatch_rows)),
        "outputs": {
            "dispatch_index": rel(index_path),
            "latest_dispatch_index": rel(latest_index),
            "dispatch_root": rel(OUTDIR),
        },
    }
    write_json(OUTDIR / f"dispatch_summary_{run_id}.json", summary)
    write_json(OUTDIR / "dispatch_summary_latest.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
