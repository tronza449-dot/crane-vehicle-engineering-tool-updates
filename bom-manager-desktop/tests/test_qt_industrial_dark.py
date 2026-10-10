"""Headless Qt smoke test: real controls, page routing, budget and data integrity."""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class IndustrialDarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        from bom_qt_theme import apply_theme
        cls.application = QApplication.instance() or QApplication([])
        apply_theme(cls.application)

    def setUp(self):
        from bom_qt import BOMWindow
        from PySide6.QtCore import Qt
        self.window = BOMWindow(auto_load=False)

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()

    def test_navigation_and_dashboard(self):
        self.assertEqual(len(self.window.nav_buttons), 6)
        self.assertEqual(self.window.stack.count(), 6)
        self.assertEqual(len(self.window.cards), 6)
        self.assertFalse(self.window.install_btn.isEnabled())
        self.window.payload = {
            "schemaVersion": 1, "project": "Engineering test",
            "currency": "THB",
            "items": [
                {"id": "1", "category": "Power", "name": "Hub motor",
                 "qty": 2, "unitPrice": 1500},
                {"id": "2", "category": "Power", "name": "Battery",
                 "qty": 1, "unitPrice": None},
            ],
            "wiring": [], "purchases": []
        }
        self.window.render_all()
        self.assertEqual(self.window.cards["items"].figure.text(), "2")
        self.assertEqual(self.window.cards["priced"].figure.text(), "1")
        self.assertEqual(self.window.cards["known_cost"].figure.text(), "3,000.00")
        self.assertEqual(self.window.price_progress.value(), 50)
        self.window.show_metric("missing")
        self.assertEqual(self.window.stack.currentIndex(), 1)
        self.assertEqual(self.window.price_filter.currentText(), "ไม่มีราคา")
        self.assertEqual(self.window.bom_table.rowCount(), 2)
        self.assertIsNone(self.window.bom_table.item(0, 0).data(Qt.ItemDataRole.UserRole))
        self.assertIn("Battery", self.window.bom_table.item(1, 1).text())
        self.window.show_metric("wiring")
        self.assertEqual(self.window.stack.currentIndex(), 2)
        self.window.show_metric("purchases")
        self.assertEqual(self.window.stack.currentIndex(), 3)

    def test_document_preserves_original_custom_data(self):
        import bom_core
        custom = {
            "schemaVersion": 1, "project": "Keep data", "customKey": {"version": 5},
            "items": [{"id": "11", "name": "Custom device", "qty": 1,
                       "unitPrice": None, "customItemKey": "keep"}]
        }
        self.window.payload = custom
        self.window.render_all()
        bom_core.ensure_doc(self.window.payload)
        self.assertEqual(self.window.payload["customKey"]["version"], 5)
        self.assertEqual(self.window.payload["items"][0]["customItemKey"], "keep")
        self.assertEqual(self.window.bom_table.rowCount(), 2)
        self.window.group_mode.setCurrentIndex(1)
        self.assertEqual(self.window.bom_table.rowCount(), 1)


if __name__ == "__main__":
    unittest.main()
