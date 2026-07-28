[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC 6538",
      "endpoint": "MIC",
      "value": "32 µg/ml",
      "peptide": "Bacteriocin Plantaricin LPL-1"
    },
    "verification_outcome": "value_match",
    "normalization_note": "strain_id_differs_value_same",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "S. aureus 6538",
      "col_header": "MIC (μg/mL)",
      "source_value": "32"
    },
    "short_reason": "Same MIC value for S. aureus 6538; source collection id differs from DB label."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Enterococcus faecalis",
      "endpoint": "MIC",
      "value": "32 µg/ml",
      "peptide": "Bacteriocin Plantaricin LPL-1"
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "E. faecalis",
      "col_header": "MIC (μg/mL)",
      "source_value": "32"
    },
    "short_reason": "Provided table reports Enterococcus faecalis MIC as 32 μg/mL."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "Lactiplantibacillus plantarum",
      "endpoint": "MIC",
      "value": "16 µg/ml",
      "peptide": "Bacteriocin Plantaricin LPL-1"
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "Lactobacillus plantarum S-35",
      "col_header": "MIC (μg/mL)",
      "source_value": "16"
    },
    "short_reason": "Provided table reports Lactobacillus plantarum MIC as 16 μg/mL."
  },
  {
    "assertion_index": 3,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC 6538",
      "endpoint": "MIC",
      "value": "32 µg/ml",
      "peptide": "Purification and Characterization of Plantaricin LPL-1, a Novel Class IIa Bacteriocin Produced by Lactobacillus plantarum LPL-1 Isolated From Fermented Fish."
    },
    "verification_outcome": "value_match",
    "normalization_note": "strain_id_differs_value_same",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "S. aureus 6538",
      "col_header": "MIC (μg/mL)",
      "source_value": "32"
    },
    "short_reason": "Same MIC value for S. aureus 6538; source collection id differs from DB label."
  },
  {
    "assertion_index": 4,
    "db_claimed": {
      "organism": "Enterococcus faecalis",
      "endpoint": "MIC",
      "value": "32 µg/ml",
      "peptide": "Purification and Characterization of Plantaricin LPL-1, a Novel Class IIa Bacteriocin Produced by Lactobacillus plantarum LPL-1 Isolated From Fermented Fish."
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "E. faecalis",
      "col_header": "MIC (μg/mL)",
      "source_value": "32"
    },
    "short_reason": "Provided table reports Enterococcus faecalis MIC as 32 μg/mL."
  },
  {
    "assertion_index": 5,
    "db_claimed": {
      "organism": "Lactiplantibacillus plantarum",
      "endpoint": "MIC",
      "value": "16 µg/ml",
      "peptide": "Purification and Characterization of Plantaricin LPL-1, a Novel Class IIa Bacteriocin Produced by Lactobacillus plantarum LPL-1 Isolated From Fermented Fish."
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "Lactobacillus plantarum S-35",
      "col_header": "MIC (μg/mL)",
      "source_value": "16"
    },
    "short_reason": "Provided table reports Lactobacillus plantarum MIC as 16 μg/mL."
  },
  {
    "assertion_index": 6,
    "db_claimed": {
      "organism": "Listeria monocytogenes NICPBP 54002[MIC = 16 microg/ml], Listeria monocytogenes ATCC 19113[MIC = 16 microg/ml], Listeria monocytogenes ATCC 19114[MIC = 16 microg/ml], Staphylococcus aureus ATCC 13565[MIC = 32 microg/ml], Staphylococcus aureus ATCC 6538[MIC = 32 microg/ml], Staphylococcus aureus CVCC 26112[MIC = 32 microg/ml], Enterococcus faecalis[MIC = 32 microg/ml], Lactobacillus delbrueckii subsp. lactis[MIC = 16 microg/ml], Lactiplantibacillus plantarum[MIC = 16 microg/ml], Lactobacillus delbrueckii subsp. bulgaricus[MIC = 16 microg/ml], Ligilactobacillus salivarius[MIC = 16 microg/ml], Lactococcus lactis MG1363[MIC = 16 microg/ml], Bacillus amyloliquefaciens[MIC = 32 microg/ml], Bacillus pumilus[MIC = 32 microg/ml], Escherichia coli DH5alpha, Escherichia coli BL21, Escherichia coli BW25113, Escherichia coli JM109, Saccharomyces cerevisiae, Pichia pastoris GS115",
      "endpoint": "text",
      "value": "Antibacterial, Antifungal",
      "peptide": "Bacteriocin Plantaricin LPL-1"
    },
    "verification_outcome": "value_mismatch",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 1,
      "row_label": "Saccharomyces cerevisiae",
      "col_header": "Activity (mm)",
      "source_value": "0"
    },
    "short_reason": "DB includes antifungal activity, but provided fungal row reports Activity (mm) as 0."
  }
]