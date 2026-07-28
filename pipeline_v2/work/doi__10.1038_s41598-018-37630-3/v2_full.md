[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "EMR Staphylococcus aureus-16 NCTC 13277",
      "endpoint": "MIC in MHB",
      "value": ">128 microg/ml",
      "peptide": "Temporin B L1FK"
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "EMR Staphylococcus aureus-16 NCTC 13277",
      "col_header": "MHB",
      "source_value": ">128"
    },
    "short_reason": "The L1FK CAMP row repeats the KKG6A MIC pattern; this value exists in the source under a different peptide variant."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "EMR Staphylococcus aureus-16 NCTC 13277",
      "endpoint": "MIC in MHB",
      "value": "16 microg/ml",
      "peptide": "Temporin B KKG6A"
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "EMR Staphylococcus aureus-16 NCTC 13277",
      "col_header": "MHB",
      "source_value": "16"
    },
    "short_reason": "The KKG6A CAMP row repeats the L1FK MIC pattern; this value exists in the source under a different peptide variant."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "Klebsiella pneumoniae M6",
      "endpoint": "MIC in MHB",
      "value": "32μg/ml",
      "peptide": "Temporin B L1FK"
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 2,
      "row_label": "Klebsiella pneumoniae M6",
      "col_header": "MHB",
      "source_value": "32"
    },
    "short_reason": "Provided Table 2 supports the L1FK MIC values; extra MBC/IC50 claims are not assessed because they are not in provided cells."
  }
]