#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PILOT = load_module("dbaasp_strict_pilot", Path(__file__).with_name("dbaasp_strict_pilot.py"))
SEMANTIC = load_module(
    "semantic_three_layer_gate",
    ROOT / ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py",
)
PUBLICATION = load_module(
    "check_three_layer_publication_quality",
    ROOT / ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py",
)
PACKET = load_module(
    "check_two_queue_packets",
    ROOT / ".codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py",
)
CANDIDATE18_VALIDATOR = load_module(
    "validate_candidate18_layer2_contract",
    Path(__file__).with_name("dbaasp_strict_pilot")
    / "papers/PMC11905587/work/review/validate_candidate18_layer2_contract.py",
)


def strict_terminal_fixture(base: Path, ticket_id: str = "rwk-1") -> tuple[Path, dict]:
    paper_id = "PMC_TEST"
    packet = base / "packets" / paper_id
    paper_final = base / "papers" / paper_id / "final"
    packet_final = packet / "final"
    gate_dir = base / "gate_artifacts"
    for directory in (packet / "rework", paper_final, packet_final, gate_dir):
        directory.mkdir(parents=True, exist_ok=True)

    final_pairs = [
        (
            "activity_toxicity_evidence.json",
            "activity_toxicity_evidence.json",
            {"activity_records": [{"id": "a1"}], "toxicity_records": []},
        ),
        (
            "database_record_verification.json",
            "database_record_verification.json",
            {"record_audits": [{"id": "d1"}]},
        ),
        ("review_report.json", "review_report.json", {"rework_targets": []}),
        (
            "mechanism_ontology_record.json",
            "mechanism_evidence.json",
            {"mechanism_claims": []},
        ),
    ]
    verified_artifacts = {}
    for index, (paper_name, packet_name, data) in enumerate(final_pairs):
        payload = json.dumps({"paper_id": paper_id, **data}, sort_keys=True) + "\n"
        paper_path = paper_final / paper_name
        packet_path = packet_final / packet_name
        paper_path.write_text(payload, encoding="utf-8")
        packet_path.write_text(payload, encoding="utf-8")
        verified_artifacts[f"paper_{index}"] = str(paper_path)
        verified_artifacts[f"packet_{index}"] = str(packet_path)

    manifest = gate_dir / "manifest.json"
    manifest.write_text(json.dumps({"paper_ids": [paper_id]}) + "\n", encoding="utf-8")
    gate_payloads = {
        "packet": {
            "paper_count": 1,
            "hard_finding_count": 0,
            "hard_finding_papers": [],
            "open_rework_ticket_count": 0,
            "results": [
                {
                    "paper_id": paper_id,
                    "hard_findings": [],
                    "missing_packet_files": [],
                    "missing_final_files": [],
                    "open_rework_ticket_ids": [],
                }
            ],
        },
        "semantic": {
            "paper_count": 1,
            "publication_grade_pass_count": 1,
            "publication_grade_fail_count": 0,
            "failed_papers": [],
            "results": [
                {
                    "paper_id": paper_id,
                    "publication_grade_pass": True,
                    "issue_count": 0,
                    "issues": [],
                }
            ],
        },
        "publication": {
            "paper_count": 1,
            "publication_grade_pass": True,
            "risk_counts": {},
            "manifest": str(manifest),
            "counts": {"activity_records": 1, "mechanism_claims": 0},
        },
    }
    gate_artifacts = {}
    for name, data in gate_payloads.items():
        path = gate_dir / f"{name}.json"
        path.write_text(json.dumps(data) + "\n", encoding="utf-8")
        gate_artifacts[name] = str(path)

    response = {
        "ticket_id": ticket_id,
        "status": "closed_repaired",
        "response_status": "closed_repaired",
        "response_by": "worker-6",
        "analysis_can_resume": True,
        "publication_grade": True,
        "review_status": "accepted_with_cautions",
        "created_at": "2026-07-15T00:00:00Z",
        "final_counts": {
            "activity_records": 1,
            "toxicity_records": 0,
            "database_record_audits": 1,
            "mechanism_claims": 0,
            "review_rework_targets": 0,
        },
        "ticket_contract_evidence": {"overall_contract_pass": True},
        "gate_return_codes": {"packet": 0, "semantic": 0, "publication": 0},
        "gate_artifact_paths": gate_artifacts,
        "verified_artifact_paths": verified_artifacts,
    }
    return packet, response


