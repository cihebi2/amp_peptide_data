Done for `PMC12022103`.

Files written/updated:
- [supplementary_evidence.json](/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12022103/work/supplementary_methods/supplementary_evidence.json)
- [supplementary_evidence.worker3.json](/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12022103/analysis/supplementary_evidence.worker3.json)
- [figure6_hemolysis_digitization.json](/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12022103/extracted/figure6_hemolysis_digitization.json)
- [figure6_digitization_repair_verification.worker3.json](/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12022103/work/supplementary_methods/figure6_digitization_repair_verification.worker3.json)
- [worker3_rework_response_contract_check.current.json](/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12022103/work/supplementary_methods/worker3_rework_response_contract_check.current.json)

Rework responses appended:
- [rework_responses.jsonl](/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12022103/rework/rework_responses.jsonl): fresh worker-3 rows at lines 23-25 for all three assigned tickets, all `repair_ready_for_adjudication`, `analysis_can_resume: true`.

Validation:
- JSON validity passed for required outputs.
- Figure 6 repair verification: 10 visible records, required null counts all zero.
- Single-paper packet gate: `rc=0`.
- Semantic gate: `rc=1`, issue count 2.
- Publication quality gate: `rc=2`, open rework target risk remains.

Status: worker-3 material lane is source-reviewed repair-ready for adjudication, with no remaining worker-3 blocker found. It is not publication-grade and not terminal; worker-6 still needs to re-adjudicate and close.