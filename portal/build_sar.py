#!/usr/bin/env python3
"""Build a matched-pair SAR layer from the atlas activity records (deterministic; no LLM).

Within each paper, find near-analog peptide pairs (clean linear sequences differing by a few
substitutions, or a truncation/extension), match them on a shared assay (endpoint + target + unit),
and record the modification + fold-change in activity + change in physicochemistry.

Output: a `sar_pairs` table in atlas.db + pipeline_v2/sar_pairs.tsv
Run: python3 build_sar.py [--db atlas.db]
"""
import sqlite3, re, json, argparse, collections, itertools, statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLEAN = re.compile(r"^[ACDEFGHIKLMNPQRSTVWY]{4,}$")
COLS = ["paper_id", "doi", "seq_parent", "seq_variant", "peptide_parent", "peptide_variant",
        "modification", "mod_type", "endpoint", "target", "unit",
        "value_parent", "value_variant", "fold_change", "censored",
        "d_net_charge", "d_gravy", "d_mu_h", "n_shared_assays"]


def norm_target(t):
    t = (t or "").strip()
    if not t:
        return ""
    try:
        d = json.loads(t)
        if isinstance(d, dict):
            return (d.get("species") or d.get("class") or d.get("name") or json.dumps(d, sort_keys=True))[:60].lower()
    except Exception:
        pass
    return t[:60].lower()


_num = re.compile(r"\s*([<>≤≥]?=?)\s*([0-9]+\.?[0-9]*)")


def parse_val(v):
    m = _num.match(str(v or ""))
    if not m:
        return None, ""
    return float(m.group(2)), m.group(1)


def mutation(a, b):
    """Describe a→b. Returns (label, mod_type) or (None,None) if too complex."""
    if len(a) == len(b):
        diffs = [(i, a[i], b[i]) for i in range(len(a)) if a[i] != b[i]]
        if not diffs or len(diffs) > 4:
            return None, None
        label = ";".join(f"{x}{i+1}{y}" for i, x, y in diffs)  # e.g. A5R (1-indexed)
        return label, "substitution"
    lo, hi = (a, b) if len(a) < len(b) else (b, a)
    if hi.startswith(lo):
        return (f"C-term +{len(hi)-len(lo)}" if b == hi else f"C-term -{len(hi)-len(lo)}"), "length_C"
    if hi.endswith(lo):
        return (f"N-term +{len(hi)-len(lo)}" if b == hi else f"N-term -{len(hi)-len(lo)}"), "length_N"
    return None, None


def build_into(db):
    db.row_factory = sqlite3.Row
    feats = {r["sequence"]: r for r in db.execute("SELECT sequence,net_charge,gravy,mu_h_per_res FROM features")}

    # per paper: sequence -> peptide name; and (seq) -> {(endpoint,target,unit): [values]}
    paper_seqs = collections.defaultdict(dict)          # paper -> {seq: peptide_name}
    paper_doi = {}
    assays = collections.defaultdict(lambda: collections.defaultdict(list))  # (paper,seq) -> key -> [rawval]
    for r in db.execute("SELECT paper_id,doi,peptide,sequence,endpoint,target,raw_value,raw_unit FROM activity WHERE sequence<>''"):
        s = (r["sequence"] or "").strip().upper()
        if not CLEAN.fullmatch(s):
            continue
        paper_seqs[r["paper_id"]][s] = r["peptide"] or ""
        paper_doi[r["paper_id"]] = r["doi"] or ""
        ep = (r["endpoint"] or "").strip()
        if not ep:
            continue
        key = (ep, norm_target(r["target"]), (r["raw_unit"] or "").strip())
        assays[(r["paper_id"], s)][key].append(r["raw_value"])

    def med_val(paper, seq, key):
        vals = [parse_val(v) for v in assays[(paper, seq)].get(key, [])]
        nums = [(n, c) for n, c in vals if n is not None]
        if not nums:
            return None, ""
        # median of numeric parts; censor flag if any censored
        n = statistics.median([x[0] for x in nums])
        c = next((x[1] for x in nums if x[1]), "")
        return n, c

    rows = []
    for paper, seqmap in paper_seqs.items():
        seqs = sorted(seqmap)
        if len(seqs) < 2:
            continue
        for a, b in itertools.combinations(seqs, 2):
            # near-analog test
            if len(a) == len(b):
                d = sum(1 for x, y in zip(a, b) if x != y)
                if not (1 <= d <= 4):
                    continue
            elif abs(len(a) - len(b)) <= 3 and (a in b or b in a):
                pass
            else:
                continue
            mod, mtype = mutation(a, b)
            if not mod:
                continue
            # shared assays
            ka = set(assays[(paper, a)]); kb = set(assays[(paper, b)])
            shared = ka & kb
            if not shared:
                continue
            fa = feats.get(a); fb = feats.get(b)
            for key in shared:
                ep, tgt, unit = key
                va, ca = med_val(paper, a, key)
                vb, cb = med_val(paper, b, key)
                if va is None or vb is None or va == 0:
                    continue
                fold = round(vb / va, 3)
                rows.append((paper, paper_doi.get(paper, ""), a, b, seqmap.get(a, ""), seqmap.get(b, ""),
                             mod, mtype, ep, tgt, unit, va, vb, fold, (ca or cb),
                             round((fb["net_charge"] - fa["net_charge"]), 2) if fa and fb else "",
                             round((fb["gravy"] - fa["gravy"]), 3) if fa and fb else "",
                             round((fb["mu_h_per_res"] - fa["mu_h_per_res"]), 3) if fa and fb else "",
                             len(shared)))

    db.execute("DROP TABLE IF EXISTS sar_pairs")
    db.execute(f"CREATE TABLE sar_pairs({','.join(c+' TEXT' for c in COLS)})")
    db.executemany(f"INSERT INTO sar_pairs VALUES({','.join('?'*len(COLS))})", rows)
    db.execute("CREATE INDEX i_sar_paper ON sar_pairs(paper_id)")
    db.execute("CREATE INDEX i_sar_modtype ON sar_pairs(mod_type)")
    db.commit()
    # export tsv
    outp = HERE.parent / "pipeline_v2" / "sar_pairs.tsv"
    with outp.open("w", encoding="utf-8") as f:
        f.write("\t".join(COLS) + "\n")
        for r in rows:
            f.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")
    # report
    npairs = len(set((r[0], r[2], r[3]) for r in rows))
    print(f"SAR rows (pair×assay): {len(rows)}  | distinct analog pairs: {npairs}  | papers: {len(set(r[0] for r in rows))}")
    mt = collections.Counter(r[7] for r in rows)
    print("by mod_type:", dict(mt))
    subs = [r for r in rows if r[7] == "substitution"]
    print(f"single-substitution rows: {sum(1 for r in subs if ';' not in r[6])}")
    print("sample big-effect single subs (|log2 fold|>=2):")
    import math
    shown = 0
    for r in rows:
        if r[7] == "substitution" and ";" not in r[6] and r[13] and float(r[13]) > 0:
            lf = abs(math.log2(float(r[13])))
            if lf >= 2 and shown < 6:
                print(f"  {r[6]:8} {r[8]:5} vs {r[9][:20]:20} fold={r[13]}  dQ={r[15]} dGravy={r[16]}  {r[0]}")
                shown += 1
    print(f"\nwrote {outp}")
    return len(rows), npairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=HERE / "atlas.db")
    args = ap.parse_args()
    db = sqlite3.connect(args.db)
    build_into(db)


if __name__ == "__main__":
    main()
