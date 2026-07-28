# AMP Evidence Atlas v1.0 分母与版本合同

时间戳：2026-07-28 17:41 CST  
正式数据版本：`amp-evidence-atlas-v1.0`

## 1. 唯一冻结分母

论文、下载包和总体审计分析使用以下完整冻结口径：

| 指标 | 数量 |
| --- | ---: |
| 具有 final artifact 的论文 | 1,471 |
| public-v1 候选论文 | 1,374 |
| 排除或未达到 publication-grade 的论文 | 97 |
| 数据库审计行 | 139,259 |
| `source_verified` | 95,941 |
| 非 `source_verified` | 43,318 |
| 活性/毒性观察 | 115,184 |
| 机制证据主张 | 4,774 |

不可变负载由
`releases/amp_evidence_atlas_v1_0/payload_checksums.txt` 定义，其清单
SHA-256 为：

`cb08afed8f53ae74591ca354a7d331541624a60d5019549e33c44bbd4ee99376`

## 2. 公共 Portal 投影

Portal 只展示 `public_v1_included=true` 的记录，所以不能把 Portal 行数
冒充完整冻结分母：

| 指标 | Portal 数量 |
| --- | ---: |
| 论文 | 1,374 |
| 活性/毒性观察 | 108,761 |
| 数据库审计行 | 128,976 |
| `source_conflict` | 28,813 |
| 机制证据主张 | 4,508 |

Portal 默认不再载入 `machine_extracted` 或 `dual_model_recovered` 增量。
如为研究目的显式载入增量，必须使用单独数据库和版本名，不得称为 v1.0。

## 3. validation420

validation420 是准确性评价样本，不是发布数据增量：

- 420 个分层样本行；
- 224 篇独立论文；
- 当前有39篇有效结果、覆盖114行；
- 暂待人工核对185篇、306行。

AI worker 一致、自动 gate 通过和 Codex 审查结果均不作为人工金标准。

## 4. 后续严格论文队列

2026-07-26 后启动的严格 DBAASP 候选审查属于 post-v1.0 增量。它们在
下一版本经过完整准入、人工验证与发布审批前，不得改变本合同分母。

## 5. 解释规则

1. `source_conflict` 是数据库主张与当前原文重构无法调和的审计状态，
   不自动等同于法律或事实意义上的“数据库错误”。
2. 差异类别为多标签，不能相加为唯一记录数。
3. 数据库分母是进入论文级审计的记录，不是五个来源数据库的原始全量。
4. 论文正文、网站、API、下载和 benchmark 必须明确自己使用的是
   “完整冻结分母”还是“公共 Portal 投影”。
5. 历史 RC1/RC2 数字只可用于版本沿革，不可与 v1.0 混合报告。

## 6. 权威机器可读文件

- 数据冻结锁：
  `releases/amp_evidence_atlas_v1_0/DATA_FREEZE_LOCK.json`
- 完整发布清单：
  `releases/amp_evidence_atlas_v1_0/release_manifest.json`
- Portal 投影：
  `portal/release_profile_v1_0.json`
