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
        finally:
            window.destroy()


if __name__ == "__main__":
    unittest.main()
