"""Project BOM category migration and Qt grouping behavior."""
import copy
import json
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import bom_categories


class CategoryDataTests(unittest.TestCase):
    def test_project_groups_cover_33_unique_ids(self):
        self.assertEqual(len(bom_categories.ID_TO_CATEGORY), 33)
        self.assertEqual(len(bom_categories.CATEGORY_ORDER), 7)
        self.assertEqual(
            [len(bom_categories.PROJECT_CATEGORY_IDS[c])
             for c in bom_categories.CATEGORY_ORDER],
            [3, 2, 6, 7, 6, 4, 5])

    def test_migration_changes_only_category(self):
        data = [{"id": str(i), "name": f"Part {i}", "qty": i,
                 "unitPrice": None, "privateInfo": {"test": i}}
                for i in range(1, 34)]
        source = copy.deepcopy(data)
        updated = bom_categories.reclassify_project_items(data)
        self.assertEqual(data, source)
        for original, item in zip(source, updated):
            self.assertEqual({k: v for k, v in item.items() if k != "category"},
                             original)
            self.assertEqual(item["category"], bom_categories.ID_TO_CATEGORY[item["id"]])
        with self.assertRaises(ValueError):
            bom_categories.reclassify_project_items(data[:-1])

    def test_live_project_bom_matches_categories(self):
        doc = json.loads((ROOT.parent / "bom-manager" / "bom.json").read_text(encoding="utf-8"))
        import bom_core
        bom_core.ensure_doc(doc)
        self.assertEqual(len(doc["items"]), 33)
        self.assertEqual(
            bom_categories.summary(doc["items"]),
            [(name, len(bom_categories.PROJECT_CATEGORY_IDS[name]))
             for name in bom_categories.CATEGORY_ORDER])
        self.assertTrue(all(item["category"] == bom_categories.ID_TO_CATEGORY[str(item["id"])]
                            for item in doc["items"]))

    def test_unrecognized_categories_are_supported(self):
        categories = bom_categories.sorted_categories([
            "New Custom", "ระบบขับเคลื่อน", "โครงสร้างและเครื่องกล", "New Custom"
        ])
        self.assertEqual(categories, [
            "โครงสร้างและเครื่องกล", "ระบบขับเคลื่อน", "New Custom"
        ])


class QtCategoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        import bom_qt_theme as theme
        cls.qt = QApplication.instance() or QApplication([])
        theme.apply_theme(cls.qt)

    def setUp(self):
        from bom_qt import BOMWindow
        self.window = BOMWindow(auto_load=False)
        self.window.payload = {
            "schemaVersion": 1, "project": "Category Test",
            "items": [
                {"id": "1", "category": "ระบบควบคุมและสื่อสาร", "name": "ESP32",
                 "qty": 1, "unitPrice": None},
                {"id": "2", "category": "ระบบขับเคลื่อน", "name": "VESC",
                 "qty": 1, "unitPrice": 200},
                {"id": "3", "category": "ระบบขับเคลื่อน", "name": "Hub motor",
                 "qty": 2, "unitPrice": 100},
            ],
        }
        self.window.render_all()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()

    def test_grouped_list_shows_headers_without_losing_indexes(self):
        from PySide6.QtCore import Qt
        table = self.window.bom_table
        self.assertEqual(self.window.group_mode.currentText(), "จัดกลุ่มตามระบบ")
        self.assertEqual(table.rowCount(), 5)
        self.assertTrue(table.item(0, 0).text().startswith("▣"))
        self.assertIsNone(table.item(0, 0).data(Qt.ItemDataRole.UserRole))
        self.assertEqual(table.item(1, 1).text(), "Hub motor")
        self.assertEqual(table.item(1, 0).data(Qt.ItemDataRole.UserRole), 2)
        self.assertEqual(table.item(2, 0).data(Qt.ItemDataRole.UserRole), 1)
        self.window.group_mode.setCurrentIndex(1)
        self.assertEqual(table.rowCount(), 3)

    def test_dashboard_double_click_category(self):
        self.window.open_category_from_dashboard(0, 0)
        self.assertEqual(self.window.stack.currentIndex(), 1)
        self.assertEqual(self.window.category.currentText(), "ระบบขับเคลื่อน")
        self.assertEqual(self.window.bom_table.rowCount(), 3)

    def test_editor_lists_standard_groups(self):
        from bom_qt import RecordDialog, ITEM_FIELDS
        from PySide6.QtWidgets import QComboBox
        dialog = RecordDialog("แก้ไขอุปกรณ์", ITEM_FIELDS, {
            "category": "ระบบเครนและวินช์", "name": "Test"
        }, self.window)
        picker = dialog.widgets["category"]
        self.assertIsInstance(picker, QComboBox)
        self.assertTrue(picker.isEditable())
        self.assertEqual(picker.currentText(), "ระบบเครนและวินช์")
        self.assertIn("ระบบขับเคลื่อน", [picker.itemText(i) for i in range(picker.count())])
        dialog.close()


if __name__ == "__main__":
    unittest.main()
