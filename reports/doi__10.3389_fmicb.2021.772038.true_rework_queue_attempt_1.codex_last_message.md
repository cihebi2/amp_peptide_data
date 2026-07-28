已完成 `doi__10.3389_fmicb.2021.772038` 的单篇 re-review。

修复结果：
- worker-2：重写 activity/toxicity，当前为 `90` 条 source-located 活性记录：`70` 条 Table 2 MIC + `20` 条 Table 3 hemolysis，另保留 `3` 条 HEK293 定性 toxicity 记录。
- worker-4：重写 database audit，`59 source_verified`，`16 source_conflict`；HEK293 figure-only 精确值和 CAMP/dbAMP 名称/数值冲突被保留为 caution，没有抹平。
- worker-6：重写 final adjudication，状态为 `accepted_with_cautions`，`publication_grade: true`，`rework_targets: []`。
- 已追加 `paper_packets/doi__10.3389_fmicb.2021.772038/rework/rework_responses.jsonl`，关闭 `rwk-complete-test-0001`。
- `quality_feedback.json` 当前 `issue_count: 0`，无 `qc_failure_reasons`，无 `unrecoverable_material_gaps`。

验证：
- Semantic gate: `pass_count=1`, `fail_count=0`, `issue_count=0`
- Publication quality gate: `publication_grade_pass=true`, `risk_counts={}`
- Workflow/packet 当前 open tickets: `[]`

主要更新路径包括：
- `papers/doi__10.3389_fmicb.2021.772038/final/*`
- `papers/doi__10.3389_fmicb.2021.772038/work/review/quality_feedback.json`
- `paper_packets/doi__10.3389_fmicb.2021.772038/analysis/*`
- `paper_packets/doi__10.3389_fmicb.2021.772038/rework/rework_responses.jsonl`
- `reports/doi__10.3389_fmicb.2021.772038.semantic_gate.json`
- `reports/doi__10.3389_fmicb.2021.772038.publication_quality.json`

`git status` 无法运行：当前目录不是 git repository。

