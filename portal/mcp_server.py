#!/usr/bin/env python3
"""AMP Evidence Atlas — MCP server (knowledge base for AI agents).

Exposes the Atlas SQLite DB as MCP tools over two transports from one codebase:
  • Streamable HTTP (default)  — POST /mcp, JSON-RPC 2.0. Point the Anthropic Messages API
      MCP connector at it: mcp_servers=[{type:"url", url:"https://<host>/mcp", name:"amp-atlas"}]
      + tools=[{type:"mcp_toolset", mcp_server_name:"amp-atlas"}], beta mcp-client-2025-11-20.
  • stdio (--stdio)            — for local Claude Code / Desktop:  claude mcp add amp-atlas -- python3 mcp_server.py --stdio

Read-only. Zero dependencies (stdlib only). Run:
  python3 mcp_server.py [PORT]          # HTTP, default 8090
  python3 mcp_server.py --stdio         # stdio
Env: BIND_ADDR (default 0.0.0.0), ATLAS_DB (default ./atlas.db), MCP_TOKEN (optional bearer gate for HTTP)
"""
import os, sys, json, re, sqlite3, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = os.environ.get("ATLAS_DB", str(BASE / "atlas.db"))
PORTAL_URL = os.environ.get("PORTAL_URL", "https://atlas.154.3.37.88.nip.io").rstrip("/")
PROTOCOL_VERSION = "2025-06-18"


def parse_locator(s):
    """source_locator (activity: JSON object; audit: JSON array) → readable string."""
    s = (s or "").strip()
    if not s:
        return ""
    try:
        d = json.loads(s)
    except Exception:
        return s[:200]

    def one(o):
        if not isinstance(o, dict):
            return str(o)
        lab = o.get("label") or o.get("kind") or ""
        bits = [lab.replace("_", " ")] if lab else []
        if o.get("row_label"):
            bits.append(f"row: {o['row_label']}")
        if o.get("column"):
            bits.append(f"col: {o['column']}")
        if o.get("locator"):
            bits.append(str(o["locator"]))
        return " · ".join(b for b in bits if b)
    return "  |  ".join(one(o) for o in d) if isinstance(d, list) else one(d)


def pdf_url(paper_id):
    return f"{PORTAL_URL}/pdf?paper={paper_id}"
SERVER_INFO = {"name": "amp-evidence-atlas", "version": "1.0.0"}
MCP_TOKEN = os.environ.get("MCP_TOKEN", "").strip()

_tl = threading.local()


def db():
    c = getattr(_tl, "c", None)
    if c is None:
        c = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, check_same_thread=False)
        c.row_factory = sqlite3.Row
        _tl.c = c
    return c


def _has_table(t):
    try:
        db().execute(f'SELECT 1 FROM {t} LIMIT 1'); return True
    except sqlite3.OperationalError:
        return False


def rows_to_dicts(cur, limit=None):
    out = [dict(r) for r in (cur.fetchmany(limit) if limit else cur.fetchall())]
    return out


def release_metadata():
    try:
        return {r["k"]: r["v"] for r in db().execute("SELECT k,v FROM metadata")}
    except sqlite3.OperationalError:
        return {"release_id": "unknown-release", "portal_scope": "unknown"}


# ------------------------------------------------------------------ tool implementations
def t_get_stats(_):
    s = {r["k"]: int(r["v"]) for r in db().execute("SELECT k,v FROM stats")}
    meta = release_metadata()
    return {
        "release": meta.get("release_id"),
        "release_version": meta.get("release_version"),
        "release_status": meta.get("release_status"),
        "portal_scope": meta.get("portal_scope"),
        "experimental_increments_included": meta.get("experimental_increments_included"),
        "papers": s.get("papers"), "activity_observations": s.get("activity"),
        "database_audit_records": s.get("audit"), "source_conflicts": s.get("conflicts_audit"),
        "human_confirmed_errors": s.get("human_confirmed"),
        "dual_model_recovered_activity": s.get("recovered_activity"),
        "machine_extracted_activity": s.get("machine_activity"),
        "mechanism_claims": s.get("mechanism"), "distinct_peptides": s.get("peptides"),
        "distinct_sequences": s.get("sequences"),
        "evidence_tiers": {
            "atlas_core": "source-reviewed canonical v1.0 records; stratified human validation is incomplete",
            "dual_model_recovered": "post-freeze experimental increment; excluded from canonical v1.0 by default",
            "machine_extracted": "post-freeze experimental increment; excluded from canonical v1.0 by default",
        },
        "description": "A source-traceable atlas of antimicrobial-peptide activity evidence; "
                       "records retain audit status and primary-source locators. AI agreement is not a human gold standard.",
    }


