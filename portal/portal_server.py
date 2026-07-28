#!/usr/bin/env python3
"""AMP Evidence Atlas — public database portal (pure stdlib).

Serves search / peptide / paper / conflict-browser / audit-evidence / downloads / about
over the SQLite DB built by build_db.py. Read-only.

Run:  python3 portal_server.py [PORT]   (default 8080)
Env:  BIND_ADDR (default 0.0.0.0; set 127.0.0.1 behind a reverse proxy)
      ATLAS_DB  (default ./atlas.db)
"""
import os, re, sqlite3, html, json, urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = os.environ.get("ATLAS_DB", str(BASE / "atlas.db"))
PAPERS_DIR = Path(os.environ.get("PAPERS_DIR", str(BASE / "papers")))
PAGE_SIZE = 50


def has_pdf(paper_id):
    return (PAPERS_DIR / paper_id / "source" / "paper.pdf").exists()


def parse_locator(s):
    """Turn a source_locator (activity: JSON object; audit: JSON array) into a readable string."""
    s = (s or "").strip()
    if not s:
        return ""
    try:
        d = json.loads(s)
    except Exception:
        return s[:160]
    def one(o):
        if not isinstance(o, dict):
            return str(o)
        lab = o.get("label") or o.get("kind") or ""
        bits = [lab.replace("_", " ")] if lab else []
        if o.get("row_label"):
            bits.append(f"row: {o['row_label']}")
        if o.get("column"):
            bits.append(f"col: {o['column']}")
        if o.get("locator") and "table" not in (lab or "").lower():
            bits.append(str(o["locator"]))
        elif o.get("locator") and o.get("kind"):
            bits.append(str(o["locator"]))
        return " · ".join(b for b in bits if b)
    if isinstance(d, list):
        parts = [one(o) for o in d]
        return "  |  ".join(p for p in parts if p)[:400]
    return one(d)[:300]

_local = None
import threading
_tl = threading.local()


def db():
    c = getattr(_tl, "c", None)
    if c is None:
        c = sqlite3.connect(DB_PATH, check_same_thread=False)
        c.row_factory = sqlite3.Row
        _tl.c = c
    return c


def stats():
    return {r["k"]: int(r["v"]) for r in db().execute("SELECT k,v FROM stats")}


def metadata():
    try:
        return {r["k"]: r["v"] for r in db().execute("SELECT k,v FROM metadata")}
    except sqlite3.OperationalError:
        return {"release_id": "unknown-release", "portal_scope": "unknown"}


def release_id():
    return metadata().get("release_id", "unknown-release")


def e(s):
    return html.escape(str(s or ""))


def fmt_num(n):
    return f"{int(n):,}"


# ---------------------------------------------------------------- layout
CSS = """
:root{--bg:#f7f8fa;--card:#fff;--ink:#1a2233;--mut:#5b6579;--line:#e4e8ef;--brand:#1d5fbf;--brandd:#164a97;
      --bad:#c0392b;--badbg:#fdecea;--ok:#1e7d46;--okbg:#e9f7ef;--warn:#a6730a;--warnbg:#fdf6e3;--mono:ui-monospace,Menlo,Consolas,monospace}
*{box-sizing:border-box}
body{margin:0;font:15px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink)}
a{color:var(--brand);text-decoration:none}a:hover{text-decoration:underline}
header.top{background:linear-gradient(120deg,#164a97,#1d5fbf);color:#fff;padding:0}
.navwrap{max-width:1080px;margin:0 auto;padding:14px 20px;display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.brand{font-size:19px;font-weight:700;color:#fff;letter-spacing:.2px}
.brand small{font-weight:400;opacity:.8;font-size:12px;display:block;letter-spacing:0}
nav.top a{color:#dce8fb;margin-right:16px;font-size:14px}nav.top a:hover{color:#fff}
.wrap{max-width:1080px;margin:22px auto;padding:0 20px}
.hero{background:linear-gradient(120deg,#164a97,#1d5fbf);color:#fff;padding:38px 20px 44px}
.hero .in{max-width:1080px;margin:0 auto}
.hero h1{margin:0 0 6px;font-size:30px}.hero p{margin:0 0 20px;opacity:.9;max-width:680px}
.searchbox{display:flex;gap:0;max-width:640px;box-shadow:0 4px 18px rgba(0,0,0,.14);border-radius:10px;overflow:hidden}
.searchbox input{flex:1;border:0;padding:14px 16px;font-size:16px;outline:0}
.searchbox button{border:0;background:#0e336e;color:#fff;padding:0 22px;font-size:16px;cursor:pointer;font-weight:600}
.searchbox button:hover{background:#0a2a5c}
.hint{margin-top:10px;font-size:13px;opacity:.85}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin:26px 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.stat .n{font-size:26px;font-weight:700;color:var(--brandd)}
.stat .l{font-size:13px;color:var(--mut);margin-top:2px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:16px 0}
.card h2{margin:0 0 12px;font-size:18px}
.chip{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;background:#eef2f8;color:#3a4a63;margin:0 4px 4px 0}
.chip.db{background:#e8f0fb;color:#164a97}
.chip.bad{background:var(--badbg);color:var(--bad)}
.chip.ok{background:var(--okbg);color:var(--ok)}
.chip.warn{background:var(--warnbg);color:var(--warn)}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.03em}
tr:hover td{background:#fafbfd}
.mono{font-family:var(--mono);font-size:13px;word-break:break-all}
.seq{font-family:var(--mono);font-size:13px;color:#2c3e50;background:#f3f5f9;padding:2px 6px;border-radius:5px;word-break:break-all}
.muted{color:var(--mut)}.small{font-size:13px}
.evi{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.evi .box{border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.evi .box.claim{border-color:#f0c9c4;background:#fdf4f3}
.evi .box.src{border-color:#bfe3cd;background:#f2faf5}
.evi .lab{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.03em}
.evi .v{font-size:20px;font-weight:700;margin-top:2px}
.pager{display:flex;gap:8px;align-items:center;margin:16px 0}
.pager a,.pager span{padding:6px 12px;border:1px solid var(--line);border-radius:8px;background:#fff}
.pager .cur{background:var(--brand);color:#fff;border-color:var(--brand)}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.filters a{padding:5px 11px;border:1px solid var(--line);border-radius:999px;background:#fff;font-size:13px}
.filters a.on{background:var(--brand);color:#fff;border-color:var(--brand)}
footer{max-width:1080px;margin:30px auto;padding:20px;color:var(--mut);font-size:13px;border-top:1px solid var(--line)}
.kv{display:grid;grid-template-columns:180px 1fr;gap:6px 14px;font-size:14px}
.kv .k{color:var(--mut)}
.notice{background:#fff8e6;border:1px solid #f0e0b0;border-radius:10px;padding:12px 14px;font-size:14px;color:#6b5615}
.pdfbtn{display:inline-block;padding:6px 13px;background:#c0392b;color:#fff;border-radius:8px;font-size:14px;font-weight:600}
.pdfbtn:hover{background:#a5301f;text-decoration:none}
.fig{padding:8px 0;border-bottom:1px solid var(--line);font-size:14px}.fig b{color:var(--brandd);margin-right:6px}
.flow{display:flex;align-items:stretch;gap:0;flex-wrap:wrap;margin:6px 0}
.flow .step{flex:1;min-width:120px;background:#f3f6fb;border:1px solid #d5e0f0;border-radius:10px;padding:10px 12px;text-align:center;font-size:13px;position:relative}
.flow .step b{display:block;color:var(--brandd);font-size:13px;margin-bottom:2px}
.flow .step small{color:var(--mut);font-size:11.5px}
.flow .arr{display:flex;align-items:center;color:#9fb2cc;font-size:20px;padding:0 4px}
.flow .step.audit{background:#fdf4f3;border-color:#f0c9c4}.flow .step.human{background:#e9f7ef;border-color:#bfe3cd}
.bars{margin:6px 0}
.bar{display:flex;align-items:center;gap:10px;margin:4px 0;font-size:13px}
.bar .lbl{width:190px;text-align:right;color:var(--mut);flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar .track{flex:1;background:#eef2f8;border-radius:5px;height:20px;position:relative}
.bar .fillb{height:100%;background:linear-gradient(90deg,#1d5fbf,#3b82e0);border-radius:5px}
.bar .fillb.bad{background:linear-gradient(90deg,#c0392b,#e05a48)}
.bar .num{width:120px;font-size:12px;color:var(--ink)}
@media(max-width:640px){.evi{grid-template-columns:1fr}.kv{grid-template-columns:1fr}}
"""


