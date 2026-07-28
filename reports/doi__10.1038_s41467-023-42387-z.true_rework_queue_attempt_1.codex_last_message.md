Re-review is complete for `doi__10.1038_s41467-023-42387-z`. I did not rerun bootstrap.

Current state is intentionally non-accepted: `review_status=blocked_missing_primary_material`, `publication_grade=false`, `validator_contract_passed=true`. The owner-2/4/6 repair artifacts retain 146 database-linked activity/toxicity rows, but all are marked database-snapshot evidence rather than primary-source verified because the local MOESM supplementary/source-data files are absent.

Fresh gate rerun evidence:
- Semantic gate: [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41467-023-42387-z.semantic_gate.json) failed expectedly, `pass_count=0/1`, `issue_count=2`: `review_status_not_publication_grade`, `publication_grade_not_true`.
- Publication QA: [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41467-023-42387-z.publication_quality.json) failed expectedly, `publication_grade_pass=false`, `activity_records=146`, `mechanism_claims=3`, `open_rework_targets=1`.

Remaining open targeted ticket is `rwk-20260503-missing-local-supplementary-source-data`, owner `worker-3`, `target_queue=material_extraction`. The unrecoverable gap records missing local `41467_2023_42387_MOESM1_ESM.pdf`, `MOESM5_ESM.xlsx`, and `MOESM6_ESM.xlsx`. I also validated the touched JSON/JSONL artifacts with `jq`; `git status` could not run because this directory is not a git repository.

