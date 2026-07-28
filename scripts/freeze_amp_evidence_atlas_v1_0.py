#!/usr/bin/env python3
"""Promote the reviewed RC2 payload into an immutable AMP Evidence Atlas v1.0 freeze.

The data payload is copied from RC2 after its published checksums are verified.
Rows carrying a ``release_id`` column are rewritten to the canonical v1.0 id.
Governance documents (validation and licensing) may be added later, but the
payload files listed in ``payload_checksums.txt`` must never change.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "releases" / "amp_evidence_atlas_v1_rc2"
DESTINATION = ROOT / "releases" / "amp_evidence_atlas_v1_0"
RELEASE_ID = "amp-evidence-atlas-v1.0"
RELEASE_VERSION = "v1.0"
SOURCE_RELEASE_ID = "amp-evidence-atlas-v1-rc2"

PAYLOAD_TOP_LEVEL = {
    "papers.tsv",
    "database_record_audits.tsv",
    "activity_observations.tsv",
    "mechanism_claims.tsv",
    "conflicts_and_cautions.tsv",
    "excluded_blocked_papers.tsv",
    "database_denominators.tsv",
    "crosstab_status_by_database.tsv",
    "crosstab_category_by_database.tsv",
    "crosstab_status_by_source_table.tsv",
    "crosstab_review_status_by_database.tsv",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_checksum_file(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split(maxsplit=1)
        rows[relative.strip()] = digest
    return rows


def verify_checksum_file(root: Path, checksum_path: Path) -> list[str]:
    failures: list[str] = []
    for relative, expected in read_checksum_file(checksum_path).items():
        target = root / relative
        if not target.is_file():
            failures.append(f"missing:{relative}")
        elif sha256_file(target) != expected:
            failures.append(f"sha256:{relative}")
    return failures


def rewrite_release_tsv(source: Path, destination: Path) -> int:
    """Copy a TSV and replace its release_id while preserving structured cells."""
    with source.open("r", encoding="utf-8", newline="") as src, destination.open(
        "w", encoding="utf-8", newline=""
    ) as dst:
        reader = csv.DictReader(src, dialect="excel-tab")
        if not reader.fieldnames:
            raise RuntimeError(f"missing TSV header: {source}")
        writer = csv.DictWriter(
            dst,
            fieldnames=reader.fieldnames,
            dialect="excel-tab",
            extrasaction="raise",
            lineterminator="\n",
        )
        writer.writeheader()
        count = 0
        for row in reader:
            if "release_id" in row:
                prior = row.get("release_id", "")
                if prior not in {"", SOURCE_RELEASE_ID}:
                    raise RuntimeError(
                        f"unexpected release_id {prior!r} in {source.name} row {count + 1}"
                    )
                row["release_id"] = RELEASE_ID
            writer.writerow(row)
            count += 1
    return count


def payload_paths(root: Path) -> list[Path]:
    paths = [root / name for name in sorted(PAYLOAD_TOP_LEVEL)]
    paths.extend(sorted((root / "schemas").glob("*.json")))
    return paths


def write_checksums(path: Path, root: Path, paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for target in sorted(paths, key=lambda item: str(item.relative_to(root))):
        relative = str(target.relative_to(root))
        records.append(
            {
                "path": relative,
                "sha256": sha256_file(target),
                "size_bytes": target.stat().st_size,
            }
        )
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(f"{record['sha256']}  {record['path']}\n")
    return records


def checksum_manifest_digest(path: Path) -> str:
    return sha256_file(path)


def count_tsv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle, dialect="excel-tab"))


def validate_frozen_package(destination: Path) -> dict[str, Any]:
    lock_path = destination / "DATA_FREEZE_LOCK.json"
    if not lock_path.is_file():
        raise RuntimeError(f"missing freeze lock: {lock_path}")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    failures = verify_checksum_file(destination, destination / "payload_checksums.txt")
    if failures:
        raise RuntimeError("payload verification failed: " + ", ".join(failures))
    actual_digest = checksum_manifest_digest(destination / "payload_checksums.txt")
    if actual_digest != lock["payload_checksum_manifest_sha256"]:
        raise RuntimeError("payload checksum manifest digest differs from freeze lock")

    manifest = json.loads((destination / "release_manifest.json").read_text(encoding="utf-8"))
    row_counts = {
        item["path"]: count_tsv_rows(destination / item["path"])
        for item in manifest["tables"]
    }
    expected_counts = {item["path"]: item["row_count"] for item in manifest["tables"]}
    if row_counts != expected_counts:
        raise RuntimeError(
            f"row-count verification failed: expected={expected_counts}, actual={row_counts}"
        )
    return {
        "release_id": lock["release_id"],
        "payload_checksum_manifest_sha256": actual_digest,
        "payload_file_count": len(read_checksum_file(destination / "payload_checksums.txt")),
        "table_row_counts": row_counts,
        "verified": True,
    }


def build(source: Path, destination: Path) -> dict[str, Any]:
    source_manifest_path = source / "release_manifest.json"
    source_checksums_path = source / "checksums.txt"
    if not source_manifest_path.is_file() or not source_checksums_path.is_file():
        raise RuntimeError(f"source RC2 package is incomplete: {source}")
    source_failures = verify_checksum_file(source, source_checksums_path)
    if source_failures:
        raise RuntimeError("source RC2 checksum verification failed: " + ", ".join(source_failures))
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if source_manifest.get("release_id") != SOURCE_RELEASE_ID:
        raise RuntimeError(
            f"expected source release {SOURCE_RELEASE_ID}, got {source_manifest.get('release_id')}"
        )
    if destination.exists():
        raise RuntimeError(
            f"refusing to overwrite frozen destination {destination}; use --verify-only"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_root = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.building-", dir=destination.parent)
    )
    try:
        (temp_root / "schemas").mkdir(parents=True)
        row_counts: dict[str, int] = {}
        for name in sorted(PAYLOAD_TOP_LEVEL):
            source_path = source / name
            destination_path = temp_root / name
            if not source_path.is_file():
                raise RuntimeError(f"missing source payload file: {source_path}")
            row_counts[name] = rewrite_release_tsv(source_path, destination_path)
        for schema_path in sorted((source / "schemas").glob("*.json")):
            shutil.copy2(schema_path, temp_root / "schemas" / schema_path.name)

        expected_counts = {
            item["path"]: item["row_count"] for item in source_manifest.get("tables", [])
        }
        for name, expected in expected_counts.items():
            if row_counts.get(name) != expected:
                raise RuntimeError(
                    f"row count changed while freezing {name}: "
                    f"expected {expected}, got {row_counts.get(name)}"
                )

        payload_records = write_checksums(
            temp_root / "payload_checksums.txt",
            temp_root,
            payload_paths(temp_root),
        )
        frozen_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        payload_manifest_sha256 = checksum_manifest_digest(
            temp_root / "payload_checksums.txt"
        )
        lock = {
            "schema": "amp_evidence_atlas_data_freeze_lock_v1",
            "release_id": RELEASE_ID,
            "release_version": RELEASE_VERSION,
            "frozen_at": frozen_at,
            "source_release_id": SOURCE_RELEASE_ID,
            "source_release_manifest": str(source_manifest_path.relative_to(ROOT)),
            "source_release_manifest_sha256": sha256_file(source_manifest_path),
            "source_checksum_manifest_sha256": sha256_file(source_checksums_path),
            "payload_checksum_manifest": "payload_checksums.txt",
            "payload_checksum_manifest_sha256": payload_manifest_sha256,
            "payload_file_count": len(payload_records),
            "immutable_payload_policy": (
                "Files listed in payload_checksums.txt are immutable. Validation, "
                "licensing and manuscript-governance documents may be appended "
                "without changing the v1.0 data payload."
            ),
            "scope": source_manifest["source_freeze_summary"]["scope"],
        }
        write_json(temp_root / "DATA_FREEZE_LOCK.json", lock)

        manifest = {
            "release_id": RELEASE_ID,
            "release_version": RELEASE_VERSION,
            "generated_at": frozen_at,
            "status": "data_payload_frozen_governance_open",
            "source_release_id": SOURCE_RELEASE_ID,
            "source_release_manifest_sha256": sha256_file(source_manifest_path),
            "data_freeze_lock": "DATA_FREEZE_LOCK.json",
            "payload_checksum_manifest": "payload_checksums.txt",
            "payload_checksum_manifest_sha256": payload_manifest_sha256,
            "scope": source_manifest["source_freeze_summary"]["scope"],
            "scope_reconciliation": source_manifest["source_freeze_summary"].get(
                "scope_reconciliation", {}
            ),
            "interpretation_notes": source_manifest["source_freeze_summary"].get(
                "interpretation_notes", []
            ),
            "tables": [
                {
                    **item,
                    "release_id": RELEASE_ID,
                }
                for item in source_manifest["tables"]
            ],
            "governance_open_items": [
                "manual stratified validation requires later human confirmation",
                "source database versions and public-hosting permissions require final legal confirmation",
                "public website/API/download deployment remains separate from this data freeze",
            ],
        }
        write_json(temp_root / "release_manifest.json", manifest)
        readme = f"""# AMP Evidence Atlas v1.0 Data Freeze

