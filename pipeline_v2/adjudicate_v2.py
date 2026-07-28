#!/usr/bin/env python3
"""pipeline_v2 step 3: round-trip-validate codex v2 output and compare vs the OLD pipeline + ground truth.

Round-trip (RC4 fix): every is_database_error verdict must cite an evidence cell that exists VERBATIM in
the deterministic longform_cells; otherwise the verdict is demoted to 'unverified_locator'.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json_array(text):
    s = text.find("[")
    e = text.rfind("]")
    return json.loads(text[s:e + 1])


def norm(v):
    return re.sub(r"\s+", "", str(v or "")).lower().replace(",", "")


def cell_index(pack):
    cells = {}   # exact (table,row,col) -> value
    rows = {}    # (table,row) -> set of values  (handles duplicate/spanned col headers)
    for t in pack["tables"]:
        for c in t["longform_cells"]:
            cells[(c["table_index"], norm(c["row_label"]), norm(c["col_header"]))] = norm(c["value"])
            rows.setdefault((c["table_index"], norm(c["row_label"])), set()).add(norm(c["value"]))
    return {"cells": cells, "rows": rows}


def roundtrip(ev, idx):
    if not ev:
        return "no_evidence"
    sv = norm(ev.get("source_value"))
    rkey = (ev.get("table_index"), norm(ev.get("row_label")))
    if rkey not in idx["rows"]:
        return "row_not_found"
    # the cited source value must actually exist in the cited source row (defeats hallucinated/drifted cells)
    if sv and any(sv in v or v in sv for v in idx["rows"][rkey]):
        return "ok"
    return "value_not_in_row"


def _nums(s):
    return [float(x) for x in re.findall(r"\d+\.?\d*", str(s or ""))]

def value_consistent(db_val, src_val):
    """True if a value_mismatch is actually NOT a contradiction (weaker bound, in-range, rounding)."""
    db, src = str(db_val or ""), str(src_val or "")
    dn, sn = _nums(db), _nums(src)
    if not dn or not sn:
        return False
    d, s = dn[0], sn[0]
    db_gt, src_gt = (">" in db or "≥" in db), (">" in src or "≥" in src)
    db_lt, src_lt = ("<" in db or "≤" in db), ("<" in src or "≤" in src)
    # weaker/compatible bounds: DB ">100" vs src ">200" (or numeric >100) -> consistent
    if db_gt and (src_gt or not (src_lt)) and s >= d:
        return True
    if db_lt and (src_lt or not (src_gt)) and s <= d:
        return True
    # source range [a,b] contains DB value
    if len(sn) >= 2 and min(sn) <= d <= max(sn):
        return True
    if len(dn) >= 2 and min(dn) <= s <= max(dn):
        return True
    # rounding / near-equal (<=5% relative)
    if max(d, s) > 0 and abs(d - s) / max(d, s) <= 0.05:
        return True
    return False


_ENDPOINT_RE = re.compile(r'(?i)\b(MIC|MBC|MFC|MBIC|MBEC|IC50|EC50|GI50|CC50|HC50|LC50|LD50|FIC|MIC100|HD50|hemoly|haemoly|cytotox|viabilit|inhibit|killing|bacterici|fungici|reduction)\b')
_FALLBACK_RE = re.compile(r'(?i)^col\d+$')

def _canon_endpoint(s):
    s = (s or "").lower()
    for k in ['ic50','ec50','gi50','cc50','hc50','lc50','ld50','mbic','mbec','mbc','mfc','mic','fic','hd50']:
        if k in s:
            return k
    if 'hemoly' in s or 'haemoly' in s: return 'hemolysis'
    if 'viabilit' in s or 'killing' in s or 'reduction' in s: return 'viability'
    if 'inhibit' in s: return 'inhibition'
    return ''

def endpoint_mismatch_reliable(db_endpoint, source_col):
    """An endpoint_mismatch is only trustworthy if the SOURCE column is a real, non-fallback endpoint
    label that canonicalises differently from the DB endpoint (defeats parser-fallback cols, peptide-name
    cols, and synonyms like MIC vs 'Minimum Inhibitory Activity')."""
    sc = (source_col or "").strip()
    if _FALLBACK_RE.match(sc) or not _ENDPOINT_RE.search(sc):
        return False
    dc, scn = _canon_endpoint(db_endpoint), _canon_endpoint(sc)
    return not (dc and scn and dc == scn)


def peptide_identity(a):
    nc = a.get("name_check") or ""
    try:
        o = json.loads(nc)
        for k in ("database_name", "db_name"):
            if o.get(k):
                return str(o[k])
    except Exception:
        pass
    return a.get("record_name") or ""


def mgs4_ground_truth(claim):
    pep = claim.get("peptide", "")
    val = claim.get("value", "")
    diag = (("V8" in pep and "34" in val) or ("V9" in pep and ("3.9" in val or "=4nM" in val))
            or ("V10" in pep and ("1.5" in val or "2.5" in val)))
    return "not_error" if diag else "error"


def main():
    papers = sys.argv[1:]
    grand = []
    for p in papers:
        wd = ROOT / f"pipeline_v2/work/{p}"
        pack = json.loads((wd / "evidence_pack.json").read_text(encoding="utf-8"))
        chosen = json.loads((wd / "chosen_assertions.json").read_text(encoding="utf-8"))
        verdicts = load_json_array((wd / "v2_result_raw.md").read_text(encoding="utf-8"))
        idx = cell_index(pack)
        by_i = {v.get("assertion_index", n): v for n, v in enumerate(verdicts)}
        print("\n" + "=" * 100)
        print(f"PAPER {p}")
        print("-" * 100)
        print(f"{'#':>2} {'old_status':16} {'v2_outcome':22} {'v2_err':6} {'roundtrip':16} {'GT':9} note")
        rows = []
        for a in chosen:
            i = a["assertion_index"]
            v = by_i.get(i, {})
            outc = v.get("verification_outcome", "MISSING")
            err = bool(v.get("is_database_error"))
            rt = roundtrip(v.get("evidence"), idx) if err else "-"
            # an error is only counted if it is a POSITIVE-evidence mismatch that round-trips;
            # absence-type outcomes can never be a confirmed error (incomplete extraction != absent from paper)
            POSITIVE = {"value_mismatch", "endpoint_mismatch", "variant_misattribution"}
            eff_err = bool(err and outc in POSITIVE and rt == "ok")
            # GUARD: variant_misattribution requires a real peptide-identity anchor; without it,
            # the "belongs to a different variant" claim is unfounded (coded/ambiguous columns).
            if eff_err and outc == "variant_misattribution" and not peptide_identity(a).strip():
                eff_err = False
                rt = "no_peptide_identity->demoted"
            # GUARD: a value_mismatch that is actually a weaker bound / in-range / rounding is NOT an error
            if eff_err and outc == "value_mismatch" and value_consistent(
                    (v.get("db_claimed") or {}).get("value"), (v.get("evidence") or {}).get("source_value")):
                eff_err = False
                rt = "values_consistent->demoted"
            # GUARD: endpoint_mismatch only when the source column is a real, differently-canonicalised endpoint
            if eff_err and outc == "endpoint_mismatch" and not endpoint_mismatch_reliable(
                    (v.get("db_claimed") or {}).get("endpoint"), (v.get("evidence") or {}).get("col_header")):
                eff_err = False
                rt = "endpoint_unreliable->demoted"
            gt = ""
            if "s42003" in p:
                gt = mgs4_ground_truth(v.get("db_claimed", {}))
            elif "ijms22136679" in p:
                gt = "not_error"  # these source_conflict strain rows: values match source, ATCC-vs-CCM only
            note = (v.get("short_reason", "") or "")[:54]
            print(f"{i:>2} {a['original_status'][:16]:16} {outc[:22]:22} {str(eff_err):6} {str(rt)[:16]:16} {gt[:9]:9} {note}")
            rows.append({"old": a["original_status"], "outcome": outc, "v2_error": eff_err, "rt": rt, "gt": gt})
        grand.append((p, rows))

    # scorecard
    print("\n" + "#" * 100)
    print("SCORECARD")
    for p, rows in grand:
        old_conf = sum(1 for r in rows if r["old"] == "source_conflict")
        v2_err = sum(1 for r in rows if r["v2_error"])
        # vs ground truth where available
        gt_rows = [r for r in rows if r["gt"] in ("error", "not_error")]
        tp = sum(1 for r in gt_rows if r["gt"] == "error" and r["v2_error"])
        fn = sum(1 for r in gt_rows if r["gt"] == "error" and not r["v2_error"])
        tn = sum(1 for r in gt_rows if r["gt"] == "not_error" and not r["v2_error"])
        fp = sum(1 for r in gt_rows if r["gt"] == "not_error" and r["v2_error"])
        rt_bad = sum(1 for r in rows if r["v2_error"] and r["rt"] != "ok")
        print(f"\n{p}")
        print(f"  old pipeline source_conflict in sample: {old_conf}/{len(rows)}")
        print(f"  v2 flagged as real error: {v2_err}/{len(rows)}")
        if gt_rows:
            print(f"  vs ground truth -> TP(caught real err)={tp} FN(missed)={fn} TN(cleared false-positive)={tn} FP(new false alarm)={fp}")
        print(f"  v2 errors failing locator round-trip: {rt_bad}")


if __name__ == "__main__":
    main()
