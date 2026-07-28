[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "SK-MEL-28; G-361; HaCaT",
      "endpoint": "IC50; toxicity",
      "value": "SK-MEL-28 IC50=50.8 µM; G-361 IC50=57.8 µM; HaCaT not induce toxicity",
      "peptide": "PCC-1 / KKRKKKAFALKFVVDLI"
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "SK-MEL-28",
      "col_header": "IC50(uM)",
      "source_value": "50.8"
    },
    "short_reason": "Provided cells contain matching IC50 values for SK-MEL-28 50.8 and G361 57.8 under IC50(uM)."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "SK-MEL-28 and G361",
      "endpoint": "mechanism/activity comment",
      "value": "induces proliferation inhibition, apoptosis, and cell cycle arrest by downregulating Sp1 expression",
      "peptide": "PCC-1"
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 3,
      "row_label": "B SK-MEL-28 Relative Sp1 expression (Sp1/GAPDH)",
      "col_header": "PCC-1 (μM) 80",
      "source_value": "0.45"
    },
    "short_reason": "Provided cells support dose-associated apoptosis and lower Sp1 expression; no conflicting source cell is present."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "",
      "endpoint": "linked literature title",
      "value": "linked literature title field mismatches primary article title",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "The provided longform cells contain figure/table values only and no article-title metadata for comparison."
  }
]