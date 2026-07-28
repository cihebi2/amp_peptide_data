#!/usr/bin/env python3
"""Compute therapeutic index / selectivity (TI = toxicity_conc / MIC) from activity records.

Deterministic (no LLM). For each (paper, peptide): pair the antibacterial MIC with a
concentration-based toxicity endpoint (HC50/HD50/MHC/CC50/LC50) in the SAME unit family and
compute TI = tox_conc / MIC (higher = more selective/safer). Percent-hemolysis endpoints are
not concentrations, so they can't yield TI and are skipped.

Output: `selectivity` table in atlas.db + pipeline_v2/selectivity.tsv
Called by build_db after activity load.
"""
import sqlite3, re, collections, statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
_JUNK = {"mic", "mbc", "ic50", "ec50", "hc50", "cc50", "mbec", "mbic", "fici", "ki", "kd", "ec90",
         "mic50", "mic90", "n/a", "na", "nd", "nt", "-", "", "value", "peptide", "control", "none", "compound", "sample"}
# plausible upper bound for a toxicity concentration (HC50/CC50/MHC); above this it's a mis-parse
_TOX_CAP = {"uM": 5000.0, "ug/mL": 5000.0}


def is_junk(e):
    e = (e or "").strip()
    return (not e) or e.lower() in _JUNK or len(e) < 2 or e[0] in "{[" or not re.search(r"[A-Za-z]", e)
COLS = ["paper_id", "peptide", "mic_value", "mic_unit", "mic_target",
        "tox_endpoint", "tox_value", "tox_unit", "ti", "note"]


def unit_family(u):
    u = (u or "").lower().replace(" ", "")
    if any(x in u for x in ("µm", "μm", "um", "µmol", "μmol", "umoll")):
        return "uM"
    if any(x in u for x in ("µg/ml", "μg/ml", "ug/ml", "mg/l", "μg/ml")):
        return "ug/mL"
    return None


def num(v):
    m = re.search(r"[0-9]+\.?[0-9]*", str(v or ""))
    return float(m.group(0)) if m else None


_TOX = re.compile(r"hc50|hd50|\bmhc\b|cc50|lc50|hemol|haemol|cytotox", re.I)
_TOX_PCT = re.compile(r"percent|%|_at_|figure_estimate", re.I)  # percent-type, not a 50% conc


def build_into(db):
    db.row_factory = sqlite3.Row
    # collect per (paper,peptide): MICs and toxicity concentrations, by unit family
    mic = collections.defaultdict(lambda: collections.defaultdict(list))   # (paper,pep)->fam->[(val,target)]
    tox = collections.defaultdict(lambda: collections.defaultdict(list))   # (paper,pep)->fam->[(val,endpoint)]
    for r in db.execute("SELECT paper_id,peptide,endpoint,raw_value,raw_unit,target FROM activity WHERE peptide<>'' AND raw_value GLOB '*[0-9]*'"):
        if is_junk(r["peptide"]):
            continue
        ep = (r["endpoint"] or ""); fam = unit_family(r["raw_unit"]); v = num(r["raw_value"])
        if not fam or v is None or v <= 0:
            continue
        key = (r["paper_id"], r["peptide"])
        epl = ep.lower()
        if "mic" in epl and not any(x in epl for x in ("combination", "_mic_", "mbc", "mbec", "mbic", "ratio", "geometric")):
            mic[key][fam].append((v, r["target"] or ""))
        elif _TOX.search(ep) and not _TOX_PCT.search(ep) and v <= _TOX_CAP.get(fam, 5000.0):
            tox[key][fam].append((v, ep))
    rows = []
    for key in mic:
        paper, pep = key
        for fam in mic[key]:
            if fam not in tox[key]:
                continue
            mv, mtgt = min(mic[key][fam], key=lambda x: x[0])   # most potent MIC
            tvals = [t[0] for t in tox[key][fam]]
            tv = round(statistics.median(tvals), 2)             # robust toxicity representative
            tep = tox[key][fam][0][1]
            ti = round(tv / mv, 1)
            rows.append((paper, pep, mv, fam, (mtgt or "")[:40], tep[:30], tv, fam, ti,
                         "TI = median toxicity_conc / min_MIC (same unit family)"))
    db.execute("DROP TABLE IF EXISTS selectivity")
    db.execute(f"CREATE TABLE selectivity({','.join(c+' TEXT' for c in COLS)})")
    db.executemany(f"INSERT INTO selectivity VALUES({','.join('?'*len(COLS))})", rows)
    db.execute("CREATE INDEX i_sel_pep ON selectivity(peptide)")
    db.execute("CREATE INDEX i_sel_paper ON selectivity(paper_id)")
    db.commit()
    (HERE.parent / "pipeline_v2" / "selectivity.tsv").write_text(
        "\t".join(COLS) + "\n" + "\n".join("\t".join(str(x) for x in r) for r in rows), encoding="utf-8")
    return len(rows)


def main():
    db = sqlite3.connect(HERE / "atlas.db")
    n = build_into(db)
    print(f"selectivity (TI) rows: {n}")
    for r in db.execute("SELECT peptide,mic_value,mic_unit,tox_endpoint,tox_value,ti FROM selectivity ORDER BY CAST(ti AS REAL) DESC LIMIT 6"):
        print(f"  {r['peptide'][:16]:16} MIC {r['mic_value']}{r['mic_unit']}  {r['tox_endpoint'][:16]} {r['tox_value']}  -> TI {r['ti']}")


if __name__ == "__main__":
    main()
