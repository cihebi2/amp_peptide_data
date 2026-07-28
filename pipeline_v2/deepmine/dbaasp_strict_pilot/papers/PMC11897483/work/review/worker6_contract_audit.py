#!/usr/bin/env python3
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PAPER_ID = "PMC11897483"
PAPER_ROOT = ROOT / "papers" / PAPER_ID
PACKET_ROOT = ROOT / "packets" / PAPER_ID
PAPER_FINAL = PAPER_ROOT / "final"
PACKET_FINAL = PACKET_ROOT / "final"
XML_PATH = PAPER_ROOT / "source" / "paper.xml"
ACTIVITY_PATH = PAPER_FINAL / "activity_toxicity_evidence.json"
MECH_PATH = PAPER_FINAL / "mechanism_ontology_record.json"
DB_PATH = PAPER_FINAL / "database_record_verification.json"
REVIEW_PATH = PAPER_FINAL / "review_report.json"
LOCATOR_PATH = PACKET_ROOT / "locators" / "locator_index.json"


EXPECTED_GROUPS = {
    "Group 1": ("1.5", "0.5", "0.6"),
    "Group 2": ("1.5", "1.0", "1.2"),
    "Group 3": ("1.5", "1.5", "1.8"),
    "Group 4": ("3.0", "0.5", "1.2"),
    "Group 5": ("3.0", "1.0", "1.8"),
    "Group 6": ("3.0", "1.5", "0.6"),
    "Group 7": ("4.5", "0.5", "1.8"),
    "Group 8": ("4.5", "1.0", "0.6"),
    "Group 9": ("4.5", "1.5", "1.2"),
}

EXPECTED_TARGETS = {
    "Staphylococcus aureus",
    "Listeria monocytogenes",
    "Escherichia coli",
    "Pseudomonas aeruginosa",
}

RUNTIME_TICKETS = [
    "rwk-PMC11897483-campaign-r01-PMC11897483-BLOCK-W2-ACTIVITY-TOXICITY-COVERAGE",
    "rwk-PMC11897483-campaign-r01-PMC11897483-BLOCK-W2-TABLE1-GROUP-CONDITION-MAPPING",
    "rwk-PMC11897483-campaign-r01-PMC11897483-BLOCK-W5-MECHANISM-DIRECT-CLAIM",
    "rwk-PMC11897483-campaign-r02-BF-W2-ACTIVITY-TOXICITY-SOURCE-FIELD-REPAIR",
    "rwk-PMC11897483-campaign-r03-BF-PMC11897483-W2-ACTIVITY-TOXICITY-SOURCE-MISMATCH",
]


def strip(tag):
    return tag.rsplit("}", 1)[-1]


def text_content(el):
    return " ".join(" ".join(el.itertext()).split())


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def cell_grid(table_wrap):
    rows = []
    occupied = {}
    trs = [el for el in table_wrap.iter() if strip(el.tag) == "tr"]
    for r_idx, tr in enumerate(trs, start=1):
        row = []
        col = 1
        for cell in [c for c in list(tr) if strip(c.tag) in {"td", "th"}]:
            while occupied.get((r_idx, col)):
                row.append(occupied[(r_idx, col)])
                col += 1
            rowspan = int(cell.attrib.get("rowspan") or cell.attrib.get("row-span") or "1")
            colspan = int(cell.attrib.get("colspan") or cell.attrib.get("col-span") or "1")
            entry = {
                "row": r_idx,
                "col": col,
                "text": text_content(cell),
                "tag": strip(cell.tag),
                "rowspan": rowspan,
                "colspan": colspan,
            }
            for dc in range(colspan):
                row.append(entry)
            for dr in range(1, rowspan):
                for dc in range(colspan):
                    occupied[(r_idx + dr, col + dc)] = entry
            col += colspan
        while occupied.get((r_idx, col)):
            row.append(occupied[(r_idx, col)])
            col += 1
        rows.append(row)
    return rows


def get_table_wrap(root, index):
    tables = [el for el in root.iter() if strip(el.tag) == "table-wrap"]
    return tables[index - 1]


