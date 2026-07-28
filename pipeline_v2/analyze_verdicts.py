#!/usr/bin/env python3
"""Report on the human-review verdicts: progress, precision, severity, per-DB/per-type breakdown,
and Cohen's kappa (if items were double-reviewed).

Verdicts source (priority):
  1. --verdicts <path>            explicit file
  2. default: pull live file from the dm server over ssh
  3. --local                      use the local deploy copy ~/amp_review_deploy/data/review_verdicts.json

Worksheet (authoritative item metadata) is always the local TSV.
Optional kappa input: --log <path>, or review_log.jsonl beside --verdicts, or pulled alongside verdicts.
"""
import csv, json, os, sys, subprocess, tempfile, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSHEET = ROOT / "pipeline_v2/HUMAN_REVIEW_worksheet.tsv"
csv.field_size_limit(10**9)

SSH = ["ssh", "-i", os.path.expanduser("~/.ssh/id_rsa_dm"), "-o", "IdentitiesOnly=yes",
       "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=12", "root@154.3.37.88"]
REMOTE_DIR = "/root/amp_review_deploy/data"


def pull_remote(name):
    try:
        r = subprocess.run(SSH + [f"cat {REMOTE_DIR}/{name} 2>/dev/null"],
                           capture_output=True, text=True, timeout=30)
        return r.stdout if r.returncode == 0 and r.stdout.strip() else ""
    except Exception:
        return ""


def get_verdicts(args):
    if "--verdicts" in args:
        p = Path(args[args.index("--verdicts") + 1])
        return json.loads(p.read_text()), str(p)
    if "--local" in args:
        p = Path.home() / "amp_review_deploy/data/review_verdicts.json"
        return (json.loads(p.read_text()) if p.exists() else {}), str(p)
    txt = pull_remote("review_verdicts.json")
    if txt:
        return json.loads(txt), "dm:review_verdicts.json (live)"
    p = Path.home() / "amp_review_deploy/data/review_verdicts.json"
    return (json.loads(p.read_text()) if p.exists() else {}), str(p) + " (ssh failed, local fallback)"


def get_log(args):
    if "--log" in args:
        p = Path(args[args.index("--log") + 1])
        return p.read_text(encoding="utf-8").splitlines() if p.exists() else []
    if "--local" in args or "--verdicts" in args:
        if "--verdicts" in args:
            vp = Path(args[args.index("--verdicts") + 1])
            for p in (vp.with_name("review_log.jsonl"), ROOT / "pipeline_v2" / "review_log.jsonl"):
                if p.exists():
                    return p.read_text(encoding="utf-8").splitlines()
        p = Path.home() / "amp_review_deploy/data/review_log.jsonl"
        return p.read_text(encoding="utf-8").splitlines() if p.exists() else []
    txt = pull_remote("review_log.jsonl")
    return txt.splitlines() if txt else []


def pct(n, d):
    return f"{100*n/d:.1f}%" if d else "n/a"


def bar(n, d, w=24):
    f = int(round(w * n / d)) if d else 0
    return "█" * f + "·" * (w - f)


def cohens_kappa(pairs):
    """pairs: list of (labelA, labelB). Returns (kappa, n, po)."""
    n = len(pairs)
    if n == 0:
        return None, 0, 0
    cats = sorted({c for ab in pairs for c in ab})
    po = sum(1 for a, b in pairs if a == b) / n
    a_cnt = collections.Counter(a for a, _ in pairs)
    b_cnt = collections.Counter(b for _, b in pairs)
    pe = sum((a_cnt[c]/n) * (b_cnt[c]/n) for c in cats)
    k = (po - pe) / (1 - pe) if (1 - pe) else 1.0
    return k, n, po


