Re-reviewed and repaired `doi__10.3390_plants9010047`.

Key outcome: final status is now `accepted_with_cautions`, `publication_grade=true`, with no open rework targets. The existing ticket `rwk-complete-test-0001` is closed in `paper_packets/.../rework/rework_responses.jsonl`.

What changed:
- Repaired worker-4 database adjudication: `13 source_verified`, `2 source_conflict`.
- Preserved the real caution: Stephensiolide C has Table/DBAASP value `128 µg/mL`, while prose says `>128 µg/mL`.
- Replaced placeholder mechanism claims with source-reviewed non-direct mechanism ontology.
- Updated worker-6 final review, adjudication, quality feedback, packet status, and after-worker gate reports.
- Added repair script: [repair_doi_10_3390_plants9010047_worker46.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_3390_plants9010047_worker46.py)

Verification:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication QA: `publication_grade_pass=true`
- JSON validation passed for updated packet/final/work/report artifacts.

Material packet status remains separately recorded as `material_extracted_with_gaps`; publication-grade review is accepted with explicit cautions, not clean acceptance.

