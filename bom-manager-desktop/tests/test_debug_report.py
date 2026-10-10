"""Privacy, accuracy, rotation and UI tests for the BOM Manager Debug Report."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bom_debug


class PrivacyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.reporter = bom_debug.DebugReporter(self.temp.name, "1.5.0")
        self.reporter.register_secret("my-super-secret-token-12345678")
        self.doc = {
            "schemaVersion": 1,
            "project": "PRIVATE PROJECT NAME",
            "items": [
                {"id": "1", "category": "CONTROL", "name": "CUSTOMER CONFIDENTIAL MOTOR",
                 "qty": 2, "unitPrice": 300},
                {"id": "2", "name": "SECRET PRIVATE ITEM", "qty": 1, "unitPrice": None},
            ],
            "wiring": [],
            "purchases": [],
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_scrubs_secrets_email_and_home(self):
        sample = ("Bearer abcSECRET_TOKEN_987 "
                  "github_pat_ABCDEFGHabcdefgh987654321 "
                  "my-super-secret-token-12345678 "
                  "alice@example.com C:\\Users\\Alice\\Documents\\abc "
                  "/var/tmp/secret/location/test.py "
                  "D:\\Build\\Projects\\private\\app.py "
                  "https://site.example/path?access_token=abcdef&other=1")
        text = self.reporter.scrub(sample)
        for leaked in ("my-super-secret-token-12345678", "abcSECRET_TOKEN_987",
                       "github_pat_ABC", "alice@example.com", "Users\\Alice",
                       "access_token=abcdef", "/var/tmp/secret",
                       "D:\\Build\\Projects\\private"):
            self.assertNotIn(leaked, text)
        self.assertIn("[REDACTED]", text)

    def test_report_contains_no_bom_rows_or_secrets(self):
        self.reporter.event(
            "ERROR", "github", "UPLOAD_FAILED",
            "token=my-super-secret-token-12345678 Bearer abcQWE123")
        self.reporter.event("INFO", "app", "STARTED", "เริ่มโปรแกรม")
        with tempfile.TemporaryDirectory() as target:
            out = Path(target) / "debug.json"
            report = self.reporter.export_json(
                out, self.doc, dirty=True, remote_loaded=False, github_token_present=True)
            raw = out.read_text(encoding="utf-8")
        self.assertEqual(report["report_type"], "CraneVehicleBOMManager-Debug")
        self.assertEqual(report["state"]["counts"]["bom_items"], 2)
        self.assertEqual(report["state"]["counts"]["without_price"], 1)
        self.assertTrue(report["state"]["github_credential_configured"])
        for leaked in ("my-super-secret-token", "CUSTOMER CONFIDENTIAL MOTOR",
                       "PRIVATE PROJECT NAME", "SECRET PRIVATE ITEM", "abcQWE123"):
            self.assertNotIn(leaked, raw)
        self.assertTrue(any(e["code"] == "UPLOAD_FAILED" for e in report["events"]))

    def test_exception_produces_safe_stack_without_locals(self):
        try:
            raise RuntimeError("Bearer my-super-secret-token-12345678")
        except RuntimeError as exc:
            result = self.reporter.exception("github", "EXCEPTION", exc)
        self.assertEqual(result["level"], "ERROR")
        self.assertNotIn("my-super-secret-token-12345678", result["detail"])
        self.assertIn("RuntimeError", result["detail"])

    def test_invalid_document_returns_fail_not_exception(self):
        report = self.reporter.snapshot({"items": [{"id": "", "qty": -1}]})
        self.assertTrue(any(c["status"] == "FAIL" for c in report["checks"]))
        self.assertIsNone(report["state"]["counts"])

    def test_retention_and_clear(self):
        import bom_debug as mod
        old = mod.MAX_LOG_BYTES
        try:
            mod.MAX_LOG_BYTES = 600
            for i in range(25):
                self.reporter.event("INFO", "test", "WRITE", "event-" + str(i))
            self.assertTrue((self.reporter.folder / "events.previous.jsonl").exists())
            self.assertLessEqual(len(self.reporter.read_events(limit=8)), 8)
            self.reporter.clear_logs()
            self.assertEqual(self.reporter.read_events(), [])
        finally:
            mod.MAX_LOG_BYTES = old


class DebugQtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        from bom_qt_theme import apply_theme
        cls.app = QApplication.instance() or QApplication([])
        apply_theme(cls.app)

    def setUp(self):
        from bom_qt import BOMWindow
        self.temp = tempfile.TemporaryDirectory()
        self.reporter = bom_debug.DebugReporter(self.temp.name, "1.5.0")
        self.win = BOMWindow(auto_load=False, debugger=self.reporter)

    def tearDown(self):
        self.win.close()
        self.win.deleteLater()
        self.temp.cleanup()

    def test_debug_page_and_data_summary(self):
        self.assertEqual(self.win.stack.count(), 6)
        self.assertEqual(len(self.win.nav_buttons), 6)
        self.win.payload = {
            "schemaVersion": 1, "project": "SECRET DESIGN",
            "items": [{"id": "1", "name": "HUB 1500W", "qty": 2, "unitPrice": None}],
        }
        self.reporter.event("ERROR", "export", "EXPORT_FAILED", "test failure")
        self.win.show_page(5)
        self.assertEqual(self.win.stack.currentIndex(), 5)
        self.assertIn("ERROR 1", self.win.debug_summary.text())
        self.assertGreaterEqual(self.win.debug_checks.rowCount(), 3)
        self.assertGreaterEqual(self.win.debug_events.rowCount(), 2)
        self.assertTrue(any(
            self.win.debug_events.item(i, 3).text() == "EXPORT_FAILED"
            for i in range(self.win.debug_events.rowCount())))
        data = self.win.refresh_diagnostics()
        self.assertEqual(data["state"]["counts"]["without_price"], 1)

    def test_logging_does_not_modify_bom(self):
        self.win.payload = {
            "schemaVersion": 1, "project": "test",
            "items": [{"id": "1", "name": "Widget", "qty": 1, "unitPrice": None}],
        }
        before = json.dumps(self.win.payload, ensure_ascii=False, sort_keys=True)
        self.win.refresh_diagnostics()
        after = json.dumps(self.win.payload, ensure_ascii=False, sort_keys=True)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
