#!/usr/bin/env python3
"""Read-only Grok fallback for structured paper review.

This module is intentionally not a canonical extraction-worker runner.  It
exposes a paper-scoped, read-only evidence tool loop to an OpenAI-compatible
Grok endpoint and returns one schema-constrained leader or verifier payload.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any, Callable


DEFAULT_BASE_URL = "http://127.0.0.1:8317/v1"
DEFAULT_ENV_FILE = "/mnt/d/software/CLIProxyAPI/.env"
DEFAULT_LEADER_MODEL = "grok-4.20-0309-reasoning"
DEFAULT_VERIFIER_MODEL = "grok-4.5"
MAX_TOOL_ROUNDS = 80
MAX_TOOL_RESULT_CHARS = 60_000


class GrokStructuredReviewError(RuntimeError):
    """Raised after a Grok review has been recorded as failed closed."""

    def __init__(self, message: str, runtime: dict[str, Any]):
        super().__init__(message)
        self.runtime = runtime


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def load_local_client_key() -> str:
    direct = os.environ.get("CLIPROXY_LOCAL_CLIENT_KEY")
    if direct:
        return direct
    env_file = Path(os.environ.get("CLIPROXY_ENV_FILE", DEFAULT_ENV_FILE))
    if not env_file.exists():
        raise RuntimeError(f"CLIProxyAPI env file is missing: {env_file}")
    for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("CLIPROXY_LOCAL_CLIENT_KEY="):
            key = line.split("=", 1)[1].strip()
            if key:
                return key
    raise RuntimeError(f"CLIPROXY_LOCAL_CLIENT_KEY is missing from {env_file}")


class PaperEvidenceTools:
    """Paper-scoped read-only tools with auditable access coverage."""

    TEXT_SUFFIXES = {
        ".csv",
        ".htm",
        ".html",
        ".json",
        ".jsonl",
        ".md",
        ".tsv",
        ".txt",
        ".xml",
        ".yaml",
        ".yml",
    }

    def __init__(self, root: Path, pilot: Path, campaign_dir: Path, paper_id: str):
        self.root = root.resolve()
        self.pilot = pilot.resolve()
        self.paper_id = paper_id
        paper = self.pilot / "papers" / paper_id
        packet = self.pilot / "packets" / paper_id
        campaign_paper = campaign_dir.resolve() / paper_id
        self.allowed_roots = [
            path.resolve()
            for path in (
                paper / "source",
                paper / "work",
                paper / "final",
                packet,
                self.pilot / "worker_logs" / paper_id,
                campaign_paper,
                self.root / ".codex/skills/amp-three-layer-curation",
                self.root / ".codex/skills/paper-batch-orchestrator",
            )
            if path.exists()
        ]
        acceptance = (
            self.pilot / "reports" / f"{paper_id}_strict_acceptance_audit_latest.json"
        )
        self.allowed_files = [acceptance.resolve()] if acceptance.exists() else []
        self._text_cache: dict[Path, str] = {}
        self.directly_read_paths: set[str] = set()
        self.searched_paths: set[str] = set()
        self.tool_trace: list[dict[str, Any]] = []

    def relative(self, path: Path) -> str:
        return str(path.resolve().relative_to(self.root))

    def resolve(self, raw_path: str, require_file: bool = True) -> Path:
        candidate = Path(raw_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError("path must be workspace-relative without '..'")
        resolved = (self.root / candidate).resolve()
        allowed = resolved in self.allowed_files or any(
            _is_within(resolved, root) for root in self.allowed_roots
        )
        if not allowed:
            raise ValueError("path is outside the paper-scoped evidence allowlist")
        if not resolved.exists():
            raise ValueError("evidence path does not exist")
        if require_file and not resolved.is_file():
            raise ValueError("evidence path must be a file")
        return resolved

    def all_files(self, prefix: str = "") -> list[Path]:
        if prefix:
            selected = self.resolve(prefix, require_file=False)
            candidates = [selected] if selected.is_file() else list(selected.rglob("*"))
        else:
            candidates = list(self.allowed_files)
            for root in self.allowed_roots:
                candidates.extend(root.rglob("*"))
        files: dict[str, Path] = {}
        for path in candidates:
            if path.is_file() and not path.is_symlink():
                files[self.relative(path)] = path.resolve()
        return [files[key] for key in sorted(files)]

    def inventory(self, prefix: str = "") -> dict[str, Any]:
        files = self.all_files(prefix)
        return {
            "paper_id": self.paper_id,
            "file_count": len(files),
            "files": [
                {
                    "path": self.relative(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                    "suffix": path.suffix.lower(),
                }
                for path in files
            ],
        }

    def _pdf_text(self, path: Path) -> str:
        completed = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            text=True,
            capture_output=True,
            timeout=180,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"pdftotext failed for {self.relative(path)}: "
                f"{completed.stderr[:500]}"
            )
        return completed.stdout

    def _xlsx_text(self, path: Path) -> str:
        try:
            import openpyxl
        except ImportError as error:
            raise RuntimeError("openpyxl is required to inspect XLSX evidence") from error
        workbook = openpyxl.load_workbook(
            path, read_only=True, data_only=False, keep_links=False
        )
        lines: list[str] = []
        try:
            for sheet in workbook.worksheets:
                lines.append(f"### SHEET {sheet.title}")
                for row_number, row in enumerate(sheet.iter_rows(values_only=True), 1):
                    values = [
                        "" if value is None else str(value).replace("\n", "\\n")
                        for value in row
                    ]
                    if any(values):
                        lines.append(f"{sheet.title}!row={row_number}\t" + "\t".join(values))
        finally:
            workbook.close()
        return "\n".join(lines)

    def _docx_text(self, path: Path) -> str:
        with zipfile.ZipFile(path) as archive:
            raw = archive.read("word/document.xml").decode(
                encoding="utf-8", errors="replace"
            )
        raw = re.sub(r"</w:p>", "\n", raw)
        raw = re.sub(r"<[^>]+>", "", raw)
        return unescape(raw)

    def _zip_inventory_text(self, path: Path) -> str:
        with zipfile.ZipFile(path) as archive:
            return "\n".join(
                f"{entry.file_size}\t{entry.filename}" for entry in archive.infolist()
            )

    def text(self, path: Path) -> str:
        path = path.resolve()
        if path in self._text_cache:
            return self._text_cache[path]
        suffix = path.suffix.lower()
        if suffix in self.TEXT_SUFFIXES or not suffix:
            value = path.read_text(encoding="utf-8", errors="replace")
        elif suffix == ".pdf":
            value = self._pdf_text(path)
        elif suffix in {".xlsx", ".xlsm"}:
            value = self._xlsx_text(path)
        elif suffix == ".docx":
            value = self._docx_text(path)
        elif suffix == ".zip":
            value = self._zip_inventory_text(path)
        else:
            value = (
                f"[Binary evidence: {self.relative(path)}, "
                f"{path.stat().st_size} bytes, sha256={sha256_file(path)}]"
            )
        self._text_cache[path] = value
        return value

    def read_text(
        self, path: str, offset_chars: int = 0, max_chars: int = 30_000
    ) -> dict[str, Any]:
        resolved = self.resolve(path)
        value = self.text(resolved)
        offset = max(0, int(offset_chars))
        length = min(max(1, int(max_chars)), MAX_TOOL_RESULT_CHARS)
        end = min(len(value), offset + length)
        relative = self.relative(resolved)
        self.directly_read_paths.add(relative)
        return {
            "path": relative,
            "source_sha256": sha256_file(resolved),
            "total_chars": len(value),
            "offset_chars": offset,
            "end_chars": end,
            "complete_file_returned": offset == 0 and end == len(value),
            "content": value[offset:end],
        }

    @staticmethod
    def _json_pointer(value: Any, pointer: str) -> Any:
        if pointer in {"", "/"}:
            return value
        current = value
        for raw_part in pointer.lstrip("/").split("/"):
            part = raw_part.replace("~1", "/").replace("~0", "~")
            if isinstance(current, list):
                current = current[int(part)]
            elif isinstance(current, dict):
                current = current[part]
            else:
                raise ValueError(f"JSON pointer cannot descend through {type(current)}")
        return current

    def read_json(
        self,
        path: str,
        json_pointer: str = "",
        start: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        resolved = self.resolve(path)
        if resolved.suffix.lower() == ".jsonl":
            value: Any = [
                json.loads(line)
                for line in resolved.read_text(
                    encoding="utf-8", errors="replace"
                ).splitlines()
                if line.strip()
            ]
        else:
            value = json.loads(
                resolved.read_text(encoding="utf-8", errors="replace")
            )
        selected = self._json_pointer(value, json_pointer)
        offset = max(0, int(start))
        count = min(max(1, int(limit)), 500)
        total_items: int | None = None
        if isinstance(selected, list):
            total_items = len(selected)
            selected = selected[offset : offset + count]
        elif isinstance(selected, dict) and offset:
            items = list(selected.items())
            total_items = len(items)
            selected = dict(items[offset : offset + count])
        serialized = json.dumps(selected, ensure_ascii=False, indent=2)
        if len(serialized) > MAX_TOOL_RESULT_CHARS:
            serialized = serialized[:MAX_TOOL_RESULT_CHARS]
        relative = self.relative(resolved)
        self.directly_read_paths.add(relative)
        return {
            "path": relative,
            "source_sha256": sha256_file(resolved),
            "json_pointer": json_pointer,
            "start": offset,
            "limit": count,
            "total_items": total_items,
            "serialized_value": serialized,
        }

    def search(
        self, query: str, path_prefix: str = "", max_results: int = 30
    ) -> dict[str, Any]:
        needle = str(query)
        if not needle:
            raise ValueError("query must be non-empty")
        maximum = min(max(1, int(max_results)), 100)
        results: list[dict[str, Any]] = []
        scanned: list[str] = []
        for path in self.all_files(path_prefix):
            try:
                value = self.text(path)
            except Exception as error:  # preserve per-file inspection failures
                results.append(
                    {
                        "path": self.relative(path),
                        "inspection_error": f"{type(error).__name__}: {error}"[:500],
                    }
                )
                continue
            relative = self.relative(path)
            scanned.append(relative)
            self.searched_paths.add(relative)
            for line_number, line in enumerate(value.splitlines(), 1):
                index = line.casefold().find(needle.casefold())
                if index < 0:
                    continue
                if len(results) < maximum:
                    start = max(0, index - 180)
                    end = min(len(line), index + len(needle) + 320)
                    results.append(
                        {
                            "path": relative,
                            "line": line_number,
                            "snippet": line[start:end],
                        }
                    )
        return {
            "query": needle,
            "path_prefix": path_prefix,
            "scanned_file_count": len(scanned),
            "scanned_paths_sha256": sha256_bytes(
                "\n".join(scanned).encode("utf-8")
            ),
            "result_count_returned": len(results),
            "results": results,
        }

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        started = time.monotonic()
        try:
            if name == "list_evidence_files":
                result = self.inventory(str(arguments.get("path_prefix") or ""))
            elif name == "read_evidence_text":
                result = self.read_text(
                    str(arguments["path"]),
                    int(arguments.get("offset_chars") or 0),
                    int(arguments.get("max_chars") or 30_000),
                )
            elif name == "read_json_value":
                result = self.read_json(
                    str(arguments["path"]),
                    str(arguments.get("json_pointer") or ""),
                    int(arguments.get("start") or 0),
                    int(arguments.get("limit") or 100),
                )
            elif name == "search_evidence":
                result = self.search(
                    str(arguments["query"]),
                    str(arguments.get("path_prefix") or ""),
                    int(arguments.get("max_results") or 30),
                )
            else:
                raise ValueError(f"unknown evidence tool: {name}")
            envelope: dict[str, Any] = {"ok": True, "result": result}
        except Exception as error:  # return tool errors for model correction
            envelope = {
                "ok": False,
                "error": f"{type(error).__name__}: {error}"[:1000],
            }
        serialized = json.dumps(envelope, ensure_ascii=False)
        if len(serialized) > MAX_TOOL_RESULT_CHARS:
            serialized = json.dumps(
                {
                    "ok": envelope["ok"],
                    "result_truncated": True,
                    "original_result_chars": len(serialized),
                    "preview": serialized[: MAX_TOOL_RESULT_CHARS - 2000],
                    "instruction": (
                        "Narrow the path/query or request a smaller text chunk."
                    ),
                },
                ensure_ascii=False,
            )
        self.tool_trace.append(
            {
                "tool": name,
                "arguments": arguments,
                "ok": envelope["ok"],
                "result_chars": len(serialized),
                "result_sha256": sha256_bytes(serialized.encode("utf-8")),
                "elapsed_seconds": round(time.monotonic() - started, 3),
            }
        )
        return serialized

    def coverage_requirements(self) -> dict[str, Any]:
        paper = self.pilot / "papers" / self.paper_id
        packet = self.pilot / "packets" / self.paper_id
        final_direct = [
            self.relative(path)
            for directory in (paper / "final", packet / "final")
            if directory.exists()
            for path in directory.rglob("*")
            if path.is_file()
        ]
        runtime_direct = []
        for path in (
            self.pilot / "worker_logs" / self.paper_id / "run_sequence_latest.json",
            self.pilot
            / "reports"
            / f"{self.paper_id}_strict_acceptance_audit_latest.json",
        ):
            if path.exists():
                runtime_direct.append(self.relative(path))
        source_seen = [
            self.relative(path)
            for path in (paper / "source").rglob("*")
            if path.is_file()
        ]
        required_groups = []
        for name, directory in (
            ("paper_work", paper / "work"),
            ("packet_extracted", packet / "extracted"),
            ("packet_analysis", packet / "analysis"),
            ("packet_database", packet / "database"),
            ("packet_rework", packet / "rework"),
        ):
            if directory.exists() and any(path.is_file() for path in directory.rglob("*")):
                required_groups.append(
                    {
                        "name": name,
                        "prefix": self.relative(directory),
                    }
                )
        return {
            "direct_read_files": sorted(set(final_direct + runtime_direct)),
            "source_files_read_or_searched": sorted(set(source_seen)),
            "at_least_one_read_or_search_in_groups": required_groups,
        }

    def coverage_failures(self) -> list[str]:
        requirements = self.coverage_requirements()
        seen = self.directly_read_paths | self.searched_paths
        failures = [
            f"required_direct_read_missing:{path}"
            for path in requirements["direct_read_files"]
            if path not in self.directly_read_paths
        ]
        failures.extend(
            f"source_file_not_inspected:{path}"
            for path in requirements["source_files_read_or_searched"]
            if path not in seen
        )
        for group in requirements["at_least_one_read_or_search_in_groups"]:
            prefix = group["prefix"].rstrip("/") + "/"
            if not any(path == group["prefix"] or path.startswith(prefix) for path in seen):
                failures.append(f"required_group_not_inspected:{group['name']}")
        return sorted(set(failures))


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_evidence_files",
            "description": (
                "List allowlisted paper evidence files with exact workspace-relative "
                "paths, sizes, and hashes. Call this before substantive review."
            ),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"path_prefix": {"type": "string"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_evidence_text",
            "description": (
                "Read a bounded text chunk from an allowlisted file. PDF, XLSX, "
                "DOCX, and ZIP evidence is converted read-only."
            ),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "path": {"type": "string"},
                    "offset_chars": {"type": "integer", "minimum": 0},
                    "max_chars": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": MAX_TOOL_RESULT_CHARS,
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_json_value",
            "description": (
                "Read an allowlisted JSON/JSONL value or paginated array using a "
                "JSON pointer. Use this for every final artifact and runtime report."
            ),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "path": {"type": "string"},
                    "json_pointer": {"type": "string"},
                    "start": {"type": "integer", "minimum": 0},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_evidence",
            "description": (
                "Case-insensitive literal search over every file under an allowlisted "
                "path. The runtime records every scanned source file."
            ),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "query": {"type": "string", "minLength": 1},
                    "path_prefix": {"type": "string"},
                    "max_results": {"type": "integer", "minimum": 1, "maximum": 100},
                },
                "required": ["query"],
            },
        },
    },
]


def _post_chat_completion(
    base_url: str,
    key: str,
    body: dict[str, Any],
    timeout: float,
) -> dict[str, Any]:
    endpoint = base_url.rstrip("/") + "/chat/completions"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=max(10.0, timeout)) as response:
                value = json.load(response)
            if not isinstance(value, dict):
                raise RuntimeError("Grok endpoint returned a non-object response")
            return value
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:2000]
            last_error = RuntimeError(f"Grok HTTP {error.code}: {detail}")
            if error.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise last_error
        except urllib.error.URLError as error:
            last_error = error
            if attempt == 2:
                raise
        time.sleep(2**attempt)
    raise RuntimeError(f"Grok request failed: {last_error}")


def _assistant_message(message: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in message.items()
        if key
        in {
            "role",
            "content",
            "tool_calls",
            "function_call",
            "reasoning_content",
        }
        and value is not None
    }


def _parse_json_content(content: Any) -> dict[str, Any]:
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Grok returned no structured content")
    stripped = content.strip()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise
        value = json.loads(stripped[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("Grok structured content must be a JSON object")
    return value


def run_grok_structured_review(
    *,
    root: Path,
    pilot: Path,
    campaign_dir: Path,
    paper_id: str,
    role: str,
    schema_path: Path,
    prompt: str,
    timeout: int,
    semantic_validator: Callable[[str, dict[str, Any]], list[str]],
    fallback_reason: str,
) -> tuple[Path, dict[str, Any]]:
    """Run one paper-scoped Grok review and fail closed on every uncertainty."""

    stamp = run_stamp()
    paper_dir = campaign_dir / paper_id
    paper_dir.mkdir(parents=True, exist_ok=True)
    output_path = paper_dir / f"{stamp}.{role}.grok.json"
    runtime_path = paper_dir / f"{stamp}.{role}.grok.runtime.json"
    trace_path = paper_dir / f"{stamp}.{role}.grok.tool_trace.json"
    prompt_path = paper_dir / f"{stamp}.{role}.grok.prompt.txt"
    model = (
        os.environ.get("GROK_LEADER_MODEL", DEFAULT_LEADER_MODEL)
        if role == "leader_semantic_auditor"
        else os.environ.get("GROK_VERIFIER_MODEL", DEFAULT_VERIFIER_MODEL)
    )
    base_url = os.environ.get("CLIPROXY_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    evidence = PaperEvidenceTools(root, pilot, campaign_dir, paper_id)
    requirements = evidence.coverage_requirements()
    system = """You are a publication-grade, read-only literature evidence auditor.

