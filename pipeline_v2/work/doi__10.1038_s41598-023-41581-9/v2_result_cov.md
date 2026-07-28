[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "Hemolysis",
      "value": "0%",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Hemolysis data are figure-only here; no structured longform cell supports this comparison."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Human colon adenocarcinoma HCT 116",
      "endpoint": "",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "HCT 116 appears in IC50 tables, but the database assertion lacks peptide, endpoint, and value."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC BAA-41",
      "endpoint": "MBEC50",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "MBEC50 claim lacks a value/peptide, and no longform cell gives an MBEC50 endpoint."
  },
  {
    "assertion_index": 3,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "Hemolysis",
      "value": "25%",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Hemolysis data are figure-only here; no structured longform cell supports the 25% comparison."
  },
  {
    "assertion_index": 4,
    "db_claimed": {
      "organism": "Human colon adenocarcinoma HCT 116",
      "endpoint": "",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "HCT 116 appears in IC50 tables, but the database assertion lacks peptide, endpoint, and value."
  },
  {
    "assertion_index": 5,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC BAA-41",
      "endpoint": "MBEC50",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "MBEC50 claim lacks a value/peptide, and no longform cell gives an MBEC50 endpoint."
  },
  {
    "assertion_index": 6,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "Hemolysis",
      "value": "0%",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Hemolysis data are figure-only here; no structured longform cell supports this comparison."
  },
  {
    "assertion_index": 7,
    "db_claimed": {
      "organism": "Salmonella enterica subsp. enterica serovar Typhimurium ATCC 14028",
      "endpoint": "Inhibition",
      "value": "45.13±2%",
      "peptide": ""
    },
    "verification_outcome": "endpoint_mismatch",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 8,
      "row_label": "100",
      "col_header": "S. enterica",
      "source_value": "45.13 ± 2"
    },
    "short_reason": "Same value is in the biofilm eradication table; source endpoint is biofilm eradication %, not generic inhibition."
  },
  {
    "assertion_index": 8,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC BAA-41",
      "endpoint": "Inhibition",
      "value": "27.05±1.3%",
      "peptide": ""
    },
    "verification_outcome": "endpoint_mismatch",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 8,
      "row_label": "100",
      "col_header": "MRSA",
      "source_value": "27.05 ±1.3"
    },
    "short_reason": "Same value is in the biofilm eradication table; source endpoint is biofilm eradication %, not generic inhibition."
  },
  {
    "assertion_index": 9,
    "db_claimed": {
      "organism": "Human embryonic kidney HEK293 cells",
      "endpoint": "Cell death",
      "value": "<10%",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "HEK293 cell-death data are figure-only here; no structured longform cell supports the comparison."
  },
  {
    "assertion_index": 10,
    "db_claimed": {
      "organism": "Bacillus subtilis ATCC 11774",
      "endpoint": "MIC",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "B. subtilis MIC cells exist, but the database assertion lacks peptide and value, so no exact comparison is possible."
  },
  {
    "assertion_index": 11,
    "db_claimed": {
      "organism": "Bacillus subtilis ATCC 11774",
      "endpoint": "MBC",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "B. subtilis MBC cells exist, but the database assertion lacks peptide and value, so no exact comparison is possible."
  }
]