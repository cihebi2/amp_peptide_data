#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "PMC11672609"
TICKET_IDS = [
    "rwk-PMC11672609-campaign-r02-BF-W2-ACTIVITY-TOXICITY-FIELD-INTEGRITY",
    "rwk-PMC11672609-campaign-r02-BF-W4-DATABASE-FINAL-MATERIAL-OBSERVATION-STALE",
    "rwk-PMC11672609-campaign-r02-BF-W5-MECHANISM-FINAL-SUPPLEMENT-CAUTION-STALE",
]

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers" / PAPER_ID
PACKET = ROOT / "packets" / PAPER_ID
WORK_REVIEW = PAPER / "work" / "review"
VALIDATION = WORK_REVIEW / "validation"
PAPER_FINAL = PAPER / "final"
PACKET_FINAL = PACKET / "final"
RESPONSES = PACKET / "rework" / "rework_responses.jsonl"
RECEIPTS = PACKET / "rework" / "closure_receipts.jsonl"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict):
            rows.append(row)
    return rows


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def terminal_response_sha256(row: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def first_list(payload: dict[str, Any], names: list[str]) -> list[Any]:
    for name in names:
        value = payload.get(name)
        if isinstance(value, list):
            return value
    return []


def final_counts() -> dict[str, int]:
    activity = read_json(PAPER_FINAL / "activity_toxicity_evidence.json")
    database = read_json(PAPER_FINAL / "database_record_verification.json")
    mechanism = read_json(PAPER_FINAL / "mechanism_ontology_record.json")
    review = read_json(PAPER_FINAL / "review_report.json")
    return {
        "activity_records": len(activity.get("activity_records") if isinstance(activity.get("activity_records"), list) else []),
        "toxicity_records": len(activity.get("toxicity_records") if isinstance(activity.get("toxicity_records"), list) else []),
        "database_record_audits": len(first_list(database, ["record_audits", "record_identity_audit", "database_record_audits"])),
        "mechanism_claims": len(mechanism.get("mechanism_claims") if isinstance(mechanism.get("mechanism_claims"), list) else []),
        "review_rework_targets": len(review.get("rework_targets") if isinstance(review.get("rework_targets"), list) else []),
    }


def verified_artifact_paths() -> dict[str, Any]:
    return {
        "activity_toxicity_evidence": {
            "paper": str(PAPER_FINAL / "activity_toxicity_evidence.json"),
            "packet": str(PACKET_FINAL / "activity_toxicity_evidence.json"),
        },
        "database_record_verification": {
            "paper": str(PAPER_FINAL / "database_record_verification.json"),
            "packet": str(PACKET_FINAL / "database_record_verification.json"),
        },
        "review_report": {
            "paper": str(PAPER_FINAL / "review_report.json"),
            "packet": str(PACKET_FINAL / "review_report.json"),
        },
        "mechanism_final": {
            "paper": str(PAPER_FINAL / "mechanism_ontology_record.json"),
            "packet": str(PACKET_FINAL / "mechanism_evidence.json"),
        },
        "mechanism_ontology_record": {
            "paper": str(PAPER_FINAL / "mechanism_ontology_record.json"),
            "packet": str(PACKET_FINAL / "mechanism_ontology_record.json"),
        },
    }


def gate_artifact_paths() -> dict[str, str]:
    return {
        "single_paper_manifest": str(WORK_REVIEW / "worker6_single_paper_manifest.json"),
        "packet": str(VALIDATION / "worker6_packet_gate.PMC11672609.json"),
        "semantic": str(VALIDATION / "worker6_semantic_gate.PMC11672609.json"),
        "publication": str(VALIDATION / "worker6_publication_quality.PMC11672609.json"),
    }


def validate_preclosure_gates() -> dict[str, Any]:
    packet = read_json(VALIDATION / "worker6_packet_gate.PMC11672609.json")
    semantic = read_json(VALIDATION / "worker6_semantic_gate.PMC11672609.json")
    publication = read_json(VALIDATION / "worker6_publication_quality.PMC11672609.json")
    manifest = read_json(WORK_REVIEW / "worker6_single_paper_manifest.json")
    packet_result = (packet.get("results") or [{}])[0]
    semantic_result = (semantic.get("results") or [{}])[0]
    risk_counts = publication.get("risk_counts") if isinstance(publication.get("risk_counts"), dict) else {}
    valid = (
        manifest.get("paper_ids") == [PAPER_ID]
        and packet.get("paper_count") == 1
        and packet.get("hard_finding_count") == 0
        and set(packet_result.get("open_rework_ticket_ids") or []).issubset(set(TICKET_IDS))
        and semantic.get("paper_count") == 1
        and semantic.get("publication_grade_pass_count") == 1
        and semantic.get("publication_grade_fail_count") == 0
        and semantic_result.get("issue_count") == 0
        and publication.get("paper_count") == 1
        and publication.get("publication_grade_pass") is True
        and not any(int(value or 0) for value in risk_counts.values())
    )
    return {
        "valid": valid,
        "packet_open_rework_ticket_ids": packet_result.get("open_rework_ticket_ids") or [],
        "semantic_issue_count": semantic_result.get("issue_count"),
        "publication_risk_counts": risk_counts,
    }


def validate_mirrors() -> dict[str, Any]:
    pairs = verified_artifact_paths()
    result: dict[str, Any] = {}
    for name, paths in pairs.items():
        left = Path(paths["paper"])
        right = Path(paths["packet"])
        result[name] = {
            "byte_identical": left.exists() and right.exists() and left.read_bytes() == right.read_bytes(),
            "paper_sha256": sha256(left) if left.exists() else None,
            "packet_sha256": sha256(right) if right.exists() else None,
        }
    result["overall_mirror_pass"] = all(item["byte_identical"] for item in result.values() if isinstance(item, dict))
    return result


def prior_terminal_responses() -> dict[str, int]:
    rows = read_jsonl(RESPONSES)
    counts: dict[str, int] = {}
    for ticket_id in TICKET_IDS:
        counts[ticket_id] = sum(
            1
            for row in rows
            if row.get("ticket_id") == ticket_id
            and row.get("response_by") == "worker-6"
            and row.get("status") == "closed_repaired"
            and row.get("response_status") == "closed_repaired"
        )
    return counts


def update_final_review_metadata(now: str, counts: dict[str, int], closure_validation_path: Path) -> None:
    gates = gate_artifact_paths()
    verified = verified_artifact_paths()
    review = read_json(PAPER_FINAL / "review_report.json")
    review["reviewed_at"] = now
    review["final_counts"] = counts
    review["gate_return_codes"] = {"packet": 0, "semantic": 0, "publication": 0}
    review["gate_artifact_paths"] = gates
    review["verified_artifact_paths"] = verified
    review["runtime_open_ticket_ids_assigned_to_worker6"] = TICKET_IDS
    review["closed_repaired_ticket_ids"] = TICKET_IDS
    review["terminal_rework_response_status"] = "worker6_r02_terminal_responses_appended"
    review["terminal_rework_response_validation"] = str(closure_validation_path)
    review.setdefault("semantic_quality_checks", {})["owner_lane_terminal_contracts_verified"] = True
    review.setdefault("semantic_quality_checks", {})["runtime_open_ticket_ids_after_terminal_closure"] = []
    write_json(PAPER_FINAL / "review_report.json", review)
    shutil.copyfile(PAPER_FINAL / "review_report.json", PACKET_FINAL / "review_report.json")

    adjudication = read_json(WORK_REVIEW / "adjudication_report.json")
    adjudication["reviewed_at"] = now
    adjudication["final_counts"] = counts
    adjudication["gate_return_codes"] = {"packet": 0, "semantic": 0, "publication": 0}
    adjudication["gate_artifact_paths"] = gates
    adjudication["verified_artifact_paths"] = verified
    adjudication["ticket_contract_validation"] = str(closure_validation_path)
    adjudication["terminal_response_appended"] = True
    adjudication["terminal_response_ticket_ids"] = TICKET_IDS
    write_json(WORK_REVIEW / "adjudication_report.json", adjudication)

    feedback = read_json(WORK_REVIEW / "quality_feedback.json")
    feedback["generated_at"] = now
    feedback["closed_repaired_ticket_ids"] = TICKET_IDS
    feedback["ticket_contract_validation"] = str(closure_validation_path)
    feedback["rework_required"] = False
    feedback["rework_targets"] = []
    write_json(WORK_REVIEW / "quality_feedback.json", feedback)


def update_packet_status(now: str) -> None:
    manifest = read_json(PACKET / "packet_manifest.json")
    manifest["analysis_queue_status"] = "analysis_source_reviewed_accepted"
    manifest["updated_at"] = now
    manifest["updated_by"] = "worker-6"
    manifest["open_rework_ticket_count"] = 0
    manifest["open_rework_ticket_ids"] = []
    manifest["closed_repaired_ticket_ids"] = sorted(set(manifest.get("closed_repaired_ticket_ids") or []) | set(TICKET_IDS))
    write_json(PACKET / "packet_manifest.json", manifest)
    analysis_status = read_json(PACKET / "analysis" / "analysis_status.json")
    analysis_status["generated_at"] = now
    analysis_status["status"] = "analysis_source_reviewed_accepted"
    analysis_status["blocking_gap_ids"] = []
    analysis_status["closed_repaired_ticket_ids"] = TICKET_IDS
    write_json(PACKET / "analysis" / "analysis_status.json", analysis_status)


def build_responses(now: str, counts: dict[str, int], validation_path: Path, contract_validation: dict[str, Any]) -> list[dict[str, Any]]:
    gates = gate_artifact_paths()
    verified = verified_artifact_paths()
    responses: list[dict[str, Any]] = []
    for ticket_id in TICKET_IDS:
        responses.append(
            {
                "ticket_id": ticket_id,
                "paper_id": PAPER_ID,
                "status": "closed_repaired",
                "response_status": "closed_repaired",
                "response_by": "worker-6",
                "created_at": now,
                "analysis_can_resume": True,
                "publication_grade": True,
                "review_status": "accepted_with_cautions",
                "final_counts": counts,
                "gate_return_codes": {"packet": 0, "semantic": 0, "publication": 0},
                "gate_artifact_paths": gates,
                "verified_artifact_paths": verified,
                "ticket_contract_evidence": {
                    "overall_contract_pass": True,
                    "ticket_id": ticket_id,
                    "ticket_contract_pass": contract_validation["ticket_contract_checks"][ticket_id]["pass"],
                    "owner_response_prerequisite": contract_validation["owner_response_prerequisites"][ticket_id],
                    "validation_artifact": str(validation_path),
                    "preclosure_packet_open_rework_ticket_ids": contract_validation["preclosure_gate_validation"]["packet_open_rework_ticket_ids"],
                    "post_response_gate_rerun_required": True,
                },
                "closure_basis": {
                    "source_reviewed_final_rebuild": True,
                    "fallback_database_rows_preserved_as_candidate_only": True,
                    "authoritative_dbaasp_ingest_ready": False,
                    "no_hard_rework_targets_remaining": True,
                },
            }
        )
    return responses


def build_receipts(now: str, responses: list[dict[str, Any]], response_start_index: int) -> list[dict[str, Any]]:
    artifact_hashes = {
        "activity_toxicity_evidence_paper": sha256(PAPER_FINAL / "activity_toxicity_evidence.json"),
        "activity_toxicity_evidence_packet": sha256(PACKET_FINAL / "activity_toxicity_evidence.json"),
        "database_record_verification_paper": sha256(PAPER_FINAL / "database_record_verification.json"),
        "database_record_verification_packet": sha256(PACKET_FINAL / "database_record_verification.json"),
        "mechanism_ontology_record_paper": sha256(PAPER_FINAL / "mechanism_ontology_record.json"),
        "mechanism_evidence_packet": sha256(PACKET_FINAL / "mechanism_evidence.json"),
        "review_report_paper": sha256(PAPER_FINAL / "review_report.json"),
        "review_report_packet": sha256(PACKET_FINAL / "review_report.json"),
    }
    receipts: list[dict[str, Any]] = []
    for offset, response in enumerate(responses):
        receipts.append(
            {
                "schema_version": "strict_ticket_closure_receipt_v1",
                "ticket_id": response["ticket_id"],
                "terminal_response_index": response_start_index + offset,
                "terminal_response_sha256": terminal_response_sha256(response),
                "sealed_at": now,
                "overall_contract_pass": True,
                "owner_response_present_at_seal": True,
                "current_state_revalidation_required": True,
                "artifact_sha256_at_seal": artifact_hashes,
            }
        )
    return receipts


def main() -> int:
    validation_path = VALIDATION / "worker6_ticket_contract_validation.PMC11672609.r02.json"
    closure_validation_path = VALIDATION / "worker6_terminal_closure_validation.PMC11672609.r02.json"
    contract_validation = read_json(validation_path)
    preclosure_gates = validate_preclosure_gates()
    mirrors = validate_mirrors()
    terminal_counts = prior_terminal_responses()
    counts = final_counts()
    closure_validation = {
        "paper_id": PAPER_ID,
        "ticket_ids": TICKET_IDS,
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "contract_validation_artifact": str(validation_path),
        "contract_overall_pass": contract_validation.get("overall_contract_pass") is True,
        "preclosure_gate_validation": preclosure_gates,
        "mirror_validation": mirrors,
        "prior_terminal_response_counts": terminal_counts,
        "final_counts": counts,
        "overall_contract_pass": (
            contract_validation.get("overall_contract_pass") is True
            and preclosure_gates["valid"]
            and mirrors["overall_mirror_pass"]
            and all(value == 0 for value in terminal_counts.values())
            and counts == {
                "activity_records": 16,
                "toxicity_records": 3,
                "database_record_audits": 13,
                "mechanism_claims": 6,
                "review_rework_targets": 0,
            }
        ),
    }
    write_json(closure_validation_path, closure_validation)
    if not closure_validation["overall_contract_pass"]:
        print(
            json.dumps(
                {
                    "paper_id": PAPER_ID,
                    "terminal_responses_appended": 0,
                    "closure_validation_artifact": str(closure_validation_path),
                },
                sort_keys=True,
            )
        )
        return 2

    now = datetime.now(timezone.utc).isoformat()
    update_final_review_metadata(now, counts, closure_validation_path)
    update_packet_status(now)
    contract_validation["preclosure_gate_validation"] = preclosure_gates
    responses = build_responses(now, counts, closure_validation_path, contract_validation)
    response_start_index = len(read_jsonl(RESPONSES))
    receipts = build_receipts(now, responses, response_start_index)
    append_jsonl(RESPONSES, responses)
    append_jsonl(RECEIPTS, receipts)
    print(
        json.dumps(
            {
                "paper_id": PAPER_ID,
                "terminal_responses_appended": len(responses),
                "closure_receipts_appended": len(receipts),
                "ticket_ids": TICKET_IDS,
                "closure_validation_artifact": str(closure_validation_path),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
