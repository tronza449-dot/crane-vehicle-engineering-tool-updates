"""Windows GUI smoke test for release packaging."""
import os
import sys
import tkinter as tk
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class DesktopSmokeTest(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Tkinter Windows UI check")
    def test_dashboard_tabs_load(self):
        from app import BOMApp, ItemDialog, FIELDS, api_request, APP_VERSION, API_URL, SERVICE
        from bom_ui import make_app
        app_type = make_app(BOMApp, ItemDialog, api_request, APP_VERSION, API_URL, SERVICE, FIELDS)
        try:
            window = app_type()
        except tk.TclError as exc:
            self.skipTest(f"Windows runner without graphical desktop: {exc}")
        try:
            window.withdraw()
            self.assertEqual(len(window.tabs.tabs()), 5)
            self.assertTrue(window.check_update_button.winfo_exists())
            self.assertTrue(window.install_update_button.winfo_exists())
            self.assertTrue(window.wiring_tree.winfo_exists())
            self.assertTrue(window.purchase_tree.winfo_exists())
            # Large readable Thai fonts and modern dashboard controls.
            from tkinter import font as tkfont, ttk
            font = tkfont.nametofont("TkDefaultFont")
            self.assertGreaterEqual(int(font.actual("size")), 12)
            self.assertIsNotNone(window.completion_bar)
            self.assertEqual(len(window.kpi_vars), 6)
            self.assertEqual(window.price_filter_var.get(), "ทุกราคา")
            sample = {"schemaVersion": 1, "project": "UI test", "items": [
                {"id": "1", "category": "ไฟฟ้า", "name": "ESP32", "qty": 1, "unitPrice": 300},
                {"id": "2", "category": "ไฟฟ้า", "name": "BMS", "qty": 1, "unitPrice": None}
            ]}
            window.payload = sample
            window.refresh_table()
            self.assertEqual(window.kpi_vars["items"].get(), "2")
            self.assertEqual(window.kpi_vars["missing"].get(), "1")
            self.assertEqual(window.completion_label.get(), "ความครบถ้วนของราคา 50%")
            window._dashboard_navigate("missing")
            self.assertEqual(window.tabs.select(), str(window.bom_tab))
            self.assertEqual(window.price_filter_var.get(), "ไม่มีราคา")
            self.assertEqual(len(window.tree.get_children()), 1)
            window._dashboard_navigate("priced")
            self.assertEqual(window.price_filter_var.get(), "มีราคา")
            self.assertEqual(len(window.tree.get_children()), 1)

        finally:
            window.destroy()


if __name__ == "__main__":
    unittest.main()
