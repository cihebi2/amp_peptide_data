# Unresolved Processing: `doi__10.1038_s41522-024-00637-y`

Generated at: `2026-06-20T02:53:48+00:00`

## Decision

- Resolution decision: `keep_unresolved_blocked_missing_primary_material`
- Status change applied: `False`
- Review status: `blocked_missing_primary_material`
- Publication grade: `False`
- Unresolved rows: `30`
- Reason: No unresolved row was promoted because local material/rework evidence preserves missing primary material or row-level ambiguity.
- Next action: Recover the named missing supplement/source material or rerun owner-worker row mapping with new evidence; otherwise keep unresolved disclosed in release notes.

## Blocker Counts

| blocker_class | count |
| --- | ---: |
| `missing_or_unparsed_supplement` | 28 |
| `row_level_source_mapping_ambiguous` | 1 |
| `synergy_partner_or_fici_mapping_ambiguous` | 1 |

## Material / Rework Evidence

| evidence | value |
| --- | --- |
| `supplementary_asset_count` | 10 |
| `supplement_parse_count` | 0 |
| `supplementary_table_count` | 0 |
| `extraction_status` | material_extracted_with_gaps |
| `gap_assessment` | Material inventory and primary extraction complete for workflow test; publication-grade supplement table and figure quantification remain analysis rework. |
| `rework_request_count` | 3 |
| `rework_response_count` | 2 |
| `quality_feedback_status` | blocked_after_bounded_worker4_worker6_source_review |

## Checked Paths

- `/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41522-024-00637-y/extracted/supplementary_index.json`
- `/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41522-024-00637-y/extracted/supplementary_tables.json`
- `/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41522-024-00637-y/extraction/extraction_status.json`
- `/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41522-024-00637-y/extraction/extraction_quality_report.json`
- `/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41522-024-00637-y/rework/rework_requests.jsonl`
- `/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41522-024-00637-y/rework/rework_responses.jsonl`
- `/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41522-024-00637-y/final/database_record_verification.json`
- `/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41522-024-00637-y/final/review_report.json`
- `/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41522-024-00637-y/work/review/quality_feedback.json`

## Policy

- Do not promote any row to `source_verified` without primary/source packet evidence.
- If new supplement/source material is recovered, rerun owner-worker row mapping before changing final status.
