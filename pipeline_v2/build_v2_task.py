#!/usr/bin/env python3
"""pipeline_v2 step 2: build the v2 audit prompt for one paper from its evidence pack.

Embeds the root-cause fixes as an explicit two-axis schema + grounding rules.
Writes pipeline_v2/work/<paper_id>/v2_prompt.md (fed to codex via stdin).
"""
import json, sys, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_ASSERTIONS = int(os.environ.get("V2_MAX_ASSERTIONS", "12"))

SCHEMA_RULES = """
You are a STRICT database-record auditor (pipeline v2). You compare what a peptide database ASSERTS
against the PRIMARY PAPER's deterministically-parsed tables that are given to you below. You must not
read raw XML or invent values: the ONLY admissible source evidence is the `longform_cells` provided.

For EACH database assertion, output one JSON object with this exact schema:
{
 "assertion_index": <int, 0-based position in db_assertions>,
 "db_claimed": {"organism": "...", "endpoint": "...", "value": "...", "peptide": "..."},
 "verification_outcome": one of
     "value_match"            (source has the SAME value for the same peptide+organism+endpoint),
     "value_mismatch"         (source has a DIFFERENT value -> candidate real DB error),
     "endpoint_mismatch"      (source reports this value under a DIFFERENT endpoint than the DB claims,
                               e.g. DB says IC50 but the source column header says GI50/EC50/MBC),
     "variant_misattribution" (the value EXISTS in source but belongs to a DIFFERENT peptide/variant
                               than the DB row names),
     "not_in_provided_tables" (the organism/target/value is NOT in the tables provided to you;
                               this is NOT evidence of a database error -- the value may live in a
                               figure, supplement, or a table not provided. Treat as undetermined.),
     "cannot_determine"       (value lives only in a figure image, or no matching cell exists in the
                               provided tables, or the table structure is too ambiguous to match),
 "normalization_note": one of
     "strain_id_differs_value_same", "modification_representation_only", "unit_differs", "none",
 "is_database_error": <bool>,
 "evidence": {"table_index": <int>, "row_label": "...", "col_header": "...", "source_value": "..."},
 "short_reason": "<=200 chars"
}

HARD RULES (these encode the fixes over the old pipeline):
1. GROUNDING: the `evidence` object MUST be copied verbatim from one of the provided `longform_cells`.
   If no provided cell supports a comparison, you MUST return "cannot_determine" and leave evidence null.
   Never guess a number that is not in the provided cells.
2. ENDPOINT FROM SOURCE: take the endpoint from the table column header / caption / footnote, NOT from
   the database. If the DB endpoint label differs from the source header for the same value -> endpoint_mismatch.
3. STRAIN-ID NORMALIZATION: if the source has the SAME value for the same GENUS+SPECIES and SAME endpoint
   but a different strain/collection id (e.g. DB "ATCC 6258" vs source "CCM 8271"; ATCC/CCM/PCM/DSM/KCTC/CGMCC),
   this is NOT an error: verification_outcome="value_match", normalization_note="strain_id_differs_value_same",
   is_database_error=false.
4. MODIFICATION NORMALIZATION: a DB "core sequence" vs a source "core sequence + terminal -NH2 / N-acetyl"
   is representation, not error: normalization_note="modification_representation_only", is_database_error=false
   (unless the residue letters themselves differ).
5. is_database_error=true ONLY for value_mismatch / endpoint_mismatch / variant_misattribution that
   (a) are NOT explained by a normalization_note AND (b) carry a positive `evidence` cell copied from
   longform_cells showing the CONFLICTING source value.
5b. VARIANT MISATTRIBUTION needs an identity anchor: only use "variant_misattribution" when the DB
   assertion provides a peptide name (db_claimed_peptide_name) that maps to a SPECIFIC source row/column.
   If the DB record has no peptide name, or the source columns are coded (e.g. #1..#25) without a legend
   you can resolve, you CANNOT know which variant the value belongs to -> use "cannot_determine".
6. ABSENCE IS NOT ERROR (critical): you are given ONLY some tables, never the whole paper. If a DB
   organism/target/value is not in the provided cells, you MUST return "not_in_provided_tables" with
   is_database_error=false. NEVER conclude the database is wrong merely because something is missing
   from the tables you were given -- it may be in a figure, supplement, or a table not provided.
7. Output ONLY a JSON array of these objects as your final message. No prose, no markdown fences.
"""


def db_claimed_name(x):
    """Extract only the database's OWN claimed peptide name; never leak old-pipeline adjudication."""
    nc = x.get("name_check") or ""
    try:
        obj = json.loads(nc)
        for k in ("database_name", "db_name"):
            if obj.get(k):
                return str(obj[k])
    except Exception:
        pass
    return x.get("record_name") or ""


