# Pilot20 Mechanism Ontology Class QC

Generated at: `2026-06-22T09:03:46Z`

- Papers checked: `20`
- Paper source: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/packet_index_latest.csv`
- Mechanism files checked: `80`
- Files with non-standard classes: `13`
- Accepted files with non-standard classes: `0` / `64`
- Nonterminal files with non-standard classes: `13` / `16`

## Bad Classes By Final Decision

| final decision | files |
| --- | ---: |
| `blocked_missing_primary_material` | 9 |
| `needs_targeted_rework` | 4 |

## Bad Class Counts

| class | files |
| --- | ---: |
| `background_mechanism_context` | 4 |
| `immunomodulatory_cell_phenotype` | 4 |
| `indirect_mechanism_context` | 4 |
| `mechanism_context_pending_review` | 1 |
| `mechanism_hypothesis_context` | 4 |
| `phenotype_activity_context` | 4 |
| `phenotypic_synergy_context` | 4 |
| `structural_supporting_mechanism` | 4 |
| `supportive_activity_mechanism` | 4 |
| `toxicity_selectivity_context` | 4 |

## Files With Bad Classes

| paper | final decision | path | bad classes |
| --- | --- | --- | --- |
| `doi__10.1038_s41522-024-00637-y` | `blocked_missing_primary_material` | `paper_packets/doi__10.1038_s41522-024-00637-y/analysis/mechanism_evidence.json` | `background_mechanism_context;indirect_mechanism_context;phenotypic_synergy_context` |
| `doi__10.1038_s41522-024-00637-y` | `blocked_missing_primary_material` | `paper_packets/doi__10.1038_s41522-024-00637-y/final/mechanism_evidence.json` | `background_mechanism_context;indirect_mechanism_context;phenotypic_synergy_context` |
| `doi__10.1038_s41522-024-00637-y` | `blocked_missing_primary_material` | `papers/doi__10.1038_s41522-024-00637-y/final/mechanism_evidence.json` | `background_mechanism_context;indirect_mechanism_context;phenotypic_synergy_context` |
| `doi__10.1038_s41522-024-00637-y` | `blocked_missing_primary_material` | `papers/doi__10.1038_s41522-024-00637-y/final/mechanism_ontology_record.json` | `background_mechanism_context;indirect_mechanism_context;phenotypic_synergy_context` |
| `doi__10.1038_s41598-017-16784-6` | `blocked_missing_primary_material` | `papers/doi__10.1038_s41598-017-16784-6/final/mechanism_evidence.json` | `mechanism_context_pending_review` |
| `doi__10.21203_rs.3.rs-578319_v1` | `blocked_missing_primary_material` | `paper_packets/doi__10.21203_rs.3.rs-578319_v1/analysis/mechanism_evidence.json` | `structural_supporting_mechanism;supportive_activity_mechanism` |
| `doi__10.21203_rs.3.rs-578319_v1` | `blocked_missing_primary_material` | `paper_packets/doi__10.21203_rs.3.rs-578319_v1/final/mechanism_evidence.json` | `structural_supporting_mechanism;supportive_activity_mechanism` |
| `doi__10.21203_rs.3.rs-578319_v1` | `blocked_missing_primary_material` | `papers/doi__10.21203_rs.3.rs-578319_v1/final/mechanism_evidence.json` | `structural_supporting_mechanism;supportive_activity_mechanism` |
| `doi__10.21203_rs.3.rs-578319_v1` | `blocked_missing_primary_material` | `papers/doi__10.21203_rs.3.rs-578319_v1/final/mechanism_ontology_record.json` | `structural_supporting_mechanism;supportive_activity_mechanism` |
| `doi__10.2174_1381612822666161027120518` | `needs_targeted_rework` | `paper_packets/doi__10.2174_1381612822666161027120518/analysis/mechanism_evidence.json` | `immunomodulatory_cell_phenotype;mechanism_hypothesis_context;phenotype_activity_context;toxicity_selectivity_context` |
| `doi__10.2174_1381612822666161027120518` | `needs_targeted_rework` | `paper_packets/doi__10.2174_1381612822666161027120518/final/mechanism_evidence.json` | `immunomodulatory_cell_phenotype;mechanism_hypothesis_context;phenotype_activity_context;toxicity_selectivity_context` |
| `doi__10.2174_1381612822666161027120518` | `needs_targeted_rework` | `papers/doi__10.2174_1381612822666161027120518/final/mechanism_evidence.json` | `immunomodulatory_cell_phenotype;mechanism_hypothesis_context;phenotype_activity_context;toxicity_selectivity_context` |
| `doi__10.2174_1381612822666161027120518` | `needs_targeted_rework` | `papers/doi__10.2174_1381612822666161027120518/final/mechanism_ontology_record.json` | `immunomodulatory_cell_phenotype;mechanism_hypothesis_context;phenotype_activity_context;toxicity_selectivity_context` |
