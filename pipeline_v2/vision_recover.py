#!/usr/bin/env python3
"""pipeline_v2 #4: gated codex-VISION recovery of figure-bound values.

Empirically (sub-agent eval + smoke test): tesseract/img2table fail on this corpus, but codex vision
(`codex exec -i <img>`) reads tables-rendered-as-images (~95-100%) and charts WITH printed data labels
(~90-100%); label-free curves only estimable. So we run codex vision ONLY on figure images and append
the extracted values to the evidence pack as figure tables, flagged with a confidence level.

GATING: pass specific figure image paths (those referenced by undetermined assertions) to avoid blanket
cost. codex auth lives under root here, so we invoke via: sudo HOME=/root codex exec ... -i <img>.

Usage: python pipeline_v2/vision_recover.py <paper_id> <img1> [img2 ...]
"""
import json, subprocess, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROMPT = (
    "You are extracting DATA from a scientific figure image. Return ONLY a JSON object: "
    '{"image_kind": "table_image|labeled_chart|unlabeled_chart|spectrum|other", '
    '"cells": [{"row_label": "<peptide/organism/series>", "col_header": "<endpoint/x-axis e.g. MIC, IC50, hemolysis %, concentration>", '
    '"value": "<printed value EXACTLY as shown>", "printed": true}]}. '
    "Rules: copy ONLY values PRINTED in the image (axis labels, bar/point data labels, table cells). "
    "If a value is not printed (must be read off an axis), set printed=false and give your best estimate. "
    "Do NOT invent rows. No prose, JSON only."
)


def run_vision(img, outpath):
    import os, shlex
    # -o MUST be inside the codex workspace (-C ROOT); codex's read-only sandbox blocks writes elsewhere.
    cmd = (f'sudo HOME=/root codex exec -C {shlex.quote(str(ROOT))} --skip-git-repo-check '
           f'-m gpt-5.5 -c \'approval_policy="never"\' -c \'model_reasoning_effort="medium"\' '
           f'-i {shlex.quote(str(img))} -o {shlex.quote(str(outpath))} -')
    try:
        subprocess.run(cmd, input=PROMPT, capture_output=True, text=True, timeout=400, shell=True, executable="/bin/bash")
        out = Path(outpath).read_text(encoding="utf-8", errors="replace")
        out = re.sub(r"^```(json)?|```$", "", out.strip(), flags=re.M).strip()
        s, e = out.find("{"), out.rfind("}")
        return json.loads(out[s:e + 1]) if s >= 0 else None
    except Exception as ex:
        print(f"  vision err {Path(img).name}: {ex}")
        return None


def main():
    paper_id = sys.argv[1]
    imgs = sys.argv[2:]
    pack_path = ROOT / f"pipeline_v2/work/{paper_id}/evidence_pack.json"
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    nxt = max([t["table_index"] for t in pack["tables"]], default=0) + 1
    added = 0
    fig_tables = []
    workdir = ROOT / f"pipeline_v2/work/{paper_id}"
    for i, img in enumerate(imgs):
        res = run_vision(img, workdir / f"_vision_tmp_{i}.txt")
        if not res or not res.get("cells"):
            continue
        kind = res.get("image_kind", "figure")
        cells = []
        for c in res["cells"]:
            cells.append({
                "table_index": nxt, "row_index": "", "col_index": "",
                "row_label": str(c.get("row_label", "")), "col_header": str(c.get("col_header", "")),
                "value": str(c.get("value", "")),
                "confidence": "printed" if c.get("printed", True) else "chart_estimate",
            })
        fig_tables.append({
            "table_index": nxt, "label": f"FIGURE(vision:{kind}) {Path(img).name}",
            "caption": f"codex-vision extracted from {img}", "footnotes": [],
            "header_rows": [], "grid": [], "longform_cells": cells, "source": "codex_vision",
        })
        nxt += 1
        added += len(cells)
    pack["tables"].extend(fig_tables)
    pack["vision"] = {"images": len(imgs), "figure_tables": len(fig_tables), "cells": added}
    pack_path.write_text(json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{paper_id}: vision +{len(fig_tables)} figure-tables (+{added} cells) from {len(imgs)} images")


if __name__ == "__main__":
    main()
