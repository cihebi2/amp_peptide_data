#!/usr/bin/env python3
"""Recover structured full text for PDF-only papers in the frozen 200 queue.

The script uses Europe PMC metadata/full-text services, preserves the canonical
local PDF as the primary binary source, and writes a strict-pilot worklist
overlay only for successfully validated XML+PDF source directories.  Material
recovery is not a scientific review or publication-grade acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
DEEPMINE = ROOT / "pipeline_v2/deepmine"
PILOT = DEEPMINE / "dbaasp_strict_pilot"
QUEUE = PILOT / "manifests/remaining_200_strict_review_queue_20260726.json"
WORKLIST = DEEPMINE / "dbaasp_worklist.json"
SOURCE_POOL = PILOT / "recovered_source_pool_20260726"
OVERLAY = PILOT / "manifests/material_recovery_worklist_overlay.json"
REPORT_DIR = PILOT / "reports/material_recovery_200"
USER_AGENT = "amp-evidence-atlas-structured-source-recovery/1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    temporary.write_bytes(body)
    os.replace(temporary, path)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write(
        path,
        (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )


def request(url: str, timeout: int, retries: int) -> tuple[bytes, dict[str, str]]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urlopen(
                Request(url, headers={"User-Agent": USER_AGENT}), timeout=timeout
            ) as response:
                headers = {key.lower(): value for key, value in response.headers.items()}
                headers["status"] = str(response.status)
                headers["final_url"] = response.geturl()
                return response.read(), headers
        except (HTTPError, URLError, TimeoutError, RuntimeError) as error:
            last_error = error
            if attempt < retries:
                time.sleep(attempt * 0.75)
    raise RuntimeError(f"{type(last_error).__name__}: {last_error}")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def validate_xml(body: bytes, requested_doi: str) -> dict[str, Any]:
    root = ET.fromstring(body)
    article_ids: dict[str, str] = {}
    supplementary_references: list[str] = []
    for element in root.iter():
        tag = local_name(element.tag)
        if tag == "article-id":
            kind = str(
                element.attrib.get("pub-id-type")
                or element.attrib.get("article-id-type")
                or ""
            )
            value = " ".join("".join(element.itertext()).split())
            if kind and value:
                article_ids[kind] = value
        if tag in {"supplementary-material", "media"}:
            href = next(
                (
                    value
                    for key, value in element.attrib.items()
                    if key.endswith("href") or "href" in key
                ),
                "",
            )
            if href:
                supplementary_references.append(str(href))
    xml_doi = str(article_ids.get("doi") or "").lower().removeprefix("https://doi.org/")
    requested = requested_doi.lower().removeprefix("https://doi.org/")
    if xml_doi and xml_doi != requested:
        raise ValueError(f"DOI mismatch: requested={requested} xml={xml_doi}")
    return {
        "structured_format": "jats",
        "article_ids": article_ids,
        "supplementary_reference_count": len(set(supplementary_references)),
        "supplementary_references": sorted(set(supplementary_references)),
    }


def validate_bioc_xml(body: bytes, requested_doi: str, pmcid: str) -> dict[str, Any]:
    root = ET.fromstring(body)
    if local_name(root.tag) != "collection":
        raise ValueError(f"expected BioC collection root, found {root.tag}")
    documents = [
        element for element in root.iter() if local_name(element.tag) == "document"
    ]
    passages = [
        element for element in root.iter() if local_name(element.tag) == "passage"
    ]
    texts = [
        " ".join("".join(element.itertext()).split())
        for element in passages
        if any(local_name(child.tag) == "text" for child in element)
    ]
    if len(documents) != 1 or len([text for text in texts if text]) < 10:
        raise ValueError(
            f"invalid BioC payload: documents={len(documents)} passages={len(texts)}"
        )
    infons = {
        str(element.attrib.get("key") or ""): str(element.text or "")
        for element in passages[0]
        if local_name(element.tag) == "infon"
    }
    xml_doi = str(infons.get("article-id_doi") or "").strip().lower()
    requested = requested_doi.strip().lower()
    if xml_doi and xml_doi != requested:
        raise ValueError(f"DOI mismatch: requested={requested} bioc={xml_doi}")
    document_id = next(
        (
            str(child.text or "").strip()
            for child in documents[0]
            if local_name(child.tag) == "id"
        ),
        "",
    )
    expected_pmc = pmcid.upper().removeprefix("PMC")
    if document_id and document_id.upper().removeprefix("PMC") != expected_pmc:
        raise ValueError(
            f"PMCID mismatch: requested={expected_pmc} bioc={document_id}"
        )
    return {
        "structured_format": "bioc_xml",
        "article_ids": {
            "doi": xml_doi or requested,
            "pmcid": f"PMC{document_id or expected_pmc}",
        },
        "document_count": len(documents),
        "passage_count": len([text for text in texts if text]),
        "supplementary_reference_count": 0,
        "supplementary_references": [],
    }


def destination_for(paper_id: str) -> Path:
    digest = hashlib.sha256(paper_id.encode("utf-8")).hexdigest()[:20]
    return SOURCE_POOL / digest


def metadata_for_doi(doi: str, timeout: int, retries: int) -> tuple[dict[str, Any], str]:
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urlencode(
        {
            "query": f'DOI:"{doi}"',
            "format": "json",
            "resultType": "core",
            "pageSize": "5",
        }
    )
    body, _headers = request(url, timeout, retries)
    payload = json.loads(body.decode("utf-8"))
    rows = (payload.get("resultList") or {}).get("result") or []
    exact = [
        row
        for row in rows
        if str(row.get("doi") or "").strip().lower() == doi.strip().lower()
    ]
    if len(exact) != 1:
        raise RuntimeError(f"expected one exact DOI result, found {len(exact)}")
    return exact[0], url


def recover_one(
    item: dict[str, Any], apply: bool, timeout: int, retries: int
) -> dict[str, Any]:
    paper_id = str(item["paper_id"])
    doi = str(item["doi"])
    source_pdf = Path(str(item["source_pdf"]))
    destination = destination_for(paper_id)
    row: dict[str, Any] = {
        "paper_id": paper_id,
        "doi": doi,
        "source_pdf": str(source_pdf),
        "destination": str(destination),
        "apply": apply,
        "started_at": utc_now(),
        "attempts": [],
    }
    if not source_pdf.exists():
        row.update(status="invalid_or_missing_canonical_pdf", finished_at=utc_now())
        return row
    with source_pdf.open("rb") as handle:
        if handle.read(4) != b"%PDF":
            row.update(status="invalid_or_missing_canonical_pdf", finished_at=utc_now())
            return row
    try:
        metadata, metadata_url = metadata_for_doi(doi, timeout, retries)
        row["attempts"].append(
            {"service": "europe_pmc_search", "url": metadata_url, "status": "ok"}
        )
    except Exception as error:  # noqa: BLE001 - durable acquisition evidence
        row["attempts"].append(
            {
                "service": "europe_pmc_search",
                "status": "failed",
                "error": f"{type(error).__name__}: {error}"[:1000],
            }
        )
        row.update(status="metadata_lookup_failed", finished_at=utc_now())
        return row
    pmcid = str(metadata.get("pmcid") or "").strip()
    row["pmcid"] = pmcid or None
    row["pmid"] = metadata.get("pmid")
    row["title"] = metadata.get("title")
    row["is_open_access"] = metadata.get("isOpenAccess")
    row["in_europe_pmc"] = metadata.get("inEPMC")
    if not pmcid:
        row.update(status="no_pmcid_for_doi", finished_at=utc_now())
        return row
    xml_url = (
        "https://www.ebi.ac.uk/europepmc/webservices/rest/"
        f"{pmcid}/fullTextXML"
    )
    try:
        xml_body, headers = request(xml_url, timeout, retries)
        xml_summary = validate_xml(xml_body, doi)
        structured_format = "jats"
        row["attempts"].append(
            {
                "service": "europe_pmc_fulltext_xml",
                "url": xml_url,
                "status": "validated",
                "http_status": headers.get("status"),
                "size_bytes": len(xml_body),
            }
        )
    except Exception as error:  # noqa: BLE001 - durable acquisition evidence
        row["attempts"].append(
            {
                "service": "europe_pmc_fulltext_xml",
                "url": xml_url,
                "status": "failed",
                "error": f"{type(error).__name__}: {error}"[:1000],
            }
        )
        bioc_url = (
            "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/"
            f"pmcoa.cgi/BioC_xml/{pmcid}/unicode"
        )
        try:
            xml_body, headers = request(bioc_url, timeout, retries)
            xml_summary = validate_bioc_xml(xml_body, doi, pmcid)
            structured_format = "bioc_xml"
            xml_url = bioc_url
            row["attempts"].append(
                {
                    "service": "ncbi_pmc_bioc_xml",
                    "url": bioc_url,
                    "status": "validated",
                    "http_status": headers.get("status"),
                    "size_bytes": len(xml_body),
                }
            )
        except Exception as bioc_error:  # noqa: BLE001 - acquisition evidence
            row["attempts"].append(
                {
                    "service": "ncbi_pmc_bioc_xml",
                    "url": bioc_url,
                    "status": "failed",
                    "error": f"{type(bioc_error).__name__}: {bioc_error}"[:1000],
                }
            )
            row.update(status="fulltext_xml_recovery_failed", finished_at=utc_now())
            return row
    row["xml_summary"] = xml_summary
    if apply:
        destination.mkdir(parents=True, exist_ok=True)
        atomic_write(destination / "paper.xml", xml_body)
        pdf_target = destination / "paper.pdf"
        if pdf_target.exists() or pdf_target.is_symlink():
            pdf_target.unlink()
        os.symlink(source_pdf.resolve(), pdf_target)
        (destination / "supplementary").mkdir(exist_ok=True)
        atomic_write_json(
            destination / "paper_meta.json",
            {
                "recovered_at": utc_now(),
                "paper_id": paper_id,
                "doi": doi,
                "pmcid": pmcid,
                "pmid": metadata.get("pmid"),
                "title": metadata.get("title"),
                "journalTitle": metadata.get("journalTitle"),
                "pubYear": metadata.get("pubYear"),
                "isOpenAccess": metadata.get("isOpenAccess"),
                "inEPMC": metadata.get("inEPMC"),
                "canonical_pdf_source": str(source_pdf),
                "fulltext_xml_source": xml_url,
                "structured_fulltext_format": structured_format,
                "material_recovery_only_not_scientific_review": True,
            },
        )
    row.update(
        status=(
            f"validated_{structured_format}_pdf_pair_staged"
            if apply
            else f"validated_{structured_format}_available"
        ),
        finished_at=utc_now(),
    )
    return row


def worklist_items(
    queue_path: Path, limit: int, filter_paper_id: str | None = None
) -> list[dict[str, Any]]:
    ids = set(read_json(queue_path)["paper_ids"])
    rows = read_json(WORKLIST)
    items = []
    for work_row in rows:
        if not isinstance(work_row, list) or len(work_row) < 3:
            continue
        paper_id, source, kind = str(work_row[0]), str(work_row[1]), str(work_row[2])
        if paper_id not in ids or kind != "pdf":
            continue
        if filter_paper_id is not None and filter_paper_id != paper_id:
            continue
        doi = paper_id if paper_id.lower().startswith("10.") else ""
        if not doi:
            continue
        items.append({"paper_id": paper_id, "doi": doi, "source_pdf": source})
    items.sort(key=lambda row: row["paper_id"])
    return items[:limit] if limit else items


def existing_overlay_rows() -> list[list[str]]:
    rows: list[list[str]] = []
    if not SOURCE_POOL.exists():
        return rows
    for meta_path in sorted(SOURCE_POOL.glob("*/paper_meta.json")):
        source_dir = meta_path.parent
        xml_path = source_dir / "paper.xml"
        pdf_path = source_dir / "paper.pdf"
        if not xml_path.exists() or not pdf_path.exists():
            continue
        metadata = read_json(meta_path)
        paper_id = str(metadata.get("paper_id") or "")
        if paper_id:
            rows.append([paper_id, str(xml_path), "xml"])
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, default=QUEUE)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--paper-id")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--run-label")
    args = parser.parse_args()

    items = worklist_items(args.queue, args.limit, args.paper_id)
    if args.paper_id and not items:
        raise SystemExit(f"no PDF-only frozen-queue worklist row for {args.paper_id}")
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(
                recover_one, item, args.apply, args.timeout, args.retries
            ): item
            for item in items
        }
        for future in as_completed(futures):
            try:
                rows.append(future.result())
            except Exception as error:  # noqa: BLE001 - preserve infra failures
                item = futures[future]
                rows.append(
                    {
                        "paper_id": item["paper_id"],
                        "status": "recovery_worker_exception",
                        "error": f"{type(error).__name__}: {error}"[:1000],
                    }
                )
    rows.sort(key=lambda row: str(row.get("paper_id")))
    status_counts = Counter(str(row.get("status")) for row in rows)
    run_label = args.run_label or f"structured_source_recovery_{stamp()}"
    report = {
        "generated_at": utc_now(),
        "run_label": run_label,
        "apply": args.apply,
        "queue_path": str(args.queue),
        "queue_sha256": hashlib.sha256(args.queue.read_bytes()).hexdigest(),
        "paper_count": len(rows),
        "status_counts": dict(sorted(status_counts.items())),
        "source_pool": str(SOURCE_POOL),
        "overlay_path": str(OVERLAY),
        "completion_claim": "material_recovery_only_not_scientific_review",
        "rows": rows,
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{run_label}.json"
    atomic_write_json(report_path, report)
    atomic_write_json(REPORT_DIR / "structured_source_recovery_latest.json", report)
    if args.apply:
        overlay_rows = existing_overlay_rows()
        atomic_write_json(
            OVERLAY,
            {
                "generated_at": utc_now(),
                "source_report": str(report_path),
                "source_report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
                "row_count": len(overlay_rows),
                "rows": overlay_rows,
                "strict_boundary": "material worklist overlay only; not scientific review",
            },
        )
    print(
        json.dumps(
            {
                "generated_at": report["generated_at"],
                "apply": args.apply,
                "paper_count": len(rows),
                "status_counts": report["status_counts"],
                "report_path": str(report_path),
                "overlay_row_count": len(existing_overlay_rows()),
                "completion_claim": report["completion_claim"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not status_counts.get("recovery_worker_exception") else 1


if __name__ == "__main__":
    raise SystemExit(main())
