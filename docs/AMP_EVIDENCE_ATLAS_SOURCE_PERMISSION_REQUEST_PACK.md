# AMP Evidence Atlas 来源授权请求包

时间戳：2026-07-28 18:18 CST

这些模板用于由项目负责人向来源数据库正式申请书面授权。AI、Atlas 项目或
多 Agent 一致意见均不能自行赋予第三方数据再分发权。

发送后必须把原始邮件、回复、日期、允许字段、允许用途、商业限制、署名文字和
撤销条件保存到：

`releases/amp_evidence_atlas_v1_0/governance/permissions/<database>/`

## 通用英文模板

**Subject:** Permission request for evidence-audit display in AMP Evidence Atlas

Dear **[database team/contact]**,

We are preparing AMP Evidence Atlas, an academic evidence-audit resource that
aligns selected antimicrobial-peptide database records with their cited primary
literature. The resource preserves audit status, experimental context, source
location, and unresolved conflicts.

We request written permission to publicly display and provide through a
read-only API the following fields derived from **[database/version/snapshot
date]**:

**[exact requested fields]**

The proposed scope excludes website code, full-text articles, figures, and
patent-origin records unless separately authorized. We will attribute
**[database name]**, link to the official resource, cite the requested
publication, retain any required license notice, and version the snapshot date.

Please confirm:

1. whether public display and API access are permitted;
2. whether bulk download is permitted;
3. whether commercial visitors are permitted to access the service;
4. the required citation/attribution text;
5. any fields or record classes that must be excluded;
6. whether a project-created license may cover only our original audit
   annotations while excluding your underlying data.

Until written permission is received, our public beta excludes copied
source-record fields from this database.

Sincerely,  
**[project owner, institution, email]**

## DBAASP 追加问题

请在通用模板后增加：

> The current DBAASP terms describe the data as public-domain information that
> may be freely distributed and copied, but the following visitor clause says
> that visitors must not otherwise distribute the data to anyone. Could you
> clarify in writing which clause governs a non-commercial academic evidence
> audit, public API display, and bulk download?

## 各库建议申请字段

| 数据库 | 申请字段 |
| --- | --- |
| APD6 | APD ID、记录名、序列/修饰表示、活动描述、机制描述、来源文献标识 |
| CAMP | CAMP ID、记录名、序列/修饰、活动/验证标签、来源文献标识；专利字段单独询问 |
| DBAASP | DBAASP ID、序列/修饰、assay endpoint/value/unit/target/conditions、文献标识 |
| DRAMP | 只在未来需要时申请 patent AMP；当前普通/临床数据按 CC BY 4.0 署名 |
| dbAMP | dbAMP ID、记录名、序列/修饰、活动标签、来源文献标识 |

## 当前替代方案

在书面回复到达前，公共网站/API 使用 field-level rights filter：

- 不公开来源库原始 ID、记录名、数据库值、单位、描述和逐行对照；
- 只公开项目原创聚合、审核计数、审计状态类别和自建 benchmark；
- DRAMP 专利 AMP 完全排除；
- 完整内部 v1.0 数据包保持 `public_release_ready=false`。