def main():
    args = sys.argv[1:]
    verdicts, vsrc = get_verdicts(args)
    rows = list(csv.DictReader(WORKSHEET.open(encoding="utf-8"), delimiter="\t"))
    by_id = {r["review_id"]: r for r in rows}
    total = len(rows)
    n_dual = sum(1 for r in rows if r["priority"] == "DUAL")

    # join
    reviewed = []
    for rid, v in verdicts.items():
        if rid not in by_id:
            continue
        r = by_id[rid]
        reviewed.append({**r, **v})

    print("=" * 64)
    print("  AMP Evidence Atlas — 人工核对报表")
    print(f"  verdicts source: {vsrc}")
    print("=" * 64)

    # ---- progress ----
    done = len(reviewed)
    dual_done = sum(1 for x in reviewed if x["priority"] == "DUAL")
    print(f"\n【进度】 {bar(done,total)}  {done}/{total} ({pct(done,total)})")
    print(f"        DUAL  {bar(dual_done,n_dual)}  {dual_done}/{n_dual} ({pct(dual_done,n_dual)})")
    if not reviewed:
        print("\n(还没有任何判定结果)"); return

    ai_like = sum(1 for x in reviewed if x.get("is_human_verdict") is False or x.get("source") == "codex_cli_ai_assisted")
    if ai_like:
        print(f"\n【来源警告】当前 verdicts 含 {ai_like} 条 AI-assisted 记录；下面统计不是纯人工 precision，不能当作人工验证结论。")

    vc = collections.Counter(x["verdict"] for x in reviewed)
    print("\n【判定分布】")
    for v in ("confirmed", "not_an_error", "uncertain"):
        print(f"  {v:14s} {vc.get(v,0)}")

    # ---- precision (confirmed / (confirmed + not_an_error)); uncertain excluded ----
    def prec(items):
        c = sum(1 for x in items if x["verdict"] == "confirmed")
        e = sum(1 for x in items if x["verdict"] == "not_an_error")
        u = sum(1 for x in items if x["verdict"] == "uncertain")
        return c, e, u, (c/(c+e) if (c+e) else None)

    print("\n【精度】 precision = confirmed / (confirmed + not_an_error)   (uncertain 单列)")
    for lab, items in (("全部", reviewed),
                       ("DUAL 双模型", [x for x in reviewed if x["priority"] == "DUAL"]),
                       ("单模型", [x for x in reviewed if x["priority"] != "DUAL"])):
        c, e, u, p = prec(items)
        print(f"  {lab:12s} confirmed={c:3d} not_err={e:3d} uncertain={u:3d}  precision={pct(c,c+e) if p is not None else 'n/a'}")

    # ---- severity (among confirmed) ----
    conf = [x for x in reviewed if x["verdict"] == "confirmed"]
    sv = collections.Counter(x.get("severity") or "(未填)" for x in conf)
    print(f"\n【严重度】（confirmed={len(conf)} 中）")
    for s in ("critical", "major", "minor", "(未填)"):
        if sv.get(s):
            print(f"  {s:10s} {bar(sv[s],len(conf))}  {sv[s]} ({pct(sv[s],len(conf))})")

    # ---- breakdown by database / error_type ----
    for key, title in (("database", "数据库"), ("error_type", "错误类型")):
        print(f"\n【按{title}】 (confirmed / not_err / uncertain · precision)")
        groups = collections.defaultdict(list)
        for x in reviewed:
            groups[x.get(key, "?")].append(x)
        for g in sorted(groups, key=lambda g: -len(groups[g])):
            c, e, u, p = prec(groups[g])
            print(f"  {g:16s} {c:3d}/{e:3d}/{u:3d}   precision={pct(c,c+e) if p is not None else 'n/a'}")

    # ---- Cohen's kappa (needs double-review) ----
    print("\n【一致性 Cohen's κ】")
    log = get_log(args)
    # group log entries by review_id -> {reviewer: verdict (latest)}
    per_item = collections.defaultdict(dict)
    for line in log:
        try:
            e = json.loads(line)
        except Exception:
            continue
        rev = (e.get("reviewer") or "").strip() or "(anon)"
        if e.get("review_id") and e.get("verdict"):
            per_item[e["review_id"]][rev] = e["verdict"]
    # find the two reviewers with the most shared items
    reviewers = collections.Counter()
    for d in per_item.values():
        for rev in d:
            reviewers[rev] += 1
    best_k = None
    if len(reviewers) >= 2:
        top = [r for r, _ in reviewers.most_common()]
        # try every pair, keep the one with most overlap
        best_pair, best_pairs = None, []
        for i in range(len(top)):
            for j in range(i + 1, len(top)):
                a, b = top[i], top[j]
                shared = [(d[a], d[b]) for d in per_item.values() if a in d and b in d]
                if len(shared) > len(best_pairs):
                    best_pairs, best_pair = shared, (a, b)
        if best_pairs:
            k, n, po = cohens_kappa(best_pairs)
            interp = ("极佳 (>0.8)" if k > .8 else "良好 (0.6-0.8)" if k > .6 else
                      "中等 (0.4-0.6)" if k > .4 else "一般 (<0.4)")
            print(f"  raters {best_pair[0]} vs {best_pair[1]}: n_shared={n}  agreement={pct(int(po*n),n)}  κ={k:.3f} [{interp}]")
            best_k = k
    if best_k is None:
        dbl = sum(1 for d in per_item.values() if len(d) >= 2)
        print(f"  暂不可算：需要 ≥2 名审查人核对同一批条目。当前重复核对的条目数={dbl}。")
        if log:
            print("  （已读取 append-only 日志；让两人各核一遍同样的若干条即可自动算出。）")
        else:
            print("  （当前未读取到 append-only 日志；新版 review_server.py 后续保存会写 pipeline_v2/review_log.jsonl。）")

    print("\n" + "=" * 64)


if __name__ == "__main__":
    main()