def _fts(q):
    terms = re.findall(r"[A-Za-z0-9\-\.]+", q or "")
    return " ".join(f'"{t}"' for t in terms) if terms else None


def t_search(args):
    q = (args.get("query") or "").strip()
    limit = min(int(args.get("limit", 20)), 100)
    if not q:
        return {"error": "query is required"}
    results, seen = [], set()
    seq = q.upper().strip()
    if re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWYXBZUO]{4,}", seq):
        for r in db().execute("SELECT DISTINCT peptide,sequence,paper_id,doi FROM activity WHERE upper(sequence)=? LIMIT ?", (seq, limit)):
            k = (r["peptide"], r["paper_id"])
            if k not in seen:
                seen.add(k); results.append({"peptide": r["peptide"], "sequence": r["sequence"], "paper_id": r["paper_id"], "doi": r["doi"], "match": "sequence"})
    fq = _fts(q)
    if fq and len(results) < limit:
        try:
            for r in db().execute("SELECT kind,name,sequence,paper_id,doi FROM search WHERE search MATCH ? LIMIT ?", (fq, limit * 3)):
                k = (r["name"], r["paper_id"])
                if k in seen:
                    continue
                seen.add(k); results.append({"peptide": r["name"], "sequence": r["sequence"], "paper_id": r["paper_id"], "doi": r["doi"], "match": r["kind"]})
                if len(results) >= limit:
                    break
        except sqlite3.OperationalError:
            pass
    return {"query": q, "count": len(results), "results": results}


def t_get_peptide(args):
    name = (args.get("name") or "").strip()
    if not name:
        return {"error": "name is required"}
    acts = rows_to_dicts(db().execute(
        "SELECT paper_id,doi,endpoint,raw_value,raw_unit,normalized_value,normalized_unit,target,assay_conditions,evidence_ladder,source_locator,evidence_tier FROM activity WHERE lower(peptide)=lower(?) LIMIT 500", (name,)))
    auds = rows_to_dicts(db().execute(
        "SELECT audit_record_id,database,database_measure,database_value,database_unit,primary_source_value,primary_source_unit,status,difference_categories,review_notes FROM audit WHERE lower(record_name)=lower(?) LIMIT 300", (name,)))
    seqs = sorted({a for a in (r["sequence"] for r in db().execute("SELECT DISTINCT sequence FROM activity WHERE lower(peptide)=lower(?)", (name,))) if a})
    feats = []
    for sq in seqs:
        fr = db().execute("SELECT * FROM features WHERE sequence=?", (sq,)).fetchone()
        if fr:
            feats.append(dict(fr))
    sel = rows_to_dicts(db().execute("SELECT mic_value,mic_unit,mic_target,tox_endpoint,tox_value,ti FROM selectivity WHERE lower(peptide)=lower(?) LIMIT 50", (name,))) if _has_table("selectivity") else []
    return {"peptide": name, "sequences": seqs, "n_activity": len(acts), "n_audit": len(auds),
            "physicochemical": feats, "selectivity_TI": sel, "activity_observations": acts, "database_audits": auds}