class ActivityHandoffRegressionTests(unittest.TestCase):
    def test_bioc_xml_metadata_and_passages_are_extracted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            xml = base / "paper.xml"
            xml.write_text(
                """<collection><document><id>9647730</id>
                <passage>
                  <infon key="article-id_doi">10.1021/acs.langmuir.6b03477</infon>
                  <infon key="article-id_pmid">27793068</infon>
                  <infon key="section_type">TITLE</infon>
                  <infon key="type">front</infon>
                  <text>Cyclization Improves Membrane Permeation</text>
                </passage>
                <passage>
                  <infon key="section_type">TABLE</infon>
                  <infon key="type">table</infon>
                  <text>peptoid MIC HC50</text>
                </passage>
                </document></collection>""",
                encoding="utf-8",
            )
            packet = base / "packet"
            metadata = PILOT.parse_xml_metadata(xml)
            sections, tables, supplements, errors = PILOT.extract_xml_surfaces(
                xml, packet
            )

            self.assertEqual(metadata["doi"], "10.1021/acs.langmuir.6b03477")
            self.assertEqual(metadata["pmcid"], "PMC9647730")
            self.assertEqual(metadata["structured_fulltext_format"], "bioc_xml")
            self.assertEqual(len(sections), 2)
            self.assertEqual(len(tables), 1)
            self.assertEqual(tables[0]["locator"], "bioc:passage=2")
            self.assertEqual(supplements, [])
            self.assertEqual(errors, [])

    def test_pmc_oa_package_fallback_recovers_named_member(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            member = base / "srep11082-s1.pdf"
            member.write_bytes(b"%PDF-1.4\nsource material")
            archive = base / "package.tar.gz"
            with tarfile.open(archive, "w:gz") as handle:
                handle.add(member, arcname="PMC4508531/srep11082-s1.pdf")

            original_curl = PILOT.curl_download

            def fake_curl(url, out_path, timeout=80, cookie=None):
                temporary = out_path.with_suffix(out_path.suffix + ".part")
                temporary.parent.mkdir(parents=True, exist_ok=True)
                if "oa.fcgi" in url:
                    temporary.write_text(
                        '<OA><records><record><link format="tgz" '
                        'href="https://example.test/package.tar.gz"/>'
                        "</record></records></OA>",
                        encoding="utf-8",
                    )
                else:
                    shutil.copy2(archive, temporary)
                return {
                    "url": url,
                    "returncode": 0,
                    "tmp_path": str(temporary),
                    "output_path": str(out_path),
                    "downloaded_bytes": temporary.stat().st_size,
                }

            try:
                PILOT.curl_download = fake_curl
                recovered, attempts = PILOT.recover_from_pmc_oa_package(
                    "PMC4508531", [member.name], base / "scratch"
                )
            finally:
                PILOT.curl_download = original_curl

            self.assertIn(member.name, recovered)
            self.assertTrue(recovered[member.name].read_bytes().startswith(b"%PDF"))
            self.assertTrue(
                any(
                    item.get("attempt_type") == "pmc_oa_package_member"
                    and item.get("validation_ok") is True
                    for item in attempts
                )
            )

    def test_candidate_probe_uses_exact_pdf_worklist_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source_pdf = Path(tmp) / "descriptive DOI filename.pdf"
            source_pdf.write_bytes(b"%PDF-1.4\n")
            paper_id = "10.1234/example"
            original_base = PILOT.BASE
            try:
                PILOT.BASE = Path(tmp) / "pilot"
                candidate = PILOT.candidate_material_probe(
                    paper_id,
                    {paper_id: (source_pdf, "pdf")},
                    PILOT.Counter({paper_id: 2}),
                    PILOT.Counter(),
                    {},
                )
            finally:
                PILOT.BASE = original_base

            self.assertTrue(candidate["pdf_exists"])
            self.assertFalse(candidate["xml_exists"])
            self.assertEqual(candidate["source_file"], str(source_pdf))
            self.assertEqual(candidate["doi"], paper_id)
            self.assertTrue(candidate["needs_structured_fulltext_recovery"])
            self.assertTrue(candidate["needs_material_recovery_before_strict_run"])
            self.assertFalse(candidate["recommended"])

    def test_worker_prompt_embeds_assigned_open_ticket_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            rework = base / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            assigned = {
                "ticket_id": "rwk-assigned",
                "owner_worker": "worker-2",
                "severity": "blocking",
                "required_actions": {"entity": "bind exact source entity"},
                "acceptance_checks": {"entity_bound": True},
            }
            unassigned = {
                "ticket_id": "rwk-unassigned",
                "owner_worker": "worker-3",
                "severity": "blocking",
                "required_actions": {"supplement": "repair provenance"},
            }
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(assigned) + "\n" + json.dumps(unassigned) + "\n",
                encoding="utf-8",
            )
            (rework / "rework_responses.jsonl").write_text("", encoding="utf-8")

            original_base = PILOT.BASE
            try:
                PILOT.BASE = base
                prompt = PILOT.worker_prompt(paper_id, "worker-2")
            finally:
                PILOT.BASE = original_base

            self.assertIn("rwk-assigned", prompt)
            self.assertIn("bind exact source entity", prompt)
            self.assertIn('"entity_bound": true', prompt)
            self.assertNotIn("rwk-unassigned", prompt)

    def test_run_worker_refreshes_non_worker2_prompt_before_codex_exec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            prompt_path = base / "prompts" / paper_id / "worker-3.md"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text("STALE PROMPT\n", encoding="utf-8")
            rework = base / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text("", encoding="utf-8")
            (rework / "rework_responses.jsonl").write_text("", encoding="utf-8")
            captured = {}

            def fake_run_cmd(cmd, *, input_text=None, timeout=120):
                captured["input_text"] = input_text
                return 0, "", "session id: 00000000-0000-0000-0000-000000000001\nmodel: gpt-5.5\nreasoning effort: xhigh\n"

            original_base = PILOT.BASE
            original_run_cmd = PILOT.run_cmd
            try:
                PILOT.BASE = base
                PILOT.run_cmd = fake_run_cmd
                PILOT.run_worker(paper_id, "worker-3", timeout=1, run_id="testrun")
            finally:
                PILOT.BASE = original_base
                PILOT.run_cmd = original_run_cmd

            self.assertNotIn("STALE PROMPT", captured["input_text"])
            self.assertIn("Runtime-open ticket IDs assigned to worker-3", captured["input_text"])

    def test_cmd_run_checkpoints_sequence_after_each_worker(self) -> None:
        original_run_worker = PILOT.run_worker
        original_write_sequence = PILOT.write_run_sequence
        calls = []

        def fake_run_worker(paper_id, worker, timeout, run_id):
            return {
                "paper_id": paper_id,
                "worker": worker,
                "returncode": 0,
                "codex_session_id": f"session-{worker}",
                "codex_model": "gpt-5.5",
                "codex_reasoning_effort": "xhigh",
            }

        def fake_write_sequence(paper_id, workers, reports, merge_existing=False):
            calls.append([report["worker"] for report in reports])
            return {"reports": list(reports)}

        try:
            PILOT.run_worker = fake_run_worker
            PILOT.write_run_sequence = fake_write_sequence
            with contextlib.redirect_stdout(io.StringIO()):
                returncode = PILOT.cmd_run(
                    argparse.Namespace(
                        paper_id="PMC_TEST",
                        workers="worker-1,worker-2",
                        timeout=30,
                        keep_going=False,
                        merge_existing=True,
                    )
                )
        finally:
            PILOT.run_worker = original_run_worker
            PILOT.write_run_sequence = original_write_sequence

        self.assertEqual(returncode, 0)
        self.assertEqual(calls, [["worker-1"], ["worker-1", "worker-2"]])

    def test_worker_prompts_accept_source_located_figure_toxicity_evidence(self) -> None:
        worker2 = PILOT.worker_prompt("PMC_TEST", "worker-2")
        worker6 = PILOT.worker_prompt("PMC_TEST", "worker-6")
        required = "Lack of a source table is not a reason to discard it"
        self.assertIn(required, worker2)
        self.assertIn(required, worker6)
        self.assertIn("Do not gate the stale pre-repair final", worker6)

    def test_worker6_can_only_close_owner_ticket_after_strict_adjudication(self) -> None:
        worker2 = PILOT.worker_prompt("PMC_TEST", "worker-2")
        worker6 = PILOT.worker_prompt("PMC_TEST", "worker-6")

        self.assertIn("Every owner response is nonterminal", worker2)
        self.assertIn("Only worker-6 may append terminal closed_repaired", worker2)
        self.assertIn("Runtime-open ticket IDs assigned to worker-2", worker2)
        self.assertIn("analysis_can_resume true", worker2)
        self.assertIn("Do not put analysis_can_resume only inside a nested summary", worker2)
        self.assertNotIn("Every owner response is nonterminal", worker6)
        self.assertIn("all three strict gates pass", worker6)
        self.assertIn("status and response_status must both be exactly closed_repaired", worker6)
        self.assertIn("response_by must be worker-6", worker6)
        self.assertIn("analysis_can_resume and publication_grade must be true", worker6)
        self.assertIn("Runtime-open ticket IDs assigned to worker-6 list is authoritative", worker6)
        self.assertIn("never skip a listed ticket", worker6)
        self.assertIn("Never append another terminal response only when", worker6)
        self.assertIn("leave the ticket open", worker6)

    def test_figure_quantitation_prompts_reject_calibratable_null_placeholders(self) -> None:
        worker3 = PILOT.worker_prompt("PMC_TEST", "worker-3")
        worker6 = PILOT.worker_prompt("PMC_TEST", "worker-6")

        self.assertIn("A null raw_value or raw_unit is not a completed digitization", worker3)
        self.assertIn("axis calibration", worker3)
        self.assertIn("leave the ticket open", worker3)
        self.assertIn("null raw_value/raw_unit", worker6)
        self.assertIn("calibratable staged image", worker6)
        self.assertIn("preserve approximation", worker6)

    def test_only_activity_tables_are_suggested(self) -> None:
        tables = {
            "xml:table-wrap:1": "Film-forming solution Components and concentration Solvent system",
            "xml:table-wrap:2": "Main FTIR absorption bands and assignments",
            "xml:table-wrap:4": "Antibacterial activity Inhibition zone diameter (mm)",
            "xml:table-wrap:5": "Number of colonies forming units Log CFU/mL",
        }

        candidates = PILOT.activity_table_locator_candidates(tables)

        self.assertEqual(
            [item["locator"] for item in candidates],
            ["xml:table-wrap:4", "xml:table-wrap:5"],
        )

    def test_generic_figure_number_is_not_toxicity_evidence(self) -> None:
        self.assertEqual(PILOT.toxicity_locator_terms("MIC", "See Fig. 6"), [])
        terms = PILOT.toxicity_locator_terms("hemolysis", "Quantified in Fig. 6")
        self.assertIn("hemolysis", terms)
        self.assertIn("fig 6", terms)

    def test_response_status_closes_rework_ticket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, response = strict_terminal_fixture(Path(tmp))
            (packet / "rework/rework_requests.jsonl").write_text(
                json.dumps({"ticket_id": "rwk-1", "target_queue": "adjudication"}) + "\n",
                encoding="utf-8",
            )
            (packet / "rework/rework_responses.jsonl").write_text(
                json.dumps(response) + "\n",
                encoding="utf-8",
            )

            self.assertEqual(PILOT.open_rework_tickets(packet), [])
            self.assertEqual(PACKET.open_rework_tickets(packet), [])

    def test_sealed_closure_remains_historical_after_unrelated_final_edit(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, response = strict_terminal_fixture(Path(tmp))
            (packet / "rework/rework_requests.jsonl").write_text(
                json.dumps(
                    {"ticket_id": "rwk-1", "target_queue": "adjudication"}
                )
                + "\n",
                encoding="utf-8",
            )
            (packet / "rework/rework_responses.jsonl").write_text(
                json.dumps(response) + "\n",
                encoding="utf-8",
            )
            self.assertEqual(PILOT.open_rework_tickets(packet), [])
            receipt_path = packet / "rework/closure_receipts.jsonl"
            self.assertTrue(receipt_path.exists())

            # A later edit must be rechecked by current gates/leader/verifier,
            # but must not erase the historical fact that this ticket passed
            # its complete closure contract.
            (packet / "final/review_report.json").write_text(
                '{"later_unrelated_edit": true}\n', encoding="utf-8"
            )
            self.assertEqual(PILOT.open_rework_tickets(packet), [])
            self.assertEqual(PACKET.open_rework_tickets(packet), [])

    def test_tampered_closure_receipt_does_not_close_ticket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, response = strict_terminal_fixture(Path(tmp))
            (packet / "rework/rework_requests.jsonl").write_text(
                json.dumps(
                    {"ticket_id": "rwk-1", "target_queue": "adjudication"}
                )
                + "\n",
                encoding="utf-8",
            )
            (packet / "rework/rework_responses.jsonl").write_text(
                json.dumps(response) + "\n",
                encoding="utf-8",
            )
            self.assertEqual(PILOT.open_rework_tickets(packet), [])
            receipt_path = packet / "rework/closure_receipts.jsonl"
            receipts = [
                json.loads(line)
                for line in receipt_path.read_text(encoding="utf-8").splitlines()
                if line
            ]
            receipts[0]["terminal_response_sha256"] = "0" * 64
            receipt_path.write_text(
                "".join(json.dumps(row) + "\n" for row in receipts),
                encoding="utf-8",
            )
            (packet / "final/review_report.json").write_text(
                '{"later_unrelated_edit": true}\n', encoding="utf-8"
            )
            expected = ["rwk-1"]
            self.assertEqual(
                [
                    row["ticket_id"]
                    for row in PILOT.open_rework_tickets(packet)
                ],
                expected,
            )
            self.assertEqual(
                [
                    row["ticket_id"]
                    for row in PACKET.open_rework_tickets(packet)
                ],
                expected,
            )

    def test_only_complete_worker6_schema_is_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _, valid = strict_terminal_fixture(Path(tmp))
            self.assertTrue(PILOT.rework_response_is_closed(valid))
            self.assertTrue(PACKET.rework_response_is_closed(valid))

            mutations = [
                {"response_by": "worker-2"},
                {"status": "repaired_material_recovery_complete"},
                {"response_status": "closed_no_match"},
                {"analysis_can_resume": False},
                {"publication_grade": False},
                {"ticket_contract_evidence": {"overall_contract_pass": False}},
                {"gate_return_codes": {"packet": 0, "semantic": 1, "publication": 0}},
                {"verified_artifact_paths": {}},
                {"gate_artifact_paths": {}},
            ]
            for mutation in mutations:
                row = {**valid, **mutation}
                with self.subTest(mutation=mutation):
                    self.assertFalse(PILOT.rework_response_is_closed(row))
                    self.assertFalse(PACKET.rework_response_is_closed(row))

    def test_bridge_and_packet_gate_share_fail_closed_terminal_statuses(self) -> None:
        statuses = [
            "repaired_material_recovery_complete",
            "repaired_source_located_activity_matrix_complete",
            "closed_repaired_worker2_outputs",
            "closed_durable_gap_confirmed_after_worker2_repair",
            "closed_needs_followup",
            "resolved_needs_followup",
            "repaired_but_needs_followup",
            "reopened_for_source_review",
            "accepted",
            "closed_repaired",
        ]
        for status in statuses:
            with self.subTest(status=status):
                row = {"status": status}
                self.assertFalse(PILOT.rework_response_is_closed(row))
                self.assertFalse(PACKET.rework_response_is_closed(row))

    def test_packet_gate_uses_same_rework_closure_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, terminal = strict_terminal_fixture(Path(tmp), "rwk-valid")
            requests = [
                {"ticket_id": "rwk-valid", "target_queue": "adjudication"},
                {"ticket_id": "rwk-material"},
                {"ticket_id": "rwk-followup"},
                {"ticket_id": "rwk-generic-accepted"},
            ]
            responses = [
                terminal,
                {
                    "ticket_id": "rwk-material",
                    "status": "repaired_material_recovery_complete",
                },
                {
                    "ticket_id": "rwk-followup",
                    "status": "closed",
                    "response_status": "needs_followup",
                },
                {"ticket_id": "rwk-generic-accepted", "status": "accepted"},
            ]
            (packet / "rework/rework_requests.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in requests),
                encoding="utf-8",
            )
            (packet / "rework/rework_responses.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in responses),
                encoding="utf-8",
            )

            self.assertEqual(
                [row["ticket_id"] for row in PACKET.open_rework_tickets(packet)],
                ["rwk-material", "rwk-followup", "rwk-generic-accepted"],
            )
            self.assertEqual(
                [row["ticket_id"] for row in PILOT.open_rework_tickets(packet)],
                ["rwk-material", "rwk-followup", "rwk-generic-accepted"],
            )

    def test_duplicate_terminal_responses_keep_ticket_open(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, terminal = strict_terminal_fixture(Path(tmp))
            (packet / "rework/rework_requests.jsonl").write_text(
                json.dumps({"ticket_id": "rwk-1", "target_queue": "adjudication"}) + "\n",
                encoding="utf-8",
            )
            (packet / "rework/rework_responses.jsonl").write_text(
                json.dumps(terminal) + "\n" + json.dumps(terminal) + "\n",
                encoding="utf-8",
            )
            self.assertEqual([row["ticket_id"] for row in PILOT.open_rework_tickets(packet)], ["rwk-1"])
            self.assertEqual([row["ticket_id"] for row in PACKET.open_rework_tickets(packet)], ["rwk-1"])

    def test_later_duplicate_terminal_response_invalidates_sealed_receipt(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, terminal = strict_terminal_fixture(Path(tmp))
            (packet / "rework/rework_requests.jsonl").write_text(
                json.dumps(
                    {"ticket_id": "rwk-1", "target_queue": "adjudication"}
                )
                + "\n",
                encoding="utf-8",
            )
            response_path = packet / "rework/rework_responses.jsonl"
            response_path.write_text(
                json.dumps(terminal) + "\n", encoding="utf-8"
            )
            self.assertEqual(PILOT.open_rework_tickets(packet), [])

            response_path.write_text(
                json.dumps(terminal) + "\n" + json.dumps(terminal) + "\n",
                encoding="utf-8",
            )
            (packet / "final/review_report.json").write_text(
                '{"later_unrelated_edit": true}\n', encoding="utf-8"
            )
            expected = ["rwk-1"]
            self.assertEqual(
                [
                    row["ticket_id"]
                    for row in PILOT.open_rework_tickets(packet)
                ],
                expected,
            )
            self.assertEqual(
                [
                    row["ticket_id"]
                    for row in PACKET.open_rework_tickets(packet)
                ],
                expected,
            )

    def test_missing_or_divergent_terminal_artifacts_keep_ticket_open(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, terminal = strict_terminal_fixture(Path(tmp))
            (packet / "rework/rework_requests.jsonl").write_text(
                json.dumps({"ticket_id": "rwk-1", "target_queue": "adjudication"}) + "\n",
                encoding="utf-8",
            )
            (packet / "final/review_report.json").write_text("{\"different\": true}\n", encoding="utf-8")
            (packet / "rework/rework_responses.jsonl").write_text(
                json.dumps(terminal) + "\n",
                encoding="utf-8",
            )
            self.assertEqual([row["ticket_id"] for row in PILOT.open_rework_tickets(packet)], ["rwk-1"])
            self.assertEqual([row["ticket_id"] for row in PACKET.open_rework_tickets(packet)], ["rwk-1"])

    def test_owner_ticket_requires_prior_matching_repair_response(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, terminal = strict_terminal_fixture(Path(tmp))
            request = {"ticket_id": "rwk-1", "owner_worker": "worker-3", "target_queue": "material_extraction"}
            (packet / "rework/rework_requests.jsonl").write_text(json.dumps(request) + "\n", encoding="utf-8")
            response_path = packet / "rework/rework_responses.jsonl"
            response_path.write_text(json.dumps(terminal) + "\n", encoding="utf-8")
            self.assertEqual([row["ticket_id"] for row in PILOT.open_rework_tickets(packet)], ["rwk-1"])
            self.assertEqual([row["ticket_id"] for row in PACKET.open_rework_tickets(packet)], ["rwk-1"])

            owner = {
                "ticket_id": "rwk-1",
                "response_by": "worker-3",
                "response_status": "repair_ready_for_adjudication",
                "analysis_can_resume": True,
                "evidence": {"artifact": "digitized"},
            }
            response_path.write_text(json.dumps(owner) + "\n" + json.dumps(terminal) + "\n", encoding="utf-8")
            self.assertEqual(PILOT.open_rework_tickets(packet), [])
            self.assertEqual(PACKET.open_rework_tickets(packet), [])

    def test_owner_response_for_another_ticket_cannot_authorize_closure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, terminal = strict_terminal_fixture(Path(tmp), "rwk-b")
            requests = [
                {"ticket_id": "rwk-a", "owner_worker": "worker-3", "target_queue": "material_extraction"},
                {"ticket_id": "rwk-b", "owner_worker": "worker-3", "target_queue": "material_extraction"},
            ]
            owner_a = {
                "ticket_id": "rwk-a",
                "response_by": "worker-3",
                "response_status": "repair_ready_for_adjudication",
                "analysis_can_resume": True,
                "evidence": {"artifact": "only-a"},
            }
            packet_gate = Path(terminal["gate_artifact_paths"]["packet"])
            payload = json.loads(packet_gate.read_text(encoding="utf-8"))
            payload["open_rework_ticket_count"] = 1
            payload["results"][0]["open_rework_ticket_ids"] = ["rwk-b"]
            packet_gate.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            (packet / "rework/rework_requests.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in requests), encoding="utf-8"
            )
            (packet / "rework/rework_responses.jsonl").write_text(
                json.dumps(owner_a) + "\n" + json.dumps(terminal) + "\n", encoding="utf-8"
            )
            expected = ["rwk-a", "rwk-b"]
            self.assertEqual([row["ticket_id"] for row in PILOT.open_rework_tickets(packet)], expected)
            self.assertEqual([row["ticket_id"] for row in PACKET.open_rework_tickets(packet)], expected)

    def test_owner_needs_followup_or_self_declared_owner_is_not_repair_ready(self) -> None:
        invalid_owner_rows = [
            {
                "ticket_id": "rwk-1",
                "response_by": "worker-3",
                "response_status": "needs_followup",
                "analysis_can_resume": True,
                "evidence": {"artifact": "not-ready"},
            },
            {
                "ticket_id": "rwk-1",
                "owner_worker": "worker-3",
                "response_status": "repair_ready_for_adjudication",
                "analysis_can_resume": True,
                "evidence": {"artifact": "missing-response-by"},
            },
        ]
        for owner in invalid_owner_rows:
            with self.subTest(owner=owner), tempfile.TemporaryDirectory() as tmp:
                packet, terminal = strict_terminal_fixture(Path(tmp))
                request = {
                    "ticket_id": "rwk-1",
                    "owner_worker": "worker-3",
                    "target_queue": "material_extraction",
                }
                (packet / "rework/rework_requests.jsonl").write_text(
                    json.dumps(request) + "\n", encoding="utf-8"
                )
                (packet / "rework/rework_responses.jsonl").write_text(
                    json.dumps(owner) + "\n" + json.dumps(terminal) + "\n", encoding="utf-8"
                )
                self.assertEqual(
                    [row["ticket_id"] for row in PILOT.open_rework_tickets(packet)], ["rwk-1"]
                )
                self.assertEqual(
                    [row["ticket_id"] for row in PACKET.open_rework_tickets(packet)], ["rwk-1"]
                )

    def test_worker6_owned_ticket_does_not_require_an_upstream_owner_response(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, terminal = strict_terminal_fixture(Path(tmp))
            request = {"ticket_id": "rwk-1", "owner_worker": "worker-6", "target_queue": "analysis"}
            (packet / "rework/rework_requests.jsonl").write_text(
                json.dumps(request) + "\n", encoding="utf-8"
            )
            (packet / "rework/rework_responses.jsonl").write_text(
                json.dumps(terminal) + "\n", encoding="utf-8"
            )
            self.assertEqual(PILOT.open_rework_tickets(packet), [])
            self.assertEqual(PACKET.open_rework_tickets(packet), [])

    def test_non_adjudication_ticket_without_declared_owner_stays_open(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, terminal = strict_terminal_fixture(Path(tmp))
            request = {"ticket_id": "rwk-1", "target_queue": "analysis"}
            owner = {
                "ticket_id": "rwk-1",
                "response_by": "worker-2",
                "response_status": "repair_ready_for_adjudication",
                "analysis_can_resume": True,
                "evidence": {"artifact": "unbound-owner"},
            }
            (packet / "rework/rework_requests.jsonl").write_text(
                json.dumps(request) + "\n", encoding="utf-8"
            )
            (packet / "rework/rework_responses.jsonl").write_text(
                json.dumps(owner) + "\n" + json.dumps(terminal) + "\n", encoding="utf-8"
            )
            self.assertEqual(
                [row["ticket_id"] for row in PILOT.open_rework_tickets(packet)], ["rwk-1"]
            )
            self.assertEqual(
                [row["ticket_id"] for row in PACKET.open_rework_tickets(packet)], ["rwk-1"]
            )

    def test_invalid_terminal_candidate_cannot_expand_another_gate_closure_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, terminal_a = strict_terminal_fixture(Path(tmp), "rwk-a")
            terminal_b = {**terminal_a, "ticket_id": "rwk-b"}
            requests = [
                {"ticket_id": "rwk-a", "target_queue": "adjudication"},
                {"ticket_id": "rwk-b", "owner_worker": "worker-3", "target_queue": "material_extraction"},
            ]
            packet_gate = Path(terminal_a["gate_artifact_paths"]["packet"])
            payload = json.loads(packet_gate.read_text(encoding="utf-8"))
            payload["open_rework_ticket_count"] = 1
            payload["results"][0]["open_rework_ticket_ids"] = ["rwk-b"]
            packet_gate.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            (packet / "rework/rework_requests.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in requests), encoding="utf-8"
            )
            (packet / "rework/rework_responses.jsonl").write_text(
                json.dumps(terminal_a) + "\n" + json.dumps(terminal_b) + "\n", encoding="utf-8"
            )
            expected = ["rwk-a", "rwk-b"]
            self.assertEqual([row["ticket_id"] for row in PILOT.open_rework_tickets(packet)], expected)
            self.assertEqual([row["ticket_id"] for row in PACKET.open_rework_tickets(packet)], expected)

    def test_stale_terminal_candidate_is_removed_from_dependent_closure_fixed_point(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet, terminal_a = strict_terminal_fixture(Path(tmp), "rwk-a")
            terminal_b = json.loads(json.dumps({**terminal_a, "ticket_id": "rwk-b"}))
            gate_dir = Path(terminal_a["gate_artifact_paths"]["packet"]).parent
            for name, source_text in terminal_a["gate_artifact_paths"].items():
                source = Path(source_text)
                target = gate_dir / f"{name}-b.json"
                target.write_bytes(source.read_bytes())
                terminal_b["gate_artifact_paths"][name] = str(target)
                os.utime(target, (1, 1))

            packet_gate_a = Path(terminal_a["gate_artifact_paths"]["packet"])
            payload = json.loads(packet_gate_a.read_text(encoding="utf-8"))
            payload["open_rework_ticket_count"] = 1
            payload["results"][0]["open_rework_ticket_ids"] = ["rwk-b"]
            packet_gate_a.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            requests = [
                {"ticket_id": "rwk-a", "target_queue": "adjudication"},
                {"ticket_id": "rwk-b", "target_queue": "adjudication"},
            ]
            (packet / "rework/rework_requests.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in requests), encoding="utf-8"
            )
            (packet / "rework/rework_responses.jsonl").write_text(
                json.dumps(terminal_a) + "\n" + json.dumps(terminal_b) + "\n", encoding="utf-8"
            )
            expected = ["rwk-a", "rwk-b"]
            self.assertEqual([row["ticket_id"] for row in PILOT.open_rework_tickets(packet)], expected)
            self.assertEqual([row["ticket_id"] for row in PACKET.open_rework_tickets(packet)], expected)

    def test_failed_stale_or_unbound_gate_artifacts_keep_ticket_open(self) -> None:
        mutations = [
            ("packet", {}),
            ("semantic", {"paper_count": 1, "publication_grade_pass_count": 0}),
            ("publication", {"paper_count": 1, "publication_grade_pass": False}),
        ]
        for gate_name, payload in mutations:
            with self.subTest(gate_name=gate_name), tempfile.TemporaryDirectory() as tmp:
                packet, terminal = strict_terminal_fixture(Path(tmp))
                (packet / "rework/rework_requests.jsonl").write_text(
                    json.dumps({"ticket_id": "rwk-1", "target_queue": "adjudication"}) + "\n",
                    encoding="utf-8",
                )
                gate_path = Path(terminal["gate_artifact_paths"][gate_name])
                gate_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
                (packet / "rework/rework_responses.jsonl").write_text(json.dumps(terminal) + "\n", encoding="utf-8")
                self.assertEqual([row["ticket_id"] for row in PILOT.open_rework_tickets(packet)], ["rwk-1"])
                self.assertEqual([row["ticket_id"] for row in PACKET.open_rework_tickets(packet)], ["rwk-1"])

        with tempfile.TemporaryDirectory() as tmp:
            packet, terminal = strict_terminal_fixture(Path(tmp))
            (packet / "rework/rework_requests.jsonl").write_text(
                json.dumps({"ticket_id": "rwk-1", "target_queue": "adjudication"}) + "\n",
                encoding="utf-8",
            )
            for value in terminal["gate_artifact_paths"].values():
                os.utime(value, (1, 1))
            (packet / "rework/rework_responses.jsonl").write_text(json.dumps(terminal) + "\n", encoding="utf-8")
            self.assertEqual([row["ticket_id"] for row in PILOT.open_rework_tickets(packet)], ["rwk-1"])
            self.assertEqual([row["ticket_id"] for row in PACKET.open_rework_tickets(packet)], ["rwk-1"])

    def test_open_analysis_rework_overrides_stale_accepted_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            packet = base / "packets" / paper_id
            (packet / "rework").mkdir(parents=True)
            (packet / "packet_manifest.json").write_text("{}\n", encoding="utf-8")
            (packet / "rework/rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "rwk-analysis-1",
                        "target_queue": "analysis",
                        "owner_worker": "worker-2",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (packet / "rework/rework_responses.jsonl").write_text("", encoding="utf-8")
            final_dir = base / "papers" / paper_id / "final"
            final_dir.mkdir(parents=True)
            (final_dir / "review_report.json").write_text(
                json.dumps(
                    {
                        "review_status": "accepted_with_cautions",
                        "publication_grade": True,
                        "rework_targets": [],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            original_base = PILOT.BASE
            try:
                PILOT.BASE = base
                PILOT.sync_packet_statuses()
            finally:
                PILOT.BASE = original_base

            manifest = json.loads((packet / "packet_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["analysis_queue_status"], "analysis_needs_analysis_rework")
            self.assertEqual(manifest["open_rework_ticket_ids"], ["rwk-analysis-1"])

    def test_scoped_status_does_not_overwrite_global_latest(self) -> None:
        self.assertEqual(PILOT.status_report_path(None).name, "status_latest.json")
        self.assertEqual(
            PILOT.status_report_path(["PMC_TEST"]).name,
            "PMC_TEST_status_latest.json",
        )
        self.assertEqual(
            PILOT.status_report_path(["PMC_A", "PMC_B"]).name,
            "status_selected_latest.json",
        )

    def test_worker6_must_follow_latest_upstream_worker(self) -> None:
        reports = [
            {
                "worker": "worker-1",
                "started_at": "2026-07-11T10:00:00Z",
                "finished_at": "2026-07-11T10:10:00Z",
            },
            {
                "worker": "worker-6",
                "started_at": "2026-07-11T10:20:00Z",
                "finished_at": "2026-07-11T10:30:00Z",
            },
            {
                "worker": "worker-2",
                "started_at": "2026-07-11T10:40:00Z",
                "finished_at": "2026-07-11T10:50:00Z",
            },
            {
                "worker": "worker-3",
                "started_at": "2026-07-11T10:10:00Z",
                "finished_at": "2026-07-11T10:11:00Z",
            },
            {
                "worker": "worker-4",
                "started_at": "2026-07-11T10:11:00Z",
                "finished_at": "2026-07-11T10:12:00Z",
            },
            {
                "worker": "worker-5",
                "started_at": "2026-07-11T10:12:00Z",
                "finished_at": "2026-07-11T10:13:00Z",
            },
        ]

        freshness = PILOT.adjudication_freshness(reports)

        self.assertFalse(freshness["worker_6_after_upstream"])
        self.assertEqual(freshness["stale_adjudication_workers"], ["worker-2"])

        reports[1]["started_at"] = "2026-07-11T11:00:00Z"
        fresh = PILOT.adjudication_freshness(reports)
        self.assertTrue(fresh["worker_6_after_upstream"])
        self.assertEqual(fresh["stale_adjudication_workers"], [])

    def test_newer_worker_alias_invalidates_stale_run_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            report_dir = base / "worker_logs" / paper_id
            report_dir.mkdir(parents=True)
            reports = []
            for index, worker in enumerate(PILOT.WORKER_SKILLS, start=1):
                reports.append(
                    {
                        "paper_id": paper_id,
                        "worker": worker,
                        "command": ["codex", "exec"],
                        "started_at": f"2026-07-11T10:{index:02d}:00Z",
                        "finished_at": f"2026-07-11T10:{index:02d}:30Z",
                        "returncode": 0,
                        "codex_session_id": f"session-{index}",
                        "codex_model": "gpt-5.5",
                        "codex_reasoning_effort": "xhigh",
                    }
                )
            sequence = report_dir / "run_sequence_latest.json"
            sequence.write_text(json.dumps({"paper_id": paper_id, "reports": reports}))
            newer_alias = dict(reports[1])
            newer_alias.update(
                {
                    "started_at": "2026-07-11T11:00:00Z",
                    "finished_at": "2026-07-11T11:10:00Z",
                    "codex_session_id": "newer-worker-2-session",
                }
            )
            (report_dir / "worker-2.run_report.json").write_text(json.dumps(newer_alias))

            original_base = PILOT.BASE
            try:
                PILOT.BASE = base
                summary = PILOT.run_sequence_summary(paper_id)
            finally:
                PILOT.BASE = original_base

            self.assertEqual(summary["worker_report_alias_newer_than_run_sequence_count"], 1)
            self.assertEqual(summary["worker_report_alias_newer_than_run_sequence_workers"], ["worker-2"])
            self.assertGreater(summary["stale_or_mutated_log_reference_count"], 0)

    def test_run_sequence_summary_requires_canonical_exact_codex_exec(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            report_dir = base / "worker_logs" / paper_id
            report_dir.mkdir(parents=True)
            reports = [
                {
                    "paper_id": paper_id,
                    "worker": worker,
                    "command": ["codex", "exec"],
                    "started_at": f"2026-07-11T10:{index:02d}:00Z",
                    "finished_at": f"2026-07-11T10:{index:02d}:30Z",
                    "returncode": 0,
                    "codex_session_id": f"session-{index}",
                    "codex_model": "gpt-5.5",
                    "codex_reasoning_effort": "xhigh",
                }
                for index, worker in enumerate(
                    PILOT.WORKER_SKILLS, start=1
                )
            ]
            sequence = report_dir / "run_sequence_latest.json"
            original_base = PILOT.BASE
            try:
                PILOT.BASE = base
                sequence.write_text(
                    json.dumps({"paper_id": paper_id, "reports": reports}),
                    encoding="utf-8",
                )
                valid = PILOT.run_sequence_summary(paper_id)
                self.assertTrue(valid["canonical_worker_order"])
                self.assertTrue(valid["all_exact_codex_exec"])

                reports[0], reports[1] = reports[1], reports[0]
                sequence.write_text(
                    json.dumps({"paper_id": paper_id, "reports": reports}),
                    encoding="utf-8",
                )
                self.assertFalse(
                    PILOT.run_sequence_summary(paper_id)[
                        "canonical_worker_order"
                    ]
                )

                reports[0], reports[1] = reports[1], reports[0]
                reports[0]["command"] = ["python", "contains codex exec"]
                sequence.write_text(
                    json.dumps({"paper_id": paper_id, "reports": reports}),
                    encoding="utf-8",
                )
                self.assertFalse(
                    PILOT.run_sequence_summary(paper_id)[
                        "all_exact_codex_exec"
                    ]
                )
            finally:
                PILOT.BASE = original_base

    def test_open_rework_blocks_paper_level_completion(self) -> None:
        self.assertTrue(
            PILOT.paper_level_completion_ready(
                worker_run_clean=True,
                publication_grade=True,
                review_status="accepted_with_cautions",
                rework_targets=[],
                open_rework_tickets=[],
            )
        )
        self.assertFalse(
            PILOT.paper_level_completion_ready(
                worker_run_clean=True,
                publication_grade=True,
                review_status="accepted_with_cautions",
                rework_targets=[],
                open_rework_tickets=[{"ticket_id": "rwk-new"}],
            )
        )

    def test_recommended_next_action_prioritizes_runtime_open_ticket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet = Path(tmp)
            (packet / "rework").mkdir()
            (packet / "rework" / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "rwk-new",
                        "owner_worker": "worker-2",
                        "target_queue": "analysis",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (packet / "rework" / "rework_responses.jsonl").write_text("", encoding="utf-8")
            action = PILOT.recommended_next_action(
                "accepted_with_cautions",
                True,
                False,
                [],
                packet,
                {"failed_worker_count": 0},
            )
            self.assertEqual(
                action,
                "repair_runtime_open_rework_tickets_then_rerun_worker_6_and_acceptance_gates",
            )

    def test_candidate18_expanded_contract_rejects_both_semantic_omissions(self) -> None:
        source = (
            Path(__file__).with_name("dbaasp_strict_pilot")
            / "papers/PMC11905587/final/activity_toxicity_evidence.json"
        )
        payload = json.loads(source.read_text(encoding="utf-8"))
        for row in payload["activity_records"]:
            fields = row["assay_conditions"]["not_reported_or_not_structured_fields"]
            if "inoculum" not in fields:
                fields.append("inoculum")
        for key, value in list(payload.items()):
            if (
                ("conflict" in key.lower() or "caution" in key.lower())
                and isinstance(value, list)
            ):
                payload[key] = [
                    item
                    for item in value
                    if "maximum" not in json.dumps(item, ensure_ascii=False).lower()
                ]
        failed = CANDIDATE18_VALIDATOR.validate(payload)
        self.assertFalse(
            failed["checks"]["structured_inoculum_is_not_listed_as_unreported"]
        )
        self.assertFalse(
            failed["checks"][
                "method_1000_vs_table_footnote_100_maximum_conflict_is_explicit"
            ]
        )

        for row in payload["activity_records"]:
            fields = row["assay_conditions"]["not_reported_or_not_structured_fields"]
            row["assay_conditions"]["not_reported_or_not_structured_fields"] = [
                field for field in fields if field != "inoculum"
            ]
        payload.setdefault("source_conflicts", []).append(
            {
                "type": "intrapaper_method_table_maximum_conflict",
                "method_maximum": "1000 µg/mL",
                "table_footnote_maximum": "100 µg/mL",
                "method_locator": "xml:p:44",
                "table_locator": "xml:table-wrap:1",
                "disposition": "preserve both source-reported maximum values",
            }
        )
        repaired = CANDIDATE18_VALIDATOR.validate(payload)
        self.assertTrue(repaired["contract_pass"], repaired["failed_checks"])
        self.assertEqual(len(repaired["checks"]), 11)

    def test_candidate19_preflight_contract_has_40_unique_cell_locators(self) -> None:
        path = (
            Path(__file__).with_name("dbaasp_strict_pilot")
            / "papers/PMC11956232/work/leader_preflight"
            / "source_surface_preflight_contract_20260726.json"
        )
        contract = json.loads(path.read_text(encoding="utf-8"))["exact_table_contract"]
        observations = contract["observations"]
        self.assertEqual(contract["expected_exact_observation_count"], 40)
        self.assertTrue(contract["require_cell_locators"])
        self.assertEqual(len(observations), 40)
        self.assertEqual(len({row["cell_locator"] for row in observations}), 40)
        self.assertEqual(len({row["row_locator"] for row in observations}), 15)

    def test_worker_audit_imports_scientific_gate_failures(self) -> None:
        findings = PILOT.verify_gate_findings(
            {
                "packet_check": {"returncode": 0},
                "semantic_gate": {"returncode": 0},
                "publication_gate": {"returncode": 2},
                "strict_worker_run_gate": {"returncode": 0},
            }
        )
        self.assertEqual(findings[0]["code"], "publication_gate_failed")

    def test_verify_findings_reject_manifest_mutation_during_gate_run(self) -> None:
        findings = PILOT.verify_gate_findings(
            {
                "packet_check": {"returncode": 0},
                "semantic_gate": {"returncode": 0},
                "publication_gate": {"returncode": 0},
                "strict_worker_run_gate": {"returncode": 0},
                "manifest_sha256_at_start": "before",
                "manifest_sha256_at_finish": "after",
                "manifest_unchanged_during_verify": False,
            }
        )
        self.assertEqual([row["code"] for row in findings], ["manifest_changed_during_verify"])

    def test_acceptance_semantic_gate_uses_acceptance_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            manifest = base / "acceptance.json"
            manifest.write_text(
                json.dumps({"paper_ids": ["PMC_TEST"]}),
                encoding="utf-8",
            )
            commands: list[list[str]] = []

            def fake_run_cmd(command, timeout):
                commands.append(command)
                return 0, "{}", ""

            original_base = PILOT.BASE
            original_run_cmd = PILOT.run_cmd
            try:
                PILOT.BASE = base
                PILOT.run_cmd = fake_run_cmd
                result = PILOT.run_acceptance_gates("PMC_TEST", manifest)
            finally:
                PILOT.BASE = original_base
                PILOT.run_cmd = original_run_cmd

            semantic = result["commands"]["semantic_gate"]
            publication = result["commands"]["publication_gate"]
            self.assertIn("--manifest", semantic)
            self.assertNotIn("--paper-id", semantic)
            self.assertEqual(
                semantic[semantic.index("--manifest") + 1],
                str(manifest),
            )
            self.assertEqual(
                publication[publication.index("--manifest") + 1],
                str(manifest),
            )
            self.assertEqual(len(commands), 3)

    def test_worker_prompt_binds_leader_preflight_contracts_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            packet = base / "packets" / paper_id
            preflight = base / "papers" / paper_id / "work" / "leader_preflight"
            (packet / "rework").mkdir(parents=True)
            preflight.mkdir(parents=True)
            (packet / "rework" / "rework_requests.jsonl").write_text("", encoding="utf-8")
            (packet / "rework" / "rework_responses.jsonl").write_text("", encoding="utf-8")
            contract = preflight / "source_surface_contract.json"
            evidence = preflight / "leader_digitized_figure.json"
            contract.write_text('{"expected_observation_count":40}\n', encoding="utf-8")
            evidence.write_text('{"artifact_role":"leader_scaffold"}\n', encoding="utf-8")

            original_base = PILOT.BASE
            try:
                PILOT.BASE = base
                prompt = PILOT.worker_prompt(paper_id, "worker-2")
            finally:
                PILOT.BASE = original_base

            self.assertIn(str(contract), prompt)
            self.assertIn(str(evidence), prompt)
            self.assertIn("Read and obey every listed leader preflight contract", prompt)
            self.assertIn("independently verify leader evidence scaffolds", prompt)

    def test_acceptance_manifest_refreshes_packet_status_before_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            packet = base / "packets" / paper_id
            (packet / "extraction").mkdir(parents=True)
            (packet / "database").mkdir(parents=True)
            (packet / "packet_manifest.json").write_text(
                json.dumps(
                    {
                        "material_queue_status": "material_extracted_complete",
                        "locator_count": 1,
                    }
                ),
                encoding="utf-8",
            )
            (packet / "extraction" / "extraction_status.json").write_text(
                json.dumps({"status": "material_extracted_complete", "error_count": 0}),
                encoding="utf-8",
            )
            (packet / "database" / "database_source_manifest.json").write_text(
                json.dumps({"row_counts": {}}),
                encoding="utf-8",
            )
            called = []

            original_base = PILOT.BASE
            original_sync = PILOT.sync_packet_statuses
            try:
                PILOT.BASE = base
                PILOT.sync_packet_statuses = lambda ids=None: called.append(ids)
                manifest = PILOT.build_acceptance_manifest(paper_id)
            finally:
                PILOT.BASE = original_base
                PILOT.sync_packet_statuses = original_sync

            self.assertEqual(called, [[paper_id]])
            self.assertTrue(manifest.exists())

    def test_scoped_status_sync_does_not_mutate_other_paper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for paper_id in ("PMC_A", "PMC_B"):
                packet = base / "packets" / paper_id
                (packet / "analysis").mkdir(parents=True)
                (packet / "extraction").mkdir(parents=True)
                (packet / "rework").mkdir(parents=True)
                (packet / "locators").mkdir(parents=True)
                (packet / "packet_manifest.json").write_text(
                    json.dumps(
                        {
                            "paper_id": paper_id,
                            "analysis_queue_status": "sentinel",
                            "locator_count": 0,
                        }
                    ),
                    encoding="utf-8",
                )
                (packet / "extraction/extraction_status.json").write_text(
                    json.dumps({"status": "material_extracted_complete"}),
                    encoding="utf-8",
                )
                (packet / "extraction/extraction_errors.jsonl").write_text(
                    "", encoding="utf-8"
                )
                (packet / "locators/locator_index.json").write_text(
                    json.dumps({"locator_count": 1, "locators": [{}]}),
                    encoding="utf-8",
                )
                (packet / "rework/rework_requests.jsonl").write_text(
                    "", encoding="utf-8"
                )
                (packet / "rework/rework_responses.jsonl").write_text(
                    "", encoding="utf-8"
                )
            untouched = base / "packets/PMC_B/packet_manifest.json"
            untouched_before = untouched.read_bytes()

            original_base = PILOT.BASE
            try:
                PILOT.BASE = base
                PILOT.sync_packet_statuses(["PMC_A"])
            finally:
                PILOT.BASE = original_base

            self.assertEqual(untouched.read_bytes(), untouched_before)
            changed = json.loads(
                (base / "packets/PMC_A/packet_manifest.json").read_text()
            )
            self.assertEqual(changed["locator_count"], 1)

    def test_append_manifest_preserves_existing_issue_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "manifests").mkdir(parents=True)
            (base / "issues").mkdir(parents=True)
            issue_path = base / "issues/dbaasp_strict_pilot_issues.jsonl"
            issue_path.write_text('{"issue_id":"keep-me"}\n', encoding="utf-8")
            (base / "manifests/dbaasp_strict_pilot_manifest.json").write_text(
                json.dumps({"paper_ids": [], "papers": []}), encoding="utf-8"
            )
            built = [
                {
                    "paper_id": "PMC_A",
                    "paper_root": "papers/PMC_A",
                    "packet_root": "packets/PMC_A",
                    "material_status": "material_extracted_complete",
                    "locator_count": 1,
                    "database_row_counts": {},
                    "error_count": 0,
                }
            ]

            original_base = PILOT.BASE
            try:
                PILOT.BASE = base
                PILOT.write_pilot_manifest(["PMC_A"], built, append=True)
            finally:
                PILOT.BASE = original_base

            self.assertEqual(
                issue_path.read_text(encoding="utf-8"),
                '{"issue_id":"keep-me"}\n',
            )

    def test_acceptance_manifest_uses_live_locator_and_error_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            packet = base / "packets" / paper_id
            (packet / "analysis").mkdir(parents=True)
            (packet / "database").mkdir(parents=True)
            (packet / "extraction").mkdir(parents=True)
            (packet / "locators").mkdir(parents=True)
            (packet / "rework").mkdir(parents=True)
            (packet / "packet_manifest.json").write_text(
                json.dumps(
                    {
                        "material_queue_status": "material_extracted_with_gaps",
                        "locator_count": 1,
                        "known_missing_or_blocked_materials": [],
                    }
                ),
                encoding="utf-8",
            )
            (packet / "locators" / "locator_index.json").write_text(
                json.dumps(
                    {
                        "locator_count": 3,
                        "locators": [{"locator": "a"}, {"locator": "b"}, {"locator": "c"}],
                    }
                ),
                encoding="utf-8",
            )
            (packet / "extraction" / "extraction_status.json").write_text(
                json.dumps({"status": "material_extracted_with_gaps", "error_count": 0}),
                encoding="utf-8",
            )
            (packet / "extraction" / "extraction_errors.jsonl").write_text(
                '{"type":"ocr"}\n{"type":"supplement"}\n',
                encoding="utf-8",
            )
            (packet / "database" / "database_source_manifest.json").write_text(
                json.dumps({"row_counts": {}}),
                encoding="utf-8",
            )
            (packet / "rework" / "rework_requests.jsonl").write_text("", encoding="utf-8")
            (packet / "rework" / "rework_responses.jsonl").write_text("", encoding="utf-8")

            original_base = PILOT.BASE
            try:
                PILOT.BASE = base
                manifest_path = PILOT.build_acceptance_manifest(paper_id)
            finally:
                PILOT.BASE = original_base

            built = json.loads(manifest_path.read_text(encoding="utf-8"))["papers"][0]
            self.assertEqual(built["locator_count"], 3)
            self.assertEqual(built["error_count"], 2)
            packet_manifest = json.loads(
                (packet / "packet_manifest.json").read_text(encoding="utf-8")
            )
            extraction_status = json.loads(
                (packet / "extraction" / "extraction_status.json").read_text(encoding="utf-8")
            )
            self.assertEqual(packet_manifest["locator_count"], 3)
            self.assertEqual(len(packet_manifest["known_missing_or_blocked_materials"]), 2)
            self.assertEqual(extraction_status["error_count"], 2)

    def test_strict_gate_rejects_nested_authority_true(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            work = base / "papers" / paper_id / "work"
            analysis = base / "packets" / paper_id / "analysis"
            work.mkdir(parents=True)
            analysis.mkdir(parents=True)
            (work / "worker4.json").write_text(
                json.dumps(
                    {
                        "paper_id": paper_id,
                        "nested": {"authoritative_dbaasp_ingest_ready": True},
                    }
                ),
                encoding="utf-8",
            )

            original_base = PILOT.BASE
            original_status = PILOT.build_status_report
            try:
                PILOT.BASE = base
                PILOT.build_status_report = lambda _ids: {
                    "paper_count": 1,
                    "source_reviewed_publication_grade_count": 1,
                    "authoritative_dbaasp_ingest_ready_count": 0,
                    "papers": [
                        {
                            "paper_id": paper_id,
                            "review_status": "accepted_with_cautions",
                            "publication_grade": True,
                            "worker_run_clean": True,
                            "worker_run": {"failed_workers": []},
                        }
                    ],
                }
                report = PILOT.strict_worker_run_gate([paper_id])
            finally:
                PILOT.BASE = original_base
                PILOT.build_status_report = original_status

            authority = [
                row for row in report["findings"]
                if row.get("code") == "recursive_authority_boundary_true"
            ]
            self.assertEqual(len(authority), 1)
            self.assertIn("worker4.json", authority[0]["path"])
            self.assertEqual(report["hard_finding_count"], 1)

    def test_strict_gate_rejects_plain_sequence_length_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            work = base / "papers" / paper_id / "work"
            work.mkdir(parents=True)
            (work / "identity.json").write_text(
                json.dumps(
                    {
                        "paper_id": paper_id,
                        "identity": {
                            "sequence": "RRWQWRPKRIVKLIKKWLR",
                            "sequence_length": 20,
                            "terminal_modification": "C-terminal amidation",
                        },
                    }
                ),
                encoding="utf-8",
            )

            original_base = PILOT.BASE
            original_status = PILOT.build_status_report
            try:
                PILOT.BASE = base
                PILOT.build_status_report = lambda _ids: {
                    "paper_count": 1,
                    "source_reviewed_publication_grade_count": 1,
                    "authoritative_dbaasp_ingest_ready_count": 0,
                    "papers": [
                        {
                            "paper_id": paper_id,
                            "review_status": "accepted_with_cautions",
                            "publication_grade": True,
                            "worker_run_clean": True,
                            "worker_run": {"failed_workers": []},
                        }
                    ],
                }
                report = PILOT.strict_worker_run_gate([paper_id])
            finally:
                PILOT.BASE = original_base
                PILOT.build_status_report = original_status

            mismatch = [
                row
                for row in report["findings"]
                if row.get("code") == "sequence_length_mismatch"
            ]
            self.assertEqual(len(mismatch), 1)
            self.assertEqual(mismatch[0]["actual_sequence_length"], 19)
            self.assertEqual(mismatch[0]["declared_sequence_length"], 20)
            self.assertEqual(report["hard_finding_count"], 1)

    def test_strict_gate_rejects_stale_review_open_ticket_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            final = base / "papers" / paper_id / "final"
            rework = base / "packets" / paper_id / "rework"
            final.mkdir(parents=True)
            rework.mkdir(parents=True)
            (final / "review_report.json").write_text(
                json.dumps(
                    {
                        "paper_id": paper_id,
                        "semantic_quality_checks": {
                            "open_rework_ticket_count": 2,
                        },
                    }
                ),
                encoding="utf-8",
            )
            (rework / "rework_requests.jsonl").write_text("", encoding="utf-8")
            (rework / "rework_responses.jsonl").write_text("", encoding="utf-8")

            original_base = PILOT.BASE
            original_status = PILOT.build_status_report
            try:
                PILOT.BASE = base
                PILOT.build_status_report = lambda _ids: {
                    "paper_count": 1,
                    "source_reviewed_publication_grade_count": 1,
                    "authoritative_dbaasp_ingest_ready_count": 0,
                    "papers": [
                        {
                            "paper_id": paper_id,
                            "review_status": "accepted_with_cautions",
                            "publication_grade": True,
                            "worker_run_clean": True,
                            "worker_run": {"failed_workers": []},
                        }
                    ],
                }
                report = PILOT.strict_worker_run_gate([paper_id])
            finally:
                PILOT.BASE = original_base
                PILOT.build_status_report = original_status

            mismatch = [
                row
                for row in report["findings"]
                if row.get("code") == "review_report_open_ticket_count_mismatch"
            ]
            self.assertEqual(len(mismatch), 1)
            self.assertEqual(mismatch[0]["declared_open_rework_ticket_count"], 2)
            self.assertEqual(mismatch[0]["actual_open_rework_ticket_count"], 0)
            self.assertEqual(report["hard_finding_count"], 1)

    def test_strict_gate_rejects_worker_artifact_as_source_locator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            final = base / "papers" / paper_id / "final"
            final.mkdir(parents=True)
            (final / "mechanism_ontology_record.json").write_text(
                json.dumps(
                    {
                        "paper_id": paper_id,
                        "mechanism_claims": [
                            {
                                "source_locator": "xml:p:27",
                                "supporting_source_locators": [
                                    "xml:p:25",
                                    (
                                        "packets/PMC_TEST/analysis/"
                                        "activity_toxicity_evidence.worker2.json"
                                    ),
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            original_base = PILOT.BASE
            original_status = PILOT.build_status_report
            try:
                PILOT.BASE = base
                PILOT.build_status_report = lambda _ids: {
                    "paper_count": 1,
                    "source_reviewed_publication_grade_count": 1,
                    "authoritative_dbaasp_ingest_ready_count": 0,
                    "papers": [
                        {
                            "paper_id": paper_id,
                            "review_status": "accepted_with_cautions",
                            "publication_grade": True,
                            "worker_run_clean": True,
                            "worker_run": {"failed_workers": []},
                        }
                    ],
                }
                report = PILOT.strict_worker_run_gate([paper_id])
            finally:
                PILOT.BASE = original_base
                PILOT.build_status_report = original_status

            recursive = [
                row
                for row in report["findings"]
                if row.get("code") == "recursive_non_source_locator_reference"
            ]
            self.assertEqual(len(recursive), 1)
            self.assertIn("/analysis/", recursive[0]["non_source_locator"])
            self.assertEqual(report["hard_finding_count"], 1)

    def test_strict_gate_rejects_locator_and_extraction_count_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            packet = base / "packets" / paper_id
            (packet / "extraction").mkdir(parents=True)
            (packet / "locators").mkdir(parents=True)
            (packet / "packet_manifest.json").write_text(
                json.dumps({"paper_id": paper_id, "locator_count": 1}),
                encoding="utf-8",
            )
            (packet / "locators" / "locator_index.json").write_text(
                json.dumps(
                    {
                        "paper_id": paper_id,
                        "locator_count": 2,
                        "locators": [{"locator": "a"}, {"locator": "b"}],
                    }
                ),
                encoding="utf-8",
            )
            (packet / "extraction" / "extraction_status.json").write_text(
                json.dumps({"paper_id": paper_id, "error_count": 0}),
                encoding="utf-8",
            )
            (packet / "extraction" / "extraction_errors.jsonl").write_text(
                '{"type":"ocr"}\n{"type":"supplement"}\n',
                encoding="utf-8",
            )

            original_base = PILOT.BASE
            original_status = PILOT.build_status_report
            try:
                PILOT.BASE = base
                PILOT.build_status_report = lambda _ids: {
                    "paper_count": 1,
                    "source_reviewed_publication_grade_count": 0,
                    "authoritative_dbaasp_ingest_ready_count": 0,
                    "papers": [
                        {
                            "paper_id": paper_id,
                            "review_status": "missing_review",
                            "publication_grade": False,
                            "worker_run_clean": False,
                            "worker_run": {"failed_workers": []},
                        }
                    ],
                }
                report = PILOT.strict_worker_run_gate([paper_id])
            finally:
                PILOT.BASE = original_base
                PILOT.build_status_report = original_status

            codes = {row["code"] for row in report["findings"]}
            self.assertIn("locator_count_mismatch", codes)
            self.assertIn("extraction_error_count_mismatch", codes)
            self.assertEqual(report["hard_finding_count"], 2)

    def test_acceptance_requires_current_gate_returncodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            final = base / "papers" / paper_id / "final"
            reports = base / "reports"
            final.mkdir(parents=True)
            reports.mkdir(parents=True)
            (final / "review_report.json").write_text(
                json.dumps(
                    {
                        "review_status": "accepted_with_cautions",
                        "publication_grade": True,
                        "validator_contract_passed": True,
                        "rework_targets": [],
                    }
                )
            )
            report_payloads = {
                "packet_gate": {"hard_finding_count": 0, "open_rework_ticket_count": 0},
                "semantic_gate": {"publication_grade_pass_count": 1, "failed_papers": []},
                "publication_gate": {"publication_grade_pass": True, "risk_counts": {}},
            }
            gate_run = {"reports": {}, "results": {}}
            for name, payload in report_payloads.items():
                path = reports / f"{name}.json"
                path.write_text(json.dumps(payload))
                gate_run["reports"][name] = str(path)
                gate_run["results"][name] = {"returncode": 1}
            status = {
                "paper_level_source_reviewed_complete": True,
                "authoritative_dbaasp_ingest_ready": False,
                "worker_run": {
                    "worker_count": 6,
                    "all_returncode_zero": True,
                    "all_gpt55_xhigh": True,
                    "unique_session_count": 6,
                },
            }

            original_base = PILOT.BASE
            original_status = PILOT.paper_status_summary
            original_strict_gate = PILOT.strict_worker_run_gate
            try:
                PILOT.BASE = base
                PILOT.paper_status_summary = lambda _paper_id: status
                PILOT.strict_worker_run_gate = lambda _ids: {
                    "hard_finding_count": 0,
                    "hard_finding_papers": [],
                    "findings": [],
                }
                audit = PILOT.build_acceptance_audit(paper_id, base / "manifest.json", gate_run)
            finally:
                PILOT.BASE = original_base
                PILOT.paper_status_summary = original_status
                PILOT.strict_worker_run_gate = original_strict_gate

            self.assertFalse(audit["acceptance_ready_for_paper_level_source_review"])
            self.assertEqual(audit["gate_summary"]["gate_returncodes"], {
                "packet_gate": 1,
                "semantic_gate": 1,
                "publication_gate": 1,
            })

    def test_acceptance_requires_explicit_fresh_reports_and_manifest_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            manifest = base / "manifest.json"
            manifest.write_text(json.dumps({"paper_ids": [paper_id]}), encoding="utf-8")
            final = base / "papers" / paper_id / "final"
            reports = base / "reports"
            final.mkdir(parents=True)
            reports.mkdir(parents=True)
            (final / "review_report.json").write_text(
                json.dumps(
                    {
                        "review_status": "accepted_with_cautions",
                        "publication_grade": True,
                        "validator_contract_passed": True,
                        "rework_targets": [],
                    }
                ),
                encoding="utf-8",
            )
            report_payloads = {
                "packet_gate": {"hard_finding_count": 0, "open_rework_ticket_count": 0},
                "semantic_gate": {"publication_grade_pass_count": 1, "failed_papers": []},
                "publication_gate": {"publication_grade_pass": True, "risk_counts": {}},
            }
            gate_run = {"reports": {}, "results": {}}
            for name, payload in report_payloads.items():
                path = reports / f"{name}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                gate_run["reports"][name] = str(path)
                gate_run["results"][name] = {"returncode": 0}
            status = {
                "paper_level_source_reviewed_complete": True,
                "authoritative_dbaasp_ingest_ready": False,
                "worker_run": {
                    "worker_count": 6,
                    "all_returncode_zero": True,
                    "all_gpt55_xhigh": True,
                    "unique_session_count": 6,
                },
            }

            original_base = PILOT.BASE
            original_status = PILOT.paper_status_summary
            original_strict_gate = PILOT.strict_worker_run_gate
            try:
                PILOT.BASE = base
                PILOT.paper_status_summary = lambda _paper_id: status
                PILOT.strict_worker_run_gate = lambda _ids: {
                    "hard_finding_count": 0,
                    "hard_finding_papers": [],
                    "findings": [],
                }
                missing_freshness = PILOT.build_acceptance_audit(paper_id, manifest, gate_run)
                self.assertFalse(
                    missing_freshness["acceptance_ready_for_paper_level_source_review"]
                )
                self.assertFalse(missing_freshness["gate_summary"]["gate_reports_fresh"])

                gate_run["manifest"] = str(manifest)
                gate_run["manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
                for name, path_text in gate_run["reports"].items():
                    path = Path(path_text)
                    report_mtime = path.stat().st_mtime
                    gate_run["results"][name].update(
                        {
                            "report_exists": True,
                            "report_fresh": True,
                            "started_epoch": report_mtime,
                            "report_mtime": report_mtime,
                        }
                    )
                current = PILOT.build_acceptance_audit(paper_id, manifest, gate_run)
            finally:
                PILOT.BASE = original_base
                PILOT.paper_status_summary = original_status
                PILOT.strict_worker_run_gate = original_strict_gate

            self.assertTrue(current["gate_summary"]["gate_reports_fresh"])
            self.assertTrue(current["gate_summary"]["gate_manifest_matches"])
            self.assertTrue(current["acceptance_ready_for_paper_level_source_review"])

    def test_acceptance_rejects_strict_artifact_consistency_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper_id = "PMC_TEST"
            manifest = base / "manifest.json"
            manifest.write_text(json.dumps({"paper_ids": [paper_id]}), encoding="utf-8")
            final = base / "papers" / paper_id / "final"
            reports = base / "reports"
            final.mkdir(parents=True)
            reports.mkdir(parents=True)
            (final / "review_report.json").write_text(
                json.dumps(
                    {
                        "review_status": "accepted_with_cautions",
                        "publication_grade": True,
                        "validator_contract_passed": True,
                        "rework_targets": [],
                    }
                ),
                encoding="utf-8",
            )
            payloads = {
                "packet_gate": {"hard_finding_count": 0, "open_rework_ticket_count": 0},
                "semantic_gate": {"publication_grade_pass_count": 1, "failed_papers": []},
                "publication_gate": {"publication_grade_pass": True, "risk_counts": {}},
            }
            gate_run = {
                "manifest": str(manifest),
                "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                "reports": {},
                "results": {},
            }
            for name, payload in payloads.items():
                path = reports / f"{name}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                mtime = path.stat().st_mtime
                gate_run["reports"][name] = str(path)
                gate_run["results"][name] = {
                    "returncode": 0,
                    "report_exists": True,
                    "report_fresh": True,
                    "started_epoch": mtime,
                    "report_mtime": mtime,
                }
            status = {
                "paper_level_source_reviewed_complete": True,
                "authoritative_dbaasp_ingest_ready": False,
                "worker_run": {
                    "worker_count": 6,
                    "all_returncode_zero": True,
                    "all_gpt55_xhigh": True,
                    "unique_session_count": 6,
                },
            }

            original_base = PILOT.BASE
            original_status = PILOT.paper_status_summary
            original_strict_gate = PILOT.strict_worker_run_gate
            try:
                PILOT.BASE = base
                PILOT.paper_status_summary = lambda _paper_id: status
                PILOT.strict_worker_run_gate = lambda _ids: {
                    "hard_finding_count": 1,
                    "hard_finding_papers": [paper_id],
                    "findings": [{"paper_id": paper_id, "code": "locator_count_mismatch"}],
                }
                audit = PILOT.build_acceptance_audit(paper_id, manifest, gate_run)
            finally:
                PILOT.BASE = original_base
                PILOT.paper_status_summary = original_status
                PILOT.strict_worker_run_gate = original_strict_gate

            self.assertFalse(audit["acceptance_ready_for_paper_level_source_review"])
            self.assertEqual(audit["gate_summary"]["strict_worker_run_hard_finding_count"], 1)

    def test_verify_command_fails_closed_unless_diagnostic(self) -> None:
        failing = {
            "packet_check": {"returncode": 0},
            "semantic_gate": {"returncode": 1},
            "publication_gate": {"returncode": 2},
            "strict_worker_run_gate": {"returncode": 0},
        }
        original_verify = PILOT.verify
        try:
            PILOT.verify = lambda: failing
            with contextlib.redirect_stdout(io.StringIO()):
                strict_code = PILOT.cmd_verify(argparse.Namespace(diagnostic=False))
                diagnostic_code = PILOT.cmd_verify(argparse.Namespace(diagnostic=True))
        finally:
            PILOT.verify = original_verify

        self.assertEqual(strict_code, 1)
        self.assertEqual(diagnostic_code, 0)

    def test_scoped_verify_uses_one_scoped_manifest_for_all_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            manifests = base / "manifests"
            manifests.mkdir(parents=True)
            (manifests / "dbaasp_strict_pilot_manifest.json").write_text(
                json.dumps(
                    {
                        "paper_ids": ["PMC_A", "PMC_B"],
                        "papers": [
                            {"paper_id": "PMC_A", "packet_root": "packets/PMC_A"},
                            {"paper_id": "PMC_B", "packet_root": "packets/PMC_B"},
                        ],
                    }
                )
            )
            commands: list[list[str]] = []
            strict_ids: list[list[str] | None] = []

            def fake_run_cmd(command, timeout):
                commands.append(command)
                return 0, "{}", ""

            def fake_strict_gate(paper_ids=None):
                strict_ids.append(paper_ids)
                return {"hard_finding_count": 0, "hard_finding_papers": []}

            original_base = PILOT.BASE
            original_run_cmd = PILOT.run_cmd
            original_sync = PILOT.sync_packet_statuses
            original_strict_gate = PILOT.strict_worker_run_gate
            try:
                PILOT.BASE = base
                PILOT.run_cmd = fake_run_cmd
                PILOT.sync_packet_statuses = lambda: None
                PILOT.strict_worker_run_gate = fake_strict_gate
                verify_report = PILOT.verify(["PMC_A"])
            finally:
                PILOT.BASE = original_base
                PILOT.run_cmd = original_run_cmd
                PILOT.sync_packet_statuses = original_sync
                PILOT.strict_worker_run_gate = original_strict_gate

            manifests_used = []
            for command in commands:
                manifests_used.append(Path(command[command.index("--manifest") + 1]).resolve())
            self.assertEqual(len(set(manifests_used)), 1)
            scoped = json.loads(manifests_used[0].read_text())
            self.assertEqual(scoped["paper_ids"], ["PMC_A"])
            self.assertEqual([item["paper_id"] for item in scoped["papers"]], ["PMC_A"])
            self.assertEqual(strict_ids, [["PMC_A"]])
            self.assertEqual(
                verify_report["manifest_sha256_at_start"],
                hashlib.sha256(manifests_used[0].read_bytes()).hexdigest(),
            )
            self.assertEqual(
                verify_report["manifest_sha256_at_start"],
                verify_report["manifest_sha256_at_finish"],
            )
            self.assertTrue(verify_report["manifest_unchanged_during_verify"])


class ActivityGateRegressionTests(unittest.TestCase):
    def test_semantic_manifest_cannot_pass_with_zero_papers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(SystemExit):
                SEMANTIC.paper_ids_from_manifest(root / "missing.json")
            empty = root / "empty.json"
            empty.write_text(json.dumps({"paper_ids": []}), encoding="utf-8")
            with self.assertRaises(SystemExit):
                SEMANTIC.paper_ids_from_manifest(empty)
            malformed = root / "malformed.json"
            malformed.write_text("{", encoding="utf-8")
            with self.assertRaises(SystemExit):
                SEMANTIC.paper_ids_from_manifest(malformed)

    def test_publication_manifest_cannot_pass_with_zero_papers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(SystemExit):
                PUBLICATION.paper_ids_from_manifest(root / "missing.json")
            empty = root / "empty.json"
            empty.write_text(json.dumps({"paper_ids": []}), encoding="utf-8")
            with self.assertRaises(SystemExit):
                PUBLICATION.paper_ids_from_manifest(empty)
            blank = root / "blank.json"
            blank.write_text(json.dumps({"paper_ids": [" "]}), encoding="utf-8")
            with self.assertRaises(SystemExit):
                PUBLICATION.paper_ids_from_manifest(blank)
            malformed = root / "malformed.json"
            malformed.write_text("{", encoding="utf-8")
            with self.assertRaises(SystemExit):
                PUBLICATION.paper_ids_from_manifest(malformed)

    def test_packet_manifest_cannot_pass_with_zero_or_invalid_papers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet_root = root / "packets"
            packet_root.mkdir()
            for filename, payload in (
                ("empty.json", {"paper_ids": []}),
                ("blank.json", {"paper_ids": [" "]}),
                ("missing-key.json", {}),
            ):
                path = root / filename
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.subTest(filename=filename), self.assertRaises(SystemExit):
                    PACKET.paper_ids_from_manifest(path, packet_root)
            malformed = root / "malformed.json"
            malformed.write_text("{", encoding="utf-8")
            with self.assertRaises(SystemExit):
                PACKET.paper_ids_from_manifest(malformed, packet_root)
            with self.assertRaises(SystemExit):
                PACKET.paper_ids_from_manifest(root / "missing.json", packet_root)

    def test_non_biological_headers_are_rejected_as_species(self) -> None:
        self.assertTrue(SEMANTIC.species_is_non_biological_label("Main FTIR peaks (cm-1)"))
        self.assertTrue(PUBLICATION.suspicious_species("Components and concentration in solution"))
        self.assertFalse(SEMANTIC.species_is_non_biological_label("Listeria monocytogenes"))

    def test_non_activity_tables_are_rejected(self) -> None:
        self.assertTrue(SEMANTIC.source_table_is_non_activity("Main FTIR absorption bands and assignments"))
        self.assertTrue(PUBLICATION.source_table_is_non_activity("Mechanical properties and tensile strength"))
        self.assertFalse(SEMANTIC.source_table_is_non_activity("Antibacterial activity inhibition zone diameter (mm)"))

    def test_cell_locator_endpoint_must_be_supported_by_its_table(self) -> None:
        table_text = {
            "xml:table-wrap:1": "Antimicrobial activity MICs and MBCs (uM) MIC MBC",
            "xml:table-wrap:2": "Bacteriocins used in this study producer and source",
        }
        payload = {
            "activity_records": [
                {
                    "record_id": "wrong-mbic-cell",
                    "endpoint": "MBIC50",
                    "source_locator": [
                        {"locator": "xml:table-wrap:1:body-row=7:cell=2"},
                        {"locator": "pdf:page=7"},
                    ],
                },
                {
                    "record_id": "valid-mic-cell",
                    "endpoint": "MIC",
                    "source_locator": "xml:table-wrap:1:body-row=7:cell=2",
                },
                {
                    "record_id": "identity-only-base-table",
                    "endpoint": "agar spot complete growth inhibition titer",
                    "source_locator": "xml:p:14; xml:table-wrap:2; xml:p:33; xml:fig:2",
                },
            ],
            "toxicity_records": [],
        }

        for module in (SEMANTIC, PUBLICATION):
            issues = module.endpoint_table_support_issues(table_text, payload)
            self.assertEqual(
                [(item["record_id"], item["source_locator"]) for item in issues],
                [("wrong-mbic-cell", "xml:table-wrap:1")],
            )

    def test_shared_quantitative_table_row_requires_column_locators(self) -> None:
        payload = {
            "activity_records": [
                {
                    "record_id": "row-only-a",
                    "endpoint": "MIC",
                    "raw_value": "100",
                    "raw_unit": "ug/mL",
                    "entity": "peptide A",
                    "source_locator": "xml:table-wrap:2:row=1",
                },
                {
                    "record_id": "row-only-b",
                    "endpoint": "MIC",
                    "raw_value": "12.5",
                    "raw_unit": "% v/v",
                    "entity": "adjuvant B",
                    "source_locator": {"locator": "xml:table-wrap:2", "row": 1},
                },
                {
                    "record_id": "cell-a",
                    "endpoint": "MIC",
                    "raw_value": "4",
                    "raw_unit": "ug/mL",
                    "source_locator": "xml:table-wrap:2:row=2:cell=2",
                },
                {
                    "record_id": "cell-b",
                    "endpoint": "MBC",
                    "raw_value": "8",
                    "raw_unit": "ug/mL",
                    "source_locator": "xml:table-wrap:2:row=2:cell=3",
                },
                {
                    "record_id": "single-row-observation",
                    "endpoint": "MIC",
                    "raw_value": "16",
                    "raw_unit": "ug/mL",
                    "source_locator": "xml:table-wrap:3:row=1",
                },
            ],
            "toxicity_records": [],
        }

        for module in (SEMANTIC, PUBLICATION):
            issues = module.ambiguous_shared_table_row_issues(payload)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0]["source_locator"], "xml:table-wrap:2:row=1")
            self.assertEqual(
                issues[0]["record_ids"],
                ["row-only-a", "row-only-b"],
            )

    def test_source_located_toxicity_candidates_cannot_be_discarded_as_tableless(self) -> None:
        payload = {
            "activity_records": [],
            "toxicity_records": [],
            "excluded_machine_candidate_rows": [
                {
                    "record_id": "tox-candidate",
                    "candidate_endpoint": "percent cell death",
                    "raw_value": "7",
                    "raw_unit": "%",
                    "source_locator": [{"locator": "xml:p:35"}, {"locator": "xml:fig:2"}],
                    "reason": "not promoted because no row-level table was available",
                },
                {
                    "record_id": "activity-candidate",
                    "candidate_endpoint": "membrane permeability",
                    "source_locator": "xml:p:46",
                },
            ],
        }

        for module in (SEMANTIC, PUBLICATION):
            issues = module.source_located_toxicity_candidate_issues(payload)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0]["record_id"], "tox-candidate")
            accepted = dict(payload)
            accepted["toxicity_records"] = [
                {
                    "record_id": "accepted-toxicity",
                    "endpoint": "percent cell death",
                    "raw_value": "7",
                    "raw_unit": "%",
                    "source_locator": "xml:p:35",
                }
            ]
            self.assertEqual(module.source_located_toxicity_candidate_issues(accepted), [])

    def test_redundant_assay_concentration_must_match_top_level_record(self) -> None:
        payload = {
            "activity_records": [
                {
                    "record_id": "mismatch",
                    "concentration": "5",
                    "concentration_unit": "uM",
                    "assay_conditions": {
                        "peptide_concentration": "10",
                        "peptide_concentration_unit": "uM",
                    },
                },
                {
                    "record_id": "match",
                    "concentration": "20",
                    "concentration_unit": "μM",
                    "assay_conditions": {
                        "peptide_concentration": "20.0",
                        "peptide_concentration_unit": "uM",
                    },
                },
            ],
            "toxicity_records": [],
        }
        for module in (SEMANTIC, PUBLICATION):
            issues = module.activity_redundant_field_issues(payload)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0]["code"], "assay_condition_concentration_mismatch")
            self.assertEqual(issues[0]["record_id"], "mismatch")

    def test_activity_and_toxicity_endpoints_cannot_be_cross_classified(self) -> None:
        payload = {
            "activity_records": [
                {"record_id": "wrong-activity", "endpoint": "percent cell death"}
            ],
            "toxicity_records": [
                {"record_id": "wrong-toxicity", "endpoint": "MIC"},
                {"record_id": "valid-toxicity", "endpoint": "percent hemolysis"},
            ],
        }
        for module in (SEMANTIC, PUBLICATION):
            issues = module.evidence_kind_endpoint_issues(payload)
            self.assertEqual(
                [(item["code"], item["record_id"]) for item in issues],
                [
                    ("toxicity_endpoint_in_activity_records", "wrong-activity"),
                    ("activity_endpoint_in_toxicity_records", "wrong-toxicity"),
                ],
            )

    def test_strong_activity_measurement_tables_require_coverage(self) -> None:
        table5 = "Number of colonies forming units (CFU/mL) of L. monocytogenes within 120 h: 0 24 48 72"
        self.assertTrue(SEMANTIC.table_has_activity_measurement(table5))
        self.assertTrue(PUBLICATION.table_has_activity_measurement(table5))
        self.assertFalse(SEMANTIC.table_has_activity_measurement("Main FTIR absorption bands 3268 cm-1"))

    def test_row_and_list_locators_normalize_to_table(self) -> None:
        locator = [
            {"locator": "xml:table-wrap:2:body-row=3:cell=5"},
            {"locator": "pdf:page=8"},
        ]
        semantic_ids = {SEMANTIC.base_table_locator(item) for item in SEMANTIC.source_locator_ids(locator)}
        publication_ids = {PUBLICATION.base_table_locator(item) for item in PUBLICATION.source_locator_ids(locator)}
        self.assertIn("xml:table-wrap:2", semantic_ids)
        self.assertIn("xml:table-wrap:2", publication_ids)

    def test_nested_and_combined_locators_extract_all_tables(self) -> None:
        locator = {
            "source_locators": [
                {"locator": "xml:p:14; xml:table-wrap:2:body-row=3:cell=5; pdf:page=8"},
                {"table_locator": "xml:table-wrap:5:row=1"},
            ]
        }
        expected = {"xml:table-wrap:2", "xml:table-wrap:5"}
        self.assertEqual(SEMANTIC.table_locator_ids(locator), expected)
        self.assertEqual(PUBLICATION.table_locator_ids(locator), expected)

    def test_note_text_is_not_locator_evidence(self) -> None:
        locator = {"note": "missing from xml:table-wrap:2"}
        self.assertEqual(SEMANTIC.source_locator_ids(locator), set())
        self.assertEqual(PUBLICATION.source_locator_ids(locator), set())
        self.assertEqual(SEMANTIC.table_locator_ids(locator), set())
        self.assertEqual(PUBLICATION.table_locator_ids(locator), set())

    def test_negative_locator_fields_are_not_evidence(self) -> None:
        for key in ("missing_locator", "not_source_locator", "candidate_locator"):
            locator = {key: "xml:table-wrap:2 was mentioned but is not evidence"}
            with self.subTest(key=key):
                self.assertEqual(SEMANTIC.table_locator_ids(locator), set())
                self.assertEqual(PUBLICATION.table_locator_ids(locator), set())

    def test_shared_target_locator_and_endpoint_helpers_stay_aligned(self) -> None:
        record = {"target": "Escherichia coli"}
        self.assertEqual(SEMANTIC.target_species(record), "Escherichia coli")
        self.assertEqual(PUBLICATION.target_species(record), "Escherichia coli")
        nested_record = {"target": {"species": {"species": "Escherichia coli"}}}
        self.assertEqual(SEMANTIC.target_species(nested_record), "Escherichia coli")
        self.assertEqual(PUBLICATION.target_species(nested_record), "Escherichia coli")
        locator = {"body_locator": "xml:p:42"}
        self.assertTrue(SEMANTIC.source_locator_has_anchor(locator))
        self.assertTrue(PUBLICATION.has_locator(locator))
        for endpoint in ("MIC50", "MIC90"):
            self.assertIn(endpoint, SEMANTIC.MIC_LIKE)
            self.assertIn(endpoint, PUBLICATION.MIC_LIKE)

    def test_plural_locator_container_has_anchor(self) -> None:
        locator = {"source_locators": [{"locator": "xml:table-wrap:2:row=1"}]}
        self.assertTrue(SEMANTIC.source_locator_has_anchor(locator))
        self.assertTrue(PUBLICATION.has_locator(locator))

    def test_toxicity_records_are_part_of_table_validation(self) -> None:
        payload = {
            "activity_records": [{"record_id": "a1"}],
            "toxicity_records": [{"record_id": "t1", "source_locator": "xml:table-wrap:3"}],
        }
        semantic_ids = [row["record_id"] for row in SEMANTIC.activity_toxicity_records(payload)]
        publication_ids = [row["record_id"] for row in PUBLICATION.activity_toxicity_records(payload)]
        self.assertEqual(semantic_ids, ["a1", "t1"])
        self.assertEqual(publication_ids, ["a1", "t1"])

    def test_structured_rework_count_contract_detects_undercoverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "rwk-count",
                        "expected_observation_counts": {"xml:table-wrap:2": 2},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            payload = {
                "activity_records": [
                    {"record_id": "a1", "source_locator": "xml:table-wrap:2:row=1"}
                ],
                "toxicity_records": [],
            }

            semantic = SEMANTIC.expected_table_observation_issues(root, paper_id, payload)
            publication = PUBLICATION.expected_table_observation_issues(root, paper_id, payload)

            self.assertEqual(semantic[0]["observed_count"], 1)
            self.assertEqual(semantic[0]["expected_count"], 2)
            self.assertEqual(publication[0]["observed_count"], 1)
            self.assertEqual(publication[0]["expected_count"], 2)

    def test_non_table_rework_contract_checks_fields_kind_and_locator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            contract = {
                "ticket_id": "figure-records",
                "expected_non_table_observations": {
                    "mbic-ms-sa": {
                        "evidence_kind": "activity",
                        "endpoint": "MBIC50",
                        "raw_value": "2",
                        "raw_unit": "uM",
                        "treatment": "mastoparan-S",
                        "target_species": "Staphylococcus aureus",
                        "target_strain_or_isolate": "ATCC 25923",
                        "required_locator_any": ["xml:p:38", "xml:fig:3"],
                    },
                    "tox-ms-raw": {
                        "evidence_kind": "toxicity",
                        "endpoint": "percent cell death",
                        "raw_value": "7",
                        "raw_unit": "%",
                        "treatment": "mastoparan-S",
                        "target_species": "RAW 264.7 cells",
                        "required_locator_any": ["xml:p:35"],
                    },
                },
            }
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(contract) + "\n", encoding="utf-8"
            )
            payload = {
                "activity_records": [
                    {
                        "record_id": "mbic",
                        "endpoint": "MBIC50",
                        "raw_value": "2",
                        "raw_unit": "uM",
                        "entity": "mastoparan-S",
                        "target_species": "Staphylococcus aureus",
                        "target_strain_or_isolate": "ATCC 25923",
                        "source_locator": "xml:p:37",
                    }
                ],
                "toxicity_records": [],
            }

            for module in (SEMANTIC, PUBLICATION):
                issues = module.expected_non_table_observation_issues(
                    root, paper_id, payload
                )
                self.assertEqual(
                    {item["code"] for item in issues},
                    {
                        "non_table_observation_locator_mismatch",
                        "non_table_observation_record_count_mismatch",
                    },
                )
                repaired = {
                    "activity_records": [
                        {**payload["activity_records"][0], "source_locator": "xml:p:38"}
                    ],
                    "toxicity_records": [
                        {
                            "record_id": "tox",
                            "endpoint": "percent cell death",
                            "raw_value": "7",
                            "raw_unit": "%",
                            "treatment": "mastoparan-S",
                            "target_species": "RAW 264.7 cells",
                            "source_locator": "xml:p:35",
                        }
                    ],
                }
                self.assertEqual(
                    module.expected_non_table_observation_issues(
                        root, paper_id, repaired
                    ),
                    [],
                )

    def test_treatment_contract_reads_assayed_entity_name(self) -> None:
        for module in (SEMANTIC, PUBLICATION):
            self.assertEqual(
                module.record_contract_field(
                    {"assayed_entity": {"name": "paenidepsin A"}},
                    "treatment",
                ),
                "paenidepsin A",
            )
            self.assertEqual(
                module.record_contract_field(
                    {"entity": {"bacteriocin": "Ent412"}},
                    "treatment",
                ),
                "Ent412",
            )

    def test_non_table_contract_checks_concentration_unit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "concentration-unit",
                        "expected_non_table_observations": {
                            "viability": {
                                "evidence_kind": "toxicity",
                                "endpoint": "cell viability",
                                "raw_value": "47.23",
                                "raw_unit": "%",
                                "treatment": "SeNPs",
                                "concentration": "125",
                                "concentration_unit": "ug/mL",
                                "target_species": "Caco2 cells",
                                "required_locator_any": ["xml:p:83"],
                            }
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            record = {
                "record_id": "tox-1",
                "endpoint": "cell viability",
                "raw_value": "47.23",
                "raw_unit": "%",
                "entity": "SeNPs",
                "concentration": "125",
                "concentration_unit": "mg/mL",
                "target_species": "Caco2 cells",
                "source_locator": "xml:p:83",
            }
            for module in (SEMANTIC, PUBLICATION):
                record["concentration_unit"] = "mg/mL"
                wrong = module.expected_non_table_observation_issues(
                    root,
                    paper_id,
                    {"activity_records": [], "toxicity_records": [record]},
                )
                self.assertIn(
                    "non_table_observation_record_count_mismatch",
                    {item["code"] for item in wrong},
                )
                record["concentration_unit"] = "ug/mL"
                self.assertEqual(
                    module.expected_non_table_observation_issues(
                        root,
                        paper_id,
                        {"activity_records": [], "toxicity_records": [record]},
                    ),
                    [],
                )

    def test_malformed_rework_count_contract_is_hard_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                '{"ticket_id":"broken","expected_observation_counts":\n',
                encoding="utf-8",
            )

            semantic = SEMANTIC.expected_table_observation_issues(root, paper_id, {})
            publication = PUBLICATION.expected_table_observation_issues(root, paper_id, {})

            self.assertEqual(semantic[0]["code"], "invalid_rework_request_json")
            self.assertEqual(publication[0]["code"], "invalid_rework_request_json")
            for module in (SEMANTIC, PUBLICATION):
                self.assertIn(
                    "invalid_rework_request_json",
                    {
                        item["code"]
                        for item in module.expected_non_table_observation_issues(
                            root, paper_id, {}
                        )
                    },
                )
                self.assertIn(
                    "invalid_rework_request_json",
                    {
                        item["code"]
                        for item in module.expected_evidence_kind_count_issues(
                            root, paper_id, {}
                        )
                    },
                )

    def test_invalid_and_conflicting_count_contracts_are_hard_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            rows = [
                {"ticket_id": "base", "expected_observation_counts": {"xml:table-wrap:2": 2}},
                {"ticket_id": "conflict", "expected_observation_counts": {"xml:table-wrap:2": 3}},
                {"ticket_id": "float", "expected_observation_counts": {"xml:table-wrap:3": 1.5}},
                {"ticket_id": "negative", "expected_observation_counts": {"xml:table-wrap:4": -1}},
            ]
            (rework / "rework_requests.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows),
                encoding="utf-8",
            )

            for module in (SEMANTIC, PUBLICATION):
                issues = module.expected_table_observation_issues(root, paper_id, {})
                codes = [item["code"] for item in issues]
                self.assertIn("conflicting_expected_observation_counts", codes)
                self.assertGreaterEqual(codes.count("invalid_expected_observation_count"), 2)

    def test_expected_count_key_with_multiple_tables_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "ambiguous-table-key",
                        "expected_observation_counts": {
                            "xml:table-wrap:2; xml:table-wrap:3": 2
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            for module in (SEMANTIC, PUBLICATION):
                expected, issues = module.expected_table_observation_contract(root, paper_id)
                self.assertEqual(expected, {})
                self.assertIn(
                    "ambiguous_expected_observation_locator",
                    {item["code"] for item in issues},
                )

    def test_nested_and_flat_targets_share_observation_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "target-aliases",
                        "expected_observation_counts": {"xml:table-wrap:3": 2},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            common = {
                "endpoint": "percent hemolysis",
                "raw_value": "5",
                "raw_unit": "%",
                "source_locator": "xml:table-wrap:3:row=8:cell=3",
            }
            payload = {
                "activity_records": [
                    {
                        **common,
                        "record_id": "nested-target",
                        "target": {
                            "species": "human erythrocytes",
                            "strain_or_isolate": "donor pool",
                        },
                    }
                ],
                "toxicity_records": [
                    {
                        **common,
                        "record_id": "flat-target",
                        "target_species": "human erythrocytes",
                        "target_strain_or_isolate": "donor pool",
                    }
                ],
            }

            for module in (SEMANTIC, PUBLICATION):
                codes = {
                    item["code"]
                    for item in module.expected_table_observation_issues(root, paper_id, payload)
                }
                self.assertIn("duplicate_table_observation", codes)
                self.assertIn("table_observation_count_mismatch", codes)

    def test_source_cell_aliases_share_observation_identity(self) -> None:
        string_locator = "xml:table-wrap:3:row=8,column=3"
        structured_locator = {
            "locator": "xml:table-wrap:3",
            "row_index": 8,
            "column_index": 3,
        }
        for module in (SEMANTIC, PUBLICATION):
            self.assertEqual(
                module.source_cell_identity(string_locator),
                module.source_cell_identity(structured_locator),
            )
            self.assertEqual(
                module.source_cell_identity(string_locator),
                ["column=3", "row=8"],
            )

    def test_numeric_equivalent_cell_coordinates_are_canonical(self) -> None:
        string_locator = "xml:table-wrap:3:row=08,column=3"
        structured_locator = {
            "locator": "xml:table-wrap:3",
            "row_index": 8,
            "column_index": 3.0,
        }
        for module in (SEMANTIC, PUBLICATION):
            self.assertEqual(
                module.source_cell_identity(string_locator),
                module.source_cell_identity(structured_locator),
            )
            self.assertEqual(
                module.source_cell_identity(string_locator),
                ["column=3", "row=8"],
            )

    def test_locator_string_in_cell_field_is_not_a_coordinate(self) -> None:
        locator = {
            "source_locator": "xml:table-wrap:2",
            "row": 4,
            "column": 2,
            "cell": "xml:table-wrap:2:row=4:column=2",
        }
        for module in (SEMANTIC, PUBLICATION):
            self.assertEqual(
                module.source_cell_identity(locator),
                ["column=2", "row=4"],
            )

    def test_singular_and_plural_source_locators_are_merged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "plural-table-locator",
                        "expected_observation_counts": {"xml:table-wrap:2": 1},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            payload = {
                "activity_records": [
                    {
                        "record_id": "a1",
                        "endpoint": "MIC",
                        "raw_value": "4",
                        "raw_unit": "ug/mL",
                        "target_species": "Escherichia coli",
                        "source_locator": "pdf:page=4",
                        "source_locators": [
                            {"locator": "xml:table-wrap:2:row=1:cell=3"}
                        ],
                    }
                ],
                "toxicity_records": [],
            }

            for module in (SEMANTIC, PUBLICATION):
                self.assertEqual(
                    module.expected_table_observation_issues(root, paper_id, payload),
                    [],
                )

    def test_required_cell_locator_contract_rejects_table_only_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "cell-locators",
                        "expected_observation_counts": {"xml:table-wrap:3": 2},
                        "require_cell_locators": {"xml:table-wrap:3": True},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            payload = {
                "activity_records": [],
                "toxicity_records": [
                    {
                        "record_id": "t1",
                        "endpoint": "percent hemolysis",
                        "raw_value": "5",
                        "raw_unit": "%",
                        "target_species": "human erythrocytes",
                        "source_locator": "xml:table-wrap:3",
                    },
                    {
                        "record_id": "t2",
                        "endpoint": "percent hemolysis",
                        "raw_value": "7",
                        "raw_unit": "%",
                        "target_species": "human erythrocytes",
                        "source_locator": "xml:table-wrap:3",
                    },
                ],
            }

            for module in (SEMANTIC, PUBLICATION):
                issues = module.expected_table_observation_issues(root, paper_id, payload)
                self.assertIn(
                    "cell_locator_coverage_mismatch",
                    {item["code"] for item in issues},
                )

    def test_cell_coordinates_from_another_table_do_not_satisfy_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "table-scoped-cell-locators",
                        "expected_observation_counts": {"xml:table-wrap:3": 1},
                        "require_cell_locators": {"xml:table-wrap:3": True},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            payload = {
                "activity_records": [],
                "toxicity_records": [
                    {
                        "record_id": "t1",
                        "endpoint": "percent hemolysis",
                        "raw_value": "5",
                        "raw_unit": "%",
                        "target_species": "human erythrocytes",
                        "source_locator": "xml:table-wrap:3",
                        "source_locators": [
                            {"locator": "xml:table-wrap:4:row=1:cell=2"}
                        ],
                    }
                ],
            }

            for module in (SEMANTIC, PUBLICATION):
                issues = module.expected_table_observation_issues(root, paper_id, payload)
                self.assertIn(
                    "cell_locator_coverage_mismatch",
                    {item["code"] for item in issues},
                )

    def test_coordinates_from_another_table_segment_do_not_satisfy_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "segment-scoped-cell-locators",
                        "expected_observation_counts": {"xml:table-wrap:3": 1},
                        "require_cell_locators": {
                            "xml:table-wrap:3:row=1:cell=2": True
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            payload = {
                "activity_records": [
                    {
                        "record_id": "a1",
                        "endpoint": "MIC",
                        "raw_value": "4",
                        "raw_unit": "ug/mL",
                        "target_species": "Escherichia coli",
                        "source_locator": (
                            "xml:table-wrap:3; "
                            "xml:table-wrap:4:row=1:cell=2"
                        ),
                    }
                ],
                "toxicity_records": [],
            }

            for module in (SEMANTIC, PUBLICATION):
                issues = module.expected_table_observation_issues(root, paper_id, payload)
                self.assertIn(
                    "cell_locator_coverage_mismatch",
                    {item["code"] for item in issues},
                )

    def test_parent_coordinates_do_not_bind_to_multiple_table_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "dict-table-scope",
                        "expected_observation_counts": {"xml:table-wrap:3": 1},
                        "require_cell_locators": {
                            "xml:table-wrap:3:row=1:cell=2": True
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            payload = {
                "activity_records": [
                    {
                        "record_id": "a1",
                        "source_locator": {
                            "locator": "xml:table-wrap:3; xml:table-wrap:4",
                            "row_index": 1,
                            "column_index": 2,
                        },
                    }
                ],
                "toxicity_records": [],
            }

            for module in (SEMANTIC, PUBLICATION):
                issues = module.expected_table_observation_issues(root, paper_id, payload)
                self.assertIn(
                    "cell_locator_coverage_mismatch",
                    {item["code"] for item in issues},
                )

    def test_required_cell_locator_accepts_unique_cells(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "valid-cell-locators",
                        "expected_observation_counts": {"xml:table-wrap:3": 2},
                        "require_cell_locators": {"xml:table-wrap:3": True},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            payload = {
                "activity_records": [],
                "toxicity_records": [
                    {
                        "record_id": "t1",
                        "endpoint": "percent hemolysis",
                        "raw_value": "5",
                        "raw_unit": "%",
                        "target_species": "human erythrocytes",
                        "source_locator": "xml:table-wrap:3:body-row=1:cell=2",
                    },
                    {
                        "record_id": "t2",
                        "endpoint": "percent hemolysis",
                        "raw_value": "7",
                        "raw_unit": "%",
                        "target_species": "human erythrocytes",
                        "source_locator": {
                            "locator": "xml:table-wrap:3",
                            "row_index": 2,
                            "column_index": 2,
                        },
                    },
                ],
            }

            for module in (SEMANTIC, PUBLICATION):
                self.assertEqual(
                    module.expected_table_observation_issues(root, paper_id, payload),
                    [],
                )

    def test_exact_required_cells_reject_different_cells(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "exact-cell-locators",
                        "expected_observation_counts": {"xml:table-wrap:3": 2},
                        "require_cell_locators": {
                            "xml:table-wrap:3:row=1:cell=1": True,
                            "xml:table-wrap:3:row=2:cell=2": True,
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            payload = {
                "activity_records": [
                    {
                        "record_id": "a1",
                        "endpoint": "MIC",
                        "raw_value": "4",
                        "raw_unit": "ug/mL",
                        "target_species": "Escherichia coli",
                        "source_locator": "xml:table-wrap:3:row=9:cell=9",
                    },
                    {
                        "record_id": "a2",
                        "endpoint": "MIC",
                        "raw_value": "8",
                        "raw_unit": "ug/mL",
                        "target_species": "Escherichia coli",
                        "source_locator": "xml:table-wrap:3:row=10:cell=10",
                    },
                ],
                "toxicity_records": [],
            }

            for module in (SEMANTIC, PUBLICATION):
                issues = module.expected_table_observation_issues(root, paper_id, payload)
                mismatch = [
                    item for item in issues if item["code"] == "cell_locator_coverage_mismatch"
                ]
                self.assertEqual(len(mismatch), 1)
                self.assertEqual(
                    set(mismatch[0]["missing_required_cells"]),
                    {"row=1|column=1", "row=2|column=2"},
                )

    def test_required_cells_without_expected_count_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "missing-cell-count",
                        "require_cell_locators": {"xml:table-wrap:3": True},
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            for module in (SEMANTIC, PUBLICATION):
                issues = module.expected_table_observation_issues(
                    root,
                    paper_id,
                    {"activity_records": [], "toxicity_records": []},
                )
                self.assertIn(
                    "missing_expected_count_for_required_cells",
                    {item["code"] for item in issues},
                )

    def test_exact_required_cells_without_expected_count_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "missing-exact-cell-count",
                        "require_cell_locators": {
                            "xml:table-wrap:3:row=1:cell=1": True
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            payload = {
                "activity_records": [
                    {
                        "record_id": "a1",
                        "source_locator": "xml:table-wrap:3:row=1:cell=1",
                    }
                ],
                "toxicity_records": [],
            }

            for module in (SEMANTIC, PUBLICATION):
                issues = module.expected_table_observation_issues(root, paper_id, payload)
                self.assertIn(
                    "missing_expected_count_for_required_cells",
                    {item["code"] for item in issues},
                )

    def test_activity_summary_metadata_cannot_contradict_rows(self) -> None:
        payload = {
            "summary_counts": {
                "activity_records": 2,
                "toxicity_records": 0,
                "activity_tables_accepted": 1,
            },
            "activity_records": [
                {
                    "record_id": "a1",
                    "source_locator": "xml:table-wrap:4:row=1:cell=2",
                },
                {
                    "record_id": "a2",
                    "source_locator": "xml:table-wrap:5:row=1:cell=2",
                },
            ],
            "toxicity_records": [],
            "quality_checks": {
                "activity_field_validation": {"record_count": 1},
                "semantic_gate_relevant_activity_checks": {
                    "non_activity_source_tables_excluded": ["xml:table-wrap:5"]
                },
            },
        }

        for module in (SEMANTIC, PUBLICATION):
            codes = {
                item["code"] for item in module.activity_metadata_consistency_issues(payload)
            }
            self.assertEqual(
                codes,
                {
                    "activity_table_summary_mismatch",
                    "activity_field_validation_count_mismatch",
                    "cited_activity_table_marked_non_activity",
                    "activity_table_excluded_summary_mismatch",
                    "source_tables_checked_summary_mismatch",
                },
            )

    def test_activity_exclusion_and_source_table_counts_cannot_be_stale(self) -> None:
        payload = {
            "summary_counts": {
                "activity_records": 2,
                "toxicity_records": 0,
                "activity_tables_accepted": 2,
                "activity_tables_excluded": 1,
                "source_tables_checked": 1,
                "accepted_activity_locators": {
                    "xml:table-wrap:4": 1,
                    "xml:table-wrap:5": 1,
                },
            },
            "activity_records": [
                {"record_id": "a1", "source_locator": "xml:table-wrap:4"},
                {"record_id": "a2", "source_locator": "xml:table-wrap:5"},
            ],
            "toxicity_records": [],
            "quality_checks": {
                "semantic_gate_relevant_activity_checks": {
                    "non_activity_source_tables_excluded": []
                }
            },
        }

        for module in (SEMANTIC, PUBLICATION):
            codes = {
                item["code"] for item in module.activity_metadata_consistency_issues(payload)
            }
            self.assertIn("activity_table_excluded_summary_mismatch", codes)
            self.assertIn("source_tables_checked_summary_mismatch", codes)

    def test_declared_table_metadata_cannot_omit_summary_counters(self) -> None:
        payload = {
            "summary_counts": {
                "activity_records": 1,
                "toxicity_records": 0,
                "activity_tables_accepted": 1,
                "accepted_activity_locators": {"xml:table-wrap:4": 1},
            },
            "activity_records": [
                {"record_id": "a1", "source_locator": "xml:table-wrap:4"}
            ],
            "toxicity_records": [],
            "quality_checks": {
                "semantic_gate_relevant_activity_checks": {
                    "non_activity_source_tables_excluded": []
                }
            },
        }

        for module in (SEMANTIC, PUBLICATION):
            codes = {
                item["code"] for item in module.activity_metadata_consistency_issues(payload)
            }
            self.assertIn("activity_table_excluded_summary_mismatch", codes)
            self.assertIn("source_tables_checked_summary_mismatch", codes)

    def test_expected_cell_fields_are_bound_to_their_locator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "cell-field-binding",
                        "expected_observation_counts": {"xml:table-wrap:3": 1},
                        "require_cell_locators": {"xml:table-wrap:3": True},
                        "expected_cell_observations": {
                            "xml:table-wrap:3:body-row=1:cell=2": {
                                "endpoint": "percent hemolysis",
                                "raw_value": "90",
                                "raw_unit": "%",
                                "treatment": "WOW peptide",
                                "concentration": "5",
                            }
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            bad_payload = {
                "activity_records": [],
                "toxicity_records": [
                    {
                        "record_id": "wrong-binding",
                        "endpoint": "percent hemolysis",
                        "raw_value": "0",
                        "raw_unit": "%",
                        "entity": "WW-185",
                        "assay_conditions": {"peptide_concentration": "10"},
                        "source_locator": "xml:table-wrap:3:body-row=1:cell=2",
                    }
                ],
            }
            good_payload = json.loads(json.dumps(bad_payload))
            good = good_payload["toxicity_records"][0]
            good.update({"raw_value": "90", "entity": "WOW peptide"})
            good["assay_conditions"]["peptide_concentration"] = "5"

            for module in (SEMANTIC, PUBLICATION):
                bad_issues = module.expected_table_observation_issues(
                    root, paper_id, bad_payload
                )
                mismatch = [
                    item
                    for item in bad_issues
                    if item["code"] == "cell_observation_field_mismatch"
                ]
                self.assertEqual(len(mismatch), 1)
                self.assertEqual(
                    set(mismatch[0]["field_mismatches"]),
                    {"raw_value", "treatment", "concentration"},
                )
                self.assertEqual(
                    module.expected_table_observation_issues(
                        root, paper_id, good_payload
                    ),
                    [],
                )

    def test_expected_cell_contract_can_strengthen_with_evidence_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            locator = "xml:table-wrap:3:body-row=1:cell=2"
            base_fields = {
                "endpoint": "MIC",
                "raw_value": "8",
                "raw_unit": "uM",
                "treatment": "test peptide",
            }
            tickets = [
                {
                    "ticket_id": "initial-cell-contract",
                    "expected_observation_counts": {"xml:table-wrap:3": 1},
                    "expected_cell_observations": {locator: base_fields},
                },
                {
                    "ticket_id": "strengthened-cell-contract",
                    "expected_observation_counts": {"xml:table-wrap:3": 1},
                    "expected_cell_observations": {
                        locator: {**base_fields, "evidence_kind": "activity"}
                    },
                },
            ]
            (rework / "rework_requests.jsonl").write_text(
                "".join(json.dumps(ticket) + "\n" for ticket in tickets),
                encoding="utf-8",
            )
            row = {
                "record_id": "cell-1",
                **base_fields,
                "source_locator": locator,
            }
            wrong_payload = {"activity_records": [], "toxicity_records": [row]}
            good_payload = {"activity_records": [row], "toxicity_records": []}

            for module in (SEMANTIC, PUBLICATION):
                wrong_issues = module.expected_table_observation_issues(
                    root, paper_id, wrong_payload
                )
                kind_mismatch = [
                    item
                    for item in wrong_issues
                    if item["code"] == "cell_observation_field_mismatch"
                ]
                self.assertEqual(len(kind_mismatch), 1)
                self.assertEqual(kind_mismatch[0]["field_mismatches"], ["evidence_kind"])
                self.assertEqual(
                    module.expected_table_observation_issues(
                        root, paper_id, good_payload
                    ),
                    [],
                )

    def test_expected_cell_locator_distinguishes_timepoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            locator = "xml:table-wrap:5:row=1:cell=2:timepoint=24"
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "timepoint-cell-contract",
                        "expected_observation_counts": {"xml:table-wrap:5": 1},
                        "expected_cell_observations": {
                            locator: {
                                "endpoint": "growth",
                                "raw_value": "8.42",
                                "raw_unit": "mm",
                                "timepoint": "24 h",
                            }
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            row = {
                "record_id": "timepoint-row",
                "endpoint": "growth",
                "raw_value": "8.42",
                "raw_unit": "mm",
                "assay_conditions": {"timepoint": "24", "timepoint_unit": "h"},
                "source_locator": "xml:table-wrap:5:row=1:cell=2:timepoint=48",
            }
            for module in (SEMANTIC, PUBLICATION):
                row["source_locator"] = (
                    "xml:table-wrap:5:row=1:cell=2:timepoint=48"
                )
                wrong = module.expected_table_observation_issues(
                    root,
                    paper_id,
                    {"activity_records": [row], "toxicity_records": []},
                )
                self.assertIn(
                    "cell_observation_record_count_mismatch",
                    {item["code"] for item in wrong},
                )
                row["source_locator"] = locator
                self.assertEqual(
                    module.expected_table_observation_issues(
                        root,
                        paper_id,
                        {"activity_records": [row], "toxicity_records": []},
                    ),
                    [],
                )

    def test_expected_cell_contract_checks_evidence_role(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            locator = "xml:table-wrap:5:row=1:cell=1:timepoint=0"
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "baseline-role",
                        "expected_observation_counts": {"xml:table-wrap:5": 1},
                        "expected_cell_observations": {
                            locator: {
                                "evidence_kind": "activity",
                                "evidence_role": "untreated_control_baseline",
                                "endpoint": "Log CFU/mL viable count",
                                "raw_value": "3.47",
                                "raw_unit": "Log CFU/mL",
                            }
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            row = {
                "record_id": "baseline",
                "endpoint": "Log CFU/mL viable count",
                "raw_value": "3.47",
                "raw_unit": "Log CFU/mL",
                "source_locator": locator,
            }
            for module in (SEMANTIC, PUBLICATION):
                row.pop("evidence_role", None)
                wrong = module.expected_table_observation_issues(
                    root,
                    paper_id,
                    {"activity_records": [row], "toxicity_records": []},
                )
                mismatch = [
                    item
                    for item in wrong
                    if item["code"] == "cell_observation_field_mismatch"
                ]
                self.assertEqual(len(mismatch), 1)
                self.assertEqual(mismatch[0]["field_mismatches"], ["evidence_role"])
                row["evidence_role"] = "untreated_control_baseline"
                self.assertEqual(
                    module.expected_table_observation_issues(
                        root,
                        paper_id,
                        {"activity_records": [row], "toxicity_records": []},
                    ),
                    [],
                )

    def test_expected_evidence_kind_counts_are_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "exact-array-counts",
                        "expected_evidence_kind_counts": {
                            "activity": 2,
                            "toxicity": 1,
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            bad_payload = {
                "activity_records": [{"record_id": "a1"}],
                "toxicity_records": [{"record_id": "t1"}, {"record_id": "t2"}],
            }
            good_payload = {
                "activity_records": [{"record_id": "a1"}, {"record_id": "a2"}],
                "toxicity_records": [{"record_id": "t1"}],
            }

            for module in (SEMANTIC, PUBLICATION):
                self.assertEqual(
                    [
                        (item["evidence_kind"], item["expected_count"], item["observed_count"])
                        for item in module.expected_evidence_kind_count_issues(
                            root, paper_id, bad_payload
                        )
                    ],
                    [("activity", 2, 1), ("toxicity", 1, 2)],
                )
                self.assertEqual(
                    module.expected_evidence_kind_count_issues(
                        root, paper_id, good_payload
                    ),
                    [],
                )

    def test_main_semantic_and_publication_paths_enforce_kind_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            final = root / "papers" / paper_id / "final"
            rework = root / "packets" / paper_id / "rework"
            final.mkdir(parents=True)
            rework.mkdir(parents=True)
            locator = "xml:table-wrap:1:row=1:cell=2"
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "main-path-contract",
                        "expected_observation_counts": {"xml:table-wrap:1": 1},
                        "expected_cell_observations": {
                            locator: {
                                "evidence_kind": "toxicity",
                                "endpoint": "MIC",
                                "raw_value": "8",
                                "raw_unit": "ug/mL",
                            }
                        },
                        "expected_evidence_kind_counts": {
                            "activity": 2,
                            "toxicity": 0,
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            activity = {
                "activity_records": [
                    {
                        "record_id": "a1",
                        "endpoint": "MIC",
                        "raw_value": "8",
                        "raw_unit": "ug/mL",
                        "target_species": "Escherichia coli",
                        "source_locator": locator,
                    }
                ],
                "toxicity_records": [],
            }
            (final / "activity_toxicity_evidence.json").write_text(
                json.dumps(activity), encoding="utf-8"
            )
            (final / "review_report.json").write_text("{}", encoding="utf-8")
            (final / "mechanism_ontology_record.json").write_text(
                json.dumps({"mechanism_claims": []}), encoding="utf-8"
            )
            (final / "database_record_verification.json").write_text(
                "{}", encoding="utf-8"
            )

            semantic_codes = {
                item["code"] for item in SEMANTIC.check_paper(root, paper_id)["issues"]
            }
            self.assertIn("cell_observation_field_mismatch", semantic_codes)
            self.assertIn("evidence_kind_record_count_mismatch", semantic_codes)

            manifest = root / "manifest.json"
            report = root / "publication.json"
            manifest.write_text(
                json.dumps({"paper_ids": [paper_id]}), encoding="utf-8"
            )
            old_argv = sys.argv
            try:
                sys.argv = [
                    "check_three_layer_publication_quality.py",
                    "--root",
                    str(root),
                    "--manifest",
                    str(manifest),
                    "--json-out",
                    str(report),
                ]
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(PUBLICATION.main(), 2)
            finally:
                sys.argv = old_argv
            risks = json.loads(report.read_text(encoding="utf-8"))["risk_counts"]
            self.assertIn("cell_observation_field_mismatch", risks)
            self.assertIn("evidence_kind_record_count_mismatch", risks)

    def test_expected_cell_fields_reject_typos_and_empty_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "bad-cell-fields",
                        "expected_observation_counts": {"xml:table-wrap:3": 1},
                        "expected_cell_observations": {
                            "xml:table-wrap:3:row=1:cell=2": {
                                "raw_value": "",
                                "raw_vlaue": "",
                            }
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            payload = {
                "activity_records": [
                    {
                        "record_id": "a1",
                        "source_locator": "xml:table-wrap:3:row=1:cell=2",
                    }
                ],
                "toxicity_records": [],
            }

            for module in (SEMANTIC, PUBLICATION):
                issues = module.expected_table_observation_issues(root, paper_id, payload)
                self.assertIn(
                    "invalid_expected_cell_observation_fields",
                    {item["code"] for item in issues},
                )

    def test_mirrored_observation_cannot_satisfy_exact_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_id = "PMC_TEST"
            rework = root / "packets" / paper_id / "rework"
            rework.mkdir(parents=True)
            (rework / "rework_requests.jsonl").write_text(
                json.dumps(
                    {
                        "ticket_id": "rwk-count",
                        "expected_observation_counts": {"xml:table-wrap:3": 2},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            row = {
                "record_id": "same-source-cell",
                "endpoint": "percent hemolysis",
                "raw_value": "5",
                "raw_unit": "%",
                "target": {"species": "erythrocytes"},
                "assay_conditions": {"peptide_concentration": "100"},
                "source_locator": {
                    "locator": "xml:table-wrap:3",
                    "row_index": 8,
                    "column_index": 3,
                },
            }
            mirrored = json.loads(json.dumps(row))
            mirrored["source_locator"]["basis"] = "compatibility mirror"
            payload = {
                "activity_records": [dict(row)],
                "toxicity_records": [mirrored],
            }

            semantic = SEMANTIC.expected_table_observation_issues(root, paper_id, payload)
            publication = PUBLICATION.expected_table_observation_issues(root, paper_id, payload)

            self.assertIn("duplicate_table_observation", {item["code"] for item in semantic})
            self.assertIn("table_observation_count_mismatch", {item["code"] for item in semantic})
            self.assertIn("duplicate_table_observation", {item["code"] for item in publication})
            self.assertIn("table_observation_count_mismatch", {item["code"] for item in publication})

    def test_nested_database_conflict_and_reason_are_recognized(self) -> None:
        conflict = {
            "status": "source_conflict",
            "identity_assessment": {
                "cross_database_conflict": "machine row is a treatment combination, not a standalone identity"
            },
        }
        unresolved = {
            "status": "sequence_modified_not_normalized",
            "not_source_verified_reason": "canonical sequence is absent from the primary-source packet",
        }
        self.assertTrue(SEMANTIC.conflict_context_present(conflict))
        self.assertTrue(SEMANTIC.unresolved_reason_present(unresolved))

    def test_normalization_contract_rejects_invalid_status_and_missing_safe_fields(self) -> None:
        payload = {
            "activity_records": [
                {
                    "record_id": "bad-status",
                    "raw_value": "62.5",
                    "raw_unit": "ug/mL",
                    "normalized_value": None,
                    "normalized_unit": None,
                    "normalization_status": "not_normalized_no_safe_conversion",
                },
                {
                    "record_id": "missing-direct-value",
                    "raw_value": "20",
                    "raw_unit": "ug/mL",
                    "normalized_value": None,
                    "normalized_unit": "ug/mL",
                    "normalization_status": "direct",
                },
            ],
            "toxicity_records": [],
        }

        for module in (SEMANTIC, PUBLICATION):
            codes = {item["code"] for item in module.activity_normalization_issues(payload)}
            self.assertIn("invalid_normalization_status", codes)
            self.assertIn("missing_normalized_value", codes)

    def test_direct_scalar_normalization_must_preserve_value(self) -> None:
        payload = {
            "activity_records": [],
            "toxicity_records": [
                {
                    "record_id": "wrong-direct-value",
                    "raw_value": "0",
                    "raw_unit": "%",
                    "normalized_value": "90",
                    "normalized_unit": "%",
                    "normalization_status": "direct",
                },
                {
                    "record_id": "statistics-projection",
                    "raw_value": "15.16 ± 0.76",
                    "raw_unit": "mm",
                    "normalized_value": "15.16",
                    "normalized_unit": "mm",
                    "normalization_status": "direct",
                },
                {
                    "record_id": "wrong-direct-value-and-unit",
                    "raw_value": "0",
                    "raw_unit": "%",
                    "normalized_value": "90",
                    "normalized_unit": "ug/mL",
                    "normalization_status": "direct",
                },
                {
                    "record_id": "valid-conversion",
                    "raw_value": "1",
                    "raw_unit": "mg/L",
                    "normalized_value": "1000",
                    "normalized_unit": "ug/L",
                    "normalization_status": "converted",
                },
            ],
        }

        for module in (SEMANTIC, PUBLICATION):
            issues = module.activity_normalization_issues(payload)
            mismatches = [
                item for item in issues if item["code"] == "direct_normalized_value_mismatch"
            ]
            unit_mismatches = [
                item for item in issues if item["code"] == "direct_normalized_unit_mismatch"
            ]
            self.assertEqual(
                [item["record_id"] for item in mismatches],
                ["wrong-direct-value", "wrong-direct-value-and-unit"],
            )
            self.assertEqual(
                [item["record_id"] for item in unit_mismatches],
                ["wrong-direct-value-and-unit"],
            )

    def test_direct_or_converted_normalized_value_must_be_scalar(self) -> None:
        payload = {
            "activity_records": [
                {
                    "record_id": "nested-direct",
                    "raw_value": "8",
                    "raw_unit": "ug/mL",
                    "normalized_value": {
                        "value": "8",
                        "unit": "ug/mL",
                        "normalization_status": "direct",
                    },
                    "normalized_unit": "ug/mL",
                    "normalization_status": "direct",
                },
                {
                    "record_id": "list-converted",
                    "raw_value": "8",
                    "raw_unit": "ug/mL",
                    "normalized_value": ["8"],
                    "normalized_unit": "uM",
                    "normalization_status": "converted",
                },
            ],
            "toxicity_records": [],
        }
        for module in (SEMANTIC, PUBLICATION):
            issues = module.activity_normalization_issues(payload)
            self.assertEqual(
                [(item["code"], item["record_id"]) for item in issues],
                [
                    ("invalid_normalized_value_shape", "nested-direct"),
                    ("invalid_normalized_value_shape", "list-converted"),
                ],
            )


if __name__ == "__main__":
    unittest.main()
