"""Accessible Thai font scaling, high-contrast UI and persistence tests."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class ReadabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        from PySide6.QtCore import QSettings
        import bom_qt_theme as theme
        self.folder = tempfile.TemporaryDirectory()
        self.settings = QSettings(
            str(Path(self.folder.name) / "ui-settings.ini"),
            QSettings.Format.IniFormat)
        self.patcher = patch.object(theme, "_settings", return_value=self.settings)
        self.patcher.start()
        theme.apply_theme(self.app)
        from bom_qt import BOMWindow
        self.window = BOMWindow(auto_load=False)

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.patcher.stop()
        self.folder.cleanup()

    def test_legibility_controls_and_default(self):
        import bom_qt_theme as theme
        from PySide6.QtWidgets import QScrollArea
        self.assertEqual(theme.current_scale(), 1.15)
        self.assertEqual(self.window.zoom_factor, 1.15)
        self.assertEqual(self.window.font_scale_selector.count(), 4)
        self.assertEqual(self.window.font_family_selector.count(), 2)
        self.assertIsInstance(self.window.stack.widget(0), QScrollArea)
        self.assertGreaterEqual(self.window.bom_table.verticalHeader().defaultSectionSize(), 60)
        self.assertGreaterEqual(self.window.bom_table.horizontalHeader().height(), 65)
        self.assertTrue(self.window.steel_table.wordWrap())
        self.assertEqual(self.window.steel_table.columnCount(), 14)
        self.assertIn("\\n", self.window.steel_table.horizontalHeaderItem(5).text())
        from PySide6.QtGui import QFont
        self.assertEqual(theme.current_font(), "Tahoma")
        self.assertEqual(self.window.font_family_selector.currentText(), "Tahoma")
        self.assertEqual(self.app.font().family(), "Tahoma")
        self.assertEqual(self.app.font().hintingPreference(),
                         QFont.HintingPreference.PreferFullHinting)
        self.assertIn("font-size: 18px", self.app.styleSheet())
        self.assertIn('font-family: "Tahoma";', self.app.styleSheet())
        self.assertIn("color: #172D45;", self.app.styleSheet())
        self.assertIn("color: #344B63;", self.app.styleSheet())
        self.assertIn("background: #10243D;", self.app.styleSheet())

    def test_switch_fonts_and_persist_text_zoom(self):
        import bom_qt_theme as theme
        # Exercise all selector callbacks and persistence without repeatedly
        # forcing Qt to re-polish every widget in the full 7-page window.
        # The actual stylesheet generator is checked separately below.
        with patch.object(theme, "apply_theme") as apply_theme:
            self.window.font_scale_selector.setCurrentIndex(2)
            self.assertEqual(theme.current_scale(), 1.3)
            self.assertEqual(self.window.zoom_factor, 1.3)
            self.assertGreaterEqual(
                self.window.bom_table.verticalHeader().defaultSectionSize(), 68)
            self.window.font_family_selector.setCurrentText("Leelawadee UI")
            self.assertEqual(theme.current_font(), "Leelawadee UI")
            self.window.font_family_selector.setCurrentText("Tahoma")
            self.assertEqual(theme.current_font(), "Tahoma")
            self.window.increase_font_scale()
            self.assertEqual(theme.current_scale(), 1.45)
            self.window.reset_font_scale()
            self.assertEqual(theme.current_scale(), 1.15)
            self.window.decrease_font_scale()
            self.assertEqual(theme.current_scale(), 1.0)
            self.assertEqual(apply_theme.call_count, 6)

    def test_stylesheet_generator_supports_each_font_without_repainting_window(self):
        import bom_qt_theme as theme

        class StyleSink:
            def setFont(self, font):
                self.font = font

            def setStyleSheet(self, stylesheet):
                self.stylesheet = stylesheet

        sink = StyleSink()
        result = theme.apply_theme(sink, scale=1.3, font_family="Leelawadee UI")
        self.assertEqual(result, {"scale": 1.3, "font_family": "Leelawadee UI"})
        self.assertIn('font-family: "Leelawadee UI";', sink.stylesheet)
        self.assertIn("font-size: 21px", sink.stylesheet)
        self.assertEqual(sink.font.family(), "Leelawadee UI")

    def test_large_text_does_not_remove_data_or_update_controls(self):
        self.window.payload = {
            "schemaVersion": 1, "project": "test",
            "items": [{"id": "1", "category": "control", "name": "ESP32",
                       "qty": 1, "unitPrice": None}]
        }
        self.window.render_all()
        self.window.font_scale_selector.setCurrentIndex(3)
        self.assertEqual(self.window.stack.count(), 7)
        self.assertEqual(self.window.bom_table.rowCount(), 2)
        self.assertTrue(self.window.update_btn.isEnabled())
        self.assertEqual(self.window.cards["missing"].figure.text(), "1")


if __name__ == "__main__":
    unittest.main()
