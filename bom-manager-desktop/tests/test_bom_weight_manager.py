"""Weight-only BOM workflow: picker exclusion, per-unit entry and totals."""
import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication, QWidget
from bom_qt import WeightEntryDialog
import bom_steel_bom


class FakeBOMOwner(QWidget):
    def __init__(self):
        super().__init__()
        self.dirty = False
        self.status_message = ""
        self.payload = {
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

    def changed(self):
        self.dirty = True

    def set_status(self, message):
        self.status_message = message


class BOMWeightManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.owner = FakeBOMOwner()
        self.dialog = WeightEntryDialog(self.owner)

    def tearDown(self):
        self.dialog.close()
        self.dialog.deleteLater()
        self.owner.close()
        self.owner.deleteLater()

    def test_weighted_item_disappears_from_picker_and_updates_total(self):
        self.assertEqual(self.dialog.item_combo.count(), 2)
        self.assertEqual(self.dialog.item_combo.itemData(0), "101")
        self.dialog.item_combo.setCurrentIndex(self.dialog.item_combo.findData("101"))
        self.dialog.weight_input.setText("2.5")
        self.dialog.save_weight()

        motor = next(x for x in self.owner.payload["items"] if x["id"] == "101")
        self.assertEqual(motor["unitWeightKg"], 2.5)
        self.assertEqual(self.dialog.item_combo.count(), 1)
        self.assertEqual(self.dialog.item_combo.itemData(0), "102")
        self.assertEqual(self.dialog.weight_table.rowCount(), 2)
        summary = bom_steel_bom.summarize_bom_and_steel(self.owner.payload)
        self.assertEqual(float(summary["equipment_known_weight_kg"]), 6.25)
        self.assertEqual(summary["equipment_weighted_items"], 2)
        self.assertEqual(summary["equipment_missing_weight_count"], 1)
        self.assertTrue(self.owner.dirty)
        self.assertIn("นำออกจากตัวเลือก", self.owner.status_message)


if __name__ == "__main__":
    unittest.main()
