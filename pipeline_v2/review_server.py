#!/usr/bin/env python3
"""Local human-review web app for the confirmed DB-error worksheet.
Pure stdlib. One card at a time: shows DB-claimed vs source value, opens the source PDF,
[Confirm]->next, [Not an error/Uncertain]->add a note. Verdicts persist (resume-safe).

The persisted JSON remains the current verdict snapshot. `review_log.jsonl` is the
append-only audit trail used for provenance and inter-rater agreement analysis.
"""
import csv
import json
import mimetypes
import os
import tempfile
import threading
import urllib.parse
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSHEET = ROOT / "pipeline_v2/HUMAN_REVIEW_worksheet.tsv"
VERDICTS = ROOT / "pipeline_v2/review_verdicts.json"
REVIEW_LOG = ROOT / "pipeline_v2/review_log.jsonl"
ALLOWED_VERDICTS = {"confirmed", "not_an_error", "uncertain"}
ALLOWED_SEVERITIES = {"critical", "major", "minor"}
ALLOWED_FILE_ROOTS = (ROOT / "papers", ROOT / "paper_packets")
_SAVE_LOCK = threading.Lock()


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_saved():
    return json.loads(VERDICTS.read_text(encoding="utf-8")) if VERDICTS.exists() else {}


def load_worksheet_rows():
    with WORKSHEET.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def review_id_set():
    return {r["review_id"] for r in load_worksheet_rows()}


def atomic_write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def normalize_verdict(review_id, data, client_host=""):
    rid = (review_id or "").strip()
    verdict = (data.get("verdict") or "").strip()
    severity = (data.get("severity") or "").strip()
    reviewer = (data.get("reviewer") or "").strip()
    notes = (data.get("notes") or "").strip()
    if verdict not in ALLOWED_VERDICTS:
        raise ValueError(f"invalid verdict: {verdict!r}")
    if verdict == "confirmed":
        if severity not in ALLOWED_SEVERITIES:
            raise ValueError("confirmed verdict requires severity: critical, major, or minor")
    else:
        severity = ""
        if not notes:
            raise ValueError("not_an_error/uncertain verdicts require notes")
    return {
        "review_id": rid,
        "verdict": verdict,
        "severity": severity,
        "reviewer": reviewer,
        "notes": notes,
        "reviewed_at": now_iso(),
        "source": "human_review_ui",
        "provenance": "manual_ui_save",
        "schema_version": "review_verdict_v2",
        "client_host": client_host,
        "is_human_verdict": True,
    }


def append_review_log(entry, previous=None):
    REVIEW_LOG.parent.mkdir(parents=True, exist_ok=True)
    log_entry = {
        "logged_at": now_iso(),
        "action": "save_verdict",
        "review_id": entry.get("review_id", ""),
        "previous_verdict": (previous or {}).get("verdict", ""),
        "entry": entry,
    }
    with REVIEW_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(log_entry, ensure_ascii=False, sort_keys=True) + "\n")


def resolve_allowed_file(q):
    raw = (q or "").strip()
    if not raw or raw.startswith("/") or "\x00" in raw:
        raise PermissionError("forbidden")
    # `papers/*/source/paper.pdf` entries are symlinks into the acquired corpus.
    # Check lexical containment before following the symlink so legitimate corpus
    # files work, while `papers/../...` traversal is still blocked.
    candidate = ROOT / raw
    lexical = Path(os.path.abspath(candidate))
    for base in ALLOWED_FILE_ROOTS:
        try:
            lexical.relative_to(Path(os.path.abspath(base)))
            return candidate
        except ValueError:
            continue
    raise PermissionError("forbidden")


def load_items():
    items = load_worksheet_rows()
    saved = load_saved()
    for it in items:
        v = saved.get(it["review_id"], {})
        it["verdict"] = v.get("verdict", "")
        it["severity"] = v.get("severity", "")
        it["reviewer"] = v.get("reviewer", "")
        it["notes"] = v.get("notes", "")
        it["reviewed_at"] = v.get("reviewed_at", "")
        it["source"] = v.get("source", "")
        it["provenance"] = v.get("provenance", "")
    return items


def save_verdict(rid, data, client_host=""):
    rid = (rid or "").strip()
    with _SAVE_LOCK:
        if rid not in review_id_set():
            raise ValueError(f"unknown review_id: {rid!r}")
        saved = load_saved()
        previous = saved.get(rid, {})
        entry = normalize_verdict(rid, data, client_host=client_host)
        saved[rid] = entry
        atomic_write_json(VERDICTS, saved)
        append_review_log(entry, previous=previous)
        return len(saved)


