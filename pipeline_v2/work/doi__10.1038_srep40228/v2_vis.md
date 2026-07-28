[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Lactococcus lactis AS1.1690",
      "endpoint": "MIC",
      "value": "",
      "peptide": "Chensinin-1 [G4,7,11W]"
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB assertion provides no MIC value, so no provided cell can verify an empty claimed value."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Lactococcus lactis AS1.1690",
      "endpoint": "MIC",
      "value": "",
      "peptide": "Chensinin-1 [G4,11W;H6W;G7Del;H15,18Del]"
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB assertion provides no MIC value, so no provided cell can verify an empty claimed value."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "Lactococcus lactis AS1.1690",
      "endpoint": "MIC",
      "value": "",
      "peptide": "Chensinin-1 [G4,7,11W;H6,15,18R]"
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB assertion provides no MIC value, so no provided cell can verify an empty claimed value."
  },
  {
    "assertion_index": 3,
    "db_claimed": {
      "organism": "Lactococcus lactis AS1.1690",
      "endpoint": "MIC",
      "value": "",
      "peptide": "Chensinin-1 [G4,7,11W]"
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB assertion provides no MIC value, so no provided cell can verify an empty claimed value."
  },
  {
    "assertion_index": 4,
    "db_claimed": {
      "organism": "Lactococcus lactis AS1.1690",
      "endpoint": "MIC",
      "value": "",
      "peptide": "Chensinin-1 [G4,11W;H6W;G7Del;H15,18Del]"
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB assertion provides no MIC value, so no provided cell can verify an empty claimed value."
  },
  {
    "assertion_index": 5,
    "db_claimed": {
      "organism": "Lactococcus lactis AS1.1690",
      "endpoint": "MIC",
      "value": "",
      "peptide": "Chensinin-1 [G4,7,11W;H6,15,18R]"
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB assertion provides no MIC value, so no provided cell can verify an empty claimed value."
  },
  {
    "assertion_index": 6,
    "db_claimed": {
      "organism": "Escherichia coli AS1.349; Pseudomonas aeruginosa CGMCC 1.860; Staphylococcus aureus AS1.72; Bacillus cereus AS1.126; Lactococcus lactis AS1.1690; Enterococcus faecalis CGMCC 1.595; Enterococcus faecium CGMCC 1.2334",
      "endpoint": "MIC",
      "value": "3.13; 1.56; 3.13; 3.13; 6.25; 1.56; 1.56 microM",
      "peptide": "Chensinin-1 [G4,11W;H6W;G7Del;H15,18Del]"
    },
    "verification_outcome": "value_match",
    "normalization_note": "strain_id_differs_value_same",
    "is_database_error": false,
    "evidence": {
      "table_index": 2,
      "row_label": "E. coli",
      "col_header": "MIC(μM)a / MC1-2 / G−",
      "source_value": "3.13"
    },
    "short_reason": "All listed MIC values match Table 2 for MC1-2; source rows use abbreviated organism names without DB strain IDs."
  },
  {
    "assertion_index": 7,
    "db_claimed": {
      "organism": "Escherichia coli AS1.349; Pseudomonas aeruginosa CGMCC 1.860; Staphylococcus aureus AS1.72; Bacillus cereus AS1.126; Lactococcus lactis AS1.1690; Enterococcus faecalis CGMCC 1.595; Enterococcus faecium CGMCC 1.2334",
      "endpoint": "MIC",
      "value": "6.25; 3.13; 6.25; 3.13; 6.25; 1.56; 3.13 microM",
      "peptide": "Chensinin-1 [G4,7,11W]"
    },
    "verification_outcome": "value_match",
    "normalization_note": "strain_id_differs_value_same",
    "is_database_error": false,
    "evidence": {
      "table_index": 2,
      "row_label": "E. coli",
      "col_header": "MIC(μM)a / MC1-1 / G−",
      "source_value": "6.25"
    },
    "short_reason": "All listed MIC values match Table 2 for MC1-1; source rows use abbreviated organism names without DB strain IDs."
  },
  {
    "assertion_index": 8,
    "db_claimed": {
      "organism": "Escherichia coli AS1.349; Pseudomonas aeruginosa CGMCC 1.860; Staphylococcus aureus AS1.72; Bacillus cereus AS1.126; Lactococcus lactis AS1.1690; Enterococcus faecalis CGMCC 1.595; Enterococcus faecium CGMCC 1.2334",
      "endpoint": "MIC",
      "value": "6.25; 6.25; 6.25; 6.25; 12.5; 6.25; 6.25 microM",
      "peptide": "Chensinin-1 [G4,7,11W;H6,15,18R]"
    },
    "verification_outcome": "value_match",
    "normalization_note": "strain_id_differs_value_same",
    "is_database_error": false,
    "evidence": {
      "table_index": 2,
      "row_label": "E. coli",
      "col_header": "MIC(μM)a / MC1-3 / G−",
      "source_value": "6.25"
    },
    "short_reason": "All listed MIC values match Table 2 for MC1-3; source rows use abbreviated organism names without DB strain IDs."
  },
  {
    "assertion_index": 9,
    "db_claimed": {
      "organism": "Escherichia coli AS1.349; Pseudomonas aeruginosa CGMCC 1.860; Staphylococcus aureus AS1.72; Bacillus cereus AS1.126; Lactococcus lactis AS1.1690; Enterococcus faecalis CGMCC 1.595; Enterococcus faecium CGMCC 1.2334",
      "endpoint": "MIC",
      "value": "3.13; 1.56; 3.13; 3.13; 6.25; 1.56; 1.56 μM",
      "peptide": "Chensinin-1 [G4,11W;H6W;G7Del;H15,18Del]"
    },
    "verification_outcome": "value_match",
    "normalization_note": "strain_id_differs_value_same",
    "is_database_error": false,
    "evidence": {
      "table_index": 2,
      "row_label": "E. coli",
      "col_header": "MIC(μM)a / MC1-2 / G−",
      "source_value": "3.13"
    },
    "short_reason": "All listed MIC values match Table 2 for MC1-2; source rows use abbreviated organism names without DB strain IDs."
  },
  {
    "assertion_index": 10,
    "db_claimed": {
      "organism": "Escherichia coli AS1.349; Pseudomonas aeruginosa CGMCC 1.860; Staphylococcus aureus AS1.72; Bacillus cereus AS1.126; Lactococcus lactis AS1.1690; Enterococcus faecalis CGMCC 1.595; Enterococcus faecium CGMCC 1.2334",
      "endpoint": "MIC",
      "value": "6.25; 3.13; 6.25; 3.13; 6.25; 1.56; 3.13 μM",
      "peptide": "Chensinin-1 [G4,7,11W]"
    },
    "verification_outcome": "value_match",
    "normalization_note": "strain_id_differs_value_same",
    "is_database_error": false,
    "evidence": {
      "table_index": 2,
      "row_label": "E. coli",
      "col_header": "MIC(μM)a / MC1-1 / G−",
      "source_value": "6.25"
    },
    "short_reason": "All listed MIC values match Table 2 for MC1-1; source rows use abbreviated organism names without DB strain IDs."
  },
  {
    "assertion_index": 11,
    "db_claimed": {
      "organism": "Escherichia coli AS1.349; Pseudomonas aeruginosa CGMCC 1.860; Staphylococcus aureus AS1.72; Bacillus cereus AS1.126; Lactococcus lactis AS1.1690; Enterococcus faecalis CGMCC 1.595; Enterococcus faecium CGMCC 1.2334",
      "endpoint": "MIC",
      "value": "6.25; 6.25; 6.25; 6.25; 12.5; 6.25; 6.25 μM",
      "peptide": "Chensinin-1 [G4,7,11W;H6,15,18R]"
    },
    "verification_outcome": "value_match",
    "normalization_note": "strain_id_differs_value_same",
    "is_database_error": false,
    "evidence": {
      "table_index": 2,
      "row_label": "E. coli",
      "col_header": "MIC(μM)a / MC1-3 / G−",
      "source_value": "6.25"
    },
    "short_reason": "All listed MIC values match Table 2 for MC1-3; source rows use abbreviated organism names without DB strain IDs."
  }
]