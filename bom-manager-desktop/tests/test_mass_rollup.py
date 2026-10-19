"""Manual equipment mass + steel-frame roll-up regression tests."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import bom_core
import bom_steel_bom
import bom_steel


def sample_doc():
    return {
        "schemaVersion": 1,
        "project": "Mass roll-up test",
        "items": [
            {"id": "1", "name": "Drive motor", "qty": 2, "unit": "ตัว",
             "unitWeightKg": 3.5, "unitPrice": 1000},
            {"id": "2", "name": "Controller", "qty": 1, "unit": "ตัว",
             "unitWeightKg": 1.2, "unitPrice": 500},
            {"id": "3", "name": "Battery", "qty": 1, "unit": "ลูก",
             "unitWeightKg": None, "unitPrice": 3000},
        ],
        "steel_members": [
            {"id": "S1", "member": "Frame rail", "material": "SS400",
             "profile": "เหล็กกล่องสี่เหลี่ยม", "size": "40x40x2 mm",
             "qty": 2, "length_mm": 500, "stock_length_m": 6,
             "weight_reference_length_m": 6, "weight_reference_kg": 12},
            {"id": "S2", "member": "Cross member", "material": "SS400",
             "profile": "เหล็กกล่องสี่เหลี่ยม", "size": "40x40x2 mm",
             "qty": 1, "length_mm": 700, "stock_length_m": 6,
             "weight_reference_length_m": None, "weight_reference_kg": None},
        ],
        "wiring": [],
        "purchases": [],
    }


class MassRollupTests(unittest.TestCase):
    def test_equipment_and_steel_known_mass_are_added(self):
        doc = sample_doc()
        bom_core.ensure_doc(doc)
        result = bom_steel_bom.summarize_bom_and_steel(doc)

        # Motors: 2 * 3.5 = 7 kg; controller: 1 * 1.2 = 1.2 kg.
        self.assertEqual(result["equipment_known_weight_kg"], 8.2)
        self.assertEqual(result["equipment_weighted_items"], 2)
        self.assertEqual(result["equipment_missing_weight_count"], 1)
        self.assertEqual(result["equipment_missing_weight_qty"], 1)

        # Two 0.5 m rails, with 12 kg per 6 m => 2 kg/m, total 2 kg.
        self.assertEqual(result["steel_known_weight_kg"], 2)
        self.assertEqual(result["steel_unknown_weight_length_m"], 0.7)
        self.assertEqual(result["combined_known_weight_kg"], 10.2)
        self.assertFalse(result["combined_weight_complete"])

    def test_blank_weight_remains_unknown_not_zero(self):
        doc = sample_doc()
        result = bom_steel_bom.summarize_bom_and_steel(doc)
        battery = next(x for x in result["equipment_weight_rows"] if x["id"] == "3")
        self.assertIsNone(battery["unit_weight_kg"])
        self.assertIsNone(battery["total_weight_kg"])
        self.assertEqual(result["equipment_known_weight_kg"], 8.2)

    def test_manual_weight_must_be_positive_when_supplied(self):
        for value in ("0", "-1", "not-a-number"):
            doc = sample_doc()
            doc["items"][0]["unitWeightKg"] = value
            with self.subTest(value=value):
                with self.assertRaises(bom_core.DataError):
                    bom_core.ensure_doc(doc)

    def test_old_bom_without_weight_field_remains_compatible(self):
        doc = {"items": [{"id": "1", "name": "Old item", "qty": 1,
                          "unitPrice": None}]}
        bom_core.ensure_doc(doc)
        result = bom_steel_bom.summarize_bom_and_steel(doc)
        self.assertEqual(result["equipment_missing_weight_count"], 1)
        self.assertEqual(result["equipment_known_weight_kg"], 0)
        self.assertEqual(result["combined_known_weight_kg"], 0)

    def test_gui_exposes_manual_weight_field_and_rollup_cards(self):
        from PySide6.QtWidgets import QApplication, QLineEdit
        from bom_qt import BOMWindow, ITEM_FIELDS, RecordDialog

        app = QApplication.instance() or QApplication([])
        window = BOMWindow(auto_load=False)
        self.addCleanup(window.close)
        window.auto_sync_timer.stop()
        window.auto_sync_retry_timer.stop()
        window.remote_refresh_timer.stop()
        window.dirty = False
        self.assertIn(("unitWeightKg", "น้ำหนักต่อหน่วย (kg)"), ITEM_FIELDS)
        dialog = RecordDialog("เพิ่มอุปกรณ์", ITEM_FIELDS,
                              {"name": "Motor", "qty": 2, "unitWeightKg": 3.5}, window)
        self.addCleanup(dialog.close)
        self.assertIsInstance(dialog.widgets["unitWeightKg"], QLineEdit)
        values = bom_core.normalize_dialog_values(dialog.get_values())
        self.assertEqual(values["unitWeightKg"], 3.5)
        self.assertTrue(hasattr(window, "mass_equipment_card"))
        self.assertTrue(hasattr(window, "mass_frame_card"))
        self.assertTrue(hasattr(window, "mass_total_card"))
        app.processEvents()


if __name__ == "__main__":
    unittest.main()
