# Worker-1 Intake Report: PMC12019989

## Scope
- Checkout-only run: yes.
- Internet used: no.
- Paper root: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989`.
- Packet root: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12019989`.
- Worker role: material intake and packet/database provenance inventory only.
- Source-verified, final database, activity, mechanism, and publication-grade claims: not made.

## Intake status
- Intake lane status: `source_reviewed_material_inventory_complete_with_analysis_rework_open`.
- Packet material queue status: `material_extracted_complete`.
- Packet analysis queue status: `analysis_needs_analysis_rework`.
- Current analysis status file status: `analysis_needs_analysis_rework`.
- Analysis status changed by worker-1 in this run: no.

## Primary assets inventoried
- Source XML/PDF/meta files: 3 present under `papers/PMC12019989/source/`.
- Packet raw XML/PDF/meta files: 3 present under `packets/PMC12019989/raw/`.
- Source-to-packet hash comparison: XML match yes; PDF match yes; metadata match yes.
- XML sections: 121.
- XML tables: 1.
- PDF pages: 12.
- PDF table extraction files: 1 table record(s).
- Figure-caption records: 13.
- Supplementary files indexed: 0.
- Supplementary text lines: 0.
- Supplementary table records: 0.
- Archive members: 0.
- Extraction errors: 0.
- Locator records: 133.

## Database provenance boundary
- Database manifest path: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12019989/database/database_source_manifest.json`.
- Authoritative match report path: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12019989/database/authoritative_match_report.json`.
- DBAASP machine candidate rows: 13.
- Linked authoritative article rows: 0.
- Linked authoritative assay rows: 0.
- Linked authoritative sequence rows: 0.
- Linked authoritative literature rows: 0.
- Source record links present: False.
- Boundary: DBAASP Codex fallback rows remain candidate machine evidence only.

## Rework state
- Packet manifest open ticket count: 1.
- Analysis status open ticket count: 1.
- Runtime-assigned ticket IDs for worker-1: 0.
- Worker-1 rework response appended: no, because the runtime-assigned list is authoritative and empty.

## Unresolved blockers and cautions
- Analysis acceptance remains blocked by an open analysis rework ticket not assigned to worker-1 in this prompt.
- Downstream database audit should treat linked authoritative row files as empty and DBAASP fallback rows as candidate machine evidence only.
- This intake lane does not establish publication-grade completion; worker-6 adjudication and strict semantic/publication gates remain required.

## Validation
- `source_inventory.json` JSON syntax: valid.
- Packet gate manifest: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/intake/packet_gate_manifest.json`.
- Packet gate result: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/intake/packet_gate_result.json`.
- Packet gate stdout/stderr logs: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/intake/packet_gate_stdout.log`, `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/intake/packet_gate_stderr.log`.
- Packet gate allow mode used: no.
- Packet gate exit status: 2.
- Packet gate single-paper summary: material `material_extracted_complete`, analysis `analysis_needs_analysis_rework`, locator count 133, extraction errors 0, open rework tickets 1, hard findings ['missing_final_files'].

## Artifacts written
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/intake/source_inventory.json`.
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/intake/intake_report.md`.
