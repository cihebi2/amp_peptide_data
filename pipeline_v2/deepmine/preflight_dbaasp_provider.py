#!/usr/bin/env python3
"""Small provider/quota preflight for DBAASP extraction.

This script intentionally sends a tiny prompt before a DBAASP extraction round.
If the provider is rate-limited or unavailable, the supervisor can stop before
launching hundreds or thousands of expensive paper-level calls.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "pipeline_v2" / "deepmine"
REPORT = HERE / "dbaasp_provider_preflight_latest.json"
_RL = re.compile(
    r"rate limit|usage limit|429|overloaded|quota|too many requests|please try again|"
    r"resource_exhausted|exceeded",
    re.I,
)


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_report(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def snippet(text, n=1200):
    text = text or ""
    return text[:n] + ("..." if len(text) > n else "")


def claude_preflight(model, timeout):
    model = model or "sonnet"
    exe = shutil.which("claude")
    report = {
        "created_at": now_iso(),
        "provider": "claude",
        "model": model,
        "executable": exe or "",
        "timeout_seconds": timeout,
        "status": "unknown",
    }
    if not exe:
        report["status"] = "unavailable"
        report["reason"] = "claude executable not found"
        return report, 1
    prompt = (
        "Provider availability check for a local batch pipeline. "
        "Return exactly this JSON array and no other text: []"
    )
    cmd = [exe, "-p", prompt, "--model", model]
    if os.geteuid() != 0 or os.environ.get("DEEPMINE_CLAUDE_DANGEROUS") == "1":
        cmd.append("--dangerously-skip-permissions")
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as ex:
        report.update({
            "status": "timeout",
            "reason": f"provider preflight timed out after {timeout}s",
            "stdout": snippet(ex.stdout if isinstance(ex.stdout, str) else ""),
            "stderr": snippet(ex.stderr if isinstance(ex.stderr, str) else ""),
            "duration_seconds": round(time.time() - t0, 3),
        })
        return report, 1
    blob = (r.stdout or "") + "\n" + (r.stderr or "")
    report.update({
        "returncode": r.returncode,
        "duration_seconds": round(time.time() - t0, 3),
        "stdout": snippet(r.stdout),
        "stderr": snippet(r.stderr),
        "rate_limit_match": bool(_RL.search(blob)),
    })
    if report["rate_limit_match"]:
        report["status"] = "ratelimited"
        report["reason"] = "provider output matched rate-limit/quota pattern"
        return report, 1
    if r.returncode != 0:
        report["status"] = "error"
        report["reason"] = "provider returned non-zero exit status"
        return report, 1
    report["status"] = "ok"
    report["reason"] = "provider accepted minimal preflight prompt"
    return report, 0


def codex_preflight(model, timeout):
    exe = shutil.which("codex")
    report = {
        "created_at": now_iso(),
        "provider": "codex",
        "model": model,
        "executable": exe or "",
        "timeout_seconds": timeout,
        "status": "unknown",
    }
    if not exe:
        report["status"] = "unavailable"
        report["reason"] = "codex executable not found"
        return report, 1
    import tempfile
    prompt = "Return exactly this JSON array and no other text: []"
    with tempfile.TemporaryDirectory() as td:
        outf = Path(td) / "codex_preflight.txt"
        cmd = [
            exe, "exec", "--skip-git-repo-check",
            "--dangerously-bypass-approvals-and-sandbox",
            "-C", str(ROOT), "-o", str(outf),
        ]
        if model:
            cmd.extend(["--model", model])
        cmd.append("-")
        t0 = time.time()
        try:
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as ex:
            report.update({
                "status": "timeout",
                "reason": f"codex preflight timed out after {timeout}s",
                "stdout": snippet(ex.stdout if isinstance(ex.stdout, str) else ""),
                "stderr": snippet(ex.stderr if isinstance(ex.stderr, str) else ""),
                "duration_seconds": round(time.time() - t0, 3),
            })
            return report, 1
        out_text = outf.read_text(encoding="utf-8", errors="replace") if outf.exists() else ""
    blob = out_text + "\n" + (r.stdout or "") + "\n" + (r.stderr or "")
    report.update({
        "returncode": r.returncode,
        "duration_seconds": round(time.time() - t0, 3),
        "stdout": snippet(r.stdout),
        "stderr": snippet(r.stderr),
        "output_file_text": snippet(out_text),
        "rate_limit_match": bool(_RL.search(blob)),
    })
    if report["rate_limit_match"]:
        report["status"] = "ratelimited"
        report["reason"] = "codex output matched rate-limit/quota pattern"
        return report, 1
    if r.returncode != 0:
        report["status"] = "error"
        report["reason"] = "codex returned non-zero exit status"
        return report, 1
    report["status"] = "ok"
    report["reason"] = "codex accepted minimal preflight prompt"
    return report, 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="claude", choices=["claude", "codex"])
    ap.add_argument("--model", default="")
    ap.add_argument("--timeout", type=int, default=45)
    ap.add_argument("--report", type=Path, default=REPORT)
    ap.add_argument("--no-call", action="store_true", help="only check local executable/config path; do not call the provider")
    args = ap.parse_args()
    if args.no_call:
        exe = shutil.which(args.provider)
        report = {
            "created_at": now_iso(),
            "provider": args.provider,
            "model": args.model,
            "executable": exe or "",
            "status": "ok" if exe else "unavailable",
            "reason": "no-call executable check",
            "called_provider": False,
        }
        write_report(args.report, report)
        print(f"{args.provider} preflight {report['status']}: {report['reason']}")
        return 0 if exe else 1
    if args.provider == "claude":
        report, rc = claude_preflight(args.model, args.timeout)
    elif args.provider == "codex":
        report, rc = codex_preflight(args.model, args.timeout)
    else:
        raise AssertionError(args.provider)
    report["called_provider"] = True
    write_report(args.report, report)
    print(f"{args.provider} preflight {report['status']}: {report.get('reason', '')}")
    print(f"report: {args.report}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
