[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "50% Hemolysis",
      "value": ">100",
      "peptide": ""
    },
    "verification_outcome": "value_mismatch",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 1,
      "row_label": "1-Pro6",
      "col_header": "HD10 / HD50",
      "source_value": "83 / >200"
    },
    "short_reason": "For row 1-Pro6, source HD10/HD50 is 83 / >200, not >100 for HD50."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Pseudomonas aeruginosa 198",
      "endpoint": "MIC",
      "value": "32",
      "peptide": ""
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "198 (MDR)",
      "col_header": "#11",
      "source_value": "32"
    },
    "short_reason": "Value 32 is in strain 198 under source #11, a different variant than the #10 row matching this record context."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "Pseudomonas aeruginosa LES400",
      "endpoint": "MIC",
      "value": "16",
      "peptide": ""
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "LES400 (MDR)",
      "col_header": "#11",
      "source_value": "16"
    },
    "short_reason": "Value 16 is in LES400 under source #11, a different variant than the #10 row matching this record context."
  },
  {
    "assertion_index": 3,
    "db_claimed": {
      "organism": "Pseudomonas aeruginosa H1027",
      "endpoint": "MIC",
      "value": "2",
      "peptide": ""
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "H1027 (MDR)",
      "col_header": "#11",
      "source_value": "2"
    },
    "short_reason": "Value 2 is in H1027 under source #11, a different variant than the #10 row matching this record context."
  },
  {
    "assertion_index": 4,
    "db_claimed": {
      "organism": "Pseudomonas aeruginosa H1030",
      "endpoint": "MIC",
      "value": "32",
      "peptide": ""
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "H1030 (MDR)",
      "col_header": "#11",
      "source_value": "32"
    },
    "short_reason": "Value 32 is in H1030 under source #11, a different variant than the #10 row matching this record context."
  },
  {
    "assertion_index": 5,
    "db_claimed": {
      "organism": "Enterobacter cloacae 218R",
      "endpoint": "MIC",
      "value": "32",
      "peptide": ""
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "218R Class C β-lactamase",
      "col_header": "#11",
      "source_value": "32"
    },
    "short_reason": "Value 32 is in 218R under source #11, a different variant than the #10 row matching this record context."
  },
  {
    "assertion_index": 6,
    "db_claimed": {
      "organism": "Escherichia coli ESBL 63103",
      "endpoint": "MIC",
      "value": "32",
      "peptide": ""
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "63103 (ESBL)",
      "col_header": "#11",
      "source_value": "32"
    },
    "short_reason": "Value 32 is in 63103 under source #11, a different variant than the #10 row matching this record context."
  },
  {
    "assertion_index": 7,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "10% Hemolysis",
      "value": "83",
      "peptide": ""
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "1-Pro6",
      "col_header": "HD10 / HD50",
      "source_value": "83 / >200"
    },
    "short_reason": "Source row 1-Pro6 reports HD10/HD50 as 83 / >200; HD10 matches 83."
  },
  {
    "assertion_index": 8,
    "db_claimed": {
      "organism": "Mouse fibroblasts NIH 3T3",
      "endpoint": "IC50",
      "value": "18",
      "peptide": ""
    },
    "verification_outcome": "endpoint_mismatch",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 1,
      "row_label": "1-Pro6",
      "col_header": "ID50 (μM)",
      "source_value": "18"
    },
    "short_reason": "DB labels IC50, but the source column header is ID50 (μM); value 18 is under ID50."
  },
  {
    "assertion_index": 9,
    "db_claimed": {
      "organism": "Bacillus subtilis ATCC 6633",
      "endpoint": "MIC",
      "value": "1.6",
      "peptide": ""
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "1-Pro6",
      "col_header": "B. subtilis (μM)",
      "source_value": "1.6"
    },
    "short_reason": "Source row 1-Pro6 has B. subtilis MIC value 1.6."
  },
  {
    "assertion_index": 10,
    "db_claimed": {
      "organism": "Escherichia coli ATCC 35218",
      "endpoint": "MIC",
      "value": "12.5",
      "peptide": ""
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "1-Pro6",
      "col_header": "E. coli (μM)",
      "source_value": "12.5"
    },
    "short_reason": "Source row 1-Pro6 has E. coli MIC value 12.5."
  },
  {
    "assertion_index": 11,
    "db_claimed": {
      "organism": "Pseudomonas aeruginosa H103",
      "endpoint": "MIC",
      "value": "8",
      "peptide": ""
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 2,
      "row_label": "H103 (wild type)",
      "col_header": "#10",
      "source_value": "8"
    },
    "short_reason": "Source table MIC row H103 has #10 value 8, matching the DB claim."
  }
]