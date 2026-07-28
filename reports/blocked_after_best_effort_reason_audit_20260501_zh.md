# 50 篇队列中 11 篇 `blocked_after_best_effort` 逐篇原因汇总

生成日期：2026-05-01  
来源聚合：`reports/true_rework_queue_50_aggregate_progress_20260501.json`  
机器可读明细：`reports/blocked_after_best_effort_reason_audit_20260501.json`

## 总览

- 本轮 50 篇真实复审队列：39 篇 `accepted_after_rework`，11 篇 `blocked_after_best_effort`。
- `blocked_after_best_effort` 是受控的非接受状态；不能等同于 publication-grade 或语义通过。
- 11 篇 blocked 的主类分布：`worker_timeout_or_overbroad_prompt` 5 篇，`activity_table_extraction_gap` 3 篇，`missing_external_supplement` 2 篇，`figure_chart_values_unrecoverable` 1 篇。
- 5 篇 timeout 更像流程/提示词/任务切片问题，不应直接解释为原始材料真实缺失。

## 逐篇原因

| Paper | 尝试次数 | 阻断分类 | 具体原因 | 当前处置 | 可优化点 |
| --- | ---: | --- | --- | --- | --- |
| `doi__10.1002_cmdc.202200291` | 1 | `worker_timeout_or_overbroad_prompt` | owner Codex worker 900 秒超时；控制器按 watchdog 规则写入 `codex_worker_timeout` 并前进。 | 保持非接受，重新投递为更窄 owner 任务。 | 把整篇 worker-6 复审拆成 worker-2/3/4/5/6 子提示词；增加 heartbeat 和部分 stdout/stderr 保留。 |
| `doi__10.1007_s00018-022-04440-w` | 1 | `worker_timeout_or_overbroad_prompt` | owner Codex worker 900 秒超时；同时 gate 仍提示 activity rows 缺失和 worker-6 source-review 未完成。 | 保持非接受，优先 worker-2 活性表格与 worker-6 adjudication 分开重跑。 | timeout 后不要再用宽提示词重试；先跑 worker-2 表格抽取，再交 worker-6。 |
| `doi__10.1007_s00253-020-10685-x` | 1 | `worker_timeout_or_overbroad_prompt` | owner Codex worker 900 秒超时；QC 同时指出活动表格 target/entity/value 行未安全解析。 | 保持非接受，重试前先缩窄到 worker-2 活性表格解析。 | 增强 worker-2 对 MIC/MBC、菌株矩阵、target/entity/value 布局的解析；失败时输出 table-shape JSON 给人工/视觉 fallback。 |
| `doi__10.1007_s10989-015-9494-4` | 1 | `worker_timeout_or_overbroad_prompt` | owner Codex worker 900 秒超时；已有问题还包括 activity MIC matrix 未 source-reviewed、mechanism artifact 仍含框架化待审说明。 | 保持非接受，分别打回 worker-2 活性矩阵和 worker-5 机制本体。 | worker-5 产物进入 worker-6 前要拒绝 framework-note/scaffold；worker-2 需要 source-located MIC matrix。 |
| `doi__10.1007_s12602-018-9501-0` | 1 | `worker_timeout_or_overbroad_prompt` | owner Codex worker 900 秒超时；QC 仍有 database conflict adjudication 和 activity table rework。 | 保持非接受，按 worker-2 与 worker-4/6 拆分复审。 | 对 source_conflict/database-only rows 做独立 worker-4 包；避免 worker-6 一次性吞掉全部 unresolved 项。 |
| `doi__10.1002_cbic.202100609` | 5 | `figure_chart_values_unrecoverable` | 本地 primary material 只有 Figure 4 柱状图、图注和方法文字；没有结构化表格或嵌入数据支持 HepG2/HEK293 精确百分比。 | 保留数据库精确百分比为 `source_conflict`，不伪造 exact values；整篇保持 blocked。 | 增加受控 chart digitization/OCR lane；若无可验证数字来源，则允许部分证据 accepted-with-conflict，但 figure-only exact value 不升格。 |
| `doi__10.1007_s12602-022-10036-4` | 5 | `missing_external_supplement` | 本地 packet、source、landed assets、supplementary index/tables/text/archive 均未找到真正的 Springer XLSX/DOCX；`landing-*.bin` 是 HTML 页面，未包含可解析 Table S5。 | 标记 external source needed；DBAASP antibiofilm exact values 保持 source_conflict，整篇 blocked。 | 增加 landing-page resolver：识别 HTML 伪装资产、抽取 MOESM 链接并下载/入库；无法获得时早停，不重复 worker loop。 |
| `doi__10.1016_j.antiviral.2005.10.005` | 5 | `activity_table_extraction_gap` | 活性表格未能安全转成 target/entity/value rows；没有 parser-supported activity/toxicity rows，5 次后仍不满足 gate。 | 保持非接受，打回 worker-2 专门处理 antiviral 活性表格。 | 增强 peptide/virus IC50、抗病毒 endpoint、复合 target 布局解析；失败时生成结构化表格形态供人工/vision lane。 |
| `doi__10.1016_j.antiviral.2008.10.001` | 5 | `activity_table_extraction_gap` | 无 parser-supported activity/toxicity rows；worker-6 source-review 和 database conflict adjudication 仍未闭合。 | 保持非接受，先补 worker-2 活性记录，再交 worker-4/6。 | 为 antiviral 论文增加专门 activity schema；避免因 parser 不支持而进入 5 次宽泛复审。 |
| `doi__10.1016_j.apsb.2021.07.026` | 5 | `activity_table_extraction_gap` | 无 parser-supported activity/toxicity rows；5 次 bounded rework 后仍达到 `bounded_rework_limit_reached`。 | 保持非接受，进入 worker-2 表格解析专项 backlog。 | 补 APSB 表格样式解析和 fallback；把 parser gap 与真实材料缺失分开记录。 |
| `doi__10.1007_s00018-020-03755-w` | 5 | `missing_external_supplement` | 本地只有 Springer HTML landing pages；HTML 指向 `18_2020_3755_MOESM1_ESM.docx`，但 DOCX 不在 packet/source/landed/downloaded/merged-output 中。 | 标记 missing primary supplementary material；worker-6 不得 publication-grade accept。 | 增加 MOESM DOCX 解析/下载/staging；若下载失败，生成 `external_source_needed` ticket 并跳过重复复审。 |