def layout(title, body, q=""):
    st = stats()
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{e(title)} · AMP Evidence Atlas</title><style>{CSS}</style></head><body>
<header class=top><div class=navwrap>
 <a class=brand href="/">AMP Evidence Atlas<small>Antimicrobial peptide activity, evidence-linked & source-verified</small></a>
 <span style="flex:1"></span>
 <nav class=top>
   <a href="/">Home</a><a href="/browse?kind=conflicts">Conflicts</a>
   <a href="/browse?kind=papers">Papers</a><a href="/stats">Statistics</a><a href="/downloads">Downloads</a><a href="/about">About &amp; Methods</a>
 </nav></div></header>
{body}
<footer>
 <b>AMP Evidence Atlas</b> — release {e(release_id())} ·
 {fmt_num(st['activity'])} activity observations · {fmt_num(st['audit'])} database audit records ·
 {fmt_num(st['conflicts_audit'])} source conflicts across {fmt_num(st['papers'])} primary papers.<br>
 Records retain primary-source locators and explicit evidence status; stratified human validation is reported separately. See <a href="/about">About &amp; citation</a>.
</footer></body></html>"""


def searchbar(val=""):
    return f"""<form class=searchbox action="/search" method=get>
 <input name=q value="{e(val)}" placeholder="Search peptide name, sequence, or DOI…" autofocus>
 <button type=submit>Search</button></form>"""


# ---------------------------------------------------------------- pages
def page_home():
    st = stats()
    cells = [("papers", "primary papers"), ("activity", "activity observations"),
             ("peptides", "distinct peptides"), ("sequences", "unique sequences"),
             ("audit", "database audit records"), ("conflicts_audit", "source conflicts")]
    grid = "".join(f'<div class=stat><div class=n>{fmt_num(st[k])}</div><div class=l>{lbl}</div></div>'
                   for k, lbl in cells)
    # a few example conflicts to showcase the scientific value
    ex = db().execute("""SELECT audit_record_id,database,record_name,database_measure,database_value,
                         primary_source_value,doi FROM audit WHERE status='source_conflict'
                         AND primary_source_value<>'' AND database_value<>'' LIMIT 6""").fetchall()
    rows = "".join(f"""<tr><td><a href="/audit?id={e(urllib.parse.quote(r['audit_record_id']))}">{e(r['record_name'] or r['database'])}</a></td>
        <td><span class="chip db">{e(r['database'])}</span></td><td class=small>{e(r['database_measure'])}</td>
        <td class=mono>{e(r['database_value'])}</td><td class=mono>{e(r['primary_source_value'])}</td></tr>""" for r in ex)
    body = f"""<section class=hero><div class=in>
 <h1>Every AMP activity value, traced to its primary source.</h1>
 <p>A curated atlas that re-reads the original papers behind {fmt_num(st['activity'])} antimicrobial-peptide
 measurements — normalizing endpoints, linking source locators, and flagging where public databases disagree with the primary literature.</p>
 {searchbar()}
 <div class=hint>Try <a style="color:#fff;text-decoration:underline" href="/search?q=LL-37">LL-37</a>,
   a sequence like <a style="color:#fff;text-decoration:underline" href="/search?q=GIGAVLKVLTTGLPALISWIKRKRQQ">GIGAVLKVLTTGLPALISWIKRKRQQ</a>,
   or a <a style="color:#fff;text-decoration:underline" href="/search?q=10.1021">DOI</a>.</div>