This is benign verification of already-published paper evidence against existing
curation artifacts. Do not provide experimental optimization, pathogen
engineering, virulence or resistance enhancement, synthesis instructions, or
operational wet-lab protocols. Only inspect, compare, classify evidence
strength, preserve source conflicts, and report concrete discrepancies.

Use the supplied paper-scoped read-only tools repeatedly. You have no evidence
unless a tool returned it. Never invent a path, locator, value, unit, identity,
or source claim. A PASS is invalid unless every required evidence surface and
every current final record has actually been inspected. If evidence is missing
or not reviewable, return a schema-valid FAIL."""
    user = (
        prompt
        + "\n\nGrok read-only evidence coverage enforced by the local runtime:\n"
        + json.dumps(requirements, ensure_ascii=False, indent=2)
        + "\nCall list_evidence_files first. Directly read every file in "
        "`direct_read_files`; inspect every file in "
        "`source_files_read_or_searched`; and inspect every required group. "
        "Continue tool calls until this is complete, then return only the "
        "schema-constrained JSON verdict."
    )
    prompt_path.write_text(system + "\n\n--- USER REVIEW CONTRACT ---\n" + user, encoding="utf-8")
    runtime: dict[str, Any] = {
        "paper_id": paper_id,
        "role": role,
        "review_provider": "xai_grok_via_local_cliproxy",
        "review_model": model,
        "review_reasoning_mode": (
            "reasoning" if "reasoning" in model else "general"
        ),
        "review_session_id": None,
        "started_at": utc_now(),
        "finished_at": None,
        "returncode": None,
        "timed_out": False,
        "endpoint": base_url,
        "schema_path": str(schema_path),
        "schema_sha256": sha256_file(schema_path),
        "fallback_reason": fallback_reason[:2000],
        "prompt_path": str(prompt_path),
        "output_path": str(output_path),
        "tool_trace_path": str(trace_path),
        "response_ids": [],
        "usage": {},
    }
    started = time.monotonic()
    input_fingerprint_before = _paper_input_fingerprint(pilot, paper_id)
    try:
        key = load_local_client_key()
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        usage: dict[str, int] = {}
        payload: dict[str, Any] | None = None
        for _round in range(1, MAX_TOOL_ROUNDS + 1):
            remaining = timeout - (time.monotonic() - started)
            if remaining <= 0:
                raise TimeoutError("Grok structured review exceeded the audit timeout")
            response = _post_chat_completion(
                base_url,
                key,
                {
                    "model": model,
                    "messages": messages,
                    "tools": TOOLS,
                    "tool_choice": "auto",
                    "temperature": 0,
                    "response_format": {
                        "type": "json_schema",
                        "json_schema": {
                            "name": role,
                            "strict": True,
                            "schema": schema,
                        },
                    },
                },
                remaining,
            )
            response_id = str(response.get("id") or "")
            if response_id:
                runtime["response_ids"].append(response_id)
                if runtime["review_session_id"] is None:
                    runtime["review_session_id"] = f"grok:{response_id}"
            for key_name, value in (response.get("usage") or {}).items():
                if isinstance(value, int):
                    usage[key_name] = usage.get(key_name, 0) + value
            choices = response.get("choices")
            if not isinstance(choices, list) or not choices:
                raise RuntimeError("Grok response has no choices")
            message = choices[0].get("message")
            if not isinstance(message, dict):
                raise RuntimeError("Grok response has no assistant message")
            tool_calls = message.get("tool_calls") or []
            if tool_calls:
                messages.append(_assistant_message(message))
                for tool_call in tool_calls:
                    function = tool_call.get("function") or {}
                    name = str(function.get("name") or "")
                    try:
                        arguments = json.loads(function.get("arguments") or "{}")
                    except json.JSONDecodeError as error:
                        arguments = {"_invalid_arguments": str(error)}
                    result = evidence.execute(name, arguments)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": str(tool_call.get("id") or ""),
                            "content": result,
                        }
                    )
                continue
            payload = _parse_json_content(message.get("content"))
            break
        if payload is None:
            raise RuntimeError(
                f"Grok did not return a final payload in {MAX_TOOL_ROUNDS} tool rounds"
            )
        input_fingerprint_after = _paper_input_fingerprint(pilot, paper_id)
        runtime["paper_input_fingerprint_after"] = input_fingerprint_after
        runtime["paper_inputs_unchanged_during_review"] = (
            input_fingerprint_before == input_fingerprint_after
        )
        coverage_failures = evidence.coverage_failures()
        if not runtime["paper_inputs_unchanged_during_review"]:
            coverage_failures.append("paper_inputs_changed_during_grok_review")
        semantic_failures = semantic_validator(paper_id, payload)
        runtime["coverage_failures"] = coverage_failures
        runtime["local_semantic_validation_failures"] = semantic_failures
        if coverage_failures or semantic_failures:
            raise RuntimeError(
                "Grok payload failed local validation: "
                f"coverage={coverage_failures}, semantic={semantic_failures}"
            )
        atomic_write_json(output_path, payload)
        latest = paper_dir / f"{role}_latest.json"
        atomic_write_json(latest, payload)
        runtime["returncode"] = 0
        return output_path, runtime
    except TimeoutError as error:
        runtime["returncode"] = 124
        runtime["timed_out"] = True
        runtime["error"] = f"{type(error).__name__}: {error}"[:4000]
        raise GrokStructuredReviewError(str(error), runtime) from error
    except Exception as error:
        runtime["returncode"] = 1
        runtime["error"] = f"{type(error).__name__}: {error}"[:4000]
        raise GrokStructuredReviewError(str(error), runtime) from error
    finally:
        runtime["finished_at"] = utc_now()
        runtime["elapsed_seconds"] = round(time.monotonic() - started, 3)
        runtime["usage"] = locals().get("usage", {})
        runtime["paper_input_fingerprint_before"] = input_fingerprint_before
        runtime["paper_input_fingerprint_after"] = runtime.get(
            "paper_input_fingerprint_after"
        ) or _paper_input_fingerprint(pilot, paper_id)
        runtime["paper_inputs_unchanged_during_review"] = (
            runtime["paper_input_fingerprint_before"]
            == runtime["paper_input_fingerprint_after"]
        )
        runtime["directly_read_paths"] = sorted(evidence.directly_read_paths)
        runtime["searched_paths"] = sorted(evidence.searched_paths)
        atomic_write_json(trace_path, evidence.tool_trace)
        atomic_write_json(runtime_path, runtime)


def _paper_input_fingerprint(pilot: Path, paper_id: str) -> str:
    digest = hashlib.sha256()
    paths = []
    for directory in (
        pilot / "papers" / paper_id / "source",
        pilot / "papers" / paper_id / "work",
        pilot / "papers" / paper_id / "final",
        pilot / "packets" / paper_id,
        pilot / "worker_logs" / paper_id,
    ):
        if directory.exists():
            paths.extend(path for path in directory.rglob("*") if path.is_file())
    acceptance = pilot / "reports" / f"{paper_id}_strict_acceptance_audit_latest.json"
    if acceptance.exists():
        paths.append(acceptance)
    for path in sorted(set(paths)):
        relative = str(path.relative_to(pilot))
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()