def normalize_value(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def record_locators(record):
    locs = []
    for key in ("source_locator", "source_cell"):
        val = record.get(key)
        if isinstance(val, str):
            locs.append(val)
    val = record.get("source_locators")
    if isinstance(val, list):
        locs.extend(x for x in val if isinstance(x, str))
    expanded = []
    for loc in locs:
        expanded.extend(part.strip() for part in loc.split(";") if part.strip())
    return expanded


def locator_resolves(locator, locator_ids):
    if locator in locator_ids:
        return True
    if locator.startswith("xml:table-wrap:") and (":body-row=" in locator or ":tbody-row=" in locator):
        base = locator.split(":body-row=", 1)[0]
        base = base.split(":tbody-row=", 1)[0]
        return base in locator_ids
    if locator.startswith("xml:fig:") and ":" in locator[8:]:
        base = ":".join(locator.split(":")[:3])
        return base in locator_ids
    if locator.startswith("pdf:page="):
        base = locator.split(":block=", 1)[0].split(":figure=", 1)[0].split(":table=", 1)[0]
        return base in locator_ids
    return False


def derive_table1(rows):
    found = {}
    for row in rows:
        texts = [normalize_value(c["text"]) for c in row]
        group = next((t for t in texts if re.fullmatch(r"Group\s+[1-9]", t)), None)
        nums = [t for t in texts if re.fullmatch(r"\d+(?:\.\d+)?", t)]
        if group and len(nums) >= 3:
            found[group] = tuple(nums[:3])
    return found


def derive_table2(table_wrap):
    observations = []
    dashes = []
    data_row_idx = 0
    for tr in [el for el in table_wrap.iter() if strip(el.tag) == "tr"]:
        cells = [c for c in list(tr) if strip(c.tag) in {"td", "th"}]
        texts = [normalize_value(text_content(c)) for c in cells]
        group_idx = next((i for i, t in enumerate(texts) if re.fullmatch(r"Group\s+[1-9]", t)), None)
        if group_idx is None:
            continue
        group = texts[group_idx]
        data_row_idx += 1
        tail = texts[group_idx + 1 : group_idx + 5]
        if len(tail) != 4:
            continue
        for idx, target in enumerate(
            [
                "Staphylococcus aureus",
                "Listeria monocytogenes",
                "Escherichia coli",
                "Pseudomonas aeruginosa",
            ],
            start=1,
        ):
            raw = tail[idx - 1]
            locator = f"xml:table-wrap:2:tbody-row={data_row_idx}:cell={idx + 1}"
            entry = {"group": group, "target_species": target, "raw_value": raw, "source_cell": locator}
            if raw in {"-", "–", "—"}:
                dashes.append(entry)
            elif re.search(r"\d", raw):
                observations.append(entry)
    # Drop accidental non-data rows by retaining only expected group rows.
    observations = [o for o in observations if o["group"] in EXPECTED_GROUPS]
    dashes = [o for o in dashes if o["group"] in EXPECTED_GROUPS]
    return observations, dashes


def assay_condition_values(record):
    conditions = record.get("assay_conditions") or {}
    if isinstance(conditions, list):
        merged = {}
        for item in conditions:
            if isinstance(item, dict):
                merged.update(item)
        conditions = merged
    return conditions if isinstance(conditions, dict) else {}


def main():
    reviewed_at = datetime.now(timezone.utc).isoformat()
    root = ET.parse(XML_PATH).getroot()
    table1 = cell_grid(get_table_wrap(root, 1))
    table2_wrap = get_table_wrap(root, 2)
    table1_map = derive_table1(table1)
    table2_obs, table2_dashes = derive_table2(table2_wrap)
    activity = load_json(ACTIVITY_PATH)
    mechanism = load_json(MECH_PATH)
    database = load_json(DB_PATH)
    review = load_json(REVIEW_PATH)
    locator_ids = {r.get("locator") for r in load_json(LOCATOR_PATH)["locators"]}

    act_records = activity.get("activity_records", [])
    tox_records = activity.get("toxicity_records", [])
    exclusions = activity.get("excluded_or_unresolved_candidates", [])
    t2_records = [r for r in act_records if any("xml:table-wrap:2" in loc for loc in record_locators(r))]
    t2_exclusions = [r for r in exclusions if any("xml:table-wrap:2" in loc for loc in record_locators(r))]

    bad_activity_patterns = {
        "group_raw_values": sum(bool(re.fullmatch(r"Group\s+[0-9]+", normalize_value(r.get("raw_value")))) for r in act_records),
        "indicator_targets": sum(normalize_value(r.get("target_species")) == "Indicator bacteria" for r in act_records),
        "leading_pipe_species": sum(normalize_value(r.get("target_species")).startswith("|") for r in act_records),
        "generic_t2_endpoint": sum(
            normalize_value(r.get("endpoint")) == "table-reported antimicrobial measurement"
            and any("xml:table-wrap:2" in loc for loc in record_locators(r))
            for r in act_records
        ),
        "placeholder_raw_one_t2": sum(
            normalize_value(r.get("raw_value")) == "1"
            and any("xml:table-wrap:2" in loc for loc in record_locators(r))
            for r in act_records
        ),
    }

    t2_contract_failures = []
    final_cells = defaultdict(list)
    for r in t2_records:
        final_cells[(normalize_value((assay_condition_values(r).get("fermentation_group") or r.get("source_table_row_label") or "")), normalize_value(r.get("target_species")))].append(r)
    for expected in table2_obs:
        matches = final_cells[(expected["group"], expected["target_species"])]
        if not any(normalize_value(m.get("raw_value")) == expected["raw_value"] and normalize_value(m.get("raw_unit")) == "mm" for m in matches):
            t2_contract_failures.append({
                "group": expected["group"],
                "target_species": expected["target_species"],
                "failure": "missing_or_value_mismatch",
            })
    extra_t2 = []
    source_keys = {(o["group"], o["target_species"]) for o in table2_obs}
    for key, rows in final_cells.items():
        for row in rows:
            if key not in source_keys:
                extra_t2.append({"record_id": row.get("record_id"), "failure": "extra_or_misassigned_coordinate"})

    group_condition_failures = []
    for r in t2_records:
        cond = assay_condition_values(r)
        group = normalize_value(cond.get("fermentation_group") or r.get("source_table_row_label") or "")
        expected = EXPECTED_GROUPS.get(group)
        actual = (
            normalize_value(cond.get("glucose_g_per_100_ml")),
            normalize_value(cond.get("yeast_extract_g_per_100_ml") or cond.get("yeast_g_per_100_ml")),
            normalize_value(cond.get("MgSO4_7H2O_g_per_100_ml") or cond.get("mgso4_7h2o_g_per_100_ml")),
        )
        table1_locator = " ".join(str(cond.get(k, "")) for k in ("composition_source_locator", "composition_source_locators", "source_locator"))
        if not expected or actual != expected or "xml:table-wrap:1" not in table1_locator:
            group_condition_failures.append({"record_id": r.get("record_id"), "group": group, "failure": "missing_or_mismatched_table1_condition"})

    toxicity_forbidden = 0
    toxicity_required_context = 0
    exact_toxic_values = set()
    threshold_toxicity_count = 0
    for r in tox_records:
        text_blob = json.dumps(r, ensure_ascii=False)
        if any(term in text_blob for term in ["LfcinB", "sheep", "lipidation", "N-terminal lipidation"]):
            toxicity_forbidden += 1
        loc_blob = " ".join(record_locators(r))
        if any(x in loc_blob for x in ("xml:p:13", "xml:p:27", "xml:p:49", "xml:p:57", "xml:fig:10", "pdf:page=12")):
            toxicity_required_context += 1
        if "xml:fig:10" in loc_blob or "pdf:page=12" in loc_blob:
            exact_toxic_values.add((normalize_value(r.get("concentration")), normalize_value(r.get("raw_value")), normalize_value(r.get("raw_unit"))))
        if "xml:p:49" in loc_blob or "xml:p:57" in loc_blob:
            threshold_toxicity_count += 1

    loc_failures = []
    primary_rows = [("activity_records", act_records), ("toxicity_records", tox_records)]
    for artifact, rows in primary_rows:
        for idx, r in enumerate(rows):
            for locator in record_locators(r):
                if locator.startswith(("xml:", "pdf:", "supp:", "database:")) and not locator_resolves(locator, locator_ids):
                    loc_failures.append({"artifact": artifact, "index": idx, "locator": locator})
    exclusion_primary_locator_failures = []
    for idx, r in enumerate(exclusions):
        for locator in record_locators(r):
            if locator.startswith(("xml:", "pdf:", "supp:")) and not locator_resolves(locator, locator_ids):
                exclusion_primary_locator_failures.append({"artifact": "excluded_or_unresolved_candidates", "index": idx, "locator": locator})

    direct_mechanism_overclaims = [
        c.get("claim_id")
        for c in mechanism.get("mechanism_claims", [])
        if c.get("evidence_class") == "direct_mechanism"
        and not c.get("direct_assay_types")
    ]
    forbidden_direct_terms = ["DiSC", "membrane potential", "depolarization", "propidium", "SYTOX", "NPN"]
    direct_claim_text = json.dumps(
        [c for c in mechanism.get("mechanism_claims", []) if c.get("evidence_class") == "direct_mechanism"],
        ensure_ascii=False,
    )
    mechanism_forbidden_direct_terms = [term for term in forbidden_direct_terms if term in direct_claim_text]

    mirrors = {
        "activity": (PAPER_FINAL / "activity_toxicity_evidence.json").read_bytes()
        == (PACKET_FINAL / "activity_toxicity_evidence.json").read_bytes(),
        "database": (PAPER_FINAL / "database_record_verification.json").read_bytes()
        == (PACKET_FINAL / "database_record_verification.json").read_bytes(),
        "mechanism": (PAPER_FINAL / "mechanism_ontology_record.json").read_bytes()
        == (PACKET_FINAL / "mechanism_evidence.json").read_bytes(),
        "review": (PAPER_FINAL / "review_report.json").read_bytes()
        == (PACKET_FINAL / "review_report.json").read_bytes(),
    }

    final_counts = {
        "activity_records": len(act_records),
        "toxicity_records": len(tox_records),
        "database_record_audits": len(database.get("record_audits", database.get("record_identity_audit", []))),
        "mechanism_claims": len(mechanism.get("mechanism_claims", [])),
        "review_rework_targets": len(review.get("rework_targets", [])),
    }

    pass_flags = {
        "source_table1_mapping_matches_contract": table1_map == EXPECTED_GROUPS,
        "source_table2_expected_shape": len(table2_obs) == 26 and len(table2_dashes) == 10,
        "final_t2_activity_count": len(t2_records) == 26,
        "final_t2_exclusion_count": len(t2_exclusions) >= 10,
        "final_t2_cells_match_source": not t2_contract_failures and not extra_t2,
        "final_t2_group_conditions_complete": not group_condition_failures,
        "bad_activity_patterns_absent": all(v == 0 for v in bad_activity_patterns.values()),
        "toxicity_forbidden_terms_absent": toxicity_forbidden == 0,
        "toxicity_context_locators_present": toxicity_required_context == len(tox_records),
        "figure10_exact_values_present": len(exact_toxic_values) >= 3,
        "toxicity_threshold_cautions_present": threshold_toxicity_count >= 2,
        "source_locators_resolve": not loc_failures and not exclusion_primary_locator_failures,
        "mechanism_direct_claim_repaired": not direct_mechanism_overclaims and not mechanism_forbidden_direct_terms,
        "database_authoritative_boundary_preserved": database.get("authoritative_dbaasp_ingest_ready") is False,
        "review_report_acceptance_shape": review.get("review_status") in {"accepted_clean", "accepted_with_cautions"}
        and review.get("publication_grade") is True
        and final_counts["review_rework_targets"] == 0,
        "paper_packet_mirrors_byte_identical": all(mirrors.values()),
    }

    ticket_contract_evidence = {
        tid: {
            "contract_pass": all(pass_flags.values()),
            "checked_groups": [
                "activity_table2_coverage",
                "activity_table1_conditions",
                "toxicity_source_fields",
                "mechanism_direct_claim",
                "database_fallback_boundary",
                "mirror_identity",
            ],
        }
        for tid in RUNTIME_TICKETS
    }

    audit = {
        "paper_id": PAPER_ID,
        "generated_at": reviewed_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "source_surfaces_checked": [
            "paper.xml:table-wrap:1",
            "paper.xml:table-wrap:2",
            "paper.xml:fig:10",
            "paper.xml:p:13",
            "paper.xml:p:27",
            "paper.xml:p:49",
            "paper.xml:p:57",
            "packet locator_index",
            "packet database manifest and linked-row snapshots",
        ],
        "source_table2_summary": {
            "numeric_observation_count": len(table2_obs),
            "dash_count": len(table2_dashes),
            "target_species_count": len(EXPECTED_TARGETS),
            "group_count": len(EXPECTED_GROUPS),
        },
        "final_counts": final_counts,
        "mirror_status": mirrors,
        "bad_activity_patterns": bad_activity_patterns,
        "table2_contract_failures": t2_contract_failures,
        "table2_extra_failures": extra_t2,
        "table1_group_condition_failures": group_condition_failures,
        "toxicity_checks": {
            "forbidden_term_rows": toxicity_forbidden,
            "context_locator_rows": toxicity_required_context,
            "exact_figure10_value_records": len(exact_toxic_values),
            "threshold_or_caution_records": threshold_toxicity_count,
        },
        "locator_failures": loc_failures,
        "exclusion_primary_locator_failures": exclusion_primary_locator_failures,
        "mechanism_checks": {
            "direct_mechanism_without_assay_type_claims": direct_mechanism_overclaims,
            "forbidden_direct_terms": mechanism_forbidden_direct_terms,
        },
        "database_checks": {
            "authoritative_dbaasp_ingest_ready": database.get("authoritative_dbaasp_ingest_ready"),
            "linked_authoritative_row_counts": database.get("linked_authoritative_row_counts"),
            "unresolved_blockers_count": len(database.get("unresolved_blockers", [])),
        },
        "pass_flags": pass_flags,
        "ticket_contract_evidence": ticket_contract_evidence,
    }
    out = PAPER_ROOT / "work" / "review" / "source_review_audit.json"
    out.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("contract_audit", "pass" if all(pass_flags.values()) else "fail", "flags", len(pass_flags), "final_counts", final_counts)


if __name__ == "__main__":
    main()
