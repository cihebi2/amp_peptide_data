#!/usr/bin/env python3
"""Validate the paper-specific ticket-006 final-layer contract."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


EXPECTED_COUNTS = {
    "activity_records": 19,
    "toxicity_records": 0,
    "database_record_audits": 1,
    "mechanism_claims": 6,
    "direct_mechanism_claims": 5,
    "fig5_af_treatment_rows": 12,
    "fig5g_rows": 2,
}

REQUIRED_CAUTIONS = {
    "zero linked authoritative DBAASP rows",
    "fallback machine rows candidate-only and excluded from authoritative release",
    "no source-located toxicity observations",
    "reported prose values outrank secondary figure digitization with uncertainty preserved",
    "predicted or modeled disulfide only, not experimentally confirmed exact bridge pairs",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_key_values(value: Any, key: str, path: str = "$") -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            child_path = f"{path}.{child_key}"
            if child_key == key:
                found.append({"path": child_path, "value": child_value})
            found.extend(find_key_values(child_value, key, child_path))
    elif isinstance(value, list):
        for index, child_value in enumerate(value):
            found.extend(find_key_values(child_value, key, f"{path}[{index}]"))
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    paper = Path(__file__).resolve().parents[2]
    pilot = Path(__file__).resolve().parents[4]
    packet = pilot / "packets" / paper.name
    issues: list[dict[str, Any]] = []
    checks: dict[str, Any] = {}

    pairs = {
        "activity_toxicity_evidence": (
            paper / "final/activity_toxicity_evidence.json",
            packet / "final/activity_toxicity_evidence.json",
        ),
        "database_record_verification": (
            paper / "final/database_record_verification.json",
            packet / "final/database_record_verification.json",
        ),
        "mechanism_ontology_record": (
            paper / "final/mechanism_ontology_record.json",
            packet / "final/mechanism_evidence.json",
        ),
        "review_report": (
            paper / "final/review_report.json",
            packet / "final/review_report.json",
        ),
    }

    mirror_checks: dict[str, Any] = {}
    for name, (paper_path, packet_path) in pairs.items():
        exists = paper_path.exists() and packet_path.exists()
        identical = exists and paper_path.read_bytes() == packet_path.read_bytes()
        mirror_checks[name] = {
            "exists": exists,
            "byte_identical": identical,
            "paper_sha256": sha256(paper_path) if paper_path.exists() else None,
            "packet_sha256": sha256(packet_path) if packet_path.exists() else None,
        }
        if not identical:
            issues.append({"code": "final_mirror_mismatch", "artifact": name})
    checks["mirror_pairs"] = mirror_checks

    layer_paths = {
        name: path_pair[0]
        for name, path_pair in pairs.items()
        if name != "review_report"
    }
    layer_metadata: dict[str, Any] = {}
    reviewed_at_values: set[str] = set()
    layer_docs: dict[str, dict[str, Any]] = {}
    for name, path in layer_paths.items():
        document = read_json(path)
        layer_docs[name] = document
        metadata = {
            key: document.get(key, "<MISSING>")
            for key in (
                "review_status",
                "publication_grade",
                "reviewed_at",
                "review_model",
                "reasoning_effort",
                "source_reviewed",
                "worker6_adjudication",
            )
        }
        layer_metadata[name] = metadata
        expected = {
            "review_status": "accepted_with_cautions",
            "publication_grade": True,
            "review_model": "gpt-5.5",
            "reasoning_effort": "xhigh",
            "source_reviewed": True,
        }
        for key, expected_value in expected.items():
            if document.get(key) != expected_value:
                issues.append(
                    {
                        "code": "final_layer_metadata_mismatch",
                        "artifact": name,
                        "field": key,
                        "expected": expected_value,
                        "actual": document.get(key, "<MISSING>"),
                    }
                )
        reviewed_at = document.get("reviewed_at")
        if not isinstance(reviewed_at, str) or not reviewed_at.strip():
            issues.append(
                {"code": "final_layer_reviewed_at_missing", "artifact": name}
            )
        else:
            reviewed_at_values.add(reviewed_at)
            try:
                dt.datetime.fromisoformat(reviewed_at.replace("Z", "+00:00"))
            except ValueError:
                issues.append(
                    {
                        "code": "final_layer_reviewed_at_invalid",
                        "artifact": name,
                        "actual": reviewed_at,
                    }
                )
        adjudication = document.get("worker6_adjudication")
        expected_adjudication = {
            "worker": "worker-6",
            "decision": "accepted_with_cautions",
            "source_reviewed": True,
        }
        if not isinstance(adjudication, dict):
            issues.append(
                {"code": "worker6_adjudication_missing", "artifact": name}
            )
        else:
            for key, expected_value in expected_adjudication.items():
                if adjudication.get(key) != expected_value:
                    issues.append(
                        {
                            "code": "worker6_adjudication_mismatch",
                            "artifact": name,
                            "field": key,
                            "expected": expected_value,
                            "actual": adjudication.get(key, "<MISSING>"),
                        }
                    )
    if len(reviewed_at_values) != 1:
        issues.append(
            {
                "code": "final_layer_reviewed_at_inconsistent",
                "values": sorted(reviewed_at_values),
            }
        )
    checks["final_layer_metadata"] = layer_metadata
    checks["consistent_reviewed_at_values"] = sorted(reviewed_at_values)

    activity = layer_docs["activity_toxicity_evidence"]
    database = layer_docs["database_record_verification"]
    mechanism = layer_docs["mechanism_ontology_record"]
    review = read_json(pairs["review_report"][0])
    actual_counts = {
        "activity_records": len(activity.get("activity_records") or []),
        "toxicity_records": len(activity.get("toxicity_records") or []),
        "database_record_audits": len(database.get("record_audits") or []),
        "mechanism_claims": len(mechanism.get("mechanism_claims") or []),
        "direct_mechanism_claims": sum(
            1
            for claim in mechanism.get("mechanism_claims") or []
            if claim.get("evidence_class") == "direct_mechanism"
        ),
        "fig5_af_treatment_rows": (activity.get("summary_counts") or {}).get(
            "fig5_af_treatment_rows"
        ),
        "fig5g_rows": (activity.get("summary_counts") or {}).get("fig5g_rows"),
    }
    checks["scientific_counts"] = actual_counts
    for key, expected_value in EXPECTED_COUNTS.items():
        if actual_counts.get(key) != expected_value:
            issues.append(
                {
                    "code": "scientific_count_mismatch",
                    "field": key,
                    "expected": expected_value,
                    "actual": actual_counts.get(key),
                }
            )

    records = database.get("record_audits") or []
    if records:
        record = records[0]
        sequence_check = record.get("sequence_check") or {}
        mature_check = record.get("mature_n_terminal_check") or {}
        disulfide = (
            (record.get("modification_check") or {}).get("reported_disulfides")
            or {}
        )
        identity_checks = {
            "full_sequence_length": sequence_check.get("primary_source_sequence_length"),
            "mature_n_terminal": mature_check.get("mature_n_terminal_edman_sequence"),
            "disulfide_evidence_strength": disulfide.get("evidence_strength"),
            "disulfide_bond_pairs": disulfide.get("bond_pairs"),
            "disulfide_experimental_confirmation": disulfide.get(
                "experimental_confirmation_found"
            ),
        }
        checks["identity_contract"] = identity_checks
        expected_identity = {
            "full_sequence_length": 219,
            "mature_n_terminal": "LPPCVCTRDYR",
            "disulfide_evidence_strength": "predicted_or_modeled_only_not_experimentally_confirmed_in_packet",
            "disulfide_bond_pairs": [],
            "disulfide_experimental_confirmation": False,
        }
        for key, expected_value in expected_identity.items():
            if identity_checks.get(key) != expected_value:
                issues.append(
                    {
                        "code": "identity_contract_mismatch",
                        "field": key,
                        "expected": expected_value,
                        "actual": identity_checks.get(key),
                    }
                )
    else:
        issues.append({"code": "identity_record_missing"})

    ingest_values = find_key_values(database, "authoritative_dbaasp_ingest_ready")
    checks["authoritative_ingest_values"] = ingest_values
    if database.get("authoritative_dbaasp_ingest_ready") is not False:
        issues.append({"code": "top_level_authoritative_ingest_not_false"})
    for item in ingest_values:
        if item["value"] is not False:
            issues.append(
                {
                    "code": "recursive_authoritative_ingest_not_false",
                    "path": item["path"],
                    "actual": item["value"],
                }
            )

    caution_rows = review.get("caution_findings") or []
    preserved_cautions = {
        row.get("required_caution")
        for row in caution_rows
        if isinstance(row, dict) and row.get("preserved_in_final") is True
    }
    checks["required_cautions"] = {
        "expected": sorted(REQUIRED_CAUTIONS),
        "preserved": sorted(value for value in preserved_cautions if value),
    }
    missing_cautions = REQUIRED_CAUTIONS - preserved_cautions
    if missing_cautions:
        issues.append(
            {"code": "required_cautions_missing", "values": sorted(missing_cautions)}
        )
    if review.get("review_status") != "accepted_with_cautions":
        issues.append({"code": "review_report_status_mismatch"})
    if review.get("publication_grade") is not True:
        issues.append({"code": "review_report_publication_grade_mismatch"})
    if review.get("rework_targets") not in ([], None):
        issues.append(
            {
                "code": "review_report_rework_targets_nonzero",
                "actual": review.get("rework_targets"),
            }
        )

    result = {
        "paper_id": paper.name,
        "ticket_id": "rwk-PMC12230126-final-layer-field-assertions-006",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "passed": not issues,
        "issue_count": len(issues),
        "issues": issues,
        "checks": checks,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
