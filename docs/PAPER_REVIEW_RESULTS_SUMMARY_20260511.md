# Batch 4-Team 当前论文审查结果统计

生成时间：2026-05-11
数据来源：`reports/all_reviewed_papers_aggregate_latest.json`、`reports/all_reviewed_papers_aggregate_latest.csv`、各 `reports/true_rework_queue_*_lane*_latest.json`、已存在的 full artifact audit 与 accepted sample audit 报告。

本统计是队列终态与收尾审计的综合快照，不是“所有论文均 publication-grade clean”的声明。`accepted_after_rework` 代表队列 accepted；blocked、初始化失败、infra retry 耗尽、source gap 等必须继续保留并单独处理。

## 1. 总览

| 指标 | 数量 |
| --- | ---: |
| lane summary 文件 | 98 |
| run 数 | 11 |
| lane result 原始记录 | 1540 |
| 去重论文数 | 1472 |
| 重复审查论文数 | 66 |
| `accepted_after_rework` | 1326 |
| 非 accepted | 146 |
| `blocked_after_best_effort` | 144 |
| `initial_queue_failed` / 初始化失败 | 2 |

终态分布：

| terminal_status | 数量 |
| --- | ---: |
| `accepted_after_rework` | 1326 |
| `blocked_after_best_effort` | 144 |
| `initial_queue_failed` | 2 |

## 2. 按 run 统计

| run | 去重论文数 | lanes | accepted | blocked | initial failed | post-run 审计状态 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `queue_next500_1800` | 500 | 10 | 425 | 75 | 0 | 早期队列，无完整 post-run latest |
| `next200_10lane_20260505T152139Z` | 200 | 10 | 189 | 11 | 0 | 早期队列，无完整 post-run latest |
| `queue_next100_1800` | 100 | 5 | 81 | 19 | 0 | 早期队列，无完整 post-run latest |
| `queue100_obtainable` | 68 | 5 | 52 | 15 | 1 | 早期队列，无完整 post-run latest |
| `queue100_timeout1800` | 32 | 5 | 26 | 6 | 0 | 早期队列，无完整 post-run latest |
| `next100_10lane_20260506T153312Z` | 100 | 10 | 97 | 3 | 0 | 早期队列，无完整 post-run latest |
| `next100_10lane_20260507T144551Z` | 100 | 10 | 96 | 4 | 0 | full artifact audit `issue_count=0` |
| `next100_10lane_20260508T121022Z` | 100 | 10 | 98 | 2 | 0 | full artifact audit `0`; accepted sample audit `67/67` 通过; semantic `98/2` |
| `next100_10lane_20260509T075436Z` | 100 | 10 | 99 | 0 | 1 | full artifact audit `0`; accepted sample audit `57/57` 通过; semantic `99/1` |
| `next100_10lane_20260509T154247Z` | 100 | 10 | 98 | 2 | 0 | full artifact audit `0`; accepted sample audit `52/52` 通过; semantic `98/2` |
| `next100_10lane_20260510T160219Z` | 72 | 10 | 65 | 7 | 0 | full artifact audit `0`; accepted sample audit `54/54` 通过; semantic `65/7` |

说明：最近 4 个完整 post-run sample audit 的 accepted 样本共 `230/230` 通过，但这只证明 accepted 样本审计通过；不覆盖所有早期 accepted，也不改变 blocked 论文状态。

## 3. blocked / 未通过原因

| result_status | 数量 | 含义 |
| --- | ---: | --- |
| `blocked_figure_chart_value_gap` | 36 | 图/曲线精确值无法从本地材料安全恢复 |
| `blocked_watchdog_timeout_retryable` | 27 | watchdog 超时，可单独 retry |
| `infrastructure_codex_worker_retry_exhausted` | 22 | Codex/API/worker 非零退出，重试耗尽 |
| `blocked_missing_external_supplement` | 21 | 缺外部补充材料 |
| `blocked_activity_table_extraction_gap` | 17 | activity/table 结构解析不安全 |
| `blocked_after_best_effort` | 15 | 早期结果中未细分的 best-effort blocked |
| `blocked_rework_cap_unresolved` | 6 | 5 次打回后仍未通过 |
| `infrastructure_initial_queue_failed` | 1 | 初始化基础设施失败 |
| `initial_queue_failed` | 1 | 初始化失败 |

推荐后续处理分组：

| 后续动作 | 数量 |
| --- | ---: |
| `defer_to_infrastructure_recovery_queue` | 12 |
| `retry_only_after_source_staging` | 2 |
| `retry_only_with_digitization_or_external_source` | 10 |
| `retry_only_with_more_specific_owner_context` | 4 |
| `retry_with_worker2_table_shape_or_manual_vision_fallback` | 2 |
| `unknown` | 116 |

`unknown` 主要来自早期队列，尚未使用后续细分状态字段。若要继续修复，应先对这 116 篇按当前 refined classifier 重新归类。

