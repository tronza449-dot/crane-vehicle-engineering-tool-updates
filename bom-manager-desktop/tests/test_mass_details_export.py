"""Regression tests for mass detail popups and locked-file-safe exports."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication, QLabel, QTableWidget
from bom_qt import BOMWindow


class MassDetailsAndExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.window = BOMWindow(auto_load=False)
        self.window.auto_sync_timer.stop()
        self.window.auto_sync_retry_timer.stop()
        self.window.remote_refresh_timer.stop()
        self.window.dirty = False
        self.window.payload = {
            "schemaVersion": 1, "project": "Mass popup test", "currency": "THB",
            "items": [
                {"id": "1", "category": "เครื่องกล", "name": "Hub motor",
                 "qty": 2, "unit": "ตัว", "unitWeightKg": 3.5},
                {"id": "2", "category": "ไฟฟ้ากำลัง", "name": "Battery",
                 "qty": 1, "unit": "ลูก", "unitWeightKg": None},
            ],
            "steel_members": [{
                "id": "S1", "member": "Frame rail", "material": "SS400",
                "profile": "เหล็กกล่องสี่เหลี่ยม", "size": "40x40x2 mm",
                "qty": 2, "length_mm": 500, "stock_length_m": 6,
                "weight_reference_length_m": 6, "weight_reference_kg": 12,
            }],
            "wiring": [], "purchases": [],
        }
        self.window.render_all()

    def tearDown(self):
        self.window.auto_sync_timer.stop()
        self.window.auto_sync_retry_timer.stop()
        self.window.remote_refresh_timer.stop()
        self.window.dirty = False
        self.window.busy = False
        self.window.close()
        self.window.deleteLater()

    def test_mass_cards_are_wired_to_details_and_tables_show_unit_and_total_weight(self):
        with patch.object(self.window, "open_mass_details") as open_details:
            self.window.mass_equipment_card.clicked.emit()
            open_details.assert_called_once_with("equipment")
        dialog = self.window._build_mass_details_dialog("equipment")
        self.assertTrue(any("รวมที่ทราบ: 9.000 kg" in label.text()
                            for label in dialog.findChildren(QLabel)))
        tables = dialog.findChildren(QTableWidget)
        self.assertEqual(len(tables), 2)
        equipment = tables[0]
        self.assertEqual(equipment.rowCount(), 2)
        self.assertEqual(equipment.item(0, 0).text(), "1")
        self.assertEqual(equipment.item(0, 2).text(), "Hub motor")
        self.assertEqual(equipment.item(0, 5).text(), "3.500")
        self.assertEqual(equipment.item(0, 6).text(), "7.000")
        self.assertEqual(equipment.item(1, 7).text(), "ยังไม่ทราบน้ำหนัก")
        frame = tables[1]
        self.assertEqual(frame.rowCount(), 1)
        self.assertEqual(frame.item(0, 1).text(), "Frame rail")
        self.assertEqual(frame.item(0, 5).text(), "1.000")
        self.assertEqual(frame.item(0, 6).text(), "2.000")
        dialog.close()

    def test_locked_target_exports_to_numbered_filename_and_preserves_original(self):
        target = Path(self.temp.name) / "Engineering_BOM_Report.xlsx"
        target.write_text("old report", encoding="utf-8")
        real_replace = os.replace
        calls = {"count": 0}
        def locked_once(source, destination):
            calls["count"] += 1
            if calls["count"] == 1:
                raise PermissionError(13, "Permission denied", str(target))
            return real_replace(source, destination)
        def fake_export(_document, destination):
            Path(destination).write_text("new report", encoding="utf-8")
        with patch("bom_qt.os.replace", side_effect=locked_once):
            actual = self.window._export_safely(fake_export, target)
        self.assertEqual(target.read_text(encoding="utf-8"), "old report")
        self.assertEqual(actual.name, "Engineering_BOM_Report_1.xlsx")
        self.assertEqual(actual.read_text(encoding="utf-8"), "new report")

    def test_export_writes_to_requested_path_when_available(self):
        target = Path(self.temp.name) / "report.pdf"
        def fake_export(_document, destination):
            Path(destination).write_bytes(b"%PDF-test")
        actual = self.window._export_safely(fake_export, target)
        self.assertEqual(actual, target)
        self.assertEqual(target.read_bytes(), b"%PDF-test")


if __name__ == "__main__":
    unittest.main()
