#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


def load_controller():
    path = Path(__file__).with_name("remaining_200_strict_controller.py")
    spec = importlib.util.spec_from_file_location("remaining_200_strict_controller", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTROLLER = load_controller()


class Remaining200StrictControllerTests(unittest.TestCase):
    def test_worker_runtime_requires_canonical_order_and_exact_codex_exec(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_pilot = CONTROLLER.PILOT
            try:
                CONTROLLER.PILOT = Path(tmp)
                paper_id = "PMC_TEST"
                report_dir = (
                    CONTROLLER.PILOT / "worker_logs" / paper_id
                )
                report_dir.mkdir(parents=True)
                reports = [
                    {
                        "worker": worker,
                        "returncode": 0,
                        "codex_session_id": f"session-{index}",
                        "codex_model": "gpt-5.5",
                        "codex_reasoning_effort": "xhigh",
                        "command": ["codex", "exec"],
                        "started_at": (
                            f"2026-07-27T00:{index:02d}:00Z"
                        ),
                        "finished_at": (
                            f"2026-07-27T00:{index:02d}:30Z"
                        ),
                    }
                    for index, worker in enumerate(
                        CONTROLLER.WORKERS, start=1
                    )
                ]
                sequence = report_dir / "run_sequence_latest.json"
                sequence.write_text(
                    json.dumps({"reports": reports}), encoding="utf-8"
                )
                self.assertTrue(
                    CONTROLLER.worker_runtime_state(paper_id)[
                        "strict_six_worker_runtime_pass"
                    ]
                )

                reports[0], reports[1] = reports[1], reports[0]
                sequence.write_text(
                    json.dumps({"reports": reports}), encoding="utf-8"
                )
                self.assertFalse(
                    CONTROLLER.worker_runtime_state(paper_id)[
                        "strict_six_worker_runtime_pass"
                    ]
                )

                reports[0], reports[1] = reports[1], reports[0]
                reports[0]["command"] = ["python", "contains codex exec"]
                sequence.write_text(
                    json.dumps({"reports": reports}), encoding="utf-8"
                )
                self.assertFalse(
                    CONTROLLER.worker_runtime_state(paper_id)[
                        "strict_six_worker_runtime_pass"
                    ]
                )
            finally:
                CONTROLLER.PILOT = original_pilot

    def test_media_inventory_includes_tiff_and_cif_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            xml = Path(tmp) / "paper.xml"
            xml.write_text(
                """<article xmlns:xlink="http://www.w3.org/1999/xlink">
                <supplementary-material>
                  <media xlink:href="figure-s1.TIFF"/>
                  <media xlink:href="structure-s2.cif"/>
                </supplementary-material>
                </article>""",
                encoding="utf-8",
            )
            CONTROLLER.declared_supplement_names.cache_clear()
            names = CONTROLLER.declared_supplement_names(str(xml))
            self.assertEqual(names, ("figure-s1.TIFF", "structure-s2.cif"))

    def test_owner_response_requires_a_passing_validation_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_root = CONTROLLER.ROOT
            try:
                CONTROLLER.ROOT = Path(tmp)
                artifact = Path(tmp) / "leader_validation.json"
                response = {"validation_artifacts": ["leader_validation.json"]}

                self.assertFalse(CONTROLLER.response_validation_passes(response))
                artifact.write_text(
                    json.dumps({"passed": False, "blocking_failure_count": 1}),
                    encoding="utf-8",
                )
                self.assertFalse(CONTROLLER.response_validation_passes(response))
                artifact.write_text(
                    json.dumps({"passed": True, "blocking_failure_count": 0}),
                    encoding="utf-8",
                )
                self.assertTrue(CONTROLLER.response_validation_passes(response))
                response["validation_artifacts"] = {
                    "leader_validator": "leader_validation.json"
                }
                self.assertTrue(CONTROLLER.response_validation_passes(response))
            finally:
                CONTROLLER.ROOT = original_root

    def test_recovered_worklist_supplement_clears_stale_snapshot_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            (source / "supplementary").mkdir(parents=True)
            xml = source / "paper.xml"
            xml.write_text(
                """<article xmlns:xlink="http://www.w3.org/1999/xlink">
                <supplementary-material><media xlink:href="s1.tif"/></supplementary-material>
                </article>""",
                encoding="utf-8",
            )
            (source / "paper.pdf").write_bytes(b"%PDF-1.4\n")
            (source / "supplementary/s1.tif").write_bytes(b"II*\x00")
            original_pilot = CONTROLLER.PILOT
            original_worklist_map = CONTROLLER.worklist_map
            try:
                CONTROLLER.PILOT = Path(tmp) / "pilot"
                CONTROLLER.worklist_map = lambda: {"PMC_TEST": (xml, "xml")}
                CONTROLLER.declared_supplement_names.cache_clear()
                material = CONTROLLER.source_material_state(
                    {
                        "paper_id": "PMC_TEST",
                        "source_snapshot": {
                            "source_dir": str(source),
                            "xml_exists": True,
                            "pdf_exists": True,
                            "missing_declared_supplements": ["s1.tif"],
                        },
                    }
                )
            finally:
                CONTROLLER.PILOT = original_pilot
                CONTROLLER.worklist_map = original_worklist_map

            self.assertEqual(material["missing_declared_supplements"], [])
            self.assertTrue(material["strict_material_ready"])

    def test_rework_action_runs_one_owner_before_worker6(self) -> None:
        row = {
            "paper_id": "PMC_TEST",
            "queue_index": 1,
            "workflow_status": "needs_targeted_semantic_rework",
            "tickets": {
                "ordered_missing_owner_workers": ["worker-2", "worker-3"],
                "ready_owner_workers": [],
            },
        }
        action = CONTROLLER.next_action(row)
        self.assertEqual(action["action"], "run_next_ticket_owner_then_recheck_leader_validator")
        self.assertIn("worker-2", action["command"])
        self.assertNotIn("worker-6", action["command"])

        row["tickets"]["ordered_missing_owner_workers"] = []
        row["tickets"]["ready_owner_workers"] = ["worker-2", "worker-3"]
        action = CONTROLLER.next_action(row)
        self.assertEqual(action["action"], "all_ticket_owners_validated_run_fresh_worker6_only")
        self.assertIn("worker-6", action["command"])


if __name__ == "__main__":
    unittest.main()