## 能做优化的地方

1. **P0：timeout 不等于材料缺失。** 保留 watchdog，但 timeout 后应自动转成窄 owner retry：worker-2 表格、worker-3 补充材料、worker-4 数据库冲突、worker-5 机制、worker-6 终审。
2. **P0：提示词切片。** `CODEX_REVIEW_PROMPT.md` 继续作为总上下文，但控制器要按失败 codes 生成 owner-specific prompts，避免一个新 Codex CLI 同时处理整篇所有问题导致超时。
3. **P1：worker-2 表格解析增强。** 覆盖 antiviral IC50/EC50/CC50/SI、MIC/MBC 矩阵、antibiofilm 百分比、target/entity/value 多层表头；parser 失败时输出 table-shape JSON，而不是只写 no rows。
4. **P1：补充材料 landing resolver。** 自动识别 `.bin`/`.xlsx`/`.zip` 实际是 HTML 的情况，抽取 Springer MOESM 真实链接，下载或明确 `external_source_needed`。
5. **P1：figure-only 数字策略。** 增加受控图表数字化/OCR lane；没有可验证来源时，保留 `source_conflict`，不要为了通过 gate 编造精确值。
6. **P1：worker-5 scaffold 拦截。** 机制本体进入 worker-6 前必须是 source-located 机制类或 explicit unknown，不能携带 framework-note/pending-review 文本。
7. **P2：并行汇总自动化。** 对 4 路 lane summary、pre-split results、after-worker gate file count 自动合并，输出唯一 aggregate，避免人工汇总造成状态漂移。

## 证据文件

- 逐篇机器可读原因：`reports/blocked_after_best_effort_reason_audit_20260501.json`
- 英文审计报告：`reports/blocked_after_best_effort_reason_audit_20260501.md`
- 50 篇 aggregate：`reports/true_rework_queue_50_aggregate_progress_20260501.json`
