#!/usr/bin/env python3
"""Append governance review metadata without changing the frozen v1.0 payload."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "releases" / "amp_evidence_atlas_v1_0"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_checksum_file(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            expected, relative = line.split("  ", 1)
            rows.append((expected, relative))
    return rows


def verify_payload() -> str:
    checksum_file = RELEASE / "payload_checksums.txt"
    lock = json.loads((RELEASE / "DATA_FREEZE_LOCK.json").read_text(encoding="utf-8"))
    actual_manifest_sha = sha256(checksum_file)
    if actual_manifest_sha != lock["payload_checksum_manifest_sha256"]:
        raise RuntimeError("immutable payload checksum manifest changed")
    failures = []
    for expected, relative in read_checksum_file(checksum_file):
        path = RELEASE / relative
        actual = sha256(path) if path.is_file() else "missing"
        if actual != expected:
            failures.append({"path": relative, "expected": expected, "actual": actual})
    if failures:
        raise RuntimeError(f"immutable payload verification failed: {failures}")
    return actual_manifest_sha


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    payload_manifest_sha = verify_payload()
    review_path = RELEASE / "governance" / "source_license_review.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    required = [
        RELEASE / "SOURCE_DATABASE_VERSIONS.tsv",
        RELEASE / "LICENSES.tsv",
        review_path,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"governance artifacts missing: {missing}")

    manifest_path = RELEASE / "release_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["payload_checksum_manifest_sha256"] != payload_manifest_sha:
        raise RuntimeError("release manifest no longer matches the immutable payload")
    manifest["governance_updated_at"] = review["reviewed_at"]
    manifest["governance_reviews"] = {
        "manual_validation": "example_pack_prepared_human_confirmation_pending",
        "source_database_version_review": "completed",
        "source_license_review": "completed_with_unresolved_permissions",
    }
    manifest["public_services"] = {
        "public_safe_projection": {
            "release_id": "amp-evidence-atlas-v1.0-public-safe-beta",
            "status": "deployed",
            "url": "https://amp-evidence-atlas.daoyu7974.chatgpt.site",
            "full_internal_payload_exposed": False,
        }
    }
    manifest["public_release_ready"] = False
    manifest["governance_open_items"] = [
        "manual stratified validation requires later human confirmation",
        (
            "source-license review is complete, but written permission or field-level "
            "rights filtering remains required for APD6, CAMP, DBAASP and dbAMP, and "
            "for DRAMP patent AMPs"
        ),
        (
            "the rights-filtered website/API is deployed, but unrestricted bulk "
            "download of the internal v1.0 payload remains blocked"
        ),
    ]

    targets = sorted(
        (
            path
            for path in RELEASE.rglob("*")
            if path.is_file()
            and path.name not in {"checksums.txt", "release_manifest.json"}
        ),
        key=lambda path: path.relative_to(RELEASE).as_posix(),
    )
    records = []
    lines = []
    for path in targets:
        relative = path.relative_to(RELEASE).as_posix()
        digest = sha256(path)
        lines.append(f"{digest}  {relative}")
        records.append(
            {"path": relative, "sha256": digest, "size_bytes": path.stat().st_size}
        )
    (RELEASE / "checksums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest["package_checksums"] = records
    write_json(manifest_path, manifest)
    print(
        json.dumps(
            {
                "release_id": manifest["release_id"],
                "payload_verified": True,
                "payload_checksum_manifest_sha256": payload_manifest_sha,
                "governance_review_completed": True,
                "public_release_ready": False,
                "package_file_count": len(records),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
