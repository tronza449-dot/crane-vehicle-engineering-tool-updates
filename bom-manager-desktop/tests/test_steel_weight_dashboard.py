"""User-entered steel mass calculations and the Steel Weight Dashboard."""
import os
import sys
import unittest
from pathlib import Path
from decimal import Decimal

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bom_steel
import bom_steel_bom


class SteelWeightCalculationTests(unittest.TestCase):
    def row(self, **updates):
        row = {
            "id": "1", "member": "คานด้านข้าง", "profile": "เหล็กกล่องสี่เหลี่ยม",
            "size": "25×25×2 mm", "qty": 4, "length_mm": 1500,
            "stock_length_m": 6, "weight_reference_length_m": 6,
            "weight_reference_kg": 18, "notes": "",
        }
        row.update(updates)
        return row

    def test_weight_per_metre_and_total_mass_use_reference_values(self):
        row = self.row()
        self.assertEqual(bom_steel.weight_per_m(row), Decimal("3.0"))
        self.assertEqual(bom_steel.total_length_m(row), Decimal("6.000"))
        self.assertEqual(bom_steel.total_weight_kg(row), Decimal("18.000"))

    def test_other_reference_length_is_converted_to_kg_per_metre(self):
        row = self.row(qty=2, length_mm=2000,
                       weight_reference_length_m=2, weight_reference_kg=5)
        self.assertEqual(bom_steel.weight_per_m(row), Decimal("2.5"))
        self.assertEqual(bom_steel.total_weight_kg(row), Decimal("10.000"))

    def test_weight_fields_are_optional_but_must_be_entered_as_a_pair(self):
        row = self.row(weight_reference_length_m="", weight_reference_kg="")
        self.assertIsNone(bom_steel.weight_per_m(row))
        self.assertIsNone(bom_steel.total_weight_kg(row))
        with self.assertRaisesRegex(bom_steel.SteelDataError, "ต้องกรอกทั้ง"):
            bom_steel.normalize_member(self.row(weight_reference_length_m="", weight_reference_kg=18))
        with self.assertRaises(bom_steel.SteelDataError):
            bom_steel.normalize_member(self.row(weight_reference_length_m=0, weight_reference_kg=18))

    def test_summary_aggregates_known_mass_and_tracks_unknown_length_separately(self):
        first = self.row()
        second = self.row(id="2", member="คานหน้า", qty=2, length_mm=2000,
                          weight_reference_length_m=2, weight_reference_kg=5)
        unknown = self.row(id="3", member="ค้ำยัน", qty=1, length_mm=1500,
                           weight_reference_length_m="", weight_reference_kg="")
        result = bom_steel.summarize([first, second, unknown])
        self.assertEqual(result["total_pieces"], 7)
        self.assertEqual(result["total_length_m"], Decimal("11.500"))
        self.assertEqual(result["known_weight_kg"], Decimal("28.000"))
        self.assertEqual(result["unknown_weight_length_m"], Decimal("1.5"))
        matching = next(group for group in result["groups"]
                         if group["size"] == "25×25×2 mm")
        self.assertEqual(matching["known_weight_kg"], Decimal("28.000"))
        self.assertEqual(matching["unknown_weight_length_m"], Decimal("1.5"))

    def test_combined_bom_steel_summary_exposes_weight_dashboard_values(self):
        doc = {"items": [], "wiring": [], "purchases": [],
               "steel_members": [
                   self.row(),
                   self.row(id="2", member="ค้ำยัน", qty=1, length_mm=1500,
                            weight_reference_length_m="", weight_reference_kg=""),
               ]}
        result = bom_steel_bom.summarize_bom_and_steel(doc, waste_percent=5)
        self.assertEqual(result["steel_known_weight_kg"], Decimal("18.000"))
        self.assertEqual(result["steel_unknown_weight_length_m"], Decimal("1.5"))
        self.assertEqual(result["steel_pieces"], 5)

    def test_manual_weight_parts_contribute_to_known_mass_not_stock_length(self):
        doc = {"items": [], "wiring": [], "purchases": [], "steel_members": [
            {"id": "M1", "member": "ขายึดมอเตอร์",
             "weight_mode": bom_steel.WEIGHT_MODE_MANUAL,
             "profile": "ชิ้นส่วนอื่น", "size": "", "qty": 3,
             "manual_unit_weight_kg": 0.85},
            self.row(id="S1", qty=2, length_mm=1000,
                     weight_reference_length_m=2, weight_reference_kg=4),
        ]}
        summary = bom_steel_bom.summarize_bom_and_steel(doc, waste_percent=5)
        self.assertEqual(summary["steel_known_weight_kg"], Decimal("6.55"))
        self.assertEqual(summary["steel_required_length_m"], Decimal("2"))
        self.assertEqual(summary["steel_stock_bars"], 1)
        self.assertEqual(summary["steel_procurement_length_m"], Decimal("6.0"))
        manual_group = next(g for g in summary["steel_groups"]
                            if g["weight_mode"] == bom_steel.WEIGHT_MODE_MANUAL)
        self.assertEqual(manual_group["known_weight_kg"], Decimal("2.55"))
        self.assertIsNone(manual_group["stock_length_m"])
        self.assertEqual(manual_group["estimated_bars_with_waste"], 0)


class SteelWeightDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        from bom_qt import BOMWindow
        self.win = BOMWindow(auto_load=False)
        self.win.auto_sync_timer.stop()
        self.win.auto_sync_retry_timer.stop()
        self.win.remote_refresh_timer.stop()
        self.win.payload = {
            "schemaVersion": 1, "project": "Steel test", "currency": "THB",
            "items": [], "wiring": [], "purchases": [],
            "steel_members": [
                {"id": "1", "member": "คาน", "profile": "เหล็กกล่องสี่เหลี่ยม",
                 "size": "25×25×2 mm", "qty": 4, "length_mm": 1500,
                 "stock_length_m": 6, "weight_reference_length_m": 6,
                 "weight_reference_kg": 18, "link": ""},
                {"id": "2", "member": "ค้ำ", "profile": "เหล็กกล่องสี่เหลี่ยม",
                 "size": "25×25×2 mm", "qty": 1, "length_mm": 1000,
                 "stock_length_m": 6, "weight_reference_length_m": "",
                 "weight_reference_kg": ""},
            ],
        }
        self.win.render_all()

    def tearDown(self):
        self.win.auto_sync_timer.stop()
        self.win.auto_sync_retry_timer.stop()
        self.win.remote_refresh_timer.stop()
        self.win.dirty = False
        self.win.close()
        self.win.deleteLater()

    def test_steel_dashboard_displays_total_length_weight_and_unknown_length(self):
        self.assertEqual(self.win.steel_member_count_card.figure.text(), "2")
        self.assertEqual(self.win.steel_piece_count_card.figure.text(), "5")
        self.assertEqual(self.win.steel_length_card.figure.text(), "7.000")
        self.assertEqual(self.win.steel_weight_card.figure.text(), "18.000")
        self.assertEqual(self.win.steel_unknown_weight_card.figure.text(), "1.000")
        self.assertIn("18.000 kg", self.win.steel_totals_label.text())
        self.assertEqual(self.win.steel_table.columnCount(), 17)
        self.assertEqual(self.win.steel_table.item(0, 11).text(), "3.000")
        self.assertEqual(self.win.steel_table.item(0, 15).text(), "—")
        self.assertEqual(self.win.steel_table.item(0, 13).text(), "18.000")
        self.assertEqual(self.win.steel_table.item(1, 13).text(), "—")

    def test_editor_switches_to_manual_weight_for_other_parts(self):
        from bom_qt import RecordDialog, STEEL_FIELDS
        dialog = RecordDialog("เพิ่มชิ้นส่วนโครงสร้างเหล็ก", STEEL_FIELDS, {
            "member": "ขายึดมอเตอร์", "profile": "ชิ้นส่วนอื่น", "size": "",
            "qty": 3, "weight_mode": bom_steel.WEIGHT_MODE_LENGTH,
        }, self.win)
        selector = dialog.widgets["weight_mode"]
        selector.setCurrentIndex(selector.findData(bom_steel.WEIGHT_MODE_MANUAL))
        self.assertFalse(dialog.widgets["manual_unit_weight_kg"].isHidden())
        self.assertTrue(dialog.widgets["length_mm"].isHidden())
        self.assertTrue(dialog.widgets["weight_reference_length_m"].isHidden())
        dialog.widgets["manual_unit_weight_kg"].setText("0.85")
        values = bom_steel.normalize_member(dialog.get_values())
        self.assertEqual(values["weight_mode"], bom_steel.WEIGHT_MODE_MANUAL)
        self.assertIsNone(values["length_mm"])
        self.assertEqual(bom_steel.total_weight_kg(values), Decimal("2.55"))
        dialog.close()

    def test_steel_editor_has_reference_length_and_weight_fields(self):
        from bom_qt import RecordDialog, STEEL_FIELDS
        dialog = RecordDialog("เพิ่มชิ้นส่วนโครงสร้างเหล็ก", STEEL_FIELDS, {
            "member": "คาน", "profile": "เหล็กกล่องสี่เหลี่ยม",
            "size": "25×25×2 mm", "qty": 4, "length_mm": 1500,
            "stock_length_m": 6, "weight_reference_length_m": 6,
            "weight_reference_kg": 18,
        }, self.win)
        self.assertTrue(dialog.widgets["material"].isEditable())
        self.assertEqual(dialog.widgets["material"].currentText(),
                         bom_steel.DEFAULT_MATERIAL)
        values = dialog.get_values()
        self.assertEqual(values["weight_reference_length_m"], "6")
        self.assertEqual(values["weight_reference_kg"], "18")
        self.assertIn("น้ำหนักอ้างอิง", dialog.widgets["weight_reference_kg"].toolTip())
        dialog.close()


    def test_default_tab_is_mass_only_and_structural_form_has_product_link(self):
        from bom_qt import FrameWeightDialog
        self.assertEqual(self.win.steel_tabs.currentIndex(), 0)
        self.assertEqual(self.win.frame_weight_table.columnCount(), 8)
        dialog = FrameWeightDialog(self.win, {
            "member": "ฐานเครน", "material": "SS400", "size": "40×40×2 mm",
            "qty": 2, "manual_unit_weight_kg": 3.75,
            "link": "https://example.org/steel", "notes": "ชิ้นส่วนโครง",
        })
        self.assertEqual(dialog.get_values()["member"], "ฐานเครน")
        self.assertEqual(dialog.get_values()["qty"], "2")
        self.assertEqual(dialog.get_values()["manual_unit_weight_kg"], "3.75")
        self.assertEqual(dialog.get_values()["link"], "https://example.org/steel")
        values = dialog.get_values()
        row = bom_steel.normalize_member({
            "id": "S9", **values, "profile": "ชิ้นส่วนอื่น",
            "weight_mode": bom_steel.WEIGHT_MODE_MANUAL,
        })
        self.assertEqual(bom_steel.total_weight_kg(row), Decimal("7.50"))
        self.assertEqual(row["link"], "https://example.org/steel")
        dialog.close()

if __name__ == "__main__":
    unittest.main()
