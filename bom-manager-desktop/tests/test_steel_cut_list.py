"""Structural steel cut-list validation, totals, GUI, sync schema and reports."""
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import bom_steel
import bom_core
import bom_advanced


class SteelQuantityTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"id": "1", "member": "คานยาวฐานรถ", "profile": "เหล็กกล่องสี่เหลี่ยม",
             "size": "25×25×2 mm", "qty": 4, "length_mm": 750,
             "stock_length_m": 6, "notes": ""},
            {"id": "2", "member": "ค้ำฐาน", "profile": "เหล็กกล่องสี่เหลี่ยม",
             "size": "25×25×2 mm", "qty": 2, "length_mm": 1200,
             "stock_length_m": 6, "notes": ""},
            {"id": "3", "member": "เสาโครง", "profile": "เหล็กกล่องสี่เหลี่ยม",
             "size": "40×40×2 mm", "qty": 2, "length_mm": 2000,
             "stock_length_m": 6, "notes": ""},
        ]

    def test_totals_group_by_profile_size_and_stock_length(self):
        result = bom_steel.summarize(self.rows)
        self.assertEqual(result["total_pieces"], 8)
        self.assertAlmostEqual(float(result["total_length_m"]), 9.4)
        self.assertEqual(result["estimated_stock_bars"], 2)
        groups = {g["size"]: g for g in result["groups"]}
        self.assertEqual(groups["25×25×2 mm"]["pieces"], 6)
        self.assertAlmostEqual(float(groups["25×25×2 mm"]["total_length_m"]), 5.4)
        self.assertEqual(groups["25×25×2 mm"]["estimated_stock_bars"], 1)
        self.assertAlmostEqual(float(groups["40×40×2 mm"]["total_length_m"]), 4.0)
        self.assertEqual(groups["40×40×2 mm"]["estimated_stock_bars"], 1)

    def test_material_is_separate_from_profile_and_does_not_mix_stock_totals(self):
        carbon = dict(self.rows[0], material="เหล็กคาร์บอน (SS400 / ASTM A36)")
        stainless = dict(self.rows[1], material="สแตนเลส SUS 304")
        same_stainless = dict(self.rows[2], material="สแตนเลส SUS 304",
                              size="25×25×2 mm", qty=1, length_mm=600)
        result = bom_steel.summarize([carbon, stainless, same_stainless])
        self.assertEqual(len(result["groups"]), 2)
        carbon_group = next(g for g in result["groups"]
                            if g["material"].startswith("เหล็กคาร์บอน"))
        stainless_group = next(g for g in result["groups"]
                               if g["material"] == "สแตนเลส SUS 304")
        self.assertEqual(carbon_group["pieces"], 4)
        self.assertEqual(stainless_group["pieces"], 3)
        self.assertEqual(stainless_group["estimated_stock_bars"], 1)
        self.assertIn("วัสดุเดิม/ไม่ระบุเกรด", bom_steel.normalize_member(self.rows[0])["material"])

    def test_invalid_values_are_rejected(self):
        invalid = dict(self.rows[0], length_mm=0)
        with self.assertRaises(bom_steel.SteelDataError):
            bom_steel.normalize_member(invalid)
        invalid = dict(self.rows[0], qty=1.5)
        with self.assertRaises(bom_steel.SteelDataError):
            bom_steel.normalize_member(invalid)
        invalid = dict(self.rows[0], size="")
        with self.assertRaises(bom_steel.SteelDataError):
            bom_steel.normalize_member(invalid)
        invalid = dict(self.rows[0], length_mm=7000, stock_length_m=6)
        with self.assertRaises(bom_steel.SteelDataError):
            bom_steel.normalize_member(invalid)

    def test_core_schema_and_multi_pc_merge_preserve_steel_members(self):
        doc = {"items": [], "wiring": [], "purchases": [],
               "steel_members": [dict(self.rows[0])]}
        bom_core.ensure_doc(doc)
        base = {"items": [], "wiring": [], "purchases": [], "steel_members": []}
        local = json.loads(json.dumps(base))
        remote = json.loads(json.dumps(base))
        local["steel_members"].append(dict(self.rows[0]))
        merged, conflicts = bom_advanced.merge_docs(base, local, remote)
        self.assertFalse(conflicts)
        self.assertEqual(merged["steel_members"][0]["id"], "1")

    def test_manual_weight_mode_supports_non_tubular_parts_without_length(self):
        row = {
            "id": "M1", "member": "ขายึดมอเตอร์", "weight_mode": bom_steel.WEIGHT_MODE_MANUAL,
            "profile": "ชิ้นส่วนอื่น", "size": "", "qty": 3,
            "manual_unit_weight_kg": "0.85", "link": "https://example.org/bracket",
        }
        normalized = bom_steel.normalize_member(row)
        self.assertEqual(normalized["size"], "ไม่ระบุขนาด")
        self.assertIsNone(normalized["length_mm"])
        self.assertIsNone(normalized["stock_length_m"])
        self.assertEqual(bom_steel.total_length_m(normalized), 0)
        self.assertEqual(bom_steel.weight_per_m(normalized), None)
        self.assertEqual(bom_steel.total_weight_kg(normalized), 2.55)
        result = bom_steel.summarize([row])
        self.assertEqual(result["total_pieces"], 3)
        self.assertEqual(result["total_length_m"], 0)
        self.assertEqual(result["known_weight_kg"], 2.55)
        self.assertEqual(result["unknown_weight_length_m"], 0)
        self.assertEqual(result["estimated_stock_bars"], 0)

    def test_excel_has_cut_list_and_summary_formulas(self):
        import bom_official_reports as reports
        report_rows = [
            dict(self.rows[0], material="สแตนเลส SUS 304",
                 link="https://example.org/steel-square-tube"),
            dict(self.rows[1], material="เหล็กคาร์บอน (SS400 / ASTM A36)"),
            dict(self.rows[2], material="อะลูมิเนียม 6061"),
        ]
        doc = {"schemaVersion": 1, "project": "Steel test", "items": [],
               "wiring": [], "purchases": [], "steel_members": report_rows}
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "steel.xlsx"
            reports.export_excel(doc, target, {"author": "Test"})
            with zipfile.ZipFile(target) as book:
                workbook = book.read("xl/workbook.xml").decode("utf-8")
                self.assertIn('name="Steel Summary"', workbook)
                self.assertIn('name="Steel Cut List"', workbook)
                shared = book.read("xl/sharedStrings.xml").decode("utf-8")
                self.assertIn("คานยาวฐานรถ", shared)
                self.assertIn("40×40×2 mm", shared)
                self.assertIn("สแตนเลส SUS 304", shared)
                self.assertIn("อะลูมิเนียม 6061", shared)
                self.assertIn("เปิดลิงก์สินค้า", shared)
                link_rels = book.read(
                    "xl/worksheets/_rels/sheet11.xml.rels").decode("utf-8")
                self.assertIn("https://example.org/steel-square-tube", link_rels)
                summary_xml = book.read("xl/worksheets/sheet10.xml").decode("utf-8")
                cut_xml = book.read("xl/worksheets/sheet11.xml").decode("utf-8")
                self.assertIn("SUMIFS", summary_xml)
                self.assertIn("ROUNDUP", summary_xml)
                self.assertIn("F8*G8/1000", cut_xml)

    def test_pdf_contains_steel_cut_list(self):
        import bom_official_reports as reports
        from bom_reports import _thai_font
        try:
            _thai_font()
        except RuntimeError:
            self.skipTest("System has no supported Thai PDF font")
        report_rows = [
            dict(self.rows[0], material="สแตนเลส SUS 304",
                 link="https://example.org/steel-square-tube"),
            dict(self.rows[1], material="เหล็กคาร์บอน (SS400 / ASTM A36)"),
            dict(self.rows[2], material="อะลูมิเนียม 6061"),
        ]
        doc = {"schemaVersion": 1, "project": "Steel test", "items": [],
               "wiring": [], "purchases": [], "steel_members": report_rows}
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "steel.pdf"
            reports.export_pdf(doc, target, {"author": "Test"})
            import fitz
            with fitz.open(str(target)) as pdf:
                text = "\n".join(page.get_text() for page in pdf)
            self.assertIn("STEEL CUT LIST", text)
            self.assertIn("คานยาวฐานรถ", text)
            self.assertIn("25×25×2 mm", text)
            self.assertIn("สแตนเลส SUS 304", text)
            self.assertIn("อะลูมิเนียม 6061", text)
            self.assertIn("example.org", text)


