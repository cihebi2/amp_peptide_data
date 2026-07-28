#!/usr/bin/env python3
"""Build the DBAASP extraction worklist: 1 source file per NEW paper (not in the merged superset).
Prefer XML (clean PMC full-text) > main PDF; skip supplementary files. Output dbaasp_worklist.json."""
import os, re, csv, json, glob
csv.field_size_limit(10**9)
DB = "/mnt/d/work/抗菌肽/数据库"; MC = f"{DB}/merged_amp_corpus"
OUT = "/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_worklist.json"


def ndoi(x):
    x = (x or "").strip().lower()
    x = re.sub(r'^https?://(dx\.)?doi\.org/', '', x)
    x = x.replace('_', '/', 1)
    x = re.sub(r'[\]\)\}>,;:.]+$', '', x)
    return x if re.match(r'^10\.\d{4,}/\S+$', x) else ""
def npmc(x):
    x = (x or "").strip().upper().replace("PMC", ""); return "PMC" + x if x.isdigit() else ""


# known superset IDs (so we only take papers NOT already in merged corpus)
known = set()
for r in csv.DictReader(open(f"{MC}/downloaded_assets/manifests/source_status.csv", encoding="utf-8", errors="replace")):
    known |= {ndoi(r.get("canonical_doi")), npmc(r.get("canonical_pmcid"))} - {""}

SUPP = re.compile(r'MOESM|_si_|/si\b|mmc\d|Data_Sheet|Image_\d|Table_\d|Presentation_\d|supplementary|/supp', re.I)
best = {}  # key -> (path, kind, is_xml, is_main)
for p in glob.glob(f"{DB}/DBAASP/**/*.pdf", recursive=True) + glob.glob(f"{DB}/DBAASP/**/*.xml", recursive=True):
    b = os.path.basename(p)
    is_supp = bool(SUPP.search(p)) and "paper.pdf" not in b.lower()
    if is_supp:
        continue
    mdoi = re.search(r'(10\.\d{4,}[._][^/]+?)\.(pdf|xml)$', b)
    mpmc = re.search(r'(PMC\d+)', b) or re.search(r'/(PMC\d+)/', p)
    if mdoi:
        key = ndoi(mdoi.group(1))
    elif mpmc:
        key = npmc(mpmc.group(1))
    else:
        continue
    if not key or key in known:
        continue
    is_xml = p.lower().endswith(".xml")
    is_main = "paper.pdf" in b.lower() or is_xml
    prev = best.get(key)
    # prefer xml, then main article, then any
    score = (2 if is_xml else 0) + (1 if is_main else 0)
    if prev is None or score > prev[3]:
        best[key] = (p, "xml" if is_xml else "pdf", is_xml, score)

work = [[k, v[0], v[1]] for k, v in best.items()]
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(work, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
print(f"DBAASP worklist: {len(work)} papers | xml={sum(1 for w in work if w[2]=='xml')} pdf={sum(1 for w in work if w[2]=='pdf')}")
