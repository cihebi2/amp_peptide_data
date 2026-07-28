#!/usr/bin/env python3
"""Ingest the AMP Evidence Atlas release TSVs into a single SQLite DB for the public portal.

Loads only public_v1_included rows. Builds FTS5 indexes for peptide/sequence/DOI search.
Run:  python3 build_db.py [--release <dir>] [--out atlas.db]
"""
import csv, json, sqlite3, sys, argparse, time, hashlib
from pathlib import Path

csv.field_size_limit(10**9)
HERE = Path(__file__).resolve().parent
DEFAULT_RELEASE = HERE.parent / "releases" / "amp_evidence_atlas_v1_0"


def _truthy(v):
    return (v or "").strip().lower() in ("true", "1", "yes")


def pub(r):
    """Use the frozen release inclusion flag without portal-side recovery rules."""
    return _truthy(r.get("public_v1_included", ""))


def rows(path, want_public=True):
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if want_public and not pub(r):
                continue
            yield r


def col(r, *names):
    for n in names:
        v = r.get(n)
        if v is not None:
            return v.strip()
    return ""


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_frozen_payload(release):
    checksums = release / "payload_checksums.txt"
    if not checksums.exists():
        return
    failures = []
    for line in checksums.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        target = release / relative.strip()
        if not target.is_file():
            failures.append(f"missing:{relative.strip()}")
        elif sha256_file(target) != expected:
            failures.append(f"sha256:{relative.strip()}")
    if failures:
        raise RuntimeError("frozen payload verification failed: " + ", ".join(failures))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", type=Path, default=DEFAULT_RELEASE)
    ap.add_argument("--out", type=Path, default=HERE / "atlas.db")
    ap.add_argument(
        "--include-experimental-increments",
        action="store_true",
        help="Opt in to recovered/machine-extracted post-freeze records. Never use for canonical v1.0 counts.",
    )
    args = ap.parse_args()
    rel, out = args.release, args.out
    assert rel.exists(), f"release dir missing: {rel}"
    verify_frozen_payload(rel)
    release_manifest = json.loads((rel / "release_manifest.json").read_text(encoding="utf-8"))
    if out.exists():
        out.unlink()
    t0 = time.time()
    db = sqlite3.connect(out)
    db.executescript("""
    PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;
    CREATE TABLE papers(paper_id TEXT PRIMARY KEY, doi TEXT, review_status TEXT,
        publication_grade TEXT, n_audit INT, n_activity INT, n_mechanism INT, caution_count INT);
    CREATE TABLE activity(activity_record_id TEXT, paper_id TEXT, doi TEXT,
        peptide TEXT, sequence TEXT, entity TEXT, entity_type TEXT, endpoint TEXT,
        raw_value TEXT, raw_unit TEXT, normalized_value TEXT, normalized_unit TEXT,
        target TEXT, assay_conditions TEXT, evidence_ladder TEXT, source_locator TEXT,
        database_traceability TEXT, curation_notes TEXT, evidence_tier TEXT);
    CREATE TABLE audit(audit_record_id TEXT PRIMARY KEY, paper_id TEXT, doi TEXT, database TEXT,
        record_name TEXT, sequence TEXT, sequence_key TEXT, database_subject TEXT,
        database_measure TEXT, database_value TEXT, database_unit TEXT,
        primary_source_subject TEXT, primary_source_value TEXT, primary_source_unit TEXT,
        status TEXT, difference_categories TEXT, conflict_flags TEXT, conflict_context TEXT,
        conflict_interpretation TEXT, review_status TEXT, review_notes TEXT,
        human_verdict TEXT, human_severity TEXT, human_review_notes TEXT, source_locator TEXT);
    CREATE TABLE conflicts(issue_id TEXT PRIMARY KEY, paper_id TEXT, doi TEXT, database TEXT,
        status TEXT, difference_categories TEXT, severity_hint TEXT, summary TEXT, source_locator TEXT);
    CREATE TABLE mechanism(mechanism_claim_id TEXT, paper_id TEXT, doi TEXT,
        claim_text TEXT, evidence_class TEXT, direct_assay_types TEXT, limitations TEXT);
    CREATE TABLE figures(paper_id TEXT, label TEXT, figure_index TEXT, caption TEXT, locator TEXT);
    CREATE TABLE metadata(k TEXT PRIMARY KEY, v TEXT);
    """)
    metadata = {
        "release_id": release_manifest.get("release_id", rel.name),
        "release_version": release_manifest.get("release_version", ""),
        "release_status": release_manifest.get("status", ""),
        "release_directory": rel.name,
        "payload_checksum_manifest_sha256": release_manifest.get(
            "payload_checksum_manifest_sha256", ""
        ),
        "portal_scope": "public_v1_included_only",
        "experimental_increments_included": str(
            args.include_experimental_increments
        ).lower(),
    }
    db.executemany("INSERT INTO metadata(k,v) VALUES(?,?)", metadata.items())
    db.commit()

    def load(name, table, cols, mapper):
        path = rel / name
        batch, n = [], 0
        ph = ",".join("?" * len(cols))
        verb = "INSERT OR IGNORE" if table in ("papers", "audit", "conflicts") else "INSERT"
        ins = f"{verb} INTO {table}({','.join(cols)}) VALUES({ph})"
        for r in rows(path):
            batch.append(mapper(r))
            if len(batch) >= 5000:
                db.executemany(ins, batch); n += len(batch); batch = []
        if batch:
            db.executemany(ins, batch); n += len(batch)
        db.commit()
        print(f"  {table:10s} {n:7d} rows")
        return n

    print("loading (public_v1_included only)...")
    load("papers.tsv", "papers",
         ["paper_id", "doi", "review_status", "publication_grade", "n_audit", "n_activity", "n_mechanism", "caution_count"],
         lambda r: (col(r, "paper_id"), col(r, "doi"), col(r, "review_status"), col(r, "publication_grade"),
                    col(r, "database_audit_records"), col(r, "activity_records"), col(r, "mechanism_claims"), col(r, "caution_count")))
    load("activity_observations.tsv", "activity",
         ["activity_record_id", "paper_id", "doi", "peptide", "sequence", "entity", "entity_type", "endpoint",
          "raw_value", "raw_unit", "normalized_value", "normalized_unit", "target", "assay_conditions",
          "evidence_ladder", "source_locator", "database_traceability", "curation_notes", "evidence_tier"],
         lambda r: (col(r, "activity_record_id"), col(r, "paper_id"), col(r, "doi"), col(r, "peptide"),
                    col(r, "sequence"), col(r, "entity"), col(r, "entity_type"), col(r, "endpoint"),
                    col(r, "raw_value"), col(r, "raw_unit"), col(r, "normalized_value"), col(r, "normalized_unit"),
                    col(r, "target"), col(r, "assay_conditions"), col(r, "evidence_ladder"), col(r, "source_locator"),
                    col(r, "database_traceability"), col(r, "curation_notes"), "atlas_core"))
    load("database_record_audits.tsv", "audit",
         ["audit_record_id", "paper_id", "doi", "database", "record_name", "sequence", "sequence_key",
          "database_subject", "database_measure", "database_value", "database_unit", "primary_source_subject",
          "primary_source_value", "primary_source_unit", "status", "difference_categories", "conflict_flags",
          "conflict_context", "conflict_interpretation", "review_status", "review_notes",
          "human_verdict", "human_severity", "human_review_notes", "source_locator"],
         lambda r: (col(r, "audit_record_id"), col(r, "paper_id"), col(r, "doi"), col(r, "database"),
                    col(r, "record_name"), col(r, "sequence"), col(r, "sequence_key"), col(r, "database_subject"),
                    col(r, "database_measure"), col(r, "database_value"), col(r, "database_unit"),
                    col(r, "primary_source_subject"), col(r, "primary_source_value"), col(r, "primary_source_unit"),
                    col(r, "status"), col(r, "difference_categories"), col(r, "conflict_flags"),
                    col(r, "conflict_context"), col(r, "conflict_interpretation"), col(r, "review_status"),
                    col(r, "review_notes"), col(r, "human_verdict"), col(r, "human_severity"),
                    col(r, "human_review_notes"), col(r, "source_locator")))
    load("conflicts_and_cautions.tsv", "conflicts",
         ["issue_id", "paper_id", "doi", "database", "status", "difference_categories", "severity_hint", "summary", "source_locator"],
         lambda r: (col(r, "issue_id"), col(r, "paper_id"), col(r, "doi"), col(r, "database"), col(r, "status"),
                    col(r, "difference_categories"), col(r, "severity_hint"), col(r, "summary"), col(r, "source_locator")))
    load("mechanism_claims.tsv", "mechanism",
         ["mechanism_claim_id", "paper_id", "doi", "claim_text", "evidence_class", "direct_assay_types", "limitations"],
         lambda r: (col(r, "mechanism_claim_id"), col(r, "paper_id"), col(r, "doi"), col(r, "claim_text"),
                    col(r, "evidence_class"), col(r, "direct_assay_types"), col(r, "limitations")))

    # dual-model-recovered activity records from excluded papers (evidence_tier=dual_model_recovered).
    # Only approved (dual-consensus supported) rows with a real peptide identity; ~93% spot-check precision.
    rec_tsv = (
        HERE.parent / "pipeline_v2" / "deepmine" / "recovered_approved.tsv"
        if args.include_experimental_increments
        else HERE / ".experimental_increments_disabled"
    )
    n_rec = 0
    if rec_tsv.exists():
        _JUNK = {"mic", "mbc", "ic50", "ec50", "hc50", "cc50", "mbec", "mbic", "fici", "ki", "kd", "ec90",
                 "mic50", "mic90", "n/a", "na", "nd", "nt", "-", "", "value", "peptide", "control", "none", "compound", "sample"}
        import re as _re
        batch = []
        for r in csv.DictReader(rec_tsv.open(encoding="utf-8"), delimiter="\t"):
            e = (r.get("entity") or "").strip()
            if not r.get("paper_id") or (r.get("approved", "").lower() not in ("true", "1")) or \
               not e or e.lower() in _JUNK or len(e) < 2 or not _re.search(r"[A-Za-z]", e):
                continue
            doi = r["paper_id"][5:].replace("_", "/", 1) if r["paper_id"].startswith("doi__") else ""
            batch.append((r.get("record_id", ""), r["paper_id"], doi, e, "", e, "", r.get("endpoint", ""),
                          r.get("raw_value", ""), r.get("raw_unit", ""), "", "", r.get("target", ""), "",
                          "recovered", (r.get("evidence", "") or "")[:300], "",
                          "dual-model recovered (claude+codex consensus)", "dual_model_recovered"))
        db.executemany("INSERT INTO activity VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", batch)
        # add minimal paper rows for recovered papers not already present
        have = {r[0] for r in db.execute("SELECT paper_id FROM papers")}
        newp = {}
        for b in batch:
            if b[1] not in have:
                newp[b[1]] = b[2]
        db.executemany("INSERT INTO papers(paper_id,doi,review_status,publication_grade,n_audit,n_activity,n_mechanism,caution_count) VALUES(?,?,?,?,?,?,?,?)",
                       [(pid, doi, "dual_model_recovered", "", "", "", "", "") for pid, doi in newp.items()])
        db.commit()
        n_rec = len(batch)
        print(f"  recovered   {n_rec:7d} activity rows (dual_model_recovered tier; +{len(newp)} papers)")

    # machine-extracted activity from never-processed papers (full-text PDFs + HTML-only), evidence_tier=machine_extracted.
    # Union of claude(text)+codex(PDF) extraction, tagged by verdict; ~100% source-traceable in spot-checks.
    import re as _re2
    _JUNK2 = {"mic", "mbc", "ic50", "ec50", "hc50", "cc50", "n/a", "na", "nd", "-", "", "value", "peptide", "control", "compound", "sample", "none"}
    n_mx = 0
    mx_have = {r[0] for r in db.execute("SELECT paper_id FROM papers")}
    mx_newp = {}
    mx_sources = (
        (
            HERE.parent / "pipeline_v2" / "deepmine" / "newpapers_extracted.tsv",
            HERE.parent / "pipeline_v2" / "deepmine" / "supphtml_extracted.tsv",
            HERE.parent / "pipeline_v2" / "deepmine" / "docxocr_extracted.tsv",
            HERE.parent / "pipeline_v2" / "deepmine" / "hardcases_extracted.tsv",
        )
        if args.include_experimental_increments
        else ()
    )
    for mx_tsv in mx_sources:
        if not mx_tsv.exists():
            continue
        batch = []
        for r in csv.DictReader(mx_tsv.open(encoding="utf-8"), delimiter="\t"):
            e = (r.get("peptide") or "").strip()
            if not r.get("paper_id") or not e or e.lower() in _JUNK2 or len(e) < 2 or not _re2.search(r"[A-Za-z]", e) or (r.get("value") in (None, "")):
                continue
            doi = r["paper_id"][5:].replace("_", "/", 1) if r["paper_id"].startswith("doi__") else ""
            cond = json.dumps({k: r.get(k, "") for k in ("assay_medium", "inoculum") if r.get(k)}, ensure_ascii=False)
            notes = f"machine-extracted ({r.get('verdict','')}); modification={r.get('modification','none')}"
            batch.append((r.get("paper_id", "") + ":mx", r["paper_id"], doi, e, r.get("sequence", ""), e, "",
                          r.get("endpoint", ""), str(r.get("value", "")), r.get("unit", ""), "", "",
                          r.get("target", ""), cond, r.get("verdict", ""), (r.get("evidence", "") or "")[:300], "",
                          notes, "machine_extracted"))
            if r["paper_id"] not in mx_have:
                mx_newp[r["paper_id"]] = doi
        db.executemany("INSERT INTO activity VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", batch)
        n_mx += len(batch)
    if mx_newp:
        db.executemany("INSERT INTO papers(paper_id,doi,review_status,publication_grade,n_audit,n_activity,n_mechanism,caution_count) VALUES(?,?,?,?,?,?,?,?)",
                       [(pid, doi, "machine_extracted", "", "", "", "", "") for pid, doi in mx_newp.items()])
    db.commit()
    if n_mx:
        print(f"  machine     {n_mx:7d} activity rows (machine_extracted tier; +{len(mx_newp)} papers)")

    # machine-extracted mechanism claims from the new papers → mechanism table (id suffixed :mx).
    mech_tsv = (
        HERE.parent / "pipeline_v2" / "deepmine" / "mechanism_extracted.tsv"
        if args.include_experimental_increments
        else HERE / ".experimental_increments_disabled"
    )
    n_mech_mx = 0
    if mech_tsv.exists():
        mrows = []
        for i, r in enumerate(csv.DictReader(mech_tsv.open(encoding="utf-8"), delimiter="\t")):
            if not r.get("paper_id") or not (r.get("claim_text") or "").strip():
                continue
            doi = r["paper_id"][5:].replace("_", "/", 1) if r["paper_id"].startswith("doi__") else ""
            mrows.append((f"{r['paper_id']}:mech:{i}", r["paper_id"], doi, r.get("claim_text", ""),
                          (r.get("evidence_class", "") or "machine") + " (machine_extracted)",
                          r.get("direct_assay_types", ""), r.get("limitations", "")))
        db.executemany("INSERT INTO mechanism VALUES(?,?,?,?,?,?,?)", mrows)
        db.commit()
        n_mech_mx = len(mrows)
        print(f"  machine-mech {n_mech_mx:6d} mechanism claims (from new papers)")

    # figures: from paper_packets/<paper_id>/extracted/figure_captions.json (public papers only)
    print("loading figures from paper_packets...")
    pub_papers = [r[0] for r in db.execute("SELECT paper_id FROM papers")]
    figrows, fig_papers = [], 0
    for pid in pub_papers:
        fc = HERE.parent / "paper_packets" / pid / "extracted" / "figure_captions.json"
        if not fc.exists():
            continue
        try:
            data = json.loads(fc.read_text(encoding="utf-8"))
        except Exception:
            continue
        figs = data.get("figures") or []
        if figs:
            fig_papers += 1
        for f in figs:
            figrows.append((pid, (f.get("label") or "").strip(), str(f.get("figure_index") or "").strip(),
                            (f.get("caption") or "").strip(), (f.get("locator") or "").strip()))
    db.executemany("INSERT INTO figures(paper_id,label,figure_index,caption,locator) VALUES(?,?,?,?,?)", figrows)
    db.commit()
    print(f"  figures    {len(figrows):7d} rows  ({fig_papers} papers)")

    print("indexing...")
    db.executescript("""
    CREATE INDEX i_fig_paper ON figures(paper_id);
    CREATE INDEX i_act_id ON activity(activity_record_id);
    CREATE INDEX i_mec_id ON mechanism(mechanism_claim_id);
    CREATE INDEX i_act_paper ON activity(paper_id);
    CREATE INDEX i_act_pep ON activity(peptide);
    CREATE INDEX i_act_seq ON activity(sequence);
    CREATE INDEX i_act_ep ON activity(endpoint);
    CREATE INDEX i_aud_paper ON audit(paper_id);
    CREATE INDEX i_aud_db ON audit(database);
    CREATE INDEX i_aud_status ON audit(status);
    CREATE INDEX i_aud_name ON audit(record_name);
    CREATE INDEX i_con_paper ON conflicts(paper_id);
    CREATE INDEX i_mec_paper ON mechanism(paper_id);
    """)
    # unified FTS over searchable peptide identities (activity + audit)
    db.executescript("""
    CREATE VIRTUAL TABLE search USING fts5(kind, ref_id, paper_id, doi, name, sequence, extra, tokenize='unicode61');
    """)
    db.execute("""INSERT INTO search(kind,ref_id,paper_id,doi,name,sequence,extra)
                  SELECT 'activity',activity_record_id,paper_id,doi,peptide,sequence,target FROM activity""")
    db.execute("""INSERT INTO search(kind,ref_id,paper_id,doi,name,sequence,extra)
                  SELECT 'audit',audit_record_id,paper_id,doi,record_name,sequence,database FROM audit""")
    db.commit()
    # summary stats table for the home page
    db.executescript("CREATE TABLE stats(k TEXT PRIMARY KEY, v TEXT);")
    def stat(k, q):
        db.execute("INSERT INTO stats VALUES(?,?)", (k, str(db.execute(q).fetchone()[0])))
    stat("papers", "SELECT COUNT(*) FROM papers")
    stat("activity", "SELECT COUNT(*) FROM activity")
    stat("audit", "SELECT COUNT(*) FROM audit")
    stat("conflicts_audit", "SELECT COUNT(*) FROM audit WHERE status='source_conflict'")
    stat("human_confirmed", "SELECT COUNT(*) FROM audit WHERE human_verdict='confirmed'")
    stat("recovered_activity", "SELECT COUNT(*) FROM activity WHERE evidence_tier='dual_model_recovered'")
    stat("machine_activity", "SELECT COUNT(*) FROM activity WHERE evidence_tier='machine_extracted'")
    stat("mechanism", "SELECT COUNT(*) FROM mechanism")
    stat("peptides", "SELECT COUNT(DISTINCT lower(peptide)) FROM activity WHERE peptide<>''")
    stat("sequences", "SELECT COUNT(DISTINCT upper(sequence)) FROM activity WHERE sequence<>''")
    db.commit()
    # physicochemical features for clean linear sequences
    import sys as _sys
    _sys.path.insert(0, str(HERE))
    import compute_features
    seen, comp, skip = compute_features.compute_into(db)
    print(f"  features   {comp:7d} rows  (of {seen} sequences; {skip} constructs skipped)")
    db.execute("INSERT OR REPLACE INTO stats VALUES('featured_sequences', ?)", (str(comp),))
    db.commit()
    # matched-pair SAR layer (needs the features table above)
    import build_sar
    n_sar, n_pairs = build_sar.build_into(db)
    print(f"  sar_pairs  {n_sar:7d} rows  ({n_pairs} distinct analog pairs)")
    db.execute("INSERT OR REPLACE INTO stats VALUES('sar_pairs', ?)", (str(n_pairs),))
    import build_selectivity
    n_sel = build_selectivity.build_into(db)
    print(f"  selectivity {n_sel:6d} rows (computed TI)")
    db.execute("INSERT OR REPLACE INTO stats VALUES('selectivity', ?)", (str(n_sel),))
    db.row_factory = None
    db.commit()
    db.execute("VACUUM")
    db.close()
    mb = out.stat().st_size / 1e6
    print(f"done -> {out} ({mb:.1f} MB) in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
