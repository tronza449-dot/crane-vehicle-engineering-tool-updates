"""Cross-device GitHub sync, crash-safe local draft, and BOM-linked purchasing."""
import base64
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication, QComboBox
from bom_qt import BOMWindow, PURCHASE_FIELDS, RecordDialog


class CloudBOMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.window = BOMWindow(auto_load=False)
        self.window.auto_sync_timer.stop()
        self.window.auto_sync_retry_timer.stop()
        self.window.remote_refresh_timer.stop()
        self.window.cache_path = Path(self.folder.name) / "draft.json"
        self.window.payload = {
            "schemaVersion": 1, "project": "Cross device project", "currency": "THB",
            "items": [
                {"id": "2", "name": "QS 1500W hub motor", "qty": 2, "unit": "ตัว",
                 "category": "ระบบขับเคลื่อน", "unitPrice": 3000,
                 "supplier": "Test Supplier", "link": "https://example.org/motor"},
                {"id": "3", "name": "ESP32-S3", "qty": 1, "unit": "ตัว",
                 "category": "ระบบควบคุมและสื่อสาร", "unitPrice": None},
            ],
            "wiring": [], "purchases": [],
        }
        self.window.sha = "base_sha"
        self.window.token = "TEST_TOKEN_NEVER_REAL"
        self.window.dirty = False
        self.window.revision = 0
        self.window.set_auto_sync(True)
        self.window.render_all()

    def tearDown(self):
        self.window.auto_sync_timer.stop()
        self.window.auto_sync_retry_timer.stop()
        self.window.remote_refresh_timer.stop()
        self.window.close()
        self.window.deleteLater()

    def inline_job(self, action, success, failed=None, context="background"):
        try:
            success(action())
        except Exception as exc:
            (failed or self.window._message_error)(str(exc))

    def test_purchase_picker_populates_from_bom_without_retyping(self):
        dialog = RecordDialog("เพิ่มการจัดซื้อ", PURCHASE_FIELDS,
                              {"status": "วางแผน"}, self.window)
        selector = dialog.widgets["itemId"]
        self.assertIsInstance(selector, QComboBox)
        self.assertFalse(selector.isEditable())
        self.assertEqual(selector.count(), 3)
        selector.setCurrentIndex(selector.findData("2"))
        v = dialog.get_values()
        self.assertEqual(v["itemId"], "2")
        self.assertEqual(v["description"], "QS 1500W hub motor")
        self.assertEqual(v["qty"], "2")
        self.assertEqual(v["unitPrice"], "3000")
        self.assertEqual(v["supplier"], "Test Supplier")
        self.assertEqual(v["link"], "https://example.org/motor")
        # Purchase qty/price are copies that can be adjusted independently.
        dialog.widgets["qty"].setText("4")
        dialog.widgets["unitPrice"].setText("2700")
        self.assertEqual(self.window.payload["items"][0]["qty"], 2)
        self.assertEqual(self.window.payload["items"][0]["unitPrice"], 3000)
        self.assertEqual(dialog.get_values()["unitPrice"], "2700")
        selector.setCurrentIndex(selector.findData("3"))
        self.assertEqual(dialog.get_values()["unitPrice"], "")
        self.assertEqual(dialog.get_values()["description"], "ESP32-S3")
        dialog.close()

    def test_autosave_pushes_once_with_expected_sha(self):
        calls = []
        def fake_api(method="GET", payload=None, token=None, url=None):
            self.assertEqual(token, "TEST_TOKEN_NEVER_REAL")
            calls.append((method, payload))
            if method == "GET":
                return {"sha": "base_sha"}
            self.assertEqual(payload["sha"], "base_sha")
            self.assertEqual(payload["branch"], "main")
            exported = json.loads(base64.b64decode(payload["content"]))
            self.assertEqual(exported["items"][0]["name"], "Updated motor")
            return {"content": {"sha": "new_sha"}}

        with patch("bom_qt.github_api", side_effect=fake_api), \
             patch.object(self.window, "_job", side_effect=self.inline_job):
            self.window.payload["items"][0]["name"] = "Updated motor"
            self.window.changed()
            self.assertTrue(self.window.dirty)
            self.assertTrue(self.window.cache_path.exists())
            self.window._autosync_if_needed()

        self.assertEqual([x[0] for x in calls], ["GET", "PUT"])
        self.assertFalse(self.window.dirty)
        self.assertEqual(self.window.sha, "new_sha")
        self.assertTrue(self.window.last_git_ok)
        self.assertIn("ซิงก์ GitHub แล้ว", self.window.sync_state.text())

    def test_conflict_pauses_cloud_sync_and_keeps_offline_draft(self):
        calls = []
        def fake_api(method="GET", payload=None, token=None, url=None):
            calls.append(method)
            return {"sha": "another_device_changed"}
        with patch("bom_qt.github_api", side_effect=fake_api), \
             patch.object(self.window, "_job", side_effect=self.inline_job):
            self.window.payload["items"][0]["name"] = "My unsynced changes"
            self.window.changed()
            self.window._autosync_if_needed()
            self.window._autosync_if_needed()
        self.assertEqual(calls, ["GET"])
        self.assertTrue(self.window.sync_paused_conflict)
        self.assertTrue(self.window.dirty)
        self.assertEqual(self.window.sha, "base_sha")
        recovered = json.loads(self.window.cache_path.read_text(encoding="utf-8"))
        self.assertTrue(recovered["dirty"])
        self.assertEqual(recovered["payload"]["items"][0]["name"],
                         "My unsynced changes")

    def test_other_machine_refreshes_from_github_only_if_clean(self):
        remote = json.loads(json.dumps(self.window.payload))
        remote["items"][0]["name"] = "Updated from laptop 1"
        content = base64.b64encode(
            json.dumps(remote, ensure_ascii=False).encode()).decode()
        calls = []
        def fake_api(method="GET", payload=None, token=None, url=None):
            calls.append(method)
            return {"sha": "laptop_one_sha", "content": content}
        with patch("bom_qt.github_api", side_effect=fake_api), \
             patch.object(self.window, "_job", side_effect=self.inline_job):
            self.window._refresh_remote_if_clean()
            self.assertEqual(self.window.payload["items"][0]["name"],
                             "Updated from laptop 1")
            self.assertEqual(self.window.sha, "laptop_one_sha")
            self.assertFalse(self.window.dirty)
            self.window.payload["items"][0]["name"] = "Laptop two draft"
            self.window.changed()
            self.window._refresh_remote_if_clean()
        self.assertEqual(calls, ["GET"])
        self.assertEqual(self.window.payload["items"][0]["name"],
                         "Laptop two draft")

    def test_in_flight_remote_load_never_overwrites_new_draft(self):
        remote = json.loads(json.dumps(self.window.payload))
        remote["items"][0]["name"] = "Older remote state"
        content = base64.b64encode(
            json.dumps(remote, ensure_ascii=False).encode()).decode()
        def fetch_while_editing(action, success, failed=None, context="github"):
            # Represents the user editing after the fetch starts but
            # before its result is applied to the UI.
            self.window.payload["items"][0]["name"] = "New local edit"
            self.window.changed()
            success(action())
        with patch("bom_qt.github_api",
                   return_value={"sha": "remote", "content": content}), \
             patch.object(self.window, "_job", side_effect=fetch_while_editing):
            self.window.load_remote(silent=True)
        self.assertEqual(self.window.payload["items"][0]["name"], "New local edit")
        self.assertTrue(self.window.sync_paused_conflict)
        self.assertTrue(self.window.dirty)

    def test_offline_error_preserves_draft_for_retry(self):
        def fail_api(*args, **kwargs):
            raise OSError("Network disconnected")
        with patch("bom_qt.github_api", side_effect=fail_api), \
             patch.object(self.window, "_job", side_effect=self.inline_job):
            self.window.payload["items"][0]["name"] = "Keep offline"
            self.window.changed()
            self.window._autosync_if_needed()
        self.assertTrue(self.window.dirty)
        self.assertFalse(self.window.sync_paused_conflict)
        self.assertEqual(json.loads(self.window.cache_path.read_text())["payload"]
                         ["items"][0]["name"], "Keep offline")

    def test_disabling_autosync_keeps_manual_save_available(self):
        self.window.set_auto_sync(False)
        self.window.payload["items"][0]["name"] = "Manually saved"
        self.window.changed()
        self.assertFalse(self.window.auto_sync_timer.isActive())
        with patch.object(self.window, "save_remote") as save:
            self.window._autosync_if_needed()
            save.assert_not_called()
        self.assertTrue(self.window.sync_btn.isEnabled())


if __name__ == "__main__":
    unittest.main()