class SteelPageTests(unittest.TestCase):
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

    def tearDown(self):
        self.win.dirty = False
        self.win.close()
        self.win.deleteLater()

    def test_steel_page_and_editor_calculate_metres(self):
        from bom_qt import RecordDialog, STEEL_FIELDS
        self.assertEqual(self.win.stack.count(), 7)
        self.assertEqual(self.win.nav_buttons[2].text(), "▦    โครงสร้างเหล็ก / Cut List")
        dialog = RecordDialog("เพิ่มชิ้นส่วนโครงสร้างเหล็ก", STEEL_FIELDS, {
            "member": "คานยาวฐานรถ", "profile": "เหล็กกล่องสี่เหลี่ยม",
            "size": "25×25×2 mm", "qty": 4, "length_mm": 750,
            "stock_length_m": 6, "link": "https://example.org/steel-square-tube",
        }, self.win)
        self.assertTrue(dialog.widgets["profile"].isEditable())
        self.assertTrue(dialog.widgets["material"].isEditable())
        dialog.widgets["material"].setEditText("เหล็ก SCM440 custom")
        dialog.widgets["profile"].setEditText("หน้าตัด Z-Channel custom")
        custom = bom_steel.normalize_member(dialog.get_values())
        self.assertEqual(custom["material"], "เหล็ก SCM440 custom")
        self.assertEqual(custom["profile"], "หน้าตัด Z-Channel custom")
        # Custom entries must survive validation and become part of the saved row.
        self.assertEqual(custom["size"], "25×25×2 mm")
        self.assertEqual(custom["link"], "https://example.org/steel-square-tube")
        self.assertEqual(dialog.widgets["link"].text(),
                         "https://example.org/steel-square-tube")
        dialog.widgets["material"].setCurrentText("วัสดุเดิม/ไม่ระบุเกรด")
        dialog.widgets["profile"].setCurrentText("เหล็กกล่องสี่เหลี่ยม")
        self.assertIn("สแตนเลส SUS 304", [
            dialog.widgets["material"].itemText(i)
            for i in range(dialog.widgets["material"].count())])
        self.assertIn("สแตนเลส SUS 316", [
            dialog.widgets["material"].itemText(i)
            for i in range(dialog.widgets["material"].count())])
        self.assertIn("อะลูมิเนียม 6061", [
            dialog.widgets["material"].itemText(i)
            for i in range(dialog.widgets["material"].count())])
        values = bom_steel.normalize_member(dialog.get_values())
        self.assertEqual(values["qty"], 4)
        self.assertAlmostEqual(float(bom_steel.total_length_m(values)), 3.0)
        dialog.close()
        self.win.payload["steel_members"] = [
            {"id": "1", **values},
            {"id": "2", "member": "ค้ำฐาน", "profile": "เหล็กกล่องสี่เหลี่ยม",
             "size": "25×25×2 mm", "qty": 2, "length_mm": 1200,
             "stock_length_m": 6},
        ]
        self.win.render_all()
        self.win.show_page(2)
        self.assertEqual(self.win.steel_table.rowCount(), 2)
        self.assertEqual(self.win.steel_table.columnCount(), 17)
        self.assertEqual(self.win.steel_table.item(0, 15).text(), "เปิดลิงก์ ↗")
        self.assertEqual(self.win.steel_table.item(0, 15).toolTip(),
                         "https://example.org/steel-square-tube")
        self.assertEqual(self.win.steel_summary_table.rowCount(), 1)
        self.assertIn("5.400 m", self.win.steel_totals_label.text())
        self.assertIn("1 ท่อน", self.win.steel_totals_label.text())


if __name__ == "__main__":
    unittest.main()
