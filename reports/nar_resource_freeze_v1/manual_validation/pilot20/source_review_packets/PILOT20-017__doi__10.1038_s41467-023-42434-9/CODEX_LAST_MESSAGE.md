Wrote the review result here: [true_review_result.json](/root/work/抗菌肽/数据库/batch/4-team/reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-017__doi__10.1038_s41467-023-42434-9/true_review_result.json)

Decision: `needs_targeted_rework`. The sampled APD6/AP03779 row is correctly preserved as `database_only_no_primary_source`, and AMP #15 Table 10 activity/toxicity rows are source-backed. The rework is for the paper-level mechanism artifact: three claims use non-canonical `evidence_class` values outside the required ontology. I also wrote [rework_ticket.json](/root/work/抗菌肽/数据库/batch/4-team/reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-017__doi__10.1038_s41467-023-42434-9/rework_ticket.json).

Validation: JSON syntax passed with `jq`; required fields/enums/consts/top-level types passed a manual schema check. The installed `jsonschema` library is too old for Draft 2020-12, so I could not use it directly.

