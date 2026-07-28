[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Tumor cells: H358; H1993; H1299; H2009",
      "endpoint": "EC50",
      "value": "H358=34nM; H1993=37nM; H1299=38nM; H2009=38nM",
      "peptide": "MGS4_V8 (monomer)"
    },
    "verification_outcome": "value_match",
    "normalization_note": "modification_representation_only",
    "is_database_error": false,
    "evidence": {
      "table_index": 2,
      "row_label": "MGS4_V8 (monomer)",
      "col_header": "EC50 (nM)",
      "source_value": "34"
    },
    "short_reason": "All listed EC50 values match source MGS4_V8 row; DB sequence omits Ac-/deleted-tail representation only."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Tumor cells: H358; H1993; H1299; H2009",
      "endpoint": "EC50",
      "value": "H358=3.9nM; H1993=4nM; H1299=5.8nM; H2009=6.8nM",
      "peptide": "MGS4_V8 (monomer)"
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "MGS4_V9 (dimer)",
      "col_header": "EC50 (nM)",
      "source_value": "3.9"
    },
    "short_reason": "The asserted EC50 set exists in source but belongs to MGS4_V9 dimer, not MGS4_V8 monomer."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "Tumor cells: H1993; H1299; H2009; H358",
      "endpoint": "EC50",
      "value": "H1993=1.5nM; H1299=2.5nM; H2009=3.4nM; H358=3.5nM",
      "peptide": "MGS4_V8 (monomer)"
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "MGS4_V10 (tetramer)",
      "col_header": "EC50 (nM)",
      "source_value": "1.5"
    },
    "short_reason": "The asserted EC50 set exists in source but belongs to MGS4_V10 tetramer, not MGS4_V8 monomer."
  },
  {
    "assertion_index": 3,
    "db_claimed": {
      "organism": "Tumor cells: H358; H1993; H1299; H2009",
      "endpoint": "EC50",
      "value": "H358=34nM; H1993=37nM; H1299=38nM; H2009=38nM",
      "peptide": "MGS4_V9 (dimer)"
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "MGS4_V8 (monomer)",
      "col_header": "EC50 (nM)",
      "source_value": "34"
    },
    "short_reason": "The asserted EC50 set exists in source but belongs to MGS4_V8 monomer, not MGS4_V9 dimer."
  },
  {
    "assertion_index": 4,
    "db_claimed": {
      "organism": "Tumor cells: H358; H1993; H1299; H2009",
      "endpoint": "EC50",
      "value": "H358=3.9nM; H1993=4nM; H1299=5.8nM; H2009=6.8nM",
      "peptide": "MGS4_V9 (dimer)"
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 2,
      "row_label": "MGS4_V9 (dimer)",
      "col_header": "EC50 (nM)",
      "source_value": "3.9"
    },
    "short_reason": "All listed EC50 values match the source MGS4_V9 dimer row for the stated tumor cell lines."
  },
  {
    "assertion_index": 5,
    "db_claimed": {
      "organism": "Tumor cells: H1993; H1299; H2009; H358",
      "endpoint": "EC50",
      "value": "H1993=1.5nM; H1299=2.5nM; H2009=3.4nM; H358=3.5nM",
      "peptide": "MGS4_V9 (dimer)"
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "MGS4_V10 (tetramer)",
      "col_header": "EC50 (nM)",
      "source_value": "1.5"
    },
    "short_reason": "The asserted EC50 set exists in source but belongs to MGS4_V10 tetramer, not MGS4_V9 dimer."
  },
  {
    "assertion_index": 6,
    "db_claimed": {
      "organism": "Tumor cells: H358; H1993; H1299; H2009",
      "endpoint": "EC50",
      "value": "H358=34nM; H1993=37nM; H1299=38nM; H2009=38nM",
      "peptide": "MGS4_V10 (tetramer)"
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "MGS4_V8 (monomer)",
      "col_header": "EC50 (nM)",
      "source_value": "34"
    },
    "short_reason": "The asserted EC50 set exists in source but belongs to MGS4_V8 monomer, not MGS4_V10 tetramer."
  },
  {
    "assertion_index": 7,
    "db_claimed": {
      "organism": "Tumor cells: H358; H1993; H1299; H2009",
      "endpoint": "EC50",
      "value": "H358=3.9nM; H1993=4nM; H1299=5.8nM; H2009=6.8nM",
      "peptide": "MGS4_V10 (tetramer)"
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "MGS4_V9 (dimer)",
      "col_header": "EC50 (nM)",
      "source_value": "3.9"
    },
    "short_reason": "The asserted EC50 set exists in source but belongs to MGS4_V9 dimer, not MGS4_V10 tetramer."
  },
  {
    "assertion_index": 8,
    "db_claimed": {
      "organism": "Tumor cells: H1993; H1299; H2009; H358",
      "endpoint": "EC50",
      "value": "H1993=1.5nM; H1299=2.5nM; H2009=3.4nM; H358=3.5nM",
      "peptide": "MGS4_V10 (tetramer)"
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 2,
      "row_label": "MGS4_V10 (tetramer)",
      "col_header": "EC50 (nM)",
      "source_value": "1.5"
    },
    "short_reason": "All listed EC50 values match the source MGS4_V10 tetramer row for the stated tumor cell lines."
  }
]