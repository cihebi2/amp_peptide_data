#!/usr/bin/env python3
"""Attempt bounded primary-source recovery for metadata-only papers.

This is a material acquisition tool, not a review worker. It stages recovered
primary PDF/XML/package files back into the landed source layout and records
every attempt. It never marks a paper scientifically reviewed.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlparse
from urllib.request import Request, urlopen


USER_AGENT = "batch4-material-source-recovery/1.0"
SUPP_EXTENSIONS = {".zip", ".gz", ".rar", ".7z", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".tsv", ".ppt", ".pptx", ".txt", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".svg", ".eps"}


class LinkParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.links: list[dict[str, str]] = []
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): (value or "") for key, value in attrs}
        if tag.lower() == "meta":
            name = (data.get("name") or data.get("property") or "").strip().lower()
            content = data.get("content", "").strip()
            if name and content:
                self.meta[name] = content
        if tag.lower() != "a":
            return
        href = data.get("href", "").strip()
        if href and not href.startswith(("javascript:", "mailto:")):
            self.links.append({"href": urljoin(self.base_url, href), "text": "", "class": data.get("class", ""), "rel": data.get("rel", "")})

    def handle_data(self, data: str) -> None:
        if self.links:
            self.links[-1]["text"] += data.strip()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def request_url(url: str, *, timeout: int, retries: int) -> tuple[bytes, dict[str, str]]:
    headers = {"User-Agent": USER_AGENT}
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urlopen(Request(url, headers=headers), timeout=timeout) as response:
                body = response.read()
                out = {key.lower(): value for key, value in response.headers.items()}
                out["status"] = str(response.status)
                out["final_url"] = response.geturl()
                return body, out
        except (HTTPError, URLError, TimeoutError, RuntimeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"request_failed:{type(last_error).__name__}:{last_error}")


def looks_like_pdf(body: bytes, content_type: str) -> bool:
    return body.startswith(b"%PDF") or "pdf" in content_type.lower()


def looks_like_xml(body: bytes, content_type: str) -> bool:
    stripped = body.lstrip()
    return stripped.startswith(b"<?xml") or (stripped.startswith(b"<") and "xml" in content_type.lower())


def looks_like_html(body: bytes, content_type: str) -> bool:
    stripped = body.lstrip().lower()
    return "html" in content_type.lower() or stripped.startswith(b"<!doctype html") or stripped.startswith(b"<html")


def looks_like_package(body: bytes, content_type: str, url: str) -> bool:
    suffixes = [suffix.lower() for suffix in Path(urlparse(url).path).suffixes]
    if body[:2] in {b"PK", b"\x1f\x8b"}:
        return True
    if suffixes[-2:] == [".tar", ".gz"] or suffixes[-1:] in [[".zip"], [".gz"], [".rar"], [".7z"]]:
        return not looks_like_html(body, content_type)
    lowered = content_type.lower()
    return "zip" in lowered or "gzip" in lowered or "compressed" in lowered


def target_suffix(url: str, content_type: str, fallback: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix:
        return suffix
    guessed = mimetypes.guess_extension(content_type.split(";", 1)[0].strip()) if content_type else ""
    return guessed or fallback


def save_if_valid(url: str, target_dir: Path, prefix: str, expected: str, timeout: int, retries: int) -> dict[str, Any]:
    body, headers = request_url(url, timeout=timeout, retries=retries)
    content_type = headers.get("content-type", "")
    final_url = headers.get("final_url", url)
    if expected == "pdf" and not looks_like_pdf(body, content_type):
        raise RuntimeError(f"expected_pdf_got:{content_type}")
    if expected == "xml" and not looks_like_xml(body, content_type):
        raise RuntimeError(f"expected_xml_got:{content_type}")
    if expected == "package" and not looks_like_package(body, content_type, final_url):
        raise RuntimeError(f"expected_package_got:{content_type}")
    suffix = target_suffix(final_url, content_type, {"pdf": ".pdf", "xml": ".xml", "package": ".tar.gz"}[expected])
    target = target_dir / f"{prefix}{suffix}"
    target_dir.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(body)
    return {"status": "downloaded", "asset_type": expected, "url": url, "final_url": final_url, "target": str(target), "size_bytes": len(body), "content_type": content_type}


def fetch_openalex_candidates(doi: str, timeout: int, retries: int) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    pdf_urls: list[str] = []
    landing_urls: list[str] = []
    if not doi:
        return pdf_urls, landing_urls, attempts
    url = "https://api.openalex.org/works/" + quote(f"doi:{doi}", safe=":")
    try:
        body, _headers = request_url(url, timeout=timeout, retries=retries)
        data = json.loads(body.decode("utf-8", errors="replace"))
        attempts.append({"tool": "openalex", "url": url, "status": "ok"})
        for location_key in ("primary_location", "best_oa_location"):
            location = data.get(location_key) or {}
            if location.get("pdf_url"):
                pdf_urls.append(str(location["pdf_url"]))
            if location.get("landing_page_url"):
                landing_urls.append(str(location["landing_page_url"]))
        oa = data.get("open_access") or {}
        if oa.get("oa_url"):
            landing_urls.append(str(oa["oa_url"]))
    except Exception as exc:  # noqa: BLE001
        attempts.append({"tool": "openalex", "url": url, "status": "failed", "error": str(exc)[:500]})
    return list(dict.fromkeys(pdf_urls)), list(dict.fromkeys(landing_urls)), attempts


def pmc_package_url(pmcid: str, timeout: int, retries: int) -> tuple[str, dict[str, Any]]:
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={quote(pmcid)}"
    try:
        body, _headers = request_url(url, timeout=timeout, retries=retries)
        text = body.decode("utf-8", errors="replace")
        match = re.search(r'href="(ftp://ftp\.ncbi\.nlm\.nih\.gov/[^\"]+\.tar\.gz)"', text)
        if match:
            return match.group(1).replace("ftp://ftp.ncbi.nlm.nih.gov/", "https://ftp.ncbi.nlm.nih.gov/"), {"tool": "pmc_oa", "url": url, "status": "ok"}
        return "", {"tool": "pmc_oa", "url": url, "status": "no_package"}
    except Exception as exc:  # noqa: BLE001
        return "", {"tool": "pmc_oa", "url": url, "status": "failed", "error": str(exc)[:500]}


def landing_candidates(url: str, timeout: int, retries: int) -> tuple[dict[str, list[str]], dict[str, Any]]:
    try:
        body, headers = request_url(url, timeout=timeout, retries=retries)
        final_url = headers.get("final_url", url)
        content_type = headers.get("content-type", "")
        if looks_like_pdf(body, content_type):
            return {"pdf": [final_url], "xml": [], "package": [], "supplementary": []}, {"tool": "landing", "url": url, "status": "direct_pdf", "final_url": final_url}
        parser = LinkParser(final_url)
        parser.feed(body.decode("utf-8", errors="replace"))
        candidates = {"pdf": [], "xml": [], "package": [], "supplementary": []}
        for key in ("citation_pdf_url", "eprints.document_url"):
            if parser.meta.get(key):
                candidates["pdf"].append(urljoin(final_url, parser.meta[key]))
        for key in ("citation_xml_url", "citation_fulltext_xml_url"):
            if parser.meta.get(key):
                candidates["xml"].append(urljoin(final_url, parser.meta[key]))
        for link in parser.links:
            href = link["href"]
            blob = f"{href} {link['text']} {link['class']} {link['rel']}".lower()
            suffix = Path(urlparse(href).path).suffix.lower()
            if suffix == ".pdf" or "/pdf" in href.lower():
                candidates["pdf"].append(href)
            elif suffix in {".xml", ".nxml"}:
                candidates["xml"].append(href)
            elif suffix in SUPP_EXTENSIONS or any(token in blob for token in ("supp", "moesm", "source data")):
                candidates["supplementary"].append(href)
        return {key: list(dict.fromkeys(value)) for key, value in candidates.items()}, {"tool": "landing", "url": url, "status": "ok", "final_url": final_url}
    except Exception as exc:  # noqa: BLE001
        return {"pdf": [], "xml": [], "package": [], "supplementary": []}, {"tool": "landing", "url": url, "status": "failed", "error": str(exc)[:500]}


def current_counts(source_path: Path) -> dict[str, int]:
    return {
        "primary_xml": sum(1 for item in (source_path / "xml").glob("*.xml") if item.is_file()),
        "xml_or_nxml": sum(1 for item in (source_path / "xml").glob("*") if item.is_file() and item.suffix.lower() in {".xml", ".nxml"}),
        "pdf": sum(1 for item in (source_path / "pdf").glob("*.pdf") if item.is_file()),
        "package": sum(1 for item in (source_path / "package").glob("*") if item.is_file()),
        "supplementary": sum(1 for item in (source_path / "supplementary").glob("*") if item.is_file()),
    }


def recover_item(item: dict[str, Any], apply: bool, timeout: int, retries: int) -> dict[str, Any]:
    paper_id = str(item["paper_id"])
    source_path = Path(str(item["source_path"]))
    ids = item.get("identifiers") or {}
    doi = str(ids.get("doi") or "").strip()
    pmcid = str(ids.get("pmcid") or "").strip().removeprefix("PMC")
    if pmcid:
        pmcid = "PMC" + pmcid
    before = current_counts(source_path)
    attempts: list[dict[str, Any]] = []
    downloads: list[dict[str, Any]] = []

    if not apply:
        return {"paper_id": paper_id, "source_path": str(source_path), "status": "not_attempted_dry_run", "before_counts": before, "after_counts": before, "attempts": attempts, "downloads": downloads}

    if pmcid:
        xml_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{quote(pmcid)}/fullTextXML"
        try:
            downloads.append(save_if_valid(xml_url, source_path / "xml", f"recovered-{pmcid}", "xml", timeout, retries))
            attempts.append({"tool": "europepmc_fulltext_xml", "url": xml_url, "status": "downloaded"})
        except Exception as exc:  # noqa: BLE001
            attempts.append({"tool": "europepmc_fulltext_xml", "url": xml_url, "status": "failed", "error": str(exc)[:500]})
        package_url, package_attempt = pmc_package_url(pmcid, timeout, retries)
        attempts.append(package_attempt)
        if package_url:
            try:
                downloads.append(save_if_valid(package_url, source_path / "package", f"recovered-{pmcid}", "package", timeout, retries))
            except Exception as exc:  # noqa: BLE001
                attempts.append({"tool": "pmc_package_download", "url": package_url, "status": "failed", "error": str(exc)[:500]})

    pdf_urls, landing_urls, openalex_attempts = fetch_openalex_candidates(doi, timeout, retries)
    attempts.extend(openalex_attempts)
    if doi:
        landing_urls.append(f"https://doi.org/{doi}")

    for index, url in enumerate(dict.fromkeys(pdf_urls), start=1):
        try:
            downloads.append(save_if_valid(url, source_path / "pdf", f"recovered-openalex-{index}", "pdf", timeout, retries))
            break
        except Exception as exc:  # noqa: BLE001
            attempts.append({"tool": "openalex_pdf", "url": url, "status": "failed", "error": str(exc)[:500]})

    for landing_url in dict.fromkeys(landing_urls):
        candidates, landing_attempt = landing_candidates(landing_url, timeout, retries)
        attempts.append(landing_attempt)
        for expected, target_dir in (("pdf", source_path / "pdf"), ("xml", source_path / "xml")):
            if current_counts(source_path)["pdf" if expected == "pdf" else "xml_or_nxml"] > 0:
                continue
            for index, url in enumerate(candidates[expected][:3], start=1):
                try:
                    downloads.append(save_if_valid(url, target_dir, f"recovered-landing-{index}", expected, timeout, retries))
                    break
                except Exception as exc:  # noqa: BLE001
                    attempts.append({"tool": f"landing_{expected}", "url": url, "status": "failed", "error": str(exc)[:500]})
        if current_counts(source_path)["pdf"] and current_counts(source_path)["xml_or_nxml"]:
            break

    after = current_counts(source_path)
    if after["primary_xml"] and after["pdf"]:
        status = "recovered_strict_primary_xml_pdf"
    elif after["xml_or_nxml"] and after["pdf"]:
        status = "recovered_primary_fulltext_with_nxml_or_pdf"
    elif after["xml_or_nxml"] or after["pdf"]:
        status = "recovered_partial_primary_source"
    else:
        status = "not_recovered_after_best_effort"
    return {"paper_id": paper_id, "source_path": str(source_path), "status": status, "before_counts": before, "after_counts": after, "attempts": attempts, "downloads": downloads}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("reports/source_recovery/metadata_only_manifest_latest.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("reports/source_recovery/metadata_acquisition"))
    parser.add_argument("--run-label", default=None)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--apply", action="store_true", help="Actually download/stage recovered files. Without this, only writes dry-run rows.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = read_json(args.manifest)
    items = [item for item in manifest.get("items", []) if isinstance(item, dict)]
    if args.limit:
        items = items[: args.limit]
    run_label = args.run_label or f"metadata_acquisition_{safe_stamp()}"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(recover_item, item, args.apply, args.timeout, args.retries): item for item in items}
        for future in as_completed(futures):
            try:
                rows.append(future.result())
            except Exception as exc:  # noqa: BLE001
                item = futures[future]
                rows.append({"paper_id": item.get("paper_id"), "status": "infra_worker_exception", "error": str(exc)[:1000]})
    rows.sort(key=lambda row: str(row.get("paper_id")))
    status_counts = Counter(str(row.get("status")) for row in rows)
    summary = {
        "generated_at": utc_now(),
        "manifest": str(args.manifest),
        "run_label": run_label,
        "apply": args.apply,
        "paper_count": len(rows),
        "status_counts": dict(status_counts),
        "completion_claim": "metadata_primary_source_acquisition_attempts_not_review_completion",
        "rows": rows,
    }
    out = args.out_dir / f"{run_label}.json"
    write_json(out, summary)
    write_json(args.out_dir / "metadata_acquisition_latest.json", summary)
    append_jsonl(args.out_dir / f"{run_label}.jsonl", rows)
    print(json.dumps({k: summary[k] for k in ["generated_at", "manifest", "run_label", "apply", "paper_count", "status_counts", "completion_claim"]}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
