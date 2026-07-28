#!/usr/bin/env python3
"""Focused regression tests for the local review workflow helpers."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("review_server", HERE / "review_server.py")
review_server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review_server)


class ReviewServerTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.old = {
            "ROOT": review_server.ROOT,
            "WORKSHEET": review_server.WORKSHEET,
            "VERDICTS": review_server.VERDICTS,
            "REVIEW_LOG": review_server.REVIEW_LOG,
            "ALLOWED_FILE_ROOTS": review_server.ALLOWED_FILE_ROOTS,
        }
        review_server.ROOT = self.root
        review_server.WORKSHEET = self.root / "HUMAN_REVIEW_worksheet.tsv"
        review_server.VERDICTS = self.root / "review_verdicts.json"
        review_server.REVIEW_LOG = self.root / "review_log.jsonl"
        review_server.ALLOWED_FILE_ROOTS = (self.root / "papers", self.root / "paper_packets")
        review_server.WORKSHEET.write_text(
            "review_id\tpriority\tpaper_id\tdoi\tdatabase\terror_type\t"
            "db_peptide\tdb_organism\tdb_endpoint\tdb_value\tsource_table\t"
            "source_row\tsource_col\tsource_value\treason\tlocal_pdf\n"
            "R001\tDUAL\tpaper1\t10.1/x\tDB\tvalue_mismatch\tpep\torg\tMIC\t1\t"
            "1\trow\tcol\t2\treason\tpapers/paper1/source/paper.pdf\n",
            encoding="utf-8",
        )

    def tearDown(self):
        for key, value in self.old.items():
            setattr(review_server, key, value)
        self.tmpdir.cleanup()

    def test_save_verdict_writes_metadata_snapshot_and_log(self):
        count = review_server.save_verdict(
            "R001",
            {"verdict": "confirmed", "severity": "major", "reviewer": "alice", "notes": ""},
            client_host="127.0.0.1",
        )
        self.assertEqual(count, 1)
        saved = json.loads(review_server.VERDICTS.read_text(encoding="utf-8"))
        entry = saved["R001"]
        self.assertEqual(entry["verdict"], "confirmed")
        self.assertEqual(entry["severity"], "major")
        self.assertEqual(entry["source"], "human_review_ui")
        self.assertEqual(entry["provenance"], "manual_ui_save")
        self.assertTrue(entry["is_human_verdict"])
        self.assertIn("reviewed_at", entry)
        log = [json.loads(x) for x in review_server.REVIEW_LOG.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["review_id"], "R001")
        self.assertEqual(log[0]["entry"]["verdict"], "confirmed")

    def test_save_rejects_confirmed_without_severity(self):
        with self.assertRaises(ValueError):
            review_server.save_verdict("R001", {"verdict": "confirmed", "severity": ""})
        self.assertFalse(review_server.VERDICTS.exists())

    def test_save_rejects_unknown_review_id(self):
        with self.assertRaises(ValueError):
            review_server.save_verdict("R999", {"verdict": "confirmed", "severity": "major"})

    def test_resolve_allowed_file_blocks_traversal(self):
        allowed = self.root / "papers" / "paper1" / "source"
        allowed.mkdir(parents=True)
        pdf = allowed / "paper.pdf"
        pdf.write_bytes(b"%PDF")
        secret = self.root / "secret.txt"
        secret.write_text("nope", encoding="utf-8")
        self.assertEqual(review_server.resolve_allowed_file("papers/paper1/source/paper.pdf"), pdf.resolve())
        with self.assertRaises(PermissionError):
            review_server.resolve_allowed_file("papers/../secret.txt")
        with self.assertRaises(PermissionError):
            review_server.resolve_allowed_file(str(secret))


if __name__ == "__main__":
    unittest.main()