</div></section>
<div class=wrap>
 <div class=grid>{grid}</div>
 <div class=card><h2>Where databases disagree with the source</h2>
  <p class=muted small>{fmt_num(st['conflicts_audit'])} records where a public database's claim could not be reconciled with the primary
   article. Each is human-inspectable against the original table/figure.</p>
  <table><thead><tr><th>Record</th><th>Database</th><th>Endpoint</th><th>DB value</th><th>Primary source</th></tr></thead>
  <tbody>{rows}</tbody></table>
  <p style="margin-top:12px"><a href="/browse?kind=conflicts">Browse all conflicts →</a></p>
 </div>
</div>"""
    return layout("Home", body)


def _fts_query(q):
    terms = re.findall(r"[A-Za-z0-9\-\.]+", q)
    if not terms:
        return None
    return " ".join(f'"{t}"' for t in terms)


def page_search(qs):
    q = (qs.get("q", [""])[0] or "").strip()
    if not q:
        return layout("Search", f'<div class=wrap>{searchbar()}</div>')
    body = [f'<div class=wrap>{searchbar(q)}']
    seq = q.upper().strip()
    results = []
    # exact/prefix sequence hit
    if re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWYXBZUO]{4,}", seq):
        for r in db().execute("SELECT DISTINCT peptide,sequence,paper_id,doi FROM activity WHERE upper(sequence)=? LIMIT 25", (seq,)):
            results.append(("sequence", r["peptide"], r["sequence"], r["paper_id"], r["doi"]))
    fq = _fts_query(q)
    if fq:
        try:
            for r in db().execute("""SELECT kind,name,sequence,paper_id,doi FROM search
                                     WHERE search MATCH ? LIMIT 200""", (fq,)):
                results.append((r["kind"], r["name"], r["sequence"], r["paper_id"], r["doi"]))
        except sqlite3.OperationalError:
            pass
    # dedup by (name,paper)
    seen, uniq = set(), []
    for kind, name, sequence, pid, doi in results:
        key = (name.lower() if name else "", pid)
        if key in seen:
            continue
        seen.add(key); uniq.append((kind, name, sequence, pid, doi))
    if not uniq:
        body.append(f'<div class=card>No matches for <b>{e(q)}</b>. Try a peptide name, an exact sequence, or a DOI fragment.</div>')
    else:
        rows = ""
        for kind, name, sequence, pid, doi in uniq[:120]:
            link = f"/peptide?name={urllib.parse.quote(name)}" if name else f"/paper?id={urllib.parse.quote(pid)}"
            rows += f"""<tr><td><a href="{link}">{e(name) or '<span class=muted>(unnamed)</span>'}</a></td>
              <td>{'<span class=seq>'+e(sequence)+'</span>' if sequence else '<span class=muted>—</span>'}</td>
              <td><a href="/paper?id={e(urllib.parse.quote(pid))}" class=small>{e(pid)}</a></td></tr>"""
        body.append(f'<div class=card><h2>{len(uniq)} result(s) for “{e(q)}”</h2>'
                    f'<table><thead><tr><th>Peptide</th><th>Sequence</th><th>Paper</th></tr></thead><tbody>{rows}</tbody></table></div>')
    body.append("</div>")
    return layout(f"Search: {q}", "".join(body))


def page_peptide(qs):
    name = (qs.get("name", [""])[0] or "").strip()
    if not name:
        return layout("Peptide", "<div class=wrap><div class=card>No peptide specified.</div></div>")
    acts = db().execute("""SELECT * FROM activity WHERE lower(peptide)=lower(?) ORDER BY endpoint LIMIT 500""", (name,)).fetchall()
    auds = db().execute("""SELECT * FROM audit WHERE lower(record_name)=lower(?) LIMIT 200""", (name,)).fetchall()
    seqs = sorted({a["sequence"] for a in acts if a["sequence"]})
    seqhtml = " ".join(f'<span class=seq>{e(s)}</span>' for s in seqs) or '<span class=muted>—</span>'
    feats = []
    for sq in seqs:
        fr = db().execute("SELECT * FROM features WHERE sequence=?", (sq,)).fetchone()
        if fr:
            feats.append(fr)
    featcard = ""
    if feats:
        def fcols(f):
            return (f"""<tr><td class=seq>{e(f['sequence'])}</td><td>{f['length']}</td><td>{f['mw']:.0f}</td>
                <td><b style="color:{'#1d5fbf' if f['net_charge']>=0 else '#c0392b'}">{f['net_charge']:+.1f}</b>{' ⚡' if f['cationic'] else ''}</td>
                <td>{f['pI']:.1f}</td><td>{f['gravy']:+.2f}</td><td>{f['hydrophobic_frac']*100:.0f}%</td>
                <td>{f['mu_h_per_res']:.2f}</td></tr>""")
        featcard = f"""<div class=card><h2>Physicochemical properties <span class="chip">computed</span></h2>
         <p class=small muted>Derived from the linear sequence (net charge &amp; pI at pH 7.4; GRAVY = Kyte-Doolittle hydropathy; μH = Eisenberg hydrophobic moment per residue, α-helix). ⚡ = cationic (net ≥ +2).</p>
         <table><thead><tr><th>Sequence</th><th>Len</th><th>MW</th><th>Net charge</th><th>pI</th><th>GRAVY</th><th>Hydrophobic</th><th>μH/res</th></tr></thead>
         <tbody>{''.join(fcols(f) for f in feats)}</tbody></table></div>"""
    actrows = "".join(f"""<tr><td>{e(a['endpoint'])}</td><td class=mono>{e(a['raw_value'])} {e(a['raw_unit'])}</td>
        <td>{e(a['target'])}</td><td class=small>{e(a['assay_conditions'])[:80]}</td>
        <td><a class=small href="/paper?id={e(urllib.parse.quote(a['paper_id']))}">{e(a['doi'] or a['paper_id'])}</a></td></tr>""" for a in acts[:200])
    audrows = "".join(f"""<tr><td><span class="chip db">{e(a['database'])}</span></td><td>{e(a['database_measure'])}</td>
        <td class=mono>{e(a['database_value'])}</td>{status_chip_cell(a['status'])}
        <td><a class=small href="/audit?id={e(urllib.parse.quote(a['audit_record_id']))}">view</a></td></tr>""" for a in auds)
    body = f"""<div class=wrap>{searchbar()}
     <div class=card><h2>{e(name)}</h2>
       <div class=kv><div class=k>Sequence(s)</div><div>{seqhtml}</div>
       <div class=k>Activity observations</div><div>{len(acts)}</div>
       <div class=k>Database audit records</div><div>{len(auds)}</div></div></div>
     {featcard}
     <div class=card><h2>Activity observations ({len(acts)})</h2>
       <table><thead><tr><th>Endpoint</th><th>Value</th><th>Target</th><th>Conditions</th><th>Source</th></tr></thead>
       <tbody>{actrows or '<tr><td colspan=5 class=muted>none</td></tr>'}</tbody></table></div>
     <div class=card><h2>Database records &amp; audits ({len(auds)})</h2>
       <table><thead><tr><th>DB</th><th>Endpoint</th><th>DB value</th><th>Status</th><th></th></tr></thead>
       <tbody>{audrows or '<tr><td colspan=5 class=muted>none</td></tr>'}</tbody></table></div>
    </div>"""
    return layout(name, body)


def status_chip(s):
    s = s or ""
    cls = "ok" if s == "source_verified" else "bad" if s == "source_conflict" else "warn"
    return f'<span class="chip {cls}">{e(s or "—")}</span>'


def _row_get(a, key, default=""):
    try:
        return a[key]
    except (KeyError, IndexError):
        return default


def human_badge(a):
    """Badge marking a human-reviewed verdict on an audit row (dict or sqlite Row)."""
    try:
        v = a["human_verdict"]
    except (KeyError, IndexError):
        v = ""
    if v == "confirmed":
        return ' <span class="chip bad" title="Verified by a human reviewer">✔ human-confirmed error</span>'
    if v == "not_an_error":
        return ' <span class="chip ok" title="Human reviewer: not an error">human-checked: not an error</span>'
    return ""


def status_chip_cell(s):
    return f"<td>{status_chip(s)}</td>"


def page_audit(qs):
    aid = (qs.get("id", [""])[0] or "").strip()
    a = db().execute("SELECT * FROM audit WHERE audit_record_id=?", (aid,)).fetchone()
    if not a:
        return layout("Audit record", "<div class=wrap><div class=card>Record not found.</div></div>")
    diffs = " ".join(f'<span class="chip">{e(x)}</span>' for x in (a["difference_categories"] or "").split(";") if x)
    body = f"""<div class=wrap>{searchbar()}
     <div class=card>
      <h2>{e(a['record_name'] or 'Database record')} &nbsp; {status_chip(a['status'])}{human_badge(a)}</h2>
      <div class=kv>
        <div class=k>Database</div><div><span class="chip db">{e(a['database'])}</span></div>
        <div class=k>Paper</div><div><a href="/paper?id={e(urllib.parse.quote(a['paper_id']))}">{e(a['paper_id'])}</a>
           {f'· <a href="https://doi.org/{e(a["doi"])}" target=_blank>doi.org/{e(a["doi"])}</a>' if a['doi'] else ''}</div>
        <div class=k>Endpoint / subject</div><div>{e(a['database_measure'])} · {e(a['database_subject'])}</div>
        {f'<div class=k>Sequence</div><div><span class=seq>{e(a["sequence"])}</span></div>' if a['sequence'] else ''}
        <div class=k>Difference categories</div><div>{diffs or '<span class=muted>—</span>'}</div>
      </div>
      <div class=evi style="margin-top:16px">
        <div class="box claim"><div class=lab>Database claims</div>
          <div class=v>{e(a['database_value']) or '—'} <span class=small>{e(a['database_unit'])}</span></div>
          <div class=small muted>{e(a['database_subject'])}</div></div>
        <div class="box src"><div class=lab>Primary source</div>
          <div class=v>{e(a['primary_source_value']) or '—'} <span class=small>{e(a['primary_source_unit'])}</span></div>
          <div class=small muted>{e(a['primary_source_subject'])}</div></div>
      </div>
      {f'<div class=notice style="margin-top:14px"><b>Curator note.</b> {e(a["review_notes"])}</div>' if a['review_notes'] else ''}
      {f'<div class="notice" style="margin-top:10px;background:#eaf6ef;border-color:#bfe3cd;color:#1e5c37"><b>Human reviewer.</b> {e(a["human_review_notes"])}</div>' if _row_get(a,"human_review_notes") else ''}
      {f'<p class=small style="margin-top:12px"><b>Where in the paper:</b> {e(parse_locator(a["source_locator"]))}</p>' if a['source_locator'] else ''}
      {f'<p style="margin-top:6px"><a class=pdfbtn href="/pdf?paper={e(urllib.parse.quote(a["paper_id"]))}" target=_blank>📄 Open original PDF</a></p>' if has_pdf(a['paper_id']) else ''}
      {f'<p class=small muted><b>Conflict context:</b> {e(a["conflict_context"])}</p>' if a['conflict_context'] else ''}
     </div></div>"""
    return layout("Audit · " + (a["record_name"] or aid), body)


def page_paper(qs):
    pid = (qs.get("id", [""])[0] or "").strip()
    p = db().execute("SELECT * FROM papers WHERE paper_id=?", (pid,)).fetchone()
    if not p:
        return layout("Paper", "<div class=wrap><div class=card>Paper not found.</div></div>")
    acts = db().execute("SELECT * FROM activity WHERE paper_id=? LIMIT 400", (pid,)).fetchall()
    auds = db().execute("SELECT * FROM audit WHERE paper_id=? LIMIT 400", (pid,)).fetchall()
    mechs = db().execute("SELECT * FROM mechanism WHERE paper_id=? LIMIT 100", (pid,)).fetchall()
    figs = db().execute("SELECT label,figure_index,caption FROM figures WHERE paper_id=? ORDER BY CAST(figure_index AS INT)", (pid,)).fetchall()
    nconf = sum(1 for a in auds if a["status"] == "source_conflict")
    pdf = has_pdf(pid)
    pdfbtn = f'<a class=pdfbtn href="/pdf?paper={e(urllib.parse.quote(pid))}" target=_blank>📄 Open original PDF</a>' if pdf else ''
    actrows = "".join(f"""<tr><td>{e(a['peptide'])}</td><td>{e(a['endpoint'])}</td>
        <td class=mono>{e(a['raw_value'])} {e(a['raw_unit'])}</td><td>{e(a['target'])}</td>
        <td class="small muted">{e(parse_locator(a['source_locator']))}</td></tr>""" for a in acts[:150])
    audrows = "".join(f"""<tr><td><span class="chip db">{e(a['database'])}</span></td><td>{e(a['record_name'])}</td>
        <td>{e(a['database_measure'])}</td><td class=mono>{e(a['database_value'])}</td>{status_chip_cell(a['status'])}
        <td><a class=small href="/audit?id={e(urllib.parse.quote(a['audit_record_id']))}">view</a></td></tr>""" for a in auds[:150])
    mechhtml = "".join(f'<li>{e(m["claim_text"])} <span class=small muted>[{e(m["evidence_class"])}]</span></li>' for m in mechs)
    fightml = "".join(f'<div class=fig><b>{e(f["label"])}</b> {e(f["caption"])}</div>' for f in figs)
    body = f"""<div class=wrap>{searchbar()}
     <div class=card><h2>{e(pid)}</h2>
       <div class=kv>
        {f'<div class=k>DOI</div><div><a href="https://doi.org/{e(p["doi"])}" target=_blank>doi.org/{e(p["doi"])}</a></div>' if p['doi'] else ''}
        <div class=k>Original paper</div><div>{pdfbtn or '<span class=muted>PDF not hosted</span>'}{f' &nbsp; <a href="https://doi.org/{e(p["doi"])}" target=_blank>publisher →</a>' if p['doi'] else ''}</div>
        <div class=k>Review status</div><div>{e(p['review_status'])} · grade {e(p['publication_grade'])}</div>
        <div class=k>Records</div><div>{len(acts)} activity · {len(auds)} database audit ({nconf} conflicts) · {len(mechs)} mechanism · {len(figs)} figures/tables</div>
       </div></div>
     <div class=card><h2>Activity observations ({len(acts)})</h2>
       <table><thead><tr><th>Peptide</th><th>Endpoint</th><th>Value</th><th>Target</th><th>Source location</th></tr></thead>
       <tbody>{actrows or '<tr><td colspan=5 class=muted>none</td></tr>'}</tbody></table></div>
     <div class=card><h2>Database audits ({len(auds)}{f' · {nconf} conflicts' if nconf else ''})</h2>
       <table><thead><tr><th>DB</th><th>Record</th><th>Endpoint</th><th>DB value</th><th>Status</th><th></th></tr></thead>
       <tbody>{audrows or '<tr><td colspan=6 class=muted>none</td></tr>'}</tbody></table></div>
     {f'<div class=card><h2>Figures &amp; tables ({len(figs)})</h2>{fightml}</div>' if figs else ''}
     {f'<div class=card><h2>Mechanism claims ({len(mechs)})</h2><ul>{mechhtml}</ul></div>' if mechs else ''}
    </div>"""
    return layout(pid, body)


def page_browse(qs):
    kind = qs.get("kind", ["conflicts"])[0]
    page = max(1, int((qs.get("page", ["1"])[0] or "1")))
    off = (page - 1) * PAGE_SIZE
    if kind == "papers":
        total = db().execute("SELECT COUNT(*) FROM papers").fetchone()[0]
        rows = db().execute("""SELECT paper_id,doi,review_status,n_activity,n_audit,caution_count FROM papers
                               ORDER BY CAST(n_audit AS INT) DESC LIMIT ? OFFSET ?""", (PAGE_SIZE, off)).fetchall()
        tr = "".join(f"""<tr><td><a href="/paper?id={e(urllib.parse.quote(r['paper_id']))}">{e(r['paper_id'])}</a></td>
            <td class=small>{e(r['review_status'])}</td><td>{e(r['n_activity'])}</td><td>{e(r['n_audit'])}</td>
            <td>{e(r['caution_count'])}</td></tr>""" for r in rows)
        table = f"""<table><thead><tr><th>Paper</th><th>Review status</th><th>Activity</th><th>Audits</th><th>Cautions</th></tr></thead>
                    <tbody>{tr}</tbody></table>"""
        title, head = "Papers", f"{fmt_num(total)} primary papers"
        base = "/browse?kind=papers"
    else:  # conflicts
        dbf = qs.get("db", [""])[0]
        human = qs.get("human", [""])[0] == "1"
        # human-confirmed errors may be source_verified (auto false-negatives), so this filter spans all statuses
        where = "human_verdict='confirmed'" if human else "status='source_conflict'"
        params = []
        if dbf:
            where += " AND database=?"; params.append(dbf)
        total = db().execute(f"SELECT COUNT(*) FROM audit WHERE {where}", params).fetchone()[0]
        order = "ORDER BY CASE WHEN human_verdict='confirmed' THEN 0 ELSE 1 END, audit_record_id"
        rows = db().execute(f"""SELECT audit_record_id,database,record_name,database_measure,database_value,
                               primary_source_value,paper_id,difference_categories,human_verdict FROM audit WHERE {where}
                               {order} LIMIT ? OFFSET ?""", params + [PAGE_SIZE, off]).fetchall()
        hconf = db().execute("SELECT COUNT(*) FROM audit WHERE human_verdict='confirmed'").fetchone()[0]
        facets = db().execute("SELECT database,COUNT(*) c FROM audit WHERE status='source_conflict' GROUP BY database ORDER BY c DESC").fetchall()
        fhtml = (f'<a href="/browse?kind=conflicts" class="{"on" if not dbf and not human else ""}">All</a>'
                 + f'<a href="/browse?kind=conflicts&human=1" class="{"on" if human else ""}" style="border-color:#c0392b;color:{"#fff" if human else "#c0392b"};background:{"#c0392b" if human else "#fff"}">✔ human-confirmed ({fmt_num(hconf)})</a>'
                 + "".join(f'<a href="/browse?kind=conflicts&db={e(urllib.parse.quote(f["database"]))}" class="{"on" if dbf==f["database"] and not human else ""}">{e(f["database"])} ({fmt_num(f["c"])})</a>' for f in facets))
        tr = "".join(f"""<tr><td><a href="/audit?id={e(urllib.parse.quote(r['audit_record_id']))}">{e(r['record_name'] or '(unnamed)')}</a>{' <span class="chip bad" style="font-size:11px">✔ human</span>' if r['human_verdict']=='confirmed' else ''}</td>
            <td><span class="chip db">{e(r['database'])}</span></td><td class=small>{e(r['database_measure'])}</td>
            <td class=mono>{e(r['database_value'])}</td><td class=mono>{e(r['primary_source_value']) or '<span class=muted>—</span>'}</td>
            <td><a class=small href="/paper?id={e(urllib.parse.quote(r['paper_id']))}">{e(r['paper_id'])}</a></td></tr>""" for r in rows)
        table = f'<div class=filters>{fhtml}</div><table><thead><tr><th>Record</th><th>DB</th><th>Endpoint</th><th>DB value</th><th>Primary source</th><th>Paper</th></tr></thead><tbody>{tr}</tbody></table>'
        title = "Conflicts"
        head = (f"{fmt_num(total)} human-confirmed errors" if human else f"{fmt_num(total)} source conflicts") + (f" · {e(dbf)}" if dbf else "")
        base = f"/browse?kind=conflicts{'&human=1' if human else ''}{('&db='+urllib.parse.quote(dbf)) if dbf else ''}"
    npages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    pager = pagination(base, page, npages)
    body = f"""<div class=wrap>{searchbar()}
      <div class=card><h2>{head}</h2>{table}{pager}</div></div>"""
    return layout(title, body)


def pagination(base, page, npages):
    if npages <= 1:
        return ""
    sep = "&" if "?" in base else "?"
    out = ['<div class=pager>']
    if page > 1:
        out.append(f'<a href="{base}{sep}page={page-1}">‹ Prev</a>')
    out.append(f'<span class=cur>Page {page} / {fmt_num(npages)}</span>')
    if page < npages:
        out.append(f'<a href="{base}{sep}page={page+1}">Next ›</a>')
    out.append('</div>')
    return "".join(out)


EXPORT_TABLES = {
    "papers": ("papers.tsv", "Primary papers with review status"),
    "activity": ("activity_observations.tsv", "Normalized activity/toxicity observations"),
    "audit": ("database_record_audits.tsv", "Database records audited against primary source"),
    "conflicts": ("conflicts_and_cautions.tsv", "Conflicts & curator cautions"),
    "mechanism": ("mechanism_claims.tsv", "Mechanism-of-action claims"),
}


def page_downloads():
    st = stats()
    counts = {"papers": st["papers"], "activity": st["activity"], "audit": st["audit"],
              "conflicts": db().execute("SELECT COUNT(*) FROM conflicts").fetchone()[0], "mechanism": st["mechanism"]}
    rows = "".join(f"""<tr><td><a href="/export/{e(t)}.tsv">{e(fn)}</a></td><td>{e(d)}</td><td>{fmt_num(counts[t])}</td></tr>"""
                   for t, (fn, d) in EXPORT_TABLES.items())
    body = f"""<div class=wrap><div class=card><h2>Downloads</h2>
     <p class=muted>Release <b>{e(release_id())}</b> — frozen public-v1 subset. Tab-separated, UTF-8; streamed live from the database, so downloads match exactly what this portal shows.</p>
     <table><thead><tr><th>File</th><th>Description</th><th>Rows</th></tr></thead><tbody>{rows}</tbody></table>
     <p class=small muted style="margin-top:12px">Programmatic access: this dataset is also served to AI agents over <b>MCP</b> — see <a href="/about">About</a>.
       The full release package (JSON schemas + SHA-256 checksums) is archived separately.</p>
     </div></div>"""
    return layout("Downloads", body)


def flow_diagram():
    steps = [
        ("Primary paper", "PDF / XML full text", ""),
        ("Extract", "activity, sequences, tables, figures", ""),
        ("Normalize", "endpoints, units, targets", ""),
        ("Audit vs database", "DBAASP · CAMP · DRAMP · dbAMP · APD", "audit"),
        ("Flag conflicts", "database ≠ primary source", "audit"),
        ("Human validation", "stratified review in progress", "human"),
    ]
    html = ['<div class=flow>']
    for i, (t, s, cls) in enumerate(steps):
        html.append(f'<div class="step {cls}"><b>{e(t)}</b><small>{e(s)}</small></div>')
        if i < len(steps) - 1:
            html.append('<div class=arr>→</div>')
    html.append('</div>')
    return "".join(html)


def _bars(rows, bad_key=None, w_of=None):
    if not rows:
        return "<p class=muted>no data</p>"
    mx = max((r[1] for r in rows), default=1) or 1
    out = ['<div class=bars>']
    for r in rows:
        lbl, val = r[0], r[1]
        extra = r[2] if len(r) > 2 else ""
        cls = "bad" if bad_key and bad_key(r) else ""
        pct = 100 * val / mx
        out.append(f'<div class=bar><div class=lbl>{e(lbl)}</div>'
                   f'<div class=track><div class="fillb {cls}" style="width:{pct:.1f}%"></div></div>'
                   f'<div class=num>{fmt_num(val)}{e(extra)}</div></div>')
    out.append('</div>')
    return "".join(out)


def page_stats():
    st = stats()
    eps = db().execute("SELECT endpoint,COUNT(*) c FROM activity WHERE endpoint<>'' GROUP BY endpoint ORDER BY c DESC LIMIT 10").fetchall()
    ep_rows = [(r["endpoint"], r["c"]) for r in eps]
    # per-database conflict rate
    dbc = db().execute("""SELECT database, SUM(CASE WHEN status='source_conflict' THEN 1 ELSE 0 END) conf, COUNT(*) tot
                          FROM audit WHERE database<>'' GROUP BY database ORDER BY tot DESC""").fetchall()
    conf_rows = [(f"{r['database']}", r["conf"], f"  ({100*r['conf']/r['tot']:.0f}% of {fmt_num(r['tot'])})") for r in dbc]
    # audit status
    stt = db().execute("SELECT status,COUNT(*) c FROM audit WHERE status<>'' GROUP BY status ORDER BY c DESC").fetchall()
    st_rows = [(r["status"], r["c"]) for r in stt]
    # feature: net-charge distribution (buckets)
    buckets = [("≤ -2 (anionic)", "net_charge <= -2"), ("-2 … 0", "net_charge > -2 AND net_charge < 0"),
               ("0 … +2", "net_charge >= 0 AND net_charge < 2"), ("+2 … +5", "net_charge >= 2 AND net_charge < 5"),
               ("+5 … +9", "net_charge >= 5 AND net_charge < 9"), ("≥ +9", "net_charge >= 9")]
    chg_rows = [(lbl, db().execute(f"SELECT COUNT(*) FROM features WHERE {cond}").fetchone()[0]) for lbl, cond in buckets]
    # length distribution
    lens = [("≤10", "length<=10"), ("11–20", "length BETWEEN 11 AND 20"), ("21–30", "length BETWEEN 21 AND 30"),
            ("31–50", "length BETWEEN 31 AND 50"), (">50", "length>50")]
    len_rows = [(lbl, db().execute(f"SELECT COUNT(*) FROM features WHERE {cond}").fetchone()[0]) for lbl, cond in lens]
    body = f"""<div class=wrap>
     <div class=card><h2>The pipeline</h2>{flow_diagram()}
       <p class=small muted style="margin-top:10px">Every value in the atlas is extracted from the primary paper, normalized, and checked against the public database that claims it. Disagreements are flagged and a subset human-reviewed.</p></div>
     <div class=grid>
       <div class=stat><div class=n>{fmt_num(st['papers'])}</div><div class=l>primary papers</div></div>
       <div class=stat><div class=n>{fmt_num(st['activity'])}</div><div class=l>activity observations</div></div>
       <div class=stat><div class=n>{fmt_num(st['audit'])}</div><div class=l>database audits</div></div>
       <div class=stat><div class=n>{fmt_num(st['conflicts_audit'])}</div><div class=l>source conflicts</div></div>
       <div class=stat><div class=n>{fmt_num(st.get('human_confirmed', 0))}</div><div class=l>human-confirmed errors</div></div>
       <div class=stat><div class=n>{fmt_num(st.get('recovered_activity', 0))}</div><div class=l>dual-model recovered</div></div>
       <div class=stat><div class=n>{fmt_num(st.get('featured_sequences', 0))}</div><div class=l>sequences profiled</div></div>
     </div>
     <div class=card><h2>Evidence tiers</h2><p class=small muted>Every activity record carries an <b>evidence_tier</b> so humans and AI agents can filter by trust level:</p>
       <div class=bars>
       <div class=bar><div class=lbl>atlas_core (source-reviewed; human validation incomplete)</div><div class=track><div class=fillb style="width:100%"></div></div><div class=num>{fmt_num(st.get('activity',0))}</div></div>
       <div class=bar><div class=lbl>dual_model_recovered (excluded from canonical v1.0)</div><div class=track><div class="fillb bad" style="width:{min(100,100*st.get('recovered_activity',0)/max(1,st.get('activity',1))*20):.0f}%"></div></div><div class=num>{fmt_num(st.get('recovered_activity',0))}</div></div>
       <div class=bar><div class=lbl>machine_extracted (excluded from canonical v1.0)</div><div class=track><div class="fillb bad" style="width:{min(100,100*st.get('machine_activity',0)/max(1,st.get('activity',1))*20):.0f}%"></div></div><div class=num>{fmt_num(st.get('machine_activity',0))}</div></div>
       </div></div>
     <div class=card><h2>Activity observations by endpoint</h2>{_bars(ep_rows)}</div>
     <div class=card><h2>Conflicts by database <span class=small muted>(count · % of that database's audited records)</span></h2>{_bars(conf_rows, bad_key=lambda r: True)}</div>
     <div class=card><h2>Audit outcome distribution</h2>{_bars(st_rows, bad_key=lambda r: r[0]=='source_conflict')}</div>
     <div class=row style="gap:16px">
       <div class=card style="flex:1;min-width:300px"><h2>Peptide net charge (computed)</h2>{_bars(chg_rows)}</div>
       <div class=card style="flex:1;min-width:300px"><h2>Peptide length (computed)</h2>{_bars(len_rows)}</div>
     </div>
    </div>"""
    return layout("Statistics", body)


def page_about():
    st = stats()
    body = f"""<div class=wrap>
     <div class=card><h2>What the AMP Evidence Atlas is</h2>
      <p>Public antimicrobial-peptide (AMP) databases are widely used but rarely traced back to the primary literature. The
       Atlas re-reads the original papers behind their activity records and, for every claim, (1) locates the exact source
       table/figure, (2) normalizes the endpoint and unit, and (3) reports whether the database value is
       <b>source-verified</b> or in <b>conflict</b> with the article. It is designed to be consumed by humans <i>and</i> by
       AI agents (via MCP).</p>
      {flow_diagram()}
     </div>
     <div class=card><h2>Scope &amp; coverage</h2>
      <div class=kv>
        <div class=k>Primary papers</div><div>{fmt_num(st['papers'])}</div>
        <div class=k>Activity observations</div><div>{fmt_num(st['activity'])}</div>
        <div class=k>Database audit records</div><div>{fmt_num(st['audit'])} across DBAASP, CAMP, DRAMP, dbAMP, APD</div>
        <div class=k>Source conflicts</div><div>{fmt_num(st['conflicts_audit'])} ({100*st['conflicts_audit']/st['audit']:.0f}% of audited records)</div>
        <div class=k>Sequences profiled</div><div>{fmt_num(st.get('featured_sequences',0))} linear sequences with computed physicochemistry</div>
      </div>
      <p class=small muted style="margin-top:8px">This public v1 subset contains records that passed publication-grade review. See <a href="/stats">Statistics</a> for distributions.</p>
     </div>
     <div class=card><h2>Methods</h2>
      <p><b>Evidence model.</b> Each activity value carries an <i>evidence ladder</i> (primary-text/table → figure-derived) and a
       machine-readable source locator (paper, table/figure label, row, column). Database audits keep the database claim and the
       primary-source value side by side, so any disagreement is transparent and checkable against the original.</p>
      <p><b>Conflict definition.</b> A record is <span class="chip bad">source_conflict</span> when the database's value/endpoint/subject
       cannot be reconciled with the primary article; <span class="chip ok">source_verified</span> when it matches. Difference
       categories (value/unit, endpoint label, target/organism, sequence/modification) are recorded per record.</p>
      <p><b>Human validation.</b> AI extraction, worker agreement, and automated gates are not treated as a human gold
       standard. A predeclared stratified validation set is being reviewed independently; publication-grade error
       estimates will be reported only after human adjudication is complete.</p>
      <p><b>Physicochemical properties</b> are computed from each linear standard-residue sequence: net charge &amp; isoelectric
       point (pH 7.4, EMBOSS pKa), GRAVY (Kyte-Doolittle), hydrophobic-residue fraction, and Eisenberg hydrophobic moment
       (α-helix). Branched/modified constructs are left unprofiled.</p>
     </div>
     <div class=card><h2>For AI agents — MCP</h2>
      <p>The atlas is served to LLM agents over the Model Context Protocol (Streamable HTTP), so an agent can ground its
       answers in source-verified evidence instead of parametric memory. Tools include <code>search</code>,
       <code>get_peptide</code>, <code>get_paper</code>, <code>get_audit_record</code>, <code>get_figures</code>,
       <code>list_conflicts</code>, <code>query_activity</code> and a read-only <code>sql_select</code>.</p>
      <div class=kv>
        <div class=k>Endpoint</div><div class=mono>POST {e(_self_origin())}/mcp</div>
        <div class=k>Anthropic API</div><div class=small>mcp_servers=[{{type:"url", url:".../mcp", name:"amp-atlas"}}] + tools=[{{type:"mcp_toolset", mcp_server_name:"amp-atlas"}}]</div>
        <div class=k>Local Claude Code</div><div class="mono small">claude mcp add amp-atlas -- python3 mcp_server.py --stdio</div>
      </div>
     </div>
     <div class=card><h2>Versioning, license &amp; citation</h2>
      <div class=kv>
        <div class=k>Release</div><div>{e(release_id())}</div>
        <div class=k>License</div><div>Research use; per-source database terms apply (see LICENSES in the release package)</div>
      </div>
      <div class=notice style="margin-top:10px">AMP Evidence Atlas ({e(release_id())}): a source-traceable, evidence-status-aware atlas of antimicrobial-peptide activity evidence. 2026.</div>
     </div>
    </div>"""
    return layout("About & Methods", body)


def _self_origin():
    return "https://atlas.154.3.37.88.nip.io"


# ---------------------------------------------------------------- HTTP
class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(u.query)
        p = u.path
        try:
            if p == "/":
                return self._send(200, page_home())
            if p == "/search":
                return self._send(200, page_search(qs))
            if p == "/peptide":
                return self._send(200, page_peptide(qs))
            if p == "/audit":
                return self._send(200, page_audit(qs))
            if p == "/paper":
                return self._send(200, page_paper(qs))
            if p == "/browse":
                return self._send(200, page_browse(qs))
            if p == "/downloads":
                return self._send(200, page_downloads())
            if p == "/about":
                return self._send(200, page_about())
            if p == "/stats":
                return self._send(200, page_stats())
            if p == "/api/stats":
                return self._send(200, json.dumps(stats()), "application/json")
            if p.startswith("/export/") and p.endswith(".tsv"):
                return self._export(p[len("/export/"):-len(".tsv")])
            if p == "/pdf":
                return self._pdf(qs.get("paper", [""])[0])
            if p == "/healthz":
                return self._send(200, "ok", "text/plain")
            return self._send(404, layout("Not found", "<div class=wrap><div class=card>Page not found. <a href=/>Home</a></div></div>"))
        except Exception as ex:
            return self._send(500, layout("Error", f"<div class=wrap><div class=card>Server error: {e(ex)}</div></div>"))

    do_HEAD = do_GET

    def _pdf(self, paper_id):
        paper_id = (paper_id or "").strip()
        # paper_id is strictly sanitized (no path separators / dots-only), so no traversal via input;
        # the target may be a curator-created symlink (trusted) — read it directly.
        if not re.fullmatch(r"[A-Za-z0-9_.\-]+", paper_id) or paper_id in (".", ".."):
            return self._send(400, "bad paper id", "text/plain")
        fp = PAPERS_DIR / paper_id / "source" / "paper.pdf"
        try:
            data = fp.read_bytes()
        except Exception:
            return self._send(404, "PDF not available", "text/plain")
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Disposition", f'inline; filename="{paper_id}.pdf"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _export(self, table):
        if table not in EXPORT_TABLES:
            return self._send(404, "unknown table", "text/plain")
        fname = EXPORT_TABLES[table][0]
        cur = db().execute(f"SELECT * FROM {table}")
        cols = [c[0] for c in cur.description]
        self.send_response(200)
        self.send_header("Content-Type", "text/tab-separated-values; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
        self.end_headers()  # chunked/unsized; stream row batches
        if self.command == "HEAD":
            return

        def clean(v):
            return str(v if v is not None else "").replace("\t", " ").replace("\r", " ").replace("\n", " ")
        buf = ["\t".join(cols)]
        n = 0
        while True:
            batch = cur.fetchmany(2000)
            if not batch:
                break
            for r in batch:
                buf.append("\t".join(clean(x) for x in r))
            n += len(batch)
            if len(buf) >= 4000:
                self.wfile.write(("\n".join(buf) + "\n").encode("utf-8")); buf = []
        if buf:
            self.wfile.write(("\n".join(buf) + "\n").encode("utf-8"))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    bind = os.environ.get("BIND_ADDR", "0.0.0.0")
    print(f"AMP Evidence Atlas portal:  http://{bind}:{port}   (db={DB_PATH})")
    ThreadingHTTPServer((bind, port), H).serve_forever()
