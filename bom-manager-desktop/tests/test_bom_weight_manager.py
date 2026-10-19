"""Weight-only BOM workflow: picker exclusion, per-unit entry and totals."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication, QPushButton
from bom_qt import BOMWindow, WeightEntryDialog
import bom_steel_bom


class BOMWeightManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.window = BOMWindow(auto_load=False)
        for timer in (self.window.auto_sync_timer,
                      self.window.auto_sync_retry_timer,
                      self.window.remote_refresh_timer):
            timer.stop()
        self.window.cache_path = Path(self.temp.name) / "draft.json"
        self.window.payload = {
            "schemaVersion": 1,
            "project": "Weight test",
            "currency": "THB",
            "items": [
                {"id": "101", "name": "Hub motor", "qty": 2, "unit": "ตัว",
                 "category": "เครื่องกล", "unitWeightKg": None, "unitPrice": 3000},
                {"id": "102", "name": "Battery", "qty": 1, "unit": "ลูก",
                 "category": "ไฟฟ้ากำลัง", "unitWeightKg": None, "unitPrice": 5000},
                {"id": "103", "name": "Controller", "qty": 1, "unit": "ตัว",
                 "category": "ไฟฟ้ากำลัง", "unitWeightKg": 1.25, "unitPrice": 1000},
            ],
            "wiring": [],
            "purchases": [],
            "steel_members": [],
        }
        self.window.sha = None
        self.window.dirty = False
        self.window.render_all()
        self.dialog = WeightEntryDialog(self.window)

    def tearDown(self):
        self.window.dirty = False
        self.dialog.close()
        self.dialog.deleteLater()
        for timer in (self.window.auto_sync_timer,
                      self.window.auto_sync_retry_timer,
                      self.window.remote_refresh_timer):
            timer.stop()
        self.window.close()
        self.window.deleteLater()

    def test_a_weighted_item_disappears_from_picker_and_updates_total(self):
        self.assertEqual(self.dialog.item_combo.count(), 2)
        self.assertEqual(self.dialog.item_combo.itemData(0), "101")
        self.dialog.item_combo.setCurrentIndex(self.dialog.item_combo.findData("101"))
        self.dialog.weight_input.setText("2.5")
        self.dialog.save_weight()

        motor = next(x for x in self.window.payload["items"] if x["id"] == "101")
        self.assertEqual(motor["unitWeightKg"], 2.5)
        self.assertEqual(self.dialog.item_combo.count(), 1)
        self.assertEqual(self.dialog.item_combo.itemData(0), "102")
        self.assertEqual(self.dialog.weight_table.rowCount(), 2)
        summary = bom_steel_bom.summarize_bom_and_steel(self.window.payload)
        self.assertEqual(float(summary["equipment_known_weight_kg"]), 6.25)
        self.assertEqual(summary["equipment_weighted_items"], 2)
        self.assertEqual(summary["equipment_missing_weight_count"], 1)
        self.assertTrue(self.window.dirty)
        self.assertTrue(self.window.cache_path.exists())

    def test_bom_weight_manager_button_is_visible_on_mass_page(self):
        labels = [button.text() for button in self.window.findChildren(QPushButton)]
        self.assertIn("＋ เลือกอุปกรณ์จาก BOM แล้วใส่น้ำหนัก", labels)
        self.assertTrue(self.window.mass_weight_count_label.text())
        self.assertFalse(any("คำนวณการล้ม" in label or "Stability" in label
                             for label in labels))


if __name__ == "__main__":
    unittest.main()
