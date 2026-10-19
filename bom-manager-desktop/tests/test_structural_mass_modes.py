"""Regression tests for the main structural mass register's two calculation modes."""
import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication
import bom_steel
from bom_qt import BOMWindow, FrameWeightDialog


class StructuralMassModeDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = BOMWindow(auto_load=False)
        self.window.auto_sync_timer.stop()
        self.window.auto_sync_retry_timer.stop()
        self.window.remote_refresh_timer.stop()

    def tearDown(self):
        self.window.auto_sync_timer.stop()
        self.window.auto_sync_retry_timer.stop()
        self.window.remote_refresh_timer.stop()
        self.window.dirty = False
        self.window.close()
        self.window.deleteLater()

    def test_steel_box_mode_calculates_length_times_kg_per_m(self):
        dialog = FrameWeightDialog(self.window)
        try:
            dialog.mode_input.setCurrentIndex(
                dialog.mode_input.findData(bom_steel.WEIGHT_MODE_LENGTH))
            dialog.member_input.setText("คานข้าง")
            dialog.material_input.setText("SS400")
            dialog.profile_input.setCurrentText("เหล็กกล่องสี่เหลี่ยม")
            dialog.size_input.setText("25×25×2 mm")
            dialog.qty_input.setText("4")
            dialog.length_input.setText("1250")
            dialog.stock_length_input.setText("6")
            dialog.kg_per_m_input.setText("1.2")

            values = dialog.get_values()
            row = bom_steel.normalize_member(values)
            self.assertEqual(row["weight_mode"], bom_steel.WEIGHT_MODE_LENGTH)
            self.assertEqual(row["qty"], 4)
            self.assertEqual(bom_steel.total_length_m(row), Decimal("5"))
            self.assertEqual(bom_steel.weight_per_m(row), Decimal("1.2"))
            self.assertEqual(bom_steel.total_weight_kg(row), Decimal("6.0"))
            self.assertIn("5.000 m", dialog.preview.text())
            self.assertIn("6.000 kg", dialog.preview.text())
            self.assertTrue(dialog.manual_weight_input.isHidden())
            self.assertFalse(dialog.length_input.isHidden())
            self.assertFalse(dialog.kg_per_m_input.isHidden())
        finally:
            dialog.close()

    def test_other_component_mode_uses_manual_weight_and_no_length(self):
        dialog = FrameWeightDialog(self.window)
        try:
            dialog.mode_input.setCurrentIndex(
                dialog.mode_input.findData(bom_steel.WEIGHT_MODE_MANUAL))
            dialog.member_input.setText("ขายึดมอเตอร์")
            dialog.material_input.setText("SS400")
            dialog.size_input.setText("แผ่นหนา 5 mm")
            dialog.qty_input.setText("3")
            dialog.manual_weight_input.setText("0.85")
            values = dialog.get_values()
            row = bom_steel.normalize_member(values)

            self.assertEqual(row["weight_mode"], bom_steel.WEIGHT_MODE_MANUAL)
            self.assertEqual(row["profile"], "ชิ้นส่วนอื่น")
            self.assertIsNone(row["length_mm"])
            self.assertIsNone(row["stock_length_m"])
            self.assertEqual(bom_steel.total_weight_kg(row), Decimal("2.55"))
            self.assertIn("2.550 kg", dialog.preview.text())
            self.assertTrue(dialog.length_input.isHidden())
            self.assertTrue(dialog.kg_per_m_input.isHidden())
            self.assertFalse(dialog.manual_weight_input.isHidden())
        finally:
            dialog.close()

    def test_can_switch_existing_row_from_steel_to_manual_component(self):
        existing = bom_steel.normalize_member({
            "id": "S1", "member": "ฐานเครน", "weight_mode": bom_steel.WEIGHT_MODE_LENGTH,
            "material": "SS400", "profile": "เหล็กกล่องสี่เหลี่ยม",
            "size": "40×40×2 mm", "qty": 2, "length_mm": 1000,
            "stock_length_m": 6, "weight_reference_length_m": 1,
            "weight_reference_kg": 2.3,
        })
        dialog = FrameWeightDialog(self.window, existing)
        try:
            dialog.mode_input.setCurrentIndex(
                dialog.mode_input.findData(bom_steel.WEIGHT_MODE_MANUAL))
            dialog.manual_weight_input.setText("4.25")
            values = dialog.get_values()
            updated = bom_steel.normalize_member({**existing, **values})
            self.assertEqual(updated["id"], "S1")
            self.assertEqual(updated["weight_mode"], bom_steel.WEIGHT_MODE_MANUAL)
            self.assertEqual(bom_steel.total_weight_kg(updated), Decimal("8.50"))
            self.assertIsNone(updated["length_mm"])
            self.assertIsNone(updated["weight_reference_length_m"])
        finally:
            dialog.close()

    def test_main_mass_table_labels_both_part_types(self):
        self.window.payload = {
            "schemaVersion": 1, "project": "Mass test", "currency": "THB",
            "items": [], "wiring": [], "purchases": [],
            "steel_members": [
                {"id": "1", "member": "คาน", "weight_mode": bom_steel.WEIGHT_MODE_LENGTH,
                 "material": "SS400", "profile": "เหล็กกล่องสี่เหลี่ยม",
                 "size": "25×25×2 mm", "qty": 2, "length_mm": 1000,
                 "stock_length_m": 6, "weight_reference_length_m": 1,
                 "weight_reference_kg": 1.2},
                {"id": "2", "member": "ขายึด", "weight_mode": bom_steel.WEIGHT_MODE_MANUAL,
                 "material": "SS400", "profile": "ชิ้นส่วนอื่น", "size": "5 mm",
                 "qty": 2, "manual_unit_weight_kg": 0.5},
            ],
        }
        self.window.render_all()
        self.assertEqual(self.window.frame_weight_table.rowCount(), 2)
        self.assertIn("เหล็กกล่อง/หน้าตัด", self.window.frame_weight_table.item(0, 2).text())
        self.assertIn("ชิ้นส่วนอื่น", self.window.frame_weight_table.item(1, 2).text())
        self.assertEqual(self.window.frame_weight_table.item(0, 5).text(), "2.400")
        self.assertEqual(self.window.frame_weight_table.item(1, 5).text(), "1.000")


if __name__ == "__main__":
    unittest.main()
