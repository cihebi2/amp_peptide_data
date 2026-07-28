#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from copy import deepcopy
from pathlib import Path


def load_campaign():
    path = Path(__file__).with_name("run_remaining_200_strict_campaign.py")
    spec = importlib.util.spec_from_file_location("run_remaining_200_strict_campaign", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CAMPAIGN = load_campaign()


def leader_payload(paper_id: str, evidence: str) -> dict:
    return {
        "paper_id": paper_id,
        "verdict": "PASS",
        "publication_grade_ready": True,
        "independently_reviewed_primary_source": True,
        "reviewed_every_current_final_record": True,
        "recursive_authority_boundary_false": True,
        "fallback_release_boundary_preserved": True,
        "field_checks": [
            {
                "check_id": check_id,
                "status": "PASS",
                "summary": "independently checked",
                "evidence_paths": [evidence],
                "source_locators": [],
            }
            for check_id in sorted(CAMPAIGN.REQUIRED_LEADER_CHECKS)
        ],
        "blocking_findings": [],
        "cautions": [],
    }


class Remaining200StrictCampaignTests(unittest.TestCase):
    def test_paper_lock_allows_distinct_papers_and_rejects_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_campaign_dir = CAMPAIGN.CAMPAIGN_DIR
            try:
                CAMPAIGN.CAMPAIGN_DIR = Path(tmp)
                with CAMPAIGN.paper_campaign_lock("PMC_A"):
                    with CAMPAIGN.paper_campaign_lock("PMC_B"):
                        pass
                    with self.assertRaisesRegex(RuntimeError, "PMC_A"):
                        with CAMPAIGN.paper_campaign_lock("PMC_A"):
                            pass
            finally:
                CAMPAIGN.CAMPAIGN_DIR = original_campaign_dir

    def test_biology_safety_rejection_classifier_is_narrow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stderr = Path(tmp) / "stderr.log"
            stderr.write_text(
                "ERROR: Invalid prompt: we've limited access to this content "
                "for safety reasons. "
                "https://openai.com/index/preparing-for-future-ai-capabilities-in-biology",
                encoding="utf-8",
            )
            self.assertTrue(
                CAMPAIGN.codex_biology_safety_access_rejected(
                    {"stderr_path": str(stderr)}
                )
            )
            stderr.write_text("ERROR: quota exceeded", encoding="utf-8")
            self.assertFalse(
                CAMPAIGN.codex_biology_safety_access_rejected(
                    {"stderr_path": str(stderr)}
                )
            )

    def test_grok_fallback_runs_only_after_classified_codex_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stderr = Path(tmp) / "stderr.log"
            stderr.write_text(
                "ERROR: Invalid prompt: we've limited access to this content "
                "for safety reasons. biology",
                encoding="utf-8",
            )
            runtime = {"stderr_path": str(stderr)}
            expected = (Path(tmp) / "audit.json", {"review_session_id": "grok:r1"})
            original_codex = CAMPAIGN.run_structured_codex
            original_grok = CAMPAIGN.run_grok_structured_review
            try:
                def reject(*_args, **_kwargs):
                    raise CAMPAIGN.StructuredReviewRunError("rejected", runtime)

                def grok(**kwargs):
                    self.assertEqual(kwargs["paper_id"], "PMC_TEST")
                    self.assertIn("biology-content safety", kwargs["fallback_reason"])
                    return expected

                CAMPAIGN.run_structured_codex = reject
                CAMPAIGN.run_grok_structured_review = grok
                actual = CAMPAIGN.run_structured_review(
                    "PMC_TEST",
                    "leader_semantic_auditor",
                    Path(tmp) / "schema.json",
                    "review",
                    30,
                    True,
                )
                self.assertEqual(actual, expected)

                stderr.write_text("ERROR: quota exceeded", encoding="utf-8")
                with self.assertRaises(CAMPAIGN.StructuredReviewRunError):
                    CAMPAIGN.run_structured_review(
                        "PMC_TEST",
                        "leader_semantic_auditor",
                        Path(tmp) / "schema.json",
                        "review",
                        30,
                        True,
                    )
            finally:
                CAMPAIGN.run_structured_codex = original_codex
                CAMPAIGN.run_grok_structured_review = original_grok

    def test_leader_pass_is_fail_closed_on_required_boolean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "evidence.json"
            evidence.write_text("{}", encoding="utf-8")
            original_root = CAMPAIGN.ROOT
            try:
                CAMPAIGN.ROOT = root
                payload = leader_payload("PMC_TEST", "evidence.json")
                self.assertEqual(
                    CAMPAIGN.validate_leader_payload("PMC_TEST", payload), []
                )
                payload["reviewed_every_current_final_record"] = False
                self.assertIn(
                    "leader_verdict_semantics_invalid",
                    CAMPAIGN.validate_leader_payload("PMC_TEST", payload),
                )
            finally:
                CAMPAIGN.ROOT = original_root

    def test_leader_fail_requires_concrete_owned_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "evidence.json"
            evidence.write_text("{}", encoding="utf-8")
            original_root = CAMPAIGN.ROOT
            try:
                CAMPAIGN.ROOT = root
                payload = leader_payload("PMC_TEST", "evidence.json")
                payload.update(verdict="FAIL", publication_grade_ready=False)
                payload["field_checks"][0]["status"] = "FAIL"
                payload["blocking_findings"] = [
                    {
                        "finding_id": "missing-table-row",
                        "owner_worker": "worker-2",
                        "reason": "one quantitative source row was omitted",
                        "evidence_paths": ["evidence.json"],
                        "source_locators": ["xml:table-wrap:1:row=2"],
                        "required_actions": ["restore the exact row"],
                        "acceptance_checks": ["row count equals source count"],
                    }
                ]
                self.assertEqual(
                    CAMPAIGN.validate_leader_payload("PMC_TEST", payload), []
                )
                payload["blocking_findings"][0]["owner_worker"] = "worker-6"
                self.assertIn(
                    "blocking_finding_owner_invalid",
                    CAMPAIGN.validate_leader_payload("PMC_TEST", payload),
                )
            finally:
                CAMPAIGN.ROOT = original_root

    def test_verifier_pass_requires_all_terminal_proofs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "evidence.json"
            evidence.write_text("{}", encoding="utf-8")
            payload = {
                "paper_id": "PMC_TEST",
                "verdict": "PASS",
                "independently_reviewed_primary_source": True,
                "independently_reviewed_current_finals": True,
                "leader_audit_is_supported": True,
                "six_worker_runtime_is_valid": True,
                "worker6_is_fresh": True,
                "zero_open_tickets": True,
                "mechanical_acceptance_passes": True,
                "recursive_authority_boundary_false": True,
                "fallback_release_boundary_preserved": True,
                "checks": [
                    {
                        "check_id": f"check-{index}",
                        "status": "PASS",
                        "summary": "verified",
                        "evidence_paths": ["evidence.json"],
                    }
                    for index in range(9)
                ],
                "blocking_reasons": [],
            }
            original_root = CAMPAIGN.ROOT
            try:
                CAMPAIGN.ROOT = root
                self.assertEqual(
                    CAMPAIGN.validate_verifier_payload("PMC_TEST", payload), []
                )
                payload["worker6_is_fresh"] = False
                self.assertIn(
                    "verifier_verdict_semantics_invalid",
                    CAMPAIGN.validate_verifier_payload("PMC_TEST", payload),
                )
            finally:
                CAMPAIGN.ROOT = original_root

    def test_partial_canonical_failure_resumes_from_first_bad_worker(self) -> None:
        reports = [
            {
                "worker": "worker-1",
                "returncode": 0,
                "codex_session_id": "session-1",
                "codex_model": "gpt-5.5",
                "codex_reasoning_effort": "xhigh",
                "command": ["codex", "exec"],
            },
            {
                "worker": "worker-2",
                "returncode": 1,
                "codex_session_id": "session-2",
                "codex_model": "gpt-5.5",
                "codex_reasoning_effort": "xhigh",
                "command": ["codex", "exec"],
            },
        ]
        self.assertEqual(
            CAMPAIGN.canonical_resume_workers_from_reports(reports),
            ["worker-2", "worker-3", "worker-4", "worker-5", "worker-6"],
        )

        reports[1]["returncode"] = 0
        self.assertEqual(
            CAMPAIGN.canonical_resume_workers_from_reports(reports),
            ["worker-3", "worker-4", "worker-5", "worker-6"],
        )

        complete = [
            {
                "worker": worker,
                "returncode": 0,
                "codex_session_id": f"session-{index}",
                "codex_model": "gpt-5.5",
                "codex_reasoning_effort": "xhigh",
                "command": ["codex", "exec"],
            }
            for index, worker in enumerate(
                CAMPAIGN.CANONICAL_WORKERS, start=1
            )
        ]
        out_of_order = deepcopy(complete)
        out_of_order[0], out_of_order[1] = (
            out_of_order[1],
            out_of_order[0],
        )
        self.assertEqual(
            CAMPAIGN.canonical_resume_workers_from_reports(out_of_order),
            CAMPAIGN.CANONICAL_WORKERS,
        )
        duplicate_session = deepcopy(complete)
        duplicate_session[1]["codex_session_id"] = "session-1"
        self.assertEqual(
            CAMPAIGN.canonical_resume_workers_from_reports(
                duplicate_session
            ),
            ["worker-2", "worker-3", "worker-4", "worker-5", "worker-6"],
        )

    def test_mechanical_failure_with_open_tickets_skips_redundant_leader(self) -> None:
        row = {"tickets": {"open_ticket_count": 3}}
        self.assertFalse(CAMPAIGN.should_run_leader_review(1, row))
        self.assertTrue(CAMPAIGN.should_run_leader_review(0, row))
        self.assertTrue(
            CAMPAIGN.should_run_leader_review(
                1, {"tickets": {"open_ticket_count": 0}}
            )
        )

    def test_exact_open_leader_finding_is_not_staged_twice(self) -> None:
        finding = {
            "finding_id": "same-source-row",
            "owner_worker": "worker-2",
            "reason": "the same quantitative source row is still omitted",
            "source_locators": ["xml:table-wrap:1:row=2"],
            "evidence_paths": ["evidence.json"],
            "required_actions": ["restore the exact row"],
            "acceptance_checks": ["row count equals source count"],
        }
        existing_open = [
            {
                "owner_worker": "worker-2",
                "reason": finding["reason"],
                "required_actions": finding["required_actions"],
                "acceptance_checks": finding["acceptance_checks"],
                "leader_finding_id": finding["finding_id"],
                "source_locators": finding["source_locators"],
                "evidence_paths": finding["evidence_paths"],
            }
        ]
        self.assertEqual(
            CAMPAIGN.new_audit_findings([finding], existing_open),
            [],
        )
        changed = deepcopy(finding)
        changed["acceptance_checks"] = ["row count and value both match source"]
        self.assertEqual(
            CAMPAIGN.new_audit_findings([changed], existing_open),
            [changed],
        )
        changed_locator = deepcopy(finding)
        changed_locator["source_locators"] = ["xml:table-wrap:1:row=3"]
        self.assertEqual(
            CAMPAIGN.new_audit_findings([changed_locator], existing_open),
            [changed_locator],
        )

    def test_process_exception_finalizes_new_process_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original_dir = CAMPAIGN.CAMPAIGN_DIR
            original_impl = CAMPAIGN._process_paper_unwrapped
            try:
                CAMPAIGN.CAMPAIGN_DIR = Path(tmp)

                def explode(_args, paper_id):
                    process_dir = (
                        CAMPAIGN.CAMPAIGN_DIR / paper_id / "process_TEST"
                    )
                    process_dir.mkdir(parents=True)
                    CAMPAIGN.atomic_write_json(
                        process_dir / "process_report.json",
                        {
                            "paper_id": paper_id,
                            "process_id": "TEST",
                            "started_at": "2026-07-27T00:00:00Z",
                            "finished_at": None,
                            "status": "in_progress",
                            "rounds": [],
                            "commands": [],
                        },
                    )
                    raise RuntimeError("synthetic process failure")

                CAMPAIGN._process_paper_unwrapped = explode
                with self.assertRaisesRegex(RuntimeError, "synthetic"):
                    CAMPAIGN.process_paper(Namespace(), "PMC_TEST")
                report = json.loads(
                    (
                        Path(tmp)
                        / "PMC_TEST/process_TEST/process_report.json"
                    ).read_text(encoding="utf-8")
                )
                self.assertEqual(
                    report["status"], "campaign_exception_fail_closed"
                )
                self.assertIsNotNone(report["finished_at"])
                self.assertIn("synthetic process failure", report["error"])
            finally:
                CAMPAIGN.CAMPAIGN_DIR = original_dir
                CAMPAIGN._process_paper_unwrapped = original_impl


if __name__ == "__main__":
    unittest.main()
