"""Deterministic integration tests: two Windows PCs sharing one GitHub BOM.

No real credentials or network requests are used. The fake GitHub repository
enforces SHA optimistic concurrency and keeps all BOM/Wiring/Purchasing records.
"""
import base64
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class FakeGitHub:
    def __init__(self):
        self.document = {
            "schemaVersion": 1, "project": "Test Shared Crane BOM", "currency": "THB",
            "items": [{"id": "1", "category": "ระบบขับเคลื่อน",
                       "name": "Hub Motor", "qty": 2, "unitPrice": 4000}],
            "wiring": [], "purchases": [],
        }
        self.number = 1
        self.offline = False

    @property
    def sha(self):
        return f"sha-{self.number}"

    def api(self, method="GET", payload=None, token=None, url=None):
        if self.offline:
            raise RuntimeError("No Internet")
        if method == "GET":
            value = base64.b64encode(json.dumps(
                self.document, ensure_ascii=False).encode()).decode("ascii")
            return {"sha": self.sha, "content": value}
        if method == "PUT":
            if payload["sha"] != self.sha:
                raise RuntimeError("GitHub SHA mismatch conflict")
            self.document = json.loads(
                base64.b64decode(payload["content"]).decode("utf-8"))
            self.number += 1
            return {"content": {"sha": self.sha}}
        raise ValueError(method)


class SharedBOMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        from bom_qt_theme import apply_theme
        cls.app = QApplication.instance() or QApplication([])
        apply_theme(cls.app)

    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.repo = FakeGitHub()
        self.windows = []
        import bom_qt
        self.api_patch = patch.object(bom_qt, "github_api", self.repo.api)
        self.api_patch.start()
        self.get_token_patch = patch.object(
            bom_qt.keyring, "get_password", return_value="FAKE_TEST_TOKEN")
        self.get_token_patch.start()
        self.cache_path_patch = patch.object(
            bom_qt.BOMWindow, "_cache_path",
            side_effect=lambda: Path(self.storage.name) /
            f"computer-{len(self.windows)+1}.json")
        self.cache_path_patch.start()

    def tearDown(self):
        for window in self.windows:
            window.auto_sync_timer.stop()
            window.auto_sync_retry_timer.stop()
            window.remote_refresh_timer.stop()
            window.dirty = False
            window.close()
            window.deleteLater()
        self.api_patch.stop()
        self.get_token_patch.stop()
        self.cache_path_patch.stop()
        self.storage.cleanup()

    def new_pc(self):
        from bom_qt import BOMWindow
        window = BOMWindow(auto_load=False)
        window.auto_sync_enabled = True
        def immediate_job(task, success, failure=None, context="github"):
            try:
                result = task()
            except Exception as exc:
                (failure or window._message_error)(str(exc))
            else:
                success(result)
        window._job = immediate_job
        self.windows.append(window)
        window.load_remote(silent=True)
        self.assertFalse(window.dirty)
        return window

    def test_push_from_pc1_is_pulled_by_pc2_including_purchase_and_wiring(self):
        one, two = self.new_pc(), self.new_pc()
        self.assertEqual(one.sha, two.sha)
        one.payload["items"][0]["name"] = "Updated motor from PC1"
        one.payload["wiring"].append({
            "id": "w1", "from": "ESP32", "to": "VESC", "signal": "CAN"
        })
        one.payload["purchases"].append({
            "id": "p1", "itemId": "1", "description": "Hub motor",
            "qty": 2, "unitPrice": 4300, "status": "รอสั่งซื้อ"
        })
        one.changed()
        self.assertTrue(one.dirty)
        self.assertTrue(one.cache_path.exists())
        one._autosync_if_needed()
        self.assertFalse(one.dirty)
        self.assertEqual(self.repo.document["items"][0]["name"],
                         "Updated motor from PC1")
        two._refresh_remote_if_clean()
        self.assertEqual(two.payload, self.repo.document)
        self.assertEqual(len(two.payload["purchases"]), 1)
        self.assertEqual(len(two.payload["wiring"]), 1)
        self.assertFalse(two.dirty)

    def test_concurrent_edits_do_not_overwrite_remote_or_local(self):
        one, two = self.new_pc(), self.new_pc()
        one.payload["items"][0]["name"] = "PC1"
        one.changed()
        two.payload["items"][0]["name"] = "PC2"
        two.changed()
        one._autosync_if_needed()
        self.assertEqual(self.repo.document["items"][0]["name"], "PC1")
        two._autosync_if_needed()
        self.assertTrue(two.dirty)
        self.assertTrue(two.sync_paused_conflict)
        self.assertEqual(two.payload["items"][0]["name"], "PC2")
        self.assertEqual(self.repo.document["items"][0]["name"], "PC1")
        self.assertEqual(json.loads(two.cache_path.read_text(
            encoding="utf-8"))["payload"]["items"][0]["name"], "PC2")

    def test_offline_edits_are_kept_for_retry(self):
        machine = self.new_pc()
        machine.payload["items"][0]["name"] = "New offline draft"
        machine.changed()
        self.repo.offline = True
        machine._autosync_if_needed()
        self.assertTrue(machine.dirty)
        self.assertEqual(self.repo.document["items"][0]["name"], "Hub Motor")
        self.assertTrue(machine.cache_path.exists())
        self.repo.offline = False
        machine._autosync_if_needed()
        self.assertFalse(machine.dirty)
        self.assertEqual(self.repo.document["items"][0]["name"],
                         "New offline draft")

    def test_loading_over_dirty_data_makes_local_recovery_backup(self):
        from PySide6.QtWidgets import QMessageBox
        machine = self.new_pc()
        machine.payload["items"][0]["name"] = "Unsaved local work"
        machine.changed()
        original_sha = machine.sha
        with patch.object(QMessageBox, "question",
                          return_value=QMessageBox.StandardButton.Yes):
            machine.load_remote(silent=False)
        self.assertFalse(machine.dirty)
        self.assertEqual(machine.sha, original_sha)
        recovery = list(machine.cache_path.parent.joinpath("recovery").glob("*.json"))
        self.assertEqual(len(recovery), 1)
        saved = json.loads(recovery[0].read_text(encoding="utf-8"))
        self.assertEqual(saved["items"][0]["name"], "Unsaved local work")

    def test_purchase_picker_uses_bom_id_and_price_without_modifying_item(self):
        from bom_qt import RecordDialog, PURCHASE_FIELDS
        machine = self.new_pc()
        before = copy.deepcopy(machine.payload["items"])
        dlg = RecordDialog("เพิ่มการจัดซื้อ", PURCHASE_FIELDS, {}, machine)
        picker = dlg.widgets["itemId"]
        self.assertFalse(picker.isEditable())
        idx = picker.findData("1")
        self.assertGreater(idx, 0)
        picker.setCurrentIndex(idx)
        values = dlg.get_values()
        self.assertEqual(values["itemId"], "1")
        self.assertEqual(values["description"], "Hub Motor")
        self.assertEqual(values["qty"], "2")
        self.assertEqual(values["unitPrice"], "4000")
        self.assertEqual(machine.payload["items"], before)
        dlg.close()


    def test_purchase_picker_excludes_existing_orders_but_allows_own_edit(self):
        from bom_qt import RecordDialog, PURCHASE_FIELDS
        machine = self.new_pc()
        order = {"id": "po1", "itemId": "1", "description": "Hub motor",
                 "qty": 2, "unitPrice": 4000, "status": "วางแผน"}
        machine.payload["purchases"].append(order)
        new_dialog = RecordDialog("เพิ่มการจัดซื้อ", PURCHASE_FIELDS, {}, machine)
        self.assertEqual(new_dialog.widgets["itemId"].findData("1"), -1)
        new_dialog.close()
        edit_dialog = RecordDialog("แก้ไขการจัดซื้อ", PURCHASE_FIELDS,
                                   order, machine)
        self.assertGreater(edit_dialog.widgets["itemId"].findData("1"), 0)
        edit_dialog.close()
        machine.payload["purchases"].clear()
        new_dialog = RecordDialog("เพิ่มการจัดซื้อ", PURCHASE_FIELDS, {}, machine)
        self.assertGreater(new_dialog.widgets["itemId"].findData("1"), 0)
        new_dialog.close()

    def test_reorder_buttons_persist_actual_item_order_without_changing_ids(self):
        from PySide6.QtCore import Qt
        machine = self.new_pc()
        machine.payload["items"].append({
            "id": "2", "category": "ระบบขับเคลื่อน",
            "name": "VESC", "qty": 1, "unitPrice": 3000
        })
        machine.changed()
        machine.group_mode.setCurrentIndex(1)  # continuous order
        self.assertEqual(machine.bom_table.rowCount(), 2)
        self.assertEqual(machine.bom_table.item(1, 0).data(
            Qt.ItemDataRole.UserRole), 1)
        machine.bom_table.selectRow(1)
        machine.move_bom_item(-1)
        self.assertEqual([x["id"] for x in machine.payload["items"]], ["2", "1"])
        self.assertTrue(machine.dirty)
        self.assertEqual(machine.bom_table.item(0, 0).text(), "2")
        machine._autosync_if_needed()
        self.assertEqual([x["id"] for x in self.repo.document["items"]],
                         ["2", "1"])
        self.assertEqual({x["id"] for x in machine.payload["items"]}, {"1", "2"})

    def test_startup_automatically_loads_latest_clean_remote(self):
        machine = self.new_pc()
        self.repo.document["items"][0]["name"] = "Latest from GitHub"
        self.repo.number += 1
        machine._startup_sync()
        self.assertEqual(machine.payload["items"][0]["name"],
                         "Latest from GitHub")
        self.assertFalse(machine.dirty)

    def test_startup_detects_divergent_dirty_draft_without_overwriting(self):
        machine = self.new_pc()
        machine.payload["items"][0]["name"] = "Offline draft"
        machine.changed()
        self.repo.document["items"][0]["name"] = "Remote other PC"
        self.repo.number += 1
        machine._startup_sync()
        self.assertEqual(machine.payload["items"][0]["name"], "Offline draft")
        self.assertTrue(machine.dirty)
        self.assertTrue(machine.sync_paused_conflict)
        self.assertEqual(self.repo.document["items"][0]["name"],
                         "Remote other PC")



if __name__ == "__main__":
    unittest.main()
