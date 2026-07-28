Done. Wrote:

[true_review_result.json](/root/work/抗菌肽/数据库/batch/4-team/reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0020__doi__10.1021_acschembio.1c00641/true_review_result.json)

[rework_tickets.jsonl](/root/work/抗菌肽/数据库/batch/4-team/reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0020__doi__10.1021_acschembio.1c00641/rework_tickets.jsonl)

Decision: `needs_targeted_rework`. VAL0108 is confirmed; VAL0104 preserves the DRAMP conflict but is tied to a repairable mechanism ontology defect: `mech-002` uses a non-standard `evidence_class`.

Validation run: JSON syntax OK, schema validation OK, JSONL parses, and the non-standard mechanism class was verified. I did not edit canonical `papers/<paper_id>/final/` artifacts. `git status` could not run because this directory is not recognized as a usable git repo from the shell.

