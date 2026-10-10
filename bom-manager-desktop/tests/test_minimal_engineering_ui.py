"""Minimal Engineering UI behavior — real data and navigation, not only styling."""
import os
import sys
import unittest
from pathlib import Path
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class MinimalEngineeringTests(unittest.TestCase):
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
            "schemaVersion": 1, "project": "โครงการรถและเครนที่ทดสอบ",
            "currency": "THB",
            "items": [
                {"id":"2","category":"ระบบขับเคลื่อน","name":"QS Hub 1500W",
                 "partNumber":"QS10-1500","qty":2,"unit":"ตัว","unitPrice":3000,
                 "status":"เลือกรุ่นแล้ว"},
                {"id":"9","category":"ระบบควบคุมและสื่อสาร","name":"ESP32",
                 "qty":1,"unit":"ตัว","unitPrice":None,
                 "status":"รอราคา"},
            ],
            "wiring": [], "purchases": [],
        }
        self.win.render_all()

    def tearDown(self):
        self.win.close()
        self.win.deleteLater()

    def test_light_shell_and_real_dashboard(self):
        sheet = self.app.styleSheet()
        self.assertIn("background: #F5F8FC;", sheet)
        self.assertIn("QFrame#sidebar", sheet)
        self.assertIn("background: #10243D;", sheet)
        self.assertEqual(len(self.win.category_buttons), 7)
        self.assertIn("โครงการรถและเครนที่ทดสอบ",self.win.hero_project_label.text())
        self.assertEqual(self.win.cards["items"].figure.text(), "2")
        self.assertEqual(self.win.cards["priced"].figure.text(), "1")
        self.assertEqual(self.win.cards["missing"].figure.text(), "1")
        self.assertEqual(self.win.cards["known_cost"].figure.text(), "6,000.00")
        self.assertIn("1 รายการ",self.win.category_buttons["ระบบขับเคลื่อน"].text())
        self.assertEqual(self.win.price_progress.value(),50)

    def test_category_tile_drills_into_filtered_bom(self):
        self.win.category_buttons["ระบบขับเคลื่อน"].click()
        self.assertEqual(self.win.stack.currentIndex(),1)
        self.assertEqual(self.win.category.currentText(),"ระบบขับเคลื่อน")
        self.assertEqual(self.win.bom_table.columnCount(),9)
        self.assertEqual(self.win.bom_table.rowCount(),2)
        self.assertEqual(self.win.bom_table.item(1,0).text(),"2")
        self.assertEqual(self.win.bom_table.item(1,1).text(),"QS Hub 1500W")
        self.assertEqual(self.win.bom_table.item(1,3).text(),"QS10-1500")
        self.assertIn("1 จาก 2",self.win.visible_count_label.text())

    def test_search_price_filter_and_quick_export_navigation(self):
        self.win.show_page(1)
        self.win.search.setText("ESP32")
        self.assertEqual(self.win.bom_table.rowCount(),2)
        self.assertIn("ESP32",self.win.bom_table.item(1,1).text())
        self.win.price_filter.setCurrentText("มีราคา")
        self.assertEqual(self.win.bom_table.rowCount(),0)
        self.win.search.clear()
        self.win.price_filter.setCurrentText("ทุกราคา")
        self.win.show_page(4)
        self.assertEqual(self.win.stack.currentIndex(),4)
        self.assertEqual(len(self.win.nav_buttons),6)

    def test_four_tab_bom_editor_keeps_all_inputs(self):
        from bom_qt import RecordDialog, ITEM_FIELDS
        dlg = RecordDialog("แก้ไขอุปกรณ์", ITEM_FIELDS, {
            "category":"ระบบขับเคลื่อน", "name":"Motor", "qty":1,
            "spec":"72V 1500W","unitPrice":123.45,"link":"https://example.org"
        }, self.win)
        self.assertEqual(dlg.tabs.count(),4)
        self.assertFalse(dlg.widgets["category"].isEditable())
        self.assertEqual(dlg.widgets["spec"].toPlainText(),"72V 1500W")
        dlg.tabs.setCurrentIndex(2)
        self.assertEqual(dlg.get_values()["unitPrice"],"123.45")
        self.assertEqual(dlg.get_values()["link"],"https://example.org")
        dlg.close()

    def test_update_button_is_in_global_header_and_tracks_availability(self):
        # Updater must be reachable from ALL pages, not hidden in Reports.
        self.assertEqual(self.win.update_btn.parentWidget().objectName(), "topbar")
        self.assertEqual(self.win.update_btn.text(), "ตรวจสอบอัปเดต")
        self.assertTrue(self.win.install_btn.isHidden())
        self.assertTrue(self.win.update_btn.isEnabled())
        from unittest.mock import patch
        info = {"version": "9.9.9"}
        with patch.object(self.win, "_job", side_effect=lambda task, ok, fail,
                          context=None: ok(info)):
            for page in range(6):
                self.win.show_page(page)
                self.win.check_version(silent=True)
                self.assertFalse(self.win.install_btn.isHidden())
                self.assertTrue(self.win.install_btn.isEnabled())
                self.assertIn("9.9.9", self.win.version_label.text())
        with patch.object(self.win, "_job", side_effect=lambda task, ok, fail,
                          context=None: ok(None)):
            self.win.check_version(silent=True)
        self.assertTrue(self.win.install_btn.isHidden())
        self.assertFalse(self.win.install_btn.isEnabled())
        self.assertIn("ล่าสุด", self.win.version_label.text())

    def test_redesign_does_not_mutate_bom_on_navigation(self):
        import json
        before=json.dumps(self.win.payload,ensure_ascii=False,sort_keys=True)
        for tab in range(6):
            self.win.show_page(tab)
        self.win.group_mode.setCurrentIndex(1)
        self.win.search.setText("ESP32")
        after=json.dumps(self.win.payload,ensure_ascii=False,sort_keys=True)
        self.assertEqual(before,after)


if __name__ == "__main__":
    unittest.main()