Release id: `{RELEASE_ID}`

Status: `data_payload_frozen_governance_open`

This package freezes the exact data denominator promoted from RC2:

- papers with final artifacts: **{lock['scope']['paper_final_artifact_count']}**
- public-v1 candidate papers: **{lock['scope']['public_v1_candidate_papers']}**
- database audit rows: **{lock['scope']['database_audit_rows']}**
- activity observations: **{lock['scope']['activity_records']}**
- mechanism claims: **{lock['scope']['mechanism_claims']}**

Files listed in `payload_checksums.txt` are immutable. The package is not yet a
claim of completed human validation, legal clearance, public deployment, or NAR
submission readiness.

Validate:

```bash
python scripts/freeze_amp_evidence_atlas_v1_0.py --verify-only
```
"""
        (temp_root / "README.md").write_text(readme, encoding="utf-8")
        all_checksum_targets = [
            path
            for path in temp_root.rglob("*")
            if path.is_file()
            and path.name not in {"checksums.txt", "release_manifest.json"}
        ]
        package_records = write_checksums(
            temp_root / "checksums.txt", temp_root, all_checksum_targets
        )
        manifest["package_checksums"] = package_records
        write_json(temp_root / "release_manifest.json", manifest)

        temp_root.rename(destination)
    except Exception:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise
    return validate_frozen_package(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--destination", type=Path, default=DESTINATION)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    result = (
        validate_frozen_package(args.destination)
        if args.verify_only
        else build(args.source, args.destination)
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
