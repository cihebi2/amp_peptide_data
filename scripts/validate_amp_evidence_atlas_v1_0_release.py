#!/usr/bin/env python3
"""Fail-closed validation for the frozen v1.0 payload and its governance layer."""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "releases" / "amp_evidence_atlas_v1_0"
PORTAL_DB = ROOT / "portal" / "atlas.db"
PROFILE = ROOT / "portal" / "release_profile_v1_0.json"
BENCHMARK = ROOT / "portal" / "benchmark_amp_qa.json"
CASE_DIR = (
    ROOT
    / "reports"
    / "nar_resource_freeze_v1"
    / "manual_validation"
    / "v1_0_human_check_examples"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def checksum_rows(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, relative = line.split("  ", 1)
            result[relative] = digest
    return result


class Validator:
    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []
        self.failures: list[str] = []

    def check(self, name: str, condition: bool, detail: Any = None) -> None:
        self.checks.append({"name": name, "passed": bool(condition), "detail": detail})
        if not condition:
            self.failures.append(name)

    def validate_checksums(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "freeze_amp_evidence_atlas_v1_0.py"),
                "--verify-only",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.check("immutable_payload", result.returncode == 0, result.stderr.strip())

        manifest = json.loads(
            (RELEASE / "release_manifest.json").read_text(encoding="utf-8")
        )
        expected = checksum_rows(RELEASE / "checksums.txt")
        actual = {
            relative: sha256(RELEASE / relative)
            for relative in expected
            if (RELEASE / relative).is_file()
        }
        self.check(
            "package_checksums",
            len(actual) == len(expected)
            and all(actual.get(path) == digest for path, digest in expected.items()),
            {"expected_files": len(expected), "verified_files": len(actual)},
        )
        manifest_records = {
            row["path"]: row["sha256"] for row in manifest["package_checksums"]
        }
        self.check(
            "manifest_checksum_index",
            manifest_records == expected,
            {"manifest_files": len(manifest_records), "checksum_files": len(expected)},
        )
        self.check(
            "release_gate",
            manifest.get("public_release_ready") is False
            and manifest.get("status") == "data_payload_frozen_governance_open",
            {
                "status": manifest.get("status"),
                "public_release_ready": manifest.get("public_release_ready"),
            },
        )

    def validate_source_governance(self) -> None:
        version_rows = tsv(RELEASE / "SOURCE_DATABASE_VERSIONS.tsv")
        license_rows = tsv(RELEASE / "LICENSES.tsv")
        permission_rows = tsv(RELEASE / "SOURCE_PERMISSION_TRACKER.tsv")
        databases = {"APD6", "CAMP", "DBAASP", "DRAMP", "dbAMP"}
        self.check(
            "source_version_five_databases",
            {row["database"] for row in version_rows} == databases
            and len(version_rows) == 5,
        )
        self.check(
            "license_five_databases",
            {row["database"] for row in license_rows} == databases
            and len(license_rows) == 5,
        )
        self.check(
            "permission_tracker_five_databases",
            {row["database"] for row in permission_rows} == databases
            and len(permission_rows) == 5
            and all(row["permission_decision"] != "approved" for row in permission_rows),
        )
        artifact_failures = []
        for row in version_rows:
            path = Path(row["primary_snapshot_artifact"])
            if (
                not path.is_file()
                or sha256(path) != row["sha256"]
                or path.stat().st_size != int(row["size_bytes"])
            ):
                artifact_failures.append(row["database"])
        self.check("source_snapshot_artifacts", not artifact_failures, artifact_failures)

        decisions = {row["database"]: row["public_hosting_decision"] for row in license_rows}
        self.check(
            "license_fail_closed",
            all("not_cleared" in decisions[db] for db in databases - {"DRAMP"})
            and "patent_AMPs_are_excluded" in decisions["DRAMP"],
            decisions,
        )
        review = json.loads(
            (RELEASE / "governance" / "source_license_review.json").read_text(
                encoding="utf-8"
            )
        )
        self.check(
            "license_review_completion_claim",
            review.get("review_completed") is True
            and review.get("raw_source_redistribution_fully_cleared") is False
            and review.get("public_release_ready") is False,
        )

    def validate_portal(self) -> None:
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        connection = sqlite3.connect(PORTAL_DB)
        metadata = dict(connection.execute("SELECT k, v FROM metadata"))
        projection = profile["denominator_contract"]["public_portal_projection"]
        counts = {
            "papers": connection.execute("SELECT COUNT(*) FROM papers").fetchone()[0],
            "activity_observations": connection.execute(
                "SELECT COUNT(*) FROM activity"
            ).fetchone()[0],
            "database_audit_records": connection.execute(
                "SELECT COUNT(*) FROM audit"
            ).fetchone()[0],
            "mechanism_claims": connection.execute(
                "SELECT COUNT(*) FROM mechanism"
            ).fetchone()[0],
            "source_conflicts": connection.execute(
                "SELECT COUNT(*) FROM audit WHERE status='source_conflict'"
            ).fetchone()[0],
        }
        connection.close()
        self.check(
            "portal_release_metadata",
            metadata.get("release_id") == "amp-evidence-atlas-v1.0"
            and metadata.get("experimental_increments_included") == "false"
            and metadata.get("payload_checksum_manifest_sha256")
            == profile["payload_checksum_manifest_sha256"],
            metadata,
        )
        self.check("portal_projection_counts", counts == {
            key: projection[key] for key in counts
        }, {"actual": counts, "expected": {key: projection[key] for key in counts}})

    def validate_benchmark(self) -> None:
        benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
        items = benchmark["items"]
        required = {"NO_RETRIEVAL", "RAW_DB", "ATLAS"}
        self.check(
            "benchmark_shape",
            benchmark["n_items"] == len(items) == 40
            and len({item["id"] for item in items}) == 40
            and set(benchmark["required_conditions"]) == required,
        )
        connection = sqlite3.connect(PORTAL_DB)
        missing = []
        for item in items:
            ref = item["source_ref"]
            paper = connection.execute(
                "SELECT 1 FROM papers WHERE paper_id=?", (ref,)
            ).fetchone()
            audit = connection.execute(
                "SELECT 1 FROM audit WHERE audit_record_id=?", (ref,)
            ).fetchone()
            if not paper and not audit:
                missing.append({"id": item["id"], "source_ref": ref})
        connection.close()
        self.check("benchmark_source_refs", not missing, missing)

    def validate_human_examples(self) -> None:
        pack = json.loads(
            (CASE_DIR / "case_pack_manifest.json").read_text(encoding="utf-8")
        )
        cases = tsv(CASE_DIR / "case_manifest.tsv")
        labels = tsv(CASE_DIR / "human_labels_template.tsv")
        human_fields = [
            "human_decision",
            "human_correct_status",
            "human_error_class",
            "human_severity",
            "human_notes",
            "reviewer_id",
            "reviewed_at",
        ]
        self.check(
            "human_example_pack_shape",
            pack["case_count"] == len(cases) == len(labels) == 21
            and pack["completion_claim"]
            == "pending_human_check_examples_not_human_validation",
        )
        self.check(
            "human_labels_blank",
            all(not row.get(field, "").strip() for row in labels for field in human_fields),
        )
        missing_sources = [
            row["case_id"]
            for row in cases
            if not (ROOT / row["source_final_path"]).is_file()
        ]
        self.check("human_example_source_files", not missing_sources, missing_sources)

    def validate_stale_claims(self) -> None:
        targets = [
            ROOT / "portal" / "benchmark_protocol.md",
            ROOT / "portal" / "benchmark_amp_qa.json",
            ROOT / "portal" / "portal_server.py",
            ROOT / "portal" / "mcp_server.py",
            ROOT / "releases" / "amp_evidence_atlas_v1_rc2" / "README.md",
            ROOT / "scripts" / "build_nar_public_release_package.py",
        ]
        forbidden = [
            "v1 RC1 Release Package",
            "amp_evidence_atlas_v1_rc1",
            "28,734",
            "99% precision (n=192)",
            "190/192",
        ]
        hits = []
        for path in targets:
            text = path.read_text(encoding="utf-8")
            for phrase in forbidden:
                if phrase in text:
                    hits.append({"path": str(path.relative_to(ROOT)), "phrase": phrase})
        self.check("stale_claim_scan", not hits, hits)


def main() -> None:
    validator = Validator()
    validator.validate_checksums()
    validator.validate_source_governance()
    validator.validate_portal()
    validator.validate_benchmark()
    validator.validate_human_examples()
    validator.validate_stale_claims()
    result = {
        "release_id": "amp-evidence-atlas-v1.0",
        "passed": not validator.failures,
        "check_count": len(validator.checks),
        "failure_count": len(validator.failures),
        "failures": validator.failures,
        "checks": validator.checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