def t_get_paper(args):
    pid = (args.get("paper_id") or "").strip()
    if not pid:
        return {"error": "paper_id is required"}
    p = db().execute("SELECT paper_id,doi,review_status,publication_grade,n_audit,n_activity,n_mechanism,caution_count FROM papers WHERE paper_id=?", (pid,)).fetchone()
    if not p:
        return {"error": f"paper not found: {pid}"}
    acts = rows_to_dicts(db().execute("SELECT peptide,sequence,endpoint,raw_value,raw_unit,target,assay_conditions,source_locator FROM activity WHERE paper_id=? LIMIT 800", (pid,)))
    auds = rows_to_dicts(db().execute("SELECT audit_record_id,database,record_name,database_measure,database_value,primary_source_value,status,difference_categories,review_notes FROM audit WHERE paper_id=? LIMIT 800", (pid,)))
    mechs = rows_to_dicts(db().execute("SELECT mechanism_claim_id,claim_text,evidence_class,direct_assay_types,limitations FROM mechanism WHERE paper_id=? LIMIT 200", (pid,)))
    figs = rows_to_dicts(db().execute("SELECT label,figure_index,caption FROM figures WHERE paper_id=? ORDER BY CAST(figure_index AS INT)", (pid,)))
    for a in acts:
        a["source_location"] = parse_locator(a.pop("source_locator", ""))
    return {"paper": dict(p), "pdf_url": pdf_url(pid), "doi_url": (f"https://doi.org/{p['doi']}" if p["doi"] else None),
            "n_conflicts": sum(1 for a in auds if a["status"] == "source_conflict"),
            "activity_observations": acts, "database_audits": auds, "mechanism_claims": mechs,
            "figures_and_tables": figs}


def t_get_audit_record(args):
    aid = (args.get("audit_record_id") or "").strip()
    a = db().execute("SELECT * FROM audit WHERE audit_record_id=?", (aid,)).fetchone()
    if not a:
        return {"error": f"audit record not found: {aid}"}
    d = dict(a)
    d["source_location_readable"] = parse_locator(d.get("source_locator"))
    d["pdf_url"] = pdf_url(d["paper_id"])
    if d.get("doi"):
        d["doi_url"] = f"https://doi.org/{d['doi']}"
    return d


def t_list_conflicts(args):
    limit = min(int(args.get("limit", 25)), 200)
    offset = max(int(args.get("offset", 0)), 0)
    dbf = (args.get("database") or "").strip()
    where, params = "status='source_conflict'", []
    if dbf:
        where += " AND database=?"; params.append(dbf)
    total = db().execute(f"SELECT COUNT(*) FROM audit WHERE {where}", params).fetchone()[0]
    rows = rows_to_dicts(db().execute(
        f"SELECT audit_record_id,paper_id,doi,database,record_name,database_measure,database_value,primary_source_value,difference_categories,review_notes,human_verdict,human_review_notes FROM audit WHERE {where} LIMIT ? OFFSET ?",
        params + [limit, offset]))
    facets = {r["database"]: r["c"] for r in db().execute("SELECT database,COUNT(*) c FROM audit WHERE status='source_conflict' GROUP BY database")}
    return {"total": total, "offset": offset, "limit": limit, "by_database": facets, "conflicts": rows}


def t_query_activity(args):
    limit = min(int(args.get("limit", 50)), 500)
    clauses, params = [], []
    for field, col in (("peptide", "lower(peptide)=lower(?)"), ("endpoint", "endpoint=?"),
                       ("target", "lower(target) LIKE lower(?)"), ("paper_id", "paper_id=?")):
        v = (args.get(field) or "").strip()
        if v:
            clauses.append(col)
            params.append(f"%{v}%" if field == "target" else v)
    if not clauses:
        return {"error": "provide at least one filter: peptide, endpoint, target, or paper_id"}
    where = " AND ".join(clauses)
    total = db().execute(f"SELECT COUNT(*) FROM activity WHERE {where}", params).fetchone()[0]
    rows = rows_to_dicts(db().execute(
        f"SELECT paper_id,doi,peptide,sequence,endpoint,raw_value,raw_unit,normalized_value,normalized_unit,target,source_locator,evidence_tier FROM activity WHERE {where} LIMIT ?",
        params + [limit]))
    return {"total_matching": total, "returned": len(rows), "activity_observations": rows}