## 4. blocked 示例

| 类型 | 示例 paper_id |
| --- | --- |
| `blocked_activity_table_extraction_gap` | `doi__10.7150_ijbs.76148`, `doi__10.1371_journal.pone.0110809`, `doi__10.1016_j.isci.2021.102480`, `doi__10.1021_acs.jmedchem.1c00477`, `doi__10.1021_acs.jmedchem.9b01078` |
| `blocked_figure_chart_value_gap` | `doi__10.3389_fmicb.2021.678330`, `doi__10.3390_antibiotics11081080`, `doi__10.3390_antibiotics11101285`, `doi__10.3390_antibiotics8010031`, `doi__10.3390_biom10071014` |
| `blocked_missing_external_supplement` | `doi__10.3389_fmicb.2021.747760`, `doi__10.3389_fphar.2024.1334419`, `doi__10.1007_s00018-020-03755-w`, `doi__10.1038_msb4100049`, `doi__10.1038_s41598-017-16784-6` |
| `blocked_rework_cap_unresolved` | `doi__10.3389_fmicb.2019.02190`, `doi__10.3390_molecules25020257`, `doi__10.3390_pharmaceutics14040693`, `doi__10.7717_peerj.10176`, `doi__10.1038_s41598-024-53662-4` |
| `blocked_watchdog_timeout_retryable` | `doi__10.1016_j.cell.2024.07.027`, `doi__10.1021_acs.jmedchem.2c01469`, `doi__10.1021_acsinfecdis.9b00157`, `doi__10.1038_s41467-017-00419-5`, `doi__10.1038_s41467-018-03746-3` |
| `infrastructure_codex_worker_retry_exhausted` | `doi__10.3390_ijms222111869`, `doi__10.3390_v11010031`, `doi__10.3390_v11010056`, `doi__10.3390_v11070609`, `doi__10.3390_v13071246` |
| 初始化失败 | `doi__10.1055_s-0029-1185675`, `doi__10.1016_s0140-6736(04)15788-7` |

## 5. artifact / sample audit 状态

已发现的 full artifact audit latest：

| run | paper_count | issue_count | papers_with_issues |
| --- | ---: | ---: | ---: |
| `next100_10lane_20260507T144551Z` | 100 | 0 | 未记录 |
| `next100_10lane_20260508T121022Z` | 100 | 0 | 0 |
| `next100_10lane_20260509T075436Z` | 100 | 0 | 0 |
| `next100_10lane_20260509T154247Z` | 100 | 0 | 0 |
| `next100_10lane_20260510T160219Z` | 72 | 0 | 0 |

已发现的 accepted sample audit combined：

| run | sample_count | passed | failed | issue_counts |
| --- | ---: | ---: | ---: | --- |
| `next100_10lane_20260508T121022Z` | 67 | 67 | 0 | `{}` |
| `next100_10lane_20260509T075436Z` | 57 | 57 | 0 | `{}` |
| `next100_10lane_20260509T154247Z` | 52 | 52 | 0 | `{}` |
| `next100_10lane_20260510T160219Z` | 54 | 54 | 0 | `{}` |

## 6. final review 粗查

基于去重 `1472` 篇的 `papers/<paper_id>/final/review_report.json` 粗查：

| 指标 | 数量 |
| --- | ---: |
| final review 缺失 | 1 |
| `publication_grade=true` | 1344 |
| `publication_grade=false` | 127 |
| `quality_feedback.issue_count` 非 0 | 127 |
| reconciled open ticket 非空 | 118 |

解释：这里的 open ticket / issue_count 大多集中在 blocked 或早期未做完整 closure repair 的论文。它们不应污染已做 post-run closure 的 accepted 样本结论，但说明全局仍有后续清理和分类工作。

## 7. 结论

当前目录内可追踪、去重后的审查论文共有 `1472` 篇：

- `1326` 篇已达到队列级 `accepted_after_rework`。
- `146` 篇仍需后续处理或保留 blocked：主要是图表精确值、外部补充材料、parser/table extraction、watchdog/infra、rework cap unresolved、初始化失败。
- 最近完成 post-run closure 的 accepted 集合质量较稳定：full artifact audit 为 0 issue，accepted sample audit 为 0 failure。
- 全局不能宣称 `1472/1472 publication-grade clean`；正确说法是：`1326` 篇队列级 accepted，其中已做 post-run closure 的近批次 accepted 样本通过；`146` 篇仍是明确 blocked/failed 后续队列。

## 8. 输出文件

- 明细 JSON：`reports/all_reviewed_papers_aggregate_latest.json`
- 明细 CSV：`reports/all_reviewed_papers_aggregate_latest.csv`
- 快照 JSON：`reports/all_reviewed_papers_aggregate_20260511T015157Z.json`
- 快照 CSV：`reports/all_reviewed_papers_aggregate_20260511T015157Z.csv`
