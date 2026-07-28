Re-review completed for `doi__10.3390_pharmaceutics15082047`.

Updated worker-owned artifacts:
- Worker-2: rebuilt activity evidence to `195` source-backed rows: `150` Table 1 MIC rows plus `45` Table 2 MHC/MIC-GM/TI rows.
- Worker-4: re-audited `406` linked database rows: `332 source_verified`, `72 source_conflict`, `2 database_only_no_primary_source`.
- Worker-6: updated final adjudication to `accepted_with_cautions`, `publication_grade: true`, `rework_targets: []`, `qc_failure_reasons: []`, and resolved `rwk-complete-test-0001`.

Cautions preserved, not hidden:
- Figure-derived exact hemolysis/HaCaT percentages remain `source_conflict` where not tabulated in XML/PDF.
- Sequence strings are database-retained with Figure 1B locator context because exact sequences are not machine-readable XML table text.
- Supplement zip was opened; it contains figure-only PDF material, no structured activity tables.

Validation:
- Semantic gate: `publication_grade_pass_count=1/1`, `issue_count=0`.
- Publication-quality gate: `publication_grade_pass=true`, `risk_counts={}`.
- JSON validity check passed for `14` repaired/report artifacts.

