import unittest

from pipeline_v2.deepmine import restart_remaining_200_parallel_at_drain as HANDOFF


class Remaining200ParallelHandoffTests(unittest.TestCase):
    def test_proc_stat_parser_reads_state_and_raw_exit_code(self) -> None:
        fields = ["0"] * 50
        fields[0] = "Z"
        fields[49] = "256"
        state, raw_exit_code = HANDOFF.parse_proc_stat(
            "123 (campaign worker) " + " ".join(fields)
        )
        self.assertEqual(state, "Z")
        self.assertEqual(raw_exit_code, 256)

    def test_attempt_set_requires_every_matching_finish(self) -> None:
        expected = {
            ("PMC1", 1),
            ("PMC2", 3),
        }
        rows = [
            {
                "event": "paper_attempt_finished",
                "paper_id": "PMC1",
                "attempt": 1,
            },
            {
                "event": "paper_attempt_finished",
                "paper_id": "PMC2",
                "attempt": 2,
            },
        ]
        self.assertFalse(HANDOFF.attempt_set_finished(expected, rows))
        rows.append(
            {
                "event": "paper_attempt_finished",
                "paper_id": "PMC2",
                "attempt": 3,
            }
        )
        self.assertTrue(HANDOFF.attempt_set_finished(expected, rows))

    def test_campaign_child_detection_is_narrow(self) -> None:
        self.assertTrue(
            HANDOFF.is_campaign_command(
                [
                    "/usr/bin/python3",
                    "/workspace/pipeline_v2/deepmine/"
                    "run_remaining_200_strict_campaign.py",
                    "--paper-id",
                    "PMC1",
                ]
            )
        )
        self.assertFalse(
            HANDOFF.is_campaign_command(
                [
                    "/usr/bin/python3",
                    "/workspace/pipeline_v2/deepmine/"
                    "dbaasp_strict_pilot.py",
                    "status",
                ]
            )
        )

    def test_new_attempt_start_after_checkpoint_is_detected(self) -> None:
        rows = [
            {
                "event": "paper_attempt_finished",
                "paper_id": "PMC1",
                "attempt": 1,
            },
            {
                "event": "paper_attempt_started",
                "paper_id": "PMC2",
                "attempt": 1,
            },
        ]
        self.assertTrue(HANDOFF.has_attempt_start(rows, checkpoint=1))
        self.assertFalse(HANDOFF.has_attempt_start(rows, checkpoint=2))

    def test_anonymous_zombie_completes_exact_missing_boundary(self) -> None:
        completed = HANDOFF.complete_campaign_child_map(
            {"PMC1", "PMC2"},
            {"PMC1": 101},
            [202],
        )
        self.assertEqual(completed, {"PMC1": 101, "PMC2": 202})
        with self.assertRaisesRegex(RuntimeError, "anonymous zombie"):
            HANDOFF.complete_campaign_child_map(
                {"PMC1", "PMC2", "PMC3"},
                {"PMC1": 101},
                [202],
            )


if __name__ == "__main__":
    unittest.main()
