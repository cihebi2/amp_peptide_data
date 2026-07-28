# Independent verifier report — 18-paper strict freeze

- Verified at: 2026-07-26 CST
- Scope: `fresh_acceptance_20260726_18paper/` and `global_freeze_20260726_18paper/`
- Verdict: **FAIL**
- Workspace modified by verifier: no

## Checks that passed

- Immutable snapshot contains 18 unique paper IDs and matches the saved acceptance, status, verify, audit, and leader paper sets.
- Snapshot SHA256 matches the leader record: `cc087699b62fe62d8ce9e8cf90c8cc84483489aee6d9d062e0ed0e7d7bee11f0`.
- The rolling live manifest contains one later paper, `PMC11956232`; its first 18 entries match the frozen snapshot.
- Fresh acceptance reports 18/18 ready, zero open tickets, and zero rework targets.
- Direct recount of canonical finals gives 1,231 activity, 210 toxicity, 164 database-audit, and 89 mechanism records.
- Current selected evidence has 108 worker reports and 108 globally unique sessions; all are exact `codex exec`, `gpt-5.5/xhigh`, and return code 0.
- Worker-6 freshness passes at available one-second timestamp precision.
- All 72 canonical paper/packet final pairs are byte-identical and their current hashes match the leader report.
- Packet, semantic, and publication gates rerun against the 18-paper snapshot return 0 with zero hard findings.
- `PMC11905587`'s executable Layer-2 contract reruns as 9/9.
- Independent regression rerun passes 86 tests; `py_compile` passes for all three targets.

## Blocking findings

### F1 — Recursive authority boundary is false

Four boolean `authoritative_dbaasp_ingest_ready=true` values remain in the current worker-4 artifacts for `PMC12230126`, despite zero linked authoritative rows:

- `papers/PMC12230126/work/database_record_audit/record_identity_audit.json`
- `packets/PMC12230126/analysis/database_record_audit.worker4.json`

Each file contains two contradictory true values. Canonical finals are false, but the broad claim that all strict-pilot artifacts preserve the false authority boundary is not true. Current gates inspect final/top-level state and miss these nested values.

### F2 — `PMC11905587` 9/9 contract misses semantic conflicts

1. Five activity rows contain a structured inoculum value while also listing `inoculum` under an unreported/not-structured field list.
2. The final caution preserves the 31.25 versus 3.125/6.25 dilution conflict, but does not preserve the separate method maximum 1,000 versus Table 1 footnote maximum 100 µg/mL conflict.

Therefore the mechanical 9/9 contract is insufficient for complete field-level semantic acceptance.

### F3 — Locator counts are inconsistent

For `PMC13013390`, the frozen/live packet-manifest entry reports 179 locators while `locators/locator_index.json` reports 408. Across the 18 papers, manifest entries total 3,009 and current locator indexes total 3,238, a difference of 229. Gates use the current index but do not enforce cross-manifest equality.

### F4 — Extraction-error counts are inconsistent

For `PMC11531597`, `extraction_status.json` says zero errors while `extraction_errors.jsonl` contains two nonblocking PaddleOCR failures. Packet checking sees two errors, but the snapshot/status entry retains zero.

### F5 — Freeze chronology metadata is insufficient

- Snapshot validation time, actual snapshot-write time, and Candidate 19 append time are different but were previously conflated.
- `leader_contract_recheck.json` was amended without an `amended_at` field.
- Saved `verify.json` points to the mutable live manifest path rather than the immutable snapshot/hash.

The paper-set binding is adequate; the chronology/provenance binding is not yet strict enough.

## Required disposition

The 18-paper freeze must remain nonterminal until:

1. the recursive authority contradiction is repaired and gated;
2. `PMC11905587` is repaired under an expanded semantic contract and freshly adjudicated;
3. locator/error-count consistency is refreshed and enforced;
4. freeze timestamps and immutable-manifest/hash bindings are explicit;
5. all affected gates and an independent verifier rerun return PASS.