def t_find_precedents(args):
    limit = min(int(args.get("limit", 25)), 200)
    clauses, params = ["fold_change<>''"], []
    if (mt := (args.get("mod_type") or "").strip()):
        clauses.append("mod_type=?"); params.append(mt)
    if (m := (args.get("modification") or "").strip()):
        clauses.append("modification LIKE ?"); params.append(f"%{m}%")
    if (t := (args.get("target") or "").strip()):
        clauses.append("lower(target) LIKE lower(?)"); params.append(f"%{t}%")
    if (ep := (args.get("endpoint") or "").strip()):
        clauses.append("endpoint=?"); params.append(ep)
    direction = (args.get("direction") or "").strip()  # more_potent | less_potent
    if direction == "more_potent":
        clauses.append("CAST(fold_change AS REAL) < 1 AND CAST(fold_change AS REAL) > 0")
    elif direction == "less_potent":
        clauses.append("CAST(fold_change AS REAL) > 1")
    where = " AND ".join(clauses)
    try:
        db().execute("SELECT 1 FROM sar_pairs LIMIT 1")
    except sqlite3.OperationalError:
        return {"error": "SAR layer not built for this database"}
    if direction == "more_potent":
        order = "ORDER BY CAST(fold_change AS REAL) ASC"      # smallest fold = biggest potency gain
    elif direction == "less_potent":
        order = "ORDER BY CAST(fold_change AS REAL) DESC"
    else:
        order = "ORDER BY n_shared_assays DESC"
    rows = rows_to_dicts(db().execute(
        f"SELECT paper_id,doi,peptide_parent,peptide_variant,seq_parent,seq_variant,modification,mod_type,"
        f"endpoint,target,value_parent,value_variant,fold_change,d_net_charge,d_gravy,d_mu_h FROM sar_pairs "
        f"WHERE {where} {order} LIMIT ?", params + [limit]))
    for r in rows:
        if r.get("doi"):
            r["doi_url"] = f"https://doi.org/{r['doi']}"
        try:
            r["interpretation"] = ("more potent" if float(r["fold_change"]) < 1 else "less potent") + \
                f" (MIC ×{float(r['fold_change']):.2f})"
        except Exception:
            pass
    return {"count": len(rows), "note": "fold_change = variant MIC / parent MIC; <1 means the modification "
            "improved potency. Each row is a real analog pair from one paper.", "precedents": rows}


def t_get_figures(args):
    pid = (args.get("paper_id") or "").strip()
    if not pid:
        return {"error": "paper_id is required"}
    figs = rows_to_dicts(db().execute("SELECT label,figure_index,caption FROM figures WHERE paper_id=? ORDER BY CAST(figure_index AS INT)", (pid,)))
    return {"paper_id": pid, "pdf_url": pdf_url(pid), "n_figures": len(figs), "figures_and_tables": figs}


# guarded read-only SQL
_SQL_DENY = re.compile(r"\b(attach|detach|pragma|insert|update|delete|drop|alter|create|replace|vacuum|reindex)\b", re.I)


def t_sql_select(args):
    sql = (args.get("sql") or "").strip().rstrip(";")
    if not sql:
        return {"error": "sql is required"}
    if ";" in sql:
        return {"error": "only a single statement is allowed"}
    if not re.match(r"^\s*(select|with)\b", sql, re.I) or _SQL_DENY.search(sql):
        return {"error": "only read-only SELECT/WITH queries are allowed"}
    limit = min(int(args.get("limit", 200)), 1000)
    wrapped = f"SELECT * FROM ({sql}) LIMIT {limit}"
    try:
        cur = db().execute(wrapped)
        rows = [dict(r) for r in cur.fetchall()]
    except sqlite3.Error as ex:
        return {"error": f"SQL error: {ex}"}
    return {"row_count": len(rows), "capped_at": limit,
            "tables": "papers, activity, audit, conflicts, mechanism (see get_stats / schema in tool description)",
            "rows": rows}


