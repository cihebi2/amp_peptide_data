# DBAASP Strict Pilot 15-Paper Independent Verification

Verified at: 2026-07-16 01:38 CST  
Verifier: native read-only `verifier` agent `019f66d3-36cd-73b3-9a05-3ae4ce4f2741`  
Verdict: **APPROVE**

## Scope

The verifier independently reopened the current manifest, final artifacts, packet mirrors, worker run reports, rework logs, gate outputs, and the raw supplementary DOCX for `PMC13031288`. It did not edit project files and did not accept controller return code 0 as scientific acceptance by itself.

## Batch Findings

- Manifest membership is 15 papers with 15 unique paper IDs. The paper sets in `status.json`, `verify.json`, `audit_workers.json`, and `fresh_acceptance_20260716/summary.json` agree; only ordering differs.
- Direct final-artifact recount is 928 activity records, 210 toxicity records, and 73 mechanism claims.
- Worker evidence contains 90 current run-sequence reports and 90 canonical `worker-1` through `worker-6` reports, with 90 globally unique Codex session IDs.
- All current workers used `codex exec`, `gpt-5.5`, and `xhigh`, returned 0, and have no missing references, stale stderr references, or newer unmerged aliases.
- Worker-6 freshness failures are zero: every worker-6 starts at or after the latest current upstream worker completion time.
- The packet, semantic, publication, and strict-worker gates all return 0. Packet hard findings, open rework tickets, rework targets, publication risks, and strict-worker hard findings are all zero.
- All 60 critical paper/packet final mirror pairs are byte-identical and SHA-256-identical: activity/toxicity, database verification, mechanism ontology, and review report for each of 15 papers.
- `authoritative_dbaasp_ingest_ready=false` for all 15 papers. Paper-level source-reviewed acceptance does not authorize release or portal ingestion.

## PMC13031288 Findings

- The final S2 matrix contains 360 activity plus 40 toxicity observations, matching 20 reported-repeat rows times 20 scalar columns.
- All 400 observations have a top-level `evidence_role`, an exact S2 value-cell locator, and a detail locator matching the primary locator. Direct non-table contract issues are zero.
- Exactly 120 nonduplicated S2 observations carry `xml:table-wrap:1` as the secondary main-text Table 1 aggregate locator.
- The raw S2 DOCX independently resolves rows 3 through 22 as 20 data rows with 22 cells per row, supporting `20 x 18 = 360` activity and `20 x 2 = 40` toxicity observations.
- Worker-4 has 7/7 nested source-verified records. `Hill_BB_C7176` resolves to `ATCDLLSPFKVGHAACALHCIALGRRGGWCDGRAVCNCRR` (length 40, S1 row 7 cell 1), and `Hill_SB_C1875` resolves to `GQGESRSLWKKIFKPVEKLGQRVRDAGIQGIAIAQQGANVLATVRGGPPQ` (length 50, S1 row 11 cell 1). Both were independently checked against raw S1 DOCX XML.
- The mechanism artifact contains six claims and exactly two direct-mechanism claims: PI uptake/permeability and BODIPY-TR-cadaverine competitive displacement against LPS/lipid A. The latter retains the caution that interaction evidence is not complete mode-of-action closure.
- All six rework requests have terminal `closed_repaired` adjudication, zero open tickets, and zero rework targets. Their packet, semantic, and publication closure evidence returns 0.

## Runtime And Scientific Boundary

This freeze proves a sequential independent `codex exec` bridge with strict source and adjudication contracts. It is not a durable OMX team mailbox/ACK/supervisor production state. It also does not complete validation420, final human reduction, public website/API/download deployment, license/source-version review, manuscript disclosure, or authoritative RC2/portal integration.

## Evidence Files

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716/status.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716/verify.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716/audit_workers.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716/leader_contract_recheck.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/fresh_acceptance_20260716/summary.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13031288_source_review_freeze_20260716.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13031288/work/activity_evidence/supplement_s2_expected_observation_contract.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13031288/final/database_record_verification.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13031288/final/mechanism_ontology_record.json`

