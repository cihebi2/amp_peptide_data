# Worker-1 Intake Report: PMC12162962

- Generated: 2026-07-28T03:45:27Z
- Worker: worker-1
- Scope: PMC12162962 only; internet not used.
- Lane boundary: material/source inventory and manifest mirror repair only; no source_verified or publication-grade claim is made by worker-1.
- Material queue status observed: `material_extracted_complete`.
- Analysis queue status mirrored in material manifest: `analysis_needs_analysis_rework`.
- Analysis status file observed: `analysis_needs_analysis_rework`.
- Open rework tickets observed in packet manifest: 3.
- Worker-1 assigned ticket response appended: `rwk-PMC12162962-campaign-r02-BF-PMC12162962-W1-FINAL-MATERIALS-MANIFEST-STALE` at JSONL line 7.

## Inventoried Surfaces

- Raw source/packet comparisons: 4 checked; mismatches: 0.
- Extracted XML/PDF/supplement/locator/database surfaces inventoried in `papers/PMC12162962/work/intake/source_inventory.json`.
- Linked authoritative database row files counted: 0 total rows across linked article/assay/sequence/literature files.
- DBAASP fallback rows remain candidate machine evidence only: 48 rows counted.

## Repair And Validation

- Repaired paper material manifest: `papers/PMC12162962/final/materials_manifest.json`.
- Repaired packet material manifest: `packets/PMC12162962/final/materials_manifest.json`.
- Material manifest status alignment pass: True.
- Stale final strict_boundary count: 0.
- Final mirror unresolved non-identical count: 0.
- Packet-only mechanism alias is byte-identical to canonical packet mechanism final: True.
- Packet gate return code: 0; artifact: `papers/PMC12162962/work/intake/packet_gate.worker1_materials_manifest_repair.one_paper.json`.
- Worker-1 validation artifact: `papers/PMC12162962/work/intake/worker1_materials_manifest_repair_validation.no_source_text.json`.

## Lane Decision

- Worker-1 lane status: `repair_ready_for_adjudication`.
- No worker-1 targeted blocker remains after this repair.
- Worker-6 must perform fresh adjudication and terminal ticket closure; other owner tickets remain outside worker-1 scope.