TOOLS = [
    ("get_stats", "Corpus-wide statistics for the AMP Evidence Atlas (counts of papers, activity observations, "
     "database audit records, source conflicts, distinct peptides/sequences). Call this first to understand scale.",
     {"type": "object", "properties": {}, "additionalProperties": False}, t_get_stats),
    ("search", "Search the atlas by peptide name, exact amino-acid sequence, or DOI fragment. Returns matching "
     "peptides with their sequence and source paper.",
     {"type": "object", "properties": {"query": {"type": "string", "description": "peptide name, sequence, or DOI"},
                                        "limit": {"type": "integer", "description": "max results (default 20, max 100)"}},
      "required": ["query"], "additionalProperties": False}, t_search),
    ("get_peptide", "All evidence for one peptide by exact name: computed physicochemical properties (length, MW, net "
     "charge, pI, GRAVY hydrophobicity, hydrophobic moment, cationic flag), every activity observation "
     "(endpoint/value/target), and every database audit record (database claim vs primary source).",
     {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"], "additionalProperties": False}, t_get_peptide),
    ("get_paper", "Full base data for one primary paper by paper_id: metadata, pdf_url + doi_url to the original, all "
     "activity observations (each with a human-readable source_location), all database audits (with conflict count), "
     "mechanism claims, and the list of figures/tables with captions.",
     {"type": "object", "properties": {"paper_id": {"type": "string", "description": "e.g. doi__10.1016_j.antiviral.2013.11.013"}},
      "required": ["paper_id"], "additionalProperties": False}, t_get_paper),
    ("get_audit_record", "One database audit record's full evidence card: database claim, primary-source value, "
     "conflict flags, difference categories, curator review notes, human-readable source location (table/row/column "
     "or section/line-range), plus pdf_url and doi_url to the original paper.",
     {"type": "object", "properties": {"audit_record_id": {"type": "string"}}, "required": ["audit_record_id"], "additionalProperties": False}, t_get_audit_record),
    ("get_figures", "List all figures and tables of a paper with their labels and full captions, plus pdf_url to view "
     "the original. Use to see what figures/tables exist and read their captions.",
     {"type": "object", "properties": {"paper_id": {"type": "string"}}, "required": ["paper_id"], "additionalProperties": False}, t_get_figures),
    ("find_precedents", "Find real matched-pair SAR precedents: analog peptides from one paper that differ by a "
     "modification, with the measured fold-change in activity — i.e. 'which modifications changed activity, and by how "
     "much, with cited cases'. Filter by mod_type (substitution|length_C|length_N), modification (e.g. a residue like "
     "'R' or a specific change 'A5R'), target organism (substring), endpoint (MIC/MBC/...), and direction "
     "(more_potent|less_potent). Use this to answer 'how do I improve this peptide's activity — what precedents exist'.",
     {"type": "object", "properties": {"mod_type": {"type": "string"}, "modification": {"type": "string"},
                                        "target": {"type": "string"}, "endpoint": {"type": "string"},
                                        "direction": {"type": "string", "enum": ["more_potent", "less_potent"]},
                                        "limit": {"type": "integer"}}, "additionalProperties": False}, t_find_precedents),
    ("list_conflicts", "Browse records where a public database disagrees with the primary source (status=source_conflict). "
     "Filter by database; paginate with limit/offset. Returns per-database counts too.",
     {"type": "object", "properties": {"database": {"type": "string", "description": "DBAASP|CAMP|DRAMP|dbAMP|APD6 (optional)"},
                                        "limit": {"type": "integer"}, "offset": {"type": "integer"}}, "additionalProperties": False}, t_list_conflicts),
    ("query_activity", "Structured filter over activity observations. Combine any of: peptide (exact), endpoint (e.g. MIC, "
     "IC50, MBC), target (substring), paper_id. Returns matching observations.",
     {"type": "object", "properties": {"peptide": {"type": "string"}, "endpoint": {"type": "string"},
                                        "target": {"type": "string"}, "paper_id": {"type": "string"},
                                        "limit": {"type": "integer"}}, "additionalProperties": False}, t_query_activity),
    ("sql_select", "Run a read-only SQL SELECT against the atlas for advanced queries. Tables: "
     "papers(paper_id,doi,review_status,n_audit,n_activity,n_mechanism), "
     "activity(paper_id,peptide,sequence,endpoint,raw_value,raw_unit,normalized_value,normalized_unit,target,evidence_tier), "
     "audit(audit_record_id,paper_id,database,record_name,database_measure,database_value,primary_source_value,status,difference_categories,review_notes,human_verdict,human_review_notes), "
     "conflicts(issue_id,paper_id,database,status,severity_hint,summary), "
     "mechanism(paper_id,claim_text,evidence_class), figures(paper_id,label,figure_index,caption), "
     "features(sequence,length,mw,net_charge,pI,gravy,hydrophobic_frac,aromatic_frac,mu_h,mu_h_per_res,cationic), selectivity(paper_id,peptide,mic_value,mic_unit,tox_endpoint,tox_value,ti), sar_pairs(paper_id,peptide_parent,peptide_variant,modification,mod_type,endpoint,fold_change,target). Results capped (default 200 rows).",
     {"type": "object", "properties": {"sql": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["sql"], "additionalProperties": False}, t_sql_select),
]
TOOL_MAP = {name: fn for (name, _d, _s, fn) in TOOLS}
TOOL_DEFS = [{"name": n, "description": d, "inputSchema": s} for (n, d, s, _fn) in TOOLS]


# ------------------------------------------------------------------ JSON-RPC dispatch
def rpc(msg):
    """Handle one JSON-RPC message. Returns a response dict, or None for notifications."""
    mid = msg.get("id")
    method = msg.get("method")
    params = msg.get("params") or {}

    def ok(result):
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    def err(code, message):
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}

    if method == "initialize":
        return ok({"protocolVersion": PROTOCOL_VERSION, "capabilities": {"tools": {"listChanged": False}}, "serverInfo": SERVER_INFO})
    if method == "notifications/initialized" or method == "notifications/cancelled":
        return None  # notification, no response
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": TOOL_DEFS})
    if method == "tools/call":
        name = params.get("name")
        fn = TOOL_MAP.get(name)
        if not fn:
            return err(-32602, f"unknown tool: {name}")
        try:
            result = fn(params.get("arguments") or {})
            is_error = isinstance(result, dict) and "error" in result
            return ok({"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=1)}], "isError": is_error})
        except Exception as ex:
            return ok({"content": [{"type": "text", "text": json.dumps({"error": str(ex)})}], "isError": True})
    if mid is None:
        return None
    return err(-32601, f"method not found: {method}")


def handle_payload(data):
    """data is a parsed JSON-RPC message or batch. Returns a response object/array or None."""
    if isinstance(data, list):
        out = [r for r in (rpc(m) for m in data) if r is not None]
        return out or None
    return rpc(data)


# ------------------------------------------------------------------ HTTP transport
class H(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8") if obj is not None else b""
        self.send_response(code)
        if b:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        if b:
            self.wfile.write(b)

    def _authed(self):
        if not MCP_TOKEN:
            return True
        h = self.headers.get("Authorization", "")
        return h.startswith("Bearer ") and h[7:].strip() == MCP_TOKEN

    def do_GET(self):
        if self.path.split("?")[0] in ("/health", "/healthz"):
            return self._json(200, {"status": "ok", "server": SERVER_INFO, "tools": len(TOOLS)})
        # GET /mcp with no session → method not allowed (we are stateless, no SSE stream)
        self._json(405, {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": "GET not supported; use POST"}})

    def do_POST(self):
        if self.path.split("?")[0] != "/mcp":
            return self._json(404, {"error": "not found"})
        if not self._authed():
            return self._json(401, {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": "unauthorized"}})
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json(400, {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}})
        resp = handle_payload(data)
        if resp is None:
            return self._json(202, None)  # notification acknowledged
        self._json(200, resp)

    def log_message(self, *a):
        pass


def run_http():
    port = 8090
    for a in sys.argv[1:]:
        if a.isdigit():
            port = int(a)
    bind = os.environ.get("BIND_ADDR", "0.0.0.0")
    print(f"AMP Atlas MCP (Streamable HTTP):  http://{bind}:{port}/mcp   ({len(TOOLS)} tools, db={DB_PATH})"
          + ("  [token-gated]" if MCP_TOKEN else ""))
    ThreadingHTTPServer((bind, port), H).serve_forever()


def run_stdio():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except Exception:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}) + "\n")
            sys.stdout.flush()
            continue
        resp = handle_payload(data)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    if "--stdio" in sys.argv:
        run_stdio()
    else:
        run_http()
