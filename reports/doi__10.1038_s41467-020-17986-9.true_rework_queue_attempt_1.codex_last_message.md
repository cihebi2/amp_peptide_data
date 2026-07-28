Re-reviewed and repaired `doi__10.1038_s41467-020-17986-9`.

I added 17 source-reviewed activity/toxicity rows from the local PDF/XML Figure 1/prose, updated database adjudication to `30 source_verified / 20 source_conflict`, preserved DRAMP/CAMP/dbAMP conflicts as cautions, closed the prior rework target, and appended gate evidence to `rework_responses.jsonl`.

Final validation:
- Semantic gate: pass count `1`, fail count `0`, no issue codes.
- Publication-quality gate: `publication_grade_pass: true`, no risks/issues.
- Status: `accepted_with_cautions`.

Remaining cautions: local MOESM4 source-data RAR is not present; DRAMP29177 has P9R MERS-CoV IC50 `22 ug/ml` conflicting with primary Fig. 1c `2.2 ug/ml`; mixed-reference aggregate database rows remain `source_conflict`.

DONE doi__10.1038_s41467-020-17986-9 accepted_with_cautions