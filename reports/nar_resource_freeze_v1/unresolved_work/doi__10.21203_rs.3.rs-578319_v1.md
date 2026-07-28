# doi__10.21203_rs.3.rs-578319_v1 unresolved DBAASP review

## Scope

- Paper: `doi__10.21203_rs.3.rs-578319_v1`
- Target unresolved records: `DBAASP:DBAASPS_17498` and `DBAASP:DBAASPS_17499`
- Files reviewed: only this paper's `paper_packets/doi__10.21203_rs.3.rs-578319_v1/`, `papers/doi__10.21203_rs.3.rs-578319_v1/`, `rework_context/doi__10.21203_rs.3.rs-578319_v1/`, plus the merged corpus rows already referenced by the target final.

## Conclusion

The two DBAASP unresolved rows cannot be repaired from the current local primary/source packet. I did not edit `papers/doi__10.21203_rs.3.rs-578319_v1/final/database_record_verification.json` because the available primary evidence supports only a qualitative/range-level uperin 3.5 statement and does not provide the missing row-level Supplementary Table 5 mapping or exact monomer/dimer topology needed to upgrade either unresolved status.

## Row-level finding

| DBAASP record | Current final status | Database row evidence checked | Primary/source support found | Can repair now? |
| --- | --- | --- | --- | --- |
| `DBAASP:DBAASPS_17498` / `Uperin-3.5 [I13C]` | `unresolved_record` | `all_sequences.csv` has sequence `GVGDLIRKAVSVCKNIV`; `all_experimental_records.csv` row `135691` maps to `Micrococcus luteus` with no MIC value (`NA`). | Main PDF mentions uperin 3.5 I13C/S11C activity against `M. luteus`, gives only a 5-7 uM range and points exact values to Supplementary Table 5. | No. Source packet lacks the supplement needed to decide whether the database `NA` assay row is a true inactive/blank row, a mapping artifact, or an omitted value. |
| `DBAASP:DBAASPS_17499` / `Di - Uperin-3.5 [I13C]` | `unresolved_record` | `all_sequences.csv` has blank sequence, length `0`, type `multimer`; `all_experimental_records.csv` row `135692` maps MIC `7+/-0.3 uM` against `Micrococcus luteus`. | Main PDF supports uperin/I13C activity qualitatively and by range only; it does not expose Supplementary Table 5 or enough figure values to assign `7+/-0.3 uM` specifically to the dimer row. | No. The exact value exists in DBAASP rows, but the local primary source does not independently verify the row-level mapping. |

## Evidence checked

- `paper_packets/doi__10.21203_rs.3.rs-578319_v1/database/linked_literature_records.jsonl`: rows 18-19 link `DBAASPS_17498` and `DBAASPS_17499` to DOI `10.21203/rs.3.rs-578319/v1`.
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv`: lines 23830-23831 contain the two DBAASP sequence catalog rows.
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/all_experimental_records.csv`: lines 153594-153595 contain assay rows `135691` and `135692`.
- `paper_packets/doi__10.21203_rs.3.rs-578319_v1/extracted/pdf_text/landing-1.txt`: lines 677-692 provide the uperin 3.5/I13C/S11C main-text summary and defer exact values to Supplementary Table 5; lines 927-950 provide MIC/DTT methods.
- `paper_packets/doi__10.21203_rs.3.rs-578319_v1/extracted/pdf_text/landing-1.txt`: lines 1376-1379 list two named supplementary PDF downloads, but those files are not present as usable local PDFs.
- `paper_packets/doi__10.21203_rs.3.rs-578319_v1/extracted/supplementary_index.json` and `paper_packets/doi__10.21203_rs.3.rs-578319_v1/extracted/supplementary_text.jsonl`: only three `.bin` supplementary assets are indexed, with no parsed Supplementary Table 5.
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.21203_rs.3.rs-578319_v1/supplementary/landing-1.bin`, `landing-2.bin`, `landing-3.bin`: `file` identifies all three as HTML, not PDF/XLSX/archive source material.
- `paper_packets/doi__10.21203_rs.3.rs-578319_v1/raw/paper.xml` and `papers/doi__10.21203_rs.3.rs-578319_v1/source/paper.xml`: current XML is a Research Square RSS/browse surface, not usable article XML with table rows.
- `papers/doi__10.21203_rs.3.rs-578319_v1/work/review/quality_feedback.json`: existing worker review already records the same true-supplement and XML material gaps.
- `paper_packets/doi__10.21203_rs.3.rs-578319_v1/rework/rework_requests.jsonl`: ticket `rwk-source-gap-0002` remains the relevant material-extraction blocker for `SIEngerbergFK13Cys2021.7.pdf` and the validation PDF.

## Blocker

The true blocker is a material gap, not a JSON/schema issue: the local packet does not contain `SIEngerbergFK13Cys2021.7.pdf`, which is the cited supplement for Supplementary Table 5. Without that source, the primary material does not verify the exact DBAASP row mapping for the two uperin I13C rows. The main PDF is enough to preserve a cautious qualitative statement, but not enough to convert either unresolved record to `source_verified`, `sequence_modified_not_normalized`, or a more precise row-level status.

## Next step

Keep both DBAASP records unresolved unless a material-extraction pass recovers the true supplementary PDF or an equivalent primary-source table. If recovered, re-check Supplementary Table 5 against DBAASP assay rows `135691` and `135692`, then update only this paper's final database JSON with a source locator for the exact table/value mapping.
