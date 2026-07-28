#!/usr/bin/env python3
"""Validate worker-5 mechanism claim entity scopes without emitting source text."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def load_xml_text_by_locator(xml_sections_path: Path) -> dict[str, str]:
    data = json.loads(xml_sections_path.read_text(encoding="utf-8"))
    return {
        item["locator"]: item.get("text", "")
        for item in data.get("sections", [])
        if isinstance(item, dict) and item.get("locator")
    }


def primary_locator(claim: dict) -> str:
    locator = claim.get("source_locator")
    if isinstance(locator, dict):
        return str(locator.get("locator", ""))
    return str(locator or "")


def claim_agent(claim: dict) -> str:
    scope = claim.get("entity_scope") or {}
    if isinstance(scope, dict):
        return str(scope.get("peptide_or_agent", ""))
    return ""


def claim_synonyms(claim: dict) -> list[str]:
    scope = claim.get("entity_scope") or {}
    values = []
    if isinstance(scope, dict):
        values.append(str(scope.get("peptide_or_agent", "")))
        for key in ("source_supported_synonyms", "synonyms"):
            raw = scope.get(key) or []
            if isinstance(raw, list):
                values.extend(str(v) for v in raw)
    return [v for v in values if v]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mechanism-json", required=True, type=Path)
    parser.add_argument("--xml-sections", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    artifact = json.loads(args.mechanism_json.read_text(encoding="utf-8"))
    xml_text = load_xml_text_by_locator(args.xml_sections)
    claims = artifact.get("mechanism_claims", [])
    counts = Counter(claim.get("evidence_class") for claim in claims)

    claim_checks = []
    failures = []
    for claim in claims:
        loc = primary_locator(claim)
        agent = claim_agent(claim)
        text = xml_text.get(loc, "")
        synonyms = claim_synonyms(claim)
        contains_agent = any(s.lower() in text.lower() for s in synonyms)
        evidence_class = claim.get("evidence_class")
        direct_types_present = evidence_class != "direct_mechanism" or bool(
            claim.get("direct_assay_types")
        )
        direct_daptomycin = (
            evidence_class == "direct_mechanism" and agent.lower() == "daptomycin"
        )
        check = {
            "claim_id": claim.get("claim_id"),
            "evidence_class": evidence_class,
            "claimed_agent": agent,
            "source_locator": loc,
            "locator_resolved": loc in xml_text,
            "locator_contains_claimed_agent_or_synonym": contains_agent,
            "direct_assay_types_present_when_required": direct_types_present,
            "direct_daptomycin_claim": direct_daptomycin,
        }
        claim_checks.append(check)
        if not check["locator_resolved"]:
            failures.append({"claim_id": claim.get("claim_id"), "failure": "locator_unresolved"})
        if not contains_agent:
            failures.append({"claim_id": claim.get("claim_id"), "failure": "agent_not_in_locator"})
        if not direct_types_present:
            failures.append({"claim_id": claim.get("claim_id"), "failure": "missing_direct_assay_types"})
        if direct_daptomycin:
            failures.append({"claim_id": claim.get("claim_id"), "failure": "direct_daptomycin_claim"})

    declared_counts = artifact.get("claim_counts_by_evidence_class", {})
    recomputed_counts = dict(sorted(counts.items()))
    counts_match = declared_counts == recomputed_counts
    if not counts_match:
        failures.append({"failure": "claim_counts_by_evidence_class_mismatch"})

    report = {
        "paper_id": artifact.get("paper_id"),
        "validated_artifact": str(args.mechanism_json),
        "xml_sections": str(args.xml_sections),
        "claim_count": len(claims),
        "claim_counts_by_evidence_class": recomputed_counts,
        "declared_counts_match_recomputed_counts": counts_match,
        "direct_daptomycin_claim_count": sum(
            1 for c in claim_checks if c["direct_daptomycin_claim"]
        ),
        "all_claim_locators_resolve": all(c["locator_resolved"] for c in claim_checks),
        "all_claim_locators_contain_claimed_agent_or_synonym": all(
            c["locator_contains_claimed_agent_or_synonym"] for c in claim_checks
        ),
        "all_direct_claims_have_direct_assay_types": all(
            c["direct_assay_types_present_when_required"] for c in claim_checks
        ),
        "claim_checks": claim_checks,
        "failures": failures,
        "passed": not failures,
        "source_text_emitted": False,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "report": str(args.report),
                "claim_count": len(claims),
                "passed": report["passed"],
                "failure_count": len(failures),
            },
            ensure_ascii=False,
        )
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
