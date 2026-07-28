Done for `doi__10.3892_etm.2017.5631`.

I kept this to the owned worker-2/4/6 layers and did not rerun the initial bootstrap. The repaired state now has 44 MIC activity rows, 110 database audits (`108 source_verified`, `2 source_conflict`), 3 bounded mechanism claims, `quality_feedback.issue_count=0`, and `rwk-complete-test-0001` closed in `rework_responses.jsonl`.

Updated/verified key surfaces:
- `paper_packets/doi__10.3892_etm.2017.5631/rework/rework_responses.jsonl`
- `paper_packets/doi__10.3892_etm.2017.5631/packet_manifest.json`
- `reports/doi__10.3892_etm.2017.5631.complete_message_test_report.json`
- final/analysis/work artifacts already repaired for activity, database, mechanism, adjudication, and quality feedback

Gate evidence:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication gate: `publication_grade_pass=true`, `activity_records=44`, `mechanism_claims=3`

Status is `accepted_with_cautions`, not “clean without caveats”: the preserved cautions are the 2 database conflicts, no local toxicity/hemolysis assay, non-tabulated figure curve values, and non-data supplementary landing assets. I used memory only for the layer-separation/anti-overclaim convention; all paper-specific evidence and gates were refreshed from local files in this turn.

