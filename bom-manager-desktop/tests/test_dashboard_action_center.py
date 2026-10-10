"""UI integration: new engineering dashboard uses live BOM values, no mock figures."""
import copy
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class DashboardActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        from bom_qt_theme import apply_theme
        cls.app = QApplication.instance() or QApplication([])
        apply_theme(cls.app)

    def setUp(self):
        from bom_qt import BOMWindow
        self.win = BOMWindow(auto_load=False)
        self.win.payload = {
            "schemaVersion": 1, "project": "ตัวอย่างโครงการจริง",
            "items": [
                {"id":"1","name":"Motor","category":"ระบบขับเคลื่อน",
                 "qty":2,"unitPrice":100,"supplier":"Vendor A"},
                {"id":"2","name":"Controller","category":"ระบบควบคุมและสื่อสาร",
                 "qty":1,"unitPrice":None,"supplier":""},
                {"id":"3","name":"Battery","category":"แบตเตอรี่และไฟฟ้ากำลัง",
                 "qty":1,"unitPrice":30,"supplier":""},
                {"id":"4","name":"Crane","category":"ระบบเครนและวินช์",
                 "qty":1,"unitPrice":100,"supplier":"Vendor Z"},
            ],
            "wiring": [],
            "purchases": [
                {"id":"1","itemId":"1","qty":1,"unitPrice":95,
                 "status":"สั่งแล้ว"},
                {"id":"2","itemId":"3","qty":1,"unitPrice":30,
                 "status":"ได้รับแล้ว"},
                {"id":"3","itemId":"4","qty":1,"unitPrice":100,
                 "status":"วางแผน"},
            ],
        }
        self.win.render_all()

    def tearDown(self):
        self.win.close()
        self.win.deleteLater()

    def test_live_kpis_and_distinct_action_count(self):
        self.assertEqual(self.win.cards["items"].figure.text(), "4")
        self.assertEqual(self.win.cards["known_cost"].figure.text(), "330.00")
        self.assertEqual(self.win.pending_actions_card.figure.text(), "4")
        self.assertEqual(self.win.dashboard_task_counts, {
            "missing_price": 1,
            "missing_supplier": 2,
            "pending_order": 3,
            "pending_receipt": 1,
        })
        self.assertIn("4 จาก 4", self.win.task_summary_label.text())
        for key, button in self.win.task_buttons.items():
            self.assertIn(str(self.win.dashboard_task_counts[key]), button.text())
            self.assertTrue(button.isEnabled())

    def test_missing_supplier_drills_into_correct_filter_without_editing(self):
        import json
        before = json.dumps(self.win.payload, sort_keys=True, ensure_ascii=False)
        self.win.task_buttons["missing_supplier"].click()
        self.assertEqual(self.win.stack.currentIndex(), 1)
        self.assertEqual(self.win.price_filter.currentText(), "ไม่มีผู้ขาย")
        self.assertIn("2 จาก 4 รายการ", self.win.visible_count_label.text())
        self.assertEqual(before, json.dumps(self.win.payload, sort_keys=True, ensure_ascii=False))

    def test_purchasing_tasks_open_purchase_table(self):
        self.win.task_buttons["pending_receipt"].click()
        self.assertEqual(self.win.stack.currentIndex(), 3)
        self.win.show_page(0)
        self.win.task_buttons["pending_order"].click()
        self.assertEqual(self.win.stack.currentIndex(), 3)
        self.assertIn("เพิ่มยอดสั่งซื้อ", self.win.status.text())

    def test_no_token_status_is_true_public_viewer_not_connected_until_verified(self):
        self.win.token = None
        self.win.sha = "cached_sha"
        self.win.last_git_ok = None
        self.win._refresh_sync_state()
        self.assertIn("ในเครื่อง", self.win.dashboard_cloud_badge.text())
        self.assertIn("ผู้ชม", self.win.dashboard_access_label.text())
        self.win.last_git_ok = True
        self.win._refresh_sync_state()
        self.assertIn("GitHub Connected", self.win.dashboard_cloud_badge.text())

    def test_task_disables_when_no_missing_items(self):
        for row in self.win.payload["items"]:
            row["unitPrice"] = 100
            row["supplier"] = "Known"
        self.win.render_all()
        self.assertFalse(self.win.task_buttons["missing_price"].isEnabled())
        self.assertFalse(self.win.task_buttons["missing_supplier"].isEnabled())
        self.assertTrue(self.win.task_buttons["pending_order"].isEnabled())


if __name__ == "__main__":
    unittest.main()
