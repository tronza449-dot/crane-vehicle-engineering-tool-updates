"""Steel member product-link regression tests."""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication, QLineEdit
from bom_qt import RecordDialog, STEEL_FIELDS
import bom_steel


class SteelProductLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_link_is_an_explicit_editable_steel_field(self):
        self.assertIn(("link", "ลิงก์สินค้า / ร้านค้าเหล็ก"), STEEL_FIELDS)
        values = {
            "weight_mode": bom_steel.WEIGHT_MODE_MANUAL,
            "member": "ค้ำโครงด้านซ้าย",
            "material": bom_steel.DEFAULT_MATERIAL,
            "profile": "ชิ้นส่วนอื่น",
            "size": "ไม่ระบุขนาด",
            "qty": 2,
            "manual_unit_weight_kg": 1.25,
            "link": "https://example.org/steel",
        }
        dialog = RecordDialog("เพิ่มชิ้นส่วนโครงสร้างเหล็ก", STEEL_FIELDS, values)
        try:
            field = dialog.widgets["link"]
            self.assertIsInstance(field, QLineEdit)
            self.assertEqual(field.text(), "https://example.org/steel")
            self.assertIn("https://", field.placeholderText())
            self.assertIn("ลิงก์สินค้า", field.toolTip())
            self.assertEqual(dialog.get_values()["link"], "https://example.org/steel")
            field.setText("https://supplier.example/steel-tube")
            self.assertEqual(dialog.get_values()["link"], "https://supplier.example/steel-tube")
        finally:
            dialog.close()

    def test_steel_normalizer_preserves_product_link(self):
        row = bom_steel.normalize_member({
            "id": "1", "weight_mode": bom_steel.WEIGHT_MODE_MANUAL,
            "member": "คานหน้า", "material": bom_steel.DEFAULT_MATERIAL,
            "profile": "ชิ้นส่วนอื่น", "size": "ไม่ระบุขนาด", "qty": 1,
            "manual_unit_weight_kg": 3.2,
            "link": "https://supplier.example/beam",
        })
        self.assertEqual(row["link"], "https://supplier.example/beam")


if __name__ == "__main__":
    unittest.main()
