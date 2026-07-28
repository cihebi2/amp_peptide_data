#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pipeline_v2.deepmine.grok_readonly_review import PaperEvidenceTools


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class GrokReadonlyReviewTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> tuple[Path, Path]:
        pilot = root / "pipeline_v2/deepmine/dbaasp_strict_pilot"
        paper = pilot / "papers/PMC_TEST"
        packet = pilot / "packets/PMC_TEST"
        (paper / "source/supplementary").mkdir(parents=True)
        (paper / "source/paper.xml").write_text("<article>x</article>", encoding="utf-8")
        (paper / "source/supplementary/s1.txt").write_text("x", encoding="utf-8")
        write_json(paper / "work/intake.json", {"x": 1})
        write_json(paper / "final/a.json", {"x": 1})
        write_json(packet / "final/a.json", {"x": 1})
        write_json(packet / "extracted/e.json", {"x": 1})
        write_json(packet / "analysis/a.json", {"x": 1})
        write_json(packet / "database/d.json", {"x": 1})
        (packet / "rework").mkdir(parents=True)
        (packet / "rework/requests.jsonl").write_text('{"x":1}\n', encoding="utf-8")
        write_json(
            pilot / "worker_logs/PMC_TEST/run_sequence_latest.json",
            {"x": 1},
        )
        write_json(
            pilot / "reports/PMC_TEST_strict_acceptance_audit_latest.json",
            {"x": 1},
        )
        campaign = pilot / "reports/remaining_200_campaign"
        (campaign / "PMC_TEST").mkdir(parents=True)
        return pilot, campaign

    def test_path_allowlist_blocks_workspace_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pilot, campaign = self.build_fixture(root)
            (root / ".env").write_text("secret", encoding="utf-8")
            tools = PaperEvidenceTools(root, pilot, campaign, "PMC_TEST")
            with self.assertRaises(ValueError):
                tools.resolve(".env")

    def test_coverage_requires_direct_final_and_runtime_reads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pilot, campaign = self.build_fixture(root)
            tools = PaperEvidenceTools(root, pilot, campaign, "PMC_TEST")
            self.assertTrue(tools.coverage_failures())

            direct = tools.coverage_requirements()["direct_read_files"]
            for path in direct:
                tools.read_json(path)
            tools.search(
                "x",
                "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/"
                "PMC_TEST/source",
            )
            for path in (
                "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/"
                "PMC_TEST/work/intake.json",
                "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/"
                "PMC_TEST/extracted/e.json",
                "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/"
                "PMC_TEST/analysis/a.json",
                "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/"
                "PMC_TEST/database/d.json",
                "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/"
                "PMC_TEST/rework/requests.jsonl",
            ):
                tools.read_json(path)
            self.assertEqual(tools.coverage_failures(), [])


if __name__ == "__main__":
    unittest.main()
