#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from collections import Counter
from pathlib import Path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SUPERVISOR = load_module(
    "supervise_remaining_200_strict_campaign",
    Path(__file__).with_name("supervise_remaining_200_strict_campaign.py"),
)
PARALLEL = load_module(
    "supervise_remaining_200_parallel_campaign",
    Path(__file__).with_name("supervise_remaining_200_parallel_campaign.py"),
)


class Remaining200StrictSupervisorTests(unittest.TestCase):
    def test_parallel_scheduler_reserves_fresh_paper_capacity(self) -> None:
        state = {
            "papers": [
                {
                    "paper_id": "R1",
                    "queue_index": 1,
                    "workflow_status": "needs_targeted_semantic_rework",
                },
                {
                    "paper_id": "R2",
                    "queue_index": 2,
                    "workflow_status": "needs_targeted_semantic_rework",
                },
                {
                    "paper_id": "N1",
                    "queue_index": 3,
                    "workflow_status": "ready_for_six_worker_review",
                },
                {
                    "paper_id": "N2",
                    "queue_index": 4,
                    "workflow_status": "ready_for_six_worker_review",
                },
                {
                    "paper_id": "N3",
                    "queue_index": 5,
                    "workflow_status": "ready_for_six_worker_review",
                },
            ]
        }
        selected = PARALLEL.eligible_launch_rows(
            state,
            active_papers=set(),
            attempts=Counter({"R1": 3, "R2": 1}),
            max_attempts_per_paper=12,
            available_slots=4,
            max_parallel_papers=4,
            max_rework_parallel=1,
            active_rework_count=0,
        )
        self.assertEqual(
            [row["paper_id"] for row in selected],
            ["R2", "N1", "N2", "N3"],
        )

    def test_parallel_scheduler_never_duplicates_active_paper(self) -> None:
        state = {
            "papers": [
                {
                    "paper_id": "N1",
                    "queue_index": 1,
                    "workflow_status": "ready_for_six_worker_review",
                },
                {
                    "paper_id": "N2",
                    "queue_index": 2,
                    "workflow_status": "ready_for_six_worker_review",
                },
            ]
        }
        selected = PARALLEL.eligible_launch_rows(
            state,
            active_papers={"N1"},
            attempts=Counter(),
            max_attempts_per_paper=12,
            available_slots=2,
            max_parallel_papers=2,
            max_rework_parallel=1,
            active_rework_count=0,
        )
        self.assertEqual([row["paper_id"] for row in selected], ["N2"])

    def test_parallel_scheduler_deduplicates_malformed_state_rows(
        self,
    ) -> None:
        duplicate = {
            "paper_id": "R1",
            "queue_index": 1,
            "workflow_status": "needs_targeted_semantic_rework",
        }
        state = {
            "papers": [
                duplicate,
                dict(duplicate),
                {
                    "paper_id": "R2",
                    "queue_index": 2,
                    "workflow_status": "needs_targeted_semantic_rework",
                },
                {
                    "paper_id": "R3",
                    "queue_index": 3,
                    "workflow_status": "needs_targeted_semantic_rework",
                },
                {
                    "paper_id": "R4",
                    "queue_index": 4,
                    "workflow_status": "needs_targeted_semantic_rework",
                },
                {
                    "paper_id": "N1",
                    "queue_index": 5,
                    "workflow_status": "ready_for_six_worker_review",
                },
            ]
        }
        selected = PARALLEL.eligible_launch_rows(
            state,
            active_papers=set(),
            attempts=Counter(),
            max_attempts_per_paper=12,
            available_slots=4,
            max_parallel_papers=4,
            max_rework_parallel=1,
            active_rework_count=0,
        )
        self.assertEqual(
            [row["paper_id"] for row in selected],
            ["R1", "R2", "R3", "N1"],
        )

    def test_parallel_scheduler_adapts_to_large_rework_backlog(self) -> None:
        state = {
            "papers": [
                {
                    "paper_id": f"R{index}",
                    "queue_index": index,
                    "workflow_status": "needs_targeted_semantic_rework",
                }
                for index in range(1, 6)
            ]
            + [
                {
                    "paper_id": "N1",
                    "queue_index": 10,
                    "workflow_status": "ready_for_six_worker_review",
                },
                {
                    "paper_id": "N2",
                    "queue_index": 11,
                    "workflow_status": "ready_for_six_worker_review",
                },
            ]
        }
        selected = PARALLEL.eligible_launch_rows(
            state,
            active_papers=set(),
            attempts=Counter(),
            max_attempts_per_paper=12,
            available_slots=4,
            max_parallel_papers=4,
            max_rework_parallel=1,
            active_rework_count=0,
        )
        self.assertEqual(
            [row["paper_id"] for row in selected],
            ["R1", "R2", "R3", "N1"],
        )

    def test_parallel_scheduler_reserves_fresh_lane_even_with_high_rework_cap(
        self,
    ) -> None:
        state = {
            "papers": [
                {
                    "paper_id": f"R{index}",
                    "queue_index": index,
                    "workflow_status": "needs_targeted_semantic_rework",
                }
                for index in range(1, 6)
            ]
            + [
                {
                    "paper_id": "N1",
                    "queue_index": 10,
                    "workflow_status": "ready_for_six_worker_review",
                }
            ]
        }
        selected = PARALLEL.eligible_launch_rows(
            state,
            active_papers=set(),
            attempts=Counter(),
            max_attempts_per_paper=12,
            available_slots=4,
            max_parallel_papers=4,
            max_rework_parallel=4,
            active_rework_count=0,
        )
        self.assertEqual(
            [row["paper_id"] for row in selected],
            ["R1", "R2", "R3", "N1"],
        )

    def test_nonterminal_order_prioritizes_rework_then_queue_index(self) -> None:
        state = {
            "papers": [
                {
                    "paper_id": "C",
                    "queue_index": 1,
                    "workflow_status": SUPERVISOR.TERMINAL_STATUS,
                },
                {
                    "paper_id": "B",
                    "queue_index": 8,
                    "workflow_status": "ready_for_six_worker_review",
                },
                {
                    "paper_id": "A",
                    "queue_index": 9,
                    "workflow_status": "needs_targeted_semantic_rework",
                },
                {
                    "paper_id": "D",
                    "queue_index": 2,
                    "workflow_status": "ready_for_six_worker_review",
                },
            ]
        }
        rows = SUPERVISOR.ordered_nonterminal_rows(state)
        self.assertEqual([row["paper_id"] for row in rows], ["A", "D", "B"])

    def test_status_markdown_exposes_denominator_and_quality_boundary(self) -> None:
        payload = {
            "generated_at": "2026-07-27T00:00:00Z",
            "supervisor_pid": 123,
            "supervisor_started_at": "2026-07-27T00:00:00Z",
            "frozen_denominator": 200,
            "terminal_scientific_review_complete": 1,
            "remaining_nonterminal": 199,
            "strict_material_ready": 200,
            "open_ticket_count": 0,
            "active_paper": "PMC_TEST",
            "active_attempt": 1,
            "sweep_number": 1,
            "workflow_status_counts": {
                "ready_for_six_worker_review": 199,
                SUPERVISOR.TERMINAL_STATUS: 1,
            },
            "latest_result": None,
            "terminal_contract": "six workers plus leader and verifier",
            "state_path": "state.json",
            "journal_path": "journal.jsonl",
        }
        text = SUPERVISOR.render_status_markdown(payload)
        self.assertIn("Frozen queue: **200**", text)
        self.assertIn("Remaining nonterminal: **199**", text)
        self.assertIn("PMC_TEST", text)
        self.assertIn("six workers plus leader and verifier", text)

    def test_immediate_retry_is_bounded_and_only_for_incomplete_work(self) -> None:
        rework = {"workflow_status": "needs_targeted_semantic_rework"}
        ready = {"workflow_status": "ready_for_six_worker_review"}
        terminal = {"workflow_status": SUPERVISOR.TERMINAL_STATUS}
        common = {
            "total_attempts": 1,
            "max_consecutive_attempts": 3,
            "max_attempts_per_paper": 12,
        }
        self.assertTrue(
            SUPERVISOR.should_immediately_retry(
                rework, consecutive_attempt=1, **common
            )
        )
        self.assertFalse(
            SUPERVISOR.should_immediately_retry(
                rework, consecutive_attempt=3, **common
            )
        )
        self.assertFalse(
            SUPERVISOR.should_immediately_retry(
                ready, consecutive_attempt=1, **common
            )
        )
        self.assertFalse(
            SUPERVISOR.should_immediately_retry(
                terminal, consecutive_attempt=1, **common
            )
        )


if __name__ == "__main__":
    unittest.main()
