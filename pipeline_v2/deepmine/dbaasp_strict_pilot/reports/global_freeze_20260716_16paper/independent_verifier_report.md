# Independent Verifier Report - 16-Paper DBAASP Strict Pilot Freeze

Generated: 2026-07-16 16:18 CST  
Verifier: native `verifier` agent `019f69fb-8f09-7243-a72c-82549bc67954`  
Mode: read-only, independent artifact recomputation  
Verdict: **PASS**

## Accepted Claims

- The fresh acceptance set contains exactly 16 papers and all 16 are `accepted_with_cautions`, not `accepted_clean`.
- Direct final-list counts are 947 activity records, 210 toxicity records, and 79 mechanism claims.
- The current run sequences contain 96 worker reports and 96 globally unique Codex session IDs. Every current report is `codex exec`, `gpt-5.5`, `xhigh`, and return code 0; worker-6 is fresh after the latest upstream worker on every paper.
- All 64 configured paper/packet final mirror pairs exist and are byte-identical.
- Fresh global `status`, `verify`, and `audit-workers` executions return 0. Open rework tickets, review rework targets, hard findings, and publication risks are all zero.
- A recursive scan of all 16 final database-verification artifacts finds zero `authoritative_dbaasp_ingest_ready: true` values. Global authoritative-ready paper count is zero.
- `PMC12230126` independently satisfies 19 activity, 0 toxicity, 1 database audit, and 6 mechanism claims, including 5 direct-mechanism claims. Its 12 Fig. 5 A-F rows retain hierarchy/calibration/coordinates/uncertainty, its 2 Fig. 5G rows are present, the source sequence is 219 aa, the mature N-terminus is `LPPCVCTRDYR`, and disulfide evidence remains predicted/model-only.
- `PMC12230126` has complete top-level adjudication metadata in all three final layer artifacts, 4 byte-identical final mirrors, and exactly one currently valid terminal closure for each of 6 rework tickets.
- The recorded test run passes 84 tests; the recorded `py_compile` return code is 0.

## Evidence

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/fresh_acceptance_20260716_16paper/summary.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_16paper/status.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_16paper/verify.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_16paper/audit_workers.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_16paper/leader_contract_recheck.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/review/leader_ticket006_leader_rerun.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/review/leader_final_semantic_audit_20260716.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_16paper/unittest.stderr.log`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_16paper/py_compile.returncode`

## Residual Risks

- Six older final database-verification artifacts do not expose `authoritative_dbaasp_ingest_ready` at the top level; five contain no occurrence of the field. None contains a true value, and global status remains explicitly zero, so this is a schema-normalization risk rather than an acceptance failure.
- `PMC12230126` keeps two historical terminal-looking rows for ticket 001 in its append-only response log. Only one is valid under the current artifact/gate contract; consumers must not count raw `closed_repaired` strings without runtime validation.
- This freeze proves a sequential independent `codex exec` bridge. It is not a durable OMX team mailbox/ACK/supervisor production state.
- This freeze does not authorize RC2/portal ingestion and does not complete validation420, final human reduction, public hosting, API/download deployment, license/source-version review, or manuscript disclosure.
