[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Tumor cells: H358; H1993; H1299; H2009",
      "endpoint": "EC50",
      "value": "H358=3.9nM; H1993=4nM; H1299=5.8nM; H2009=6.8nM",
      "peptide": "MGS4_V8 (monomer)"
    },
    "verification_outcome": "value_mismatch",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "MGS4_V8 (monomer)",
      "col_header": "EC50 (nM)",
      "source_value": "34"
    },
    "short_reason": "For MGS4_V8, source EC50 values are 34/37/38/38 nM, not the DB's 3.9/4/5.8/6.8 nM set."
  },
  {
    "assertion_index": 1,
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
    "short_reason": "The DB's EC50 set matches MGS4_V10 tetramer values, not the named MGS4_V8 monomer row."
  },
  {
    "assertion_index": 2,
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
    "short_reason": "The DB's EC50 set matches MGS4_V8 monomer values, not the named MGS4_V9 dimer row."
  },
  {
    "assertion_index": 3,
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
    "short_reason": "The DB's EC50 set matches MGS4_V10 tetramer values, not the named MGS4_V9 dimer row."
  },
  {
    "assertion_index": 4,
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
    "short_reason": "The DB's EC50 set matches MGS4_V8 monomer values, not the named MGS4_V10 tetramer row."
  },
  {
    "assertion_index": 5,
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
    "short_reason": "The DB's EC50 set matches MGS4_V9 dimer values, not the named MGS4_V10 tetramer row."
  }
]