PAGE = """<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>数据库错误人工核对</title><style>
*{box-sizing:border-box} body{font:15px/1.5 system-ui,sans-serif;margin:0;background:#0f1220;color:#e7e9f0}
header{display:flex;gap:12px;align-items:center;padding:10px 16px;background:#171a2b;position:sticky;top:0;border-bottom:1px solid #2a2f45;flex-wrap:wrap}
header b{font-size:16px} .pill{padding:2px 8px;border-radius:999px;font-size:12px;background:#2a2f45}
.wrap{max-width:880px;margin:18px auto;padding:0 16px}
.card{background:#171a2b;border:1px solid #2a2f45;border-radius:14px;padding:18px 20px}
.dual{background:#3b2f12;color:#ffd479;border:1px solid #6b551f}
.row{display:flex;gap:14px;flex-wrap:wrap;margin:6px 0}
.kv{flex:1;min-width:240px;background:#0f1220;border:1px solid #2a2f45;border-radius:10px;padding:10px 12px}
.kv .lab{font-size:12px;color:#8b90a8} .kv .val{font-size:18px;font-weight:600;word-break:break-word}
.bad{border-color:#7a2540} .good{border-color:#2f6b3b}
.meta{color:#aab;font-size:13px;margin:4px 0} .reason{margin:10px 0;padding:10px 12px;background:#10131f;border-left:3px solid #5a6;border-radius:6px;color:#cfd}
.links a{display:inline-block;margin:6px 8px 0 0;padding:8px 12px;background:#23314d;color:#cfe;border-radius:8px;text-decoration:none}
.acts{display:flex;gap:10px;margin-top:16px;flex-wrap:wrap}
button{font:inherit;padding:11px 16px;border:0;border-radius:10px;cursor:pointer;color:#fff}
.c{background:#2f7d44} .n{background:#a23b54} .u{background:#7a6a2a} .skip{background:#3a3f55}
textarea{width:100%;margin-top:10px;background:#0f1220;color:#e7e9f0;border:1px solid #2a2f45;border-radius:8px;padding:10px;min-height:70px}
.sev{margin-top:10px} .sev button{padding:6px 10px;background:#3a3f55;margin-right:6px}
.sev button.on{background:#2f7d44}
small{color:#8b90a8}
.done{text-align:center;padding:40px;font-size:20px}
select,input{font:inherit;background:#0f1220;color:#e7e9f0;border:1px solid #2a2f45;border-radius:8px;padding:6px 8px}
</style></head><body>
<header>
 <b>数据库错误人工核对</b>
 <span class=pill id=prog>…</span>
 <label>筛选 <select id=filter>
   <option value=todo>未核对</option><option value=dual>仅DUAL</option><option value=all>全部</option>
 </select></label>
 <label>审查人 <input id=rev size=8 placeholder=姓名></label>
 <span style="flex:1"></span><small id=pos></small>
</header>
<div class=wrap><div id=app></div></div>
<script>
let items=[], idx=0, sev="";
const $=s=>document.querySelector(s);
async function load(){items=await (await fetch('/api/items')).json(); $('#rev').value=localStorage.rev||''; refresh();}
function pool(){const f=$('#filter').value;
 return items.filter(it=> f==='all'?true : f==='dual'?it.priority==='DUAL' : !it.verdict);}
function refresh(){const p=pool(); const done=items.filter(i=>i.verdict).length;
 $('#prog').textContent=`已核 ${done} / ${items.length}（DUAL ${items.filter(i=>i.priority==='DUAL'&&i.verdict).length}/${items.filter(i=>i.priority==='DUAL').length}）`;
 if(idx>=p.length) idx=0;
 if(!p.length){$('#app').innerHTML='<div class=card done>🎉 当前筛选下没有待核条目了。切换筛选或查看“全部”。</div>';$('#pos').textContent='';return;}
 render(p[idx], p.length);}
function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function render(it,n){sev=it.severity||'';
 $('#pos').textContent=`第 ${idx+1} / ${n} 条`;
 const doi=it.doi?`https://doi.org/${encodeURIComponent(it.doi)}`:'';
 $('#app').innerHTML=`<div class=card>
  <div class=row style="align-items:center">
   <span class="pill ${it.priority==='DUAL'?'dual':''}">${it.priority==='DUAL'?'★ 双模型共识 DUAL':'单模型'}</span>
   <span class=pill>${esc(it.error_type)}</span>
   <span class=pill>${esc(it.database)}</span>
   <span class=pill>${esc(it.review_id)}</span>
   ${it.verdict?`<span class=pill style="background:#2f7d44">已判:${esc(it.verdict)}${it.severity?'/'+esc(it.severity):''}</span>`:''}
  </div>
  <div class=meta>肽：<b>${esc(it.db_peptide)||'—'}</b> ｜ 靶标/细胞：${esc(it.db_organism)||'—'}</div>
  <div class=row>
   <div class="kv bad"><div class=lab>数据库标注 (${esc(it.db_endpoint)||'值'})</div><div class=val>${esc(it.db_value)||'(空/见下)'}</div></div>
   <div class="kv good"><div class=lab>原文 ${esc(it.source_table?('表'+it.source_table):'')} ${esc(it.source_row)} / ${esc(it.source_col)}</div><div class=val>${esc(it.source_value)||'—'}</div></div>
  </div>
  <div class=reason>判定理由：${esc(it.reason)}</div>
  <div class=links>
   ${doi?`<a href="${doi}" target=_blank>🔗 按 DOI 打开原文</a>`:''}
   <a href="/file?path=${encodeURIComponent(it.local_pdf)}" target=_blank>📄 打开本地 PDF（找 表${esc(it.source_table)}）</a>
  </div>
  <div class=sev>严重度（确认时）：
   ${['critical','major','minor'].map(s=>`<button data-sev="${s}" class="${sev===s?'on':''}">${s}</button>`).join('')}</div>
  <div class=acts>
   <button class=c id=ok>✅ 确认是错误 → 下一条</button>
   <button class=n id=no>❌ 不是错误 / 需补充</button>
   <button class=u id=unc>❓ 存疑</button>
   <button class=skip id=skip>⏭ 跳过</button>
  </div>
  <textarea id=notes placeholder="补充说明（驳回/存疑时填，原文实际是什么…）">${esc(it.notes)}</textarea>
 </div>`;
 document.querySelectorAll('.sev button').forEach(b=>b.onclick=()=>{sev=b.dataset.sev;render(it,n);});
 $('#ok').onclick=()=>commit(it,'confirmed');
 $('#no').onclick=()=>commit(it,'not_an_error');
 $('#unc').onclick=()=>commit(it,'uncertain');
 $('#skip').onclick=()=>{idx++;refresh();};
}
async function commit(it,verdict){
 const notes=$('#notes').value.trim(), reviewer=$('#rev').value.trim();
 if(verdict==='confirmed' && !sev){alert('确认是错误前，请先选择严重度：critical / major / minor');return;}
 if(verdict!=='confirmed' && !notes){$('#notes').focus();$('#notes').style.borderColor='#a23b54';return;}
 localStorage.rev=reviewer;
 const res=await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({review_id:it.review_id,verdict,severity:verdict==='confirmed'?sev:'',reviewer,notes})});
 if(!res.ok){alert(await res.text());return;}
 it.verdict=verdict;it.severity=verdict==='confirmed'?sev:'';it.reviewer=reviewer;it.notes=notes;
 if($('#filter').value==='todo'){refresh();} else {idx++;refresh();}
}
$('#filter').onchange=()=>{idx=0;refresh();};
$('#rev').onchange=()=>localStorage.rev=$('#rev').value;
document.onkeydown=e=>{if(e.target.tagName==='TEXTAREA'||e.target.tagName==='INPUT')return;
 if(e.key==='1')$('#ok')?.click(); if(e.key==='2')$('#no')?.click(); if(e.key==='3')$('#unc')?.click();};
load();
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            return self._send(200, PAGE, "text/html; charset=utf-8")
        if u.path == "/api/items":
            return self._send(200, json.dumps(load_items(), ensure_ascii=False))
        if u.path == "/file":
            q = urllib.parse.parse_qs(u.query).get("path", [""])[0]
            try:
                fp = resolve_allowed_file(q)
            except PermissionError:
                return self._send(403, b"forbidden", "text/plain")
            if not fp.is_file():
                return self._send(404, b"not found", "text/plain")
            try:
                data = fp.read_bytes()
            except Exception:
                return self._send(404, b"not found", "text/plain")
            ct = mimetypes.guess_type(str(fp))[0] or "application/octet-stream"
            return self._send(200, data, ct)
        return self._send(404, b"404", "text/plain")

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/api/save":
            n = int(self.headers.get("Content-Length", 0))
            try:
                d = json.loads(self.rfile.read(n) or b"{}")
                cnt = save_verdict(d.get("review_id", ""), d, client_host=self.client_address[0])
            except (KeyError, ValueError, json.JSONDecodeError) as ex:
                return self._send(400, str(ex), "text/plain; charset=utf-8")
            return self._send(200, json.dumps({"ok": True, "saved": cnt}, ensure_ascii=False))
        return self._send(404, b"404", "text/plain")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"Human-review UI:  http://127.0.0.1:{port}   ({len(load_items())} items)")
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
