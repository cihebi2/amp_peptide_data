[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "Hemolysis",
      "value": "<5%",
      "peptide": "FP-CATH"
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 6,
      "row_label": "50 µg/mL",
      "col_header": "Hemolytic activity (%)",
      "source_value": "4.6"
    },
    "short_reason": "Source hemolytic activity is 4.6%, satisfying the DB claim of <5% hemolysis."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "Hemolysis",
      "value": "11%",
      "peptide": "FP-CATH"
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 6,
      "row_label": "100 µg/mL",
      "col_header": "Hemolytic activity (%)",
      "source_value": "10.5"
    },
    "short_reason": "Source hemolytic activity is 10.5%, consistent with DB's rounded 11% claim."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "Hemolysis",
      "value": "17%",
      "peptide": "FP-CATH"
    },
    "verification_outcome": "value_mismatch",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 6,
      "row_label": "200 µg/mL",
      "col_header": "Hemolytic activity (%)",
      "source_value": "16"
    },
    "short_reason": "Source cell reports 16% hemolytic activity, not the DB-claimed 17%."
  },
  {
    "assertion_index": 3,
    "db_claimed": {
      "organism": "Candida albicans SC5314",
      "endpoint": "MFC",
      "value": "",
      "peptide": "FP-CATH"
    },
    "verification_outcome": "endpoint_mismatch",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "C. albicans SC-5314",
      "col_header": "MBC (μg/mL) / FP-CATH",
      "source_value": "50"
    },
    "short_reason": "DB claims MFC, but source header reports this FP-CATH value under MBC."
  },
  {
    "assertion_index": 4,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "Hemolysis",
      "value": "<5%",
      "peptide": "Identification of a Novel Cathelicidin from the Deinagkistrodon acutus Genome with Antibacterial Activity by Multiple Mechanisms."
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB peptide field is a paper title, not a source peptide row or column; identity cannot be anchored."
  },
  {
    "assertion_index": 5,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "Hemolysis",
      "value": "11%",
      "peptide": "Identification of a Novel Cathelicidin from the Deinagkistrodon acutus Genome with Antibacterial Activity by Multiple Mechanisms."
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB peptide field is a paper title, not a source peptide row or column; identity cannot be anchored."
  },
  {
    "assertion_index": 6,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "Hemolysis",
      "value": "17%",
      "peptide": "Identification of a Novel Cathelicidin from the Deinagkistrodon acutus Genome with Antibacterial Activity by Multiple Mechanisms."
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB peptide field is a paper title, not a source peptide row or column; identity cannot be anchored."
  },
  {
    "assertion_index": 7,
    "db_claimed": {
      "organism": "Candida albicans SC5314",
      "endpoint": "MFC",
      "value": "",
      "peptide": "Identification of a Novel Cathelicidin from the Deinagkistrodon acutus Genome with Antibacterial Activity by Multiple Mechanisms."
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB peptide field is a paper title, not a source peptide row or column; identity cannot be anchored."
  }
]