CONSERV = re.compile(r'not_promoted|not_matched|not_match|not_fully_source|preserved|not_recoverable|not locally recoverable|figure-only|figure_derived|tables_and_sections_unmatched|normalization_not|snapshot_absent|not_closed|granularity|database_only|without_primary_source|raster|not_exactly_supported|core_sequence_only|stores_core', re.I)
CONTRA = re.compile(r'differs|mislink|mixes|incorrect|\bwrong\b|mismatch|conflict_db_|label_conflict|variant_label|target_or_value_differs|differ_', re.I)


def select_assertions(pack):
    a = pack["db_assertions"]
    mode = os.environ.get("V2_SELECT", "mixed")
    if mode == "all_conflict":
        # full-scale: audit source_conflict assertions; V2_OFFSET windows the residual (21st+, etc.)
        off = int(os.environ.get("V2_OFFSET", "0"))
        chosen = [x for x in a if x["original_status"] == "source_conflict"][off:off + MAX_ASSERTIONS]
    elif mode == "genuine":
        # full-run mode: audit the contradiction-flagged ("genuine discordance") conflict rows
        genuine = [x for x in a if x["original_status"] == "source_conflict"
                   and (x.get("original_flags") or "").strip() not in ("", "[]")
                   and CONTRA.search(x.get("original_flags", "")) and not CONSERV.search(x.get("original_flags", ""))]
        chosen = genuine[:MAX_ASSERTIONS]
    else:
        conflict = [x for x in a if x["original_status"] == "source_conflict"]
        verified = [x for x in a if x["original_status"] == "source_verified"]
        n_conf = min(len(conflict), 7)
        n_ver = min(len(verified), MAX_ASSERTIONS - n_conf)
        chosen = conflict[:n_conf] + verified[:n_ver]
        if len(chosen) < MAX_ASSERTIONS:
            rest = [x for x in a if x not in chosen]
            chosen += rest[: MAX_ASSERTIONS - len(chosen)]
    for i, x in enumerate(chosen):
        x["assertion_index"] = i
    return chosen


def compact_tables(pack):
    out = []
    for t in pack["tables"]:
        out.append({
            "table_index": t["table_index"],
            "label": t["label"],
            "caption": t["caption"],
            "footnotes": t["footnotes"],
            "header_rows": t["header_rows"],
            "longform_cells": t["longform_cells"],
        })
    return out


def assertion_block(x):
    return {
        "assertion_index": x["assertion_index"], "database": x["database"],
        "db_subject_text": x["db_subject"], "db_measure": x["db_measure"],
        "db_value": x["db_value"], "db_unit": x["db_unit"], "db_sequence": x["db_sequence"],
        "db_claimed_peptide_name": db_claimed_name(x),
    }


def build_prompt(paper_id, tables, ft_block, assertions):
    return (
        SCHEMA_RULES
        + "\n\n=== PAPER ID ===\n" + paper_id
        + "\n\n=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===\n"
        + json.dumps(tables, ensure_ascii=False)
        + ft_block
        + "\n\n=== DATABASE ASSERTIONS TO VERIFY ===\n"
        + json.dumps([assertion_block(x) for x in assertions], ensure_ascii=False)
        + "\n\nReturn ONLY the JSON array now (one object per assertion above)."
    )


def main():
    paper_id = sys.argv[1]
    wd = ROOT / f"pipeline_v2/work/{paper_id}"
    pack = json.loads((wd / "evidence_pack.json").read_text(encoding="utf-8"))
    chosen = select_assertions(pack)
    tables = compact_tables(pack)
    fulltext = pack.get("fulltext", "")
    ft_block = ""
    if fulltext:
        ft_block = (
            "\n\n=== PRIMARY PAPER FULL TEXT (context only) ===\n"
            "Use this ONLY to (a) confirm whether an organism/target/assay was tested in this paper "
            "(prevents false 'absent' calls), and (b) read an endpoint label. You may NOT cite full text as "
            "the `evidence` cell for is_database_error=true; that still requires a structured longform cell.\n"
            + fulltext
        )
    (wd / "chosen_assertions.json").write_text(json.dumps(chosen, ensure_ascii=False, indent=1), encoding="utf-8")
    chunk = int(os.environ.get("V2_CHUNK_SIZE", "0"))
    if chunk > 0 and len(chosen) > chunk:
        # split into chunks so the model fully enumerates every assertion (fixes MISSING on mega-papers)
        n = 0
        for ci in range(0, len(chosen), chunk):
            sl = chosen[ci:ci + chunk]
            (wd / f"v2_prompt_c{n}.md").write_text(build_prompt(paper_id, tables, ft_block, sl), encoding="utf-8")
            n += 1
        print(f"{paper_id}: assertions={len(chosen)} -> {n} chunks of <= {chunk}")
    else:
        outp = wd / "v2_prompt.md"
        outp.write_text(build_prompt(paper_id, tables, ft_block, chosen), encoding="utf-8")
        print(f"{paper_id}: assertions={len(chosen)} prompt_chars={len((outp).read_text())} (single)")


if __name__ == "__main__":
    main()
