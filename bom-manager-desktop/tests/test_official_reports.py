"""Checks the formal PDF and Excel artifacts for presentation-ready structure."""
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import bom_official_reports as reports
import bom_core

MAIN = ROOT.parent / "bom-manager" / "bom.json"


class ReportExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(MAIN.read_text(encoding="utf-8"))
        bom_core.ensure_doc(cls.doc)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.metadata = {
            "author": "ทดสอบการจัดทำรายงาน",
            "institution": "สถาบันทดสอบด้านวิศวกรรม",
            "document_no": "ENG-BOM-2026-01",
            "revision": "A",
        }

    def test_category_totals_match_budget(self):
        rows = reports.category_stats(self.doc["items"])
        stats = bom_core.metrics(self.doc)
        self.assertEqual(sum(x[1] for x in rows), 33)
        self.assertEqual(sum(x[2] for x in rows), stats["missing"])
        self.assertAlmostEqual(sum(x[3] for x in rows), stats["known_cost"])
        self.assertEqual(len(rows), 7)

    def test_custom_item_order_is_preserved_in_formal_reports(self):
        # Names are deliberately reverse alphabetical, as a user-arranged BOM.
        doc = {"items": [
            {"id": "20", "category": "ระบบขับเคลื่อน", "name": "Z Motor"},
            {"id": "5", "category": "ระบบขับเคลื่อน", "name": "A Motor"},
            {"id": "6", "category": "แบตเตอรี่และไฟฟ้ากำลัง",
             "name": "Battery"},
        ]}
        ordered = reports.sorted_items(doc)
        self.assertEqual([x["id"] for x in ordered], ["20", "5", "6"])
        self.assertEqual([x["id"] for x in doc["items"]], ["20", "5", "6"])

    def test_formal_excel_has_sections_and_working_budget_formulas(self):
        file = Path(self.temp.name) / "formal.xlsx"
        snapshot = json.dumps(self.doc, ensure_ascii=False, sort_keys=True)
        reports.export_excel(self.doc, file, self.metadata)
        self.assertEqual(snapshot, json.dumps(self.doc, ensure_ascii=False, sort_keys=True))
        self.assertGreater(file.stat().st_size, 10000)
        with zipfile.ZipFile(file) as xlsx:
            names = set(xlsx.namelist())
            self.assertIn("xl/worksheets/sheet6.xml", names)
            self.assertIn("xl/worksheets/sheet7.xml", names)
            self.assertIn("xl/worksheets/sheet8.xml", names)
            wb = xlsx.read("xl/workbook.xml").decode("utf-8")
            for tab in ("Summary","BOM","Specification","Wiring","Purchasing",
                        "Notes","References","Completeness"):
                self.assertIn('name="'+tab+'"', wb)
            summary = xlsx.read("xl/worksheets/sheet1.xml").decode("utf-8")
            detail = xlsx.read("xl/worksheets/sheet2.xml").decode("utf-8")
            self.assertIn("COUNTIFS", summary)
            self.assertIn("SUMIF", summary)
            self.assertIn("COUNTA", summary)
            self.assertIn("IF(G8", detail)
            self.assertIn("E8*G8", detail)
            self.assertIn("SUMIF", summary)
            self.assertIn("COUNTIFS", summary)
            self.assertIn("autoFilter", detail)
            self.assertIn("sheetViews", detail)
            self.assertIn("pageSetup", detail)
            # Unknown pricing must not be exported as a numeric zero input.
            root = ET.fromstring(detail)
            ns={"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            formula_cells = [c for c in root.findall(".//x:c",ns)
                             if c.find("x:f",ns) is not None]
            self.assertEqual(len(formula_cells), len(self.doc["items"]))
            blank_inputs = sum(reports.price(x.get("unitPrice")) is None
                               for x in self.doc["items"])
            self.assertGreater(blank_inputs,0)
            self.assertIn("xl/styles.xml", names)
            self.assertIn("autoFilter", xlsx.read("xl/worksheets/sheet7.xml").decode())
            review = xlsx.read("xl/worksheets/sheet8.xml").decode("utf-8")
            self.assertIn("mergeCell", review)

    def test_formal_pdf_sections_and_metadata(self):
        from bom_reports import _thai_font
        try:
            _thai_font()
        except RuntimeError:
            self.skipTest("System has no supported Thai PDF font")
        pdf = Path(self.temp.name) / "formal.pdf"
        reports.export_pdf(self.doc, pdf, self.metadata)
        self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
        self.assertGreater(pdf.stat().st_size, 10000)

    def test_explicit_identification_and_traceability_counts(self):
        gaps = reports.report_quality(self.doc["items"])
        for metric, field in (
            ("part_number_missing", "partNumber"),
            ("supplier_missing", "supplier"),
            ("reference_missing", "link"),
        ):
            expected = sum(not str(item.get(field) or "").strip()
                           for item in self.doc["items"])
            self.assertEqual(gaps[metric], expected)
        missing_prices = sum(reports.price(item.get("unitPrice")) is None
                             for item in self.doc["items"])
        self.assertEqual(gaps["price_missing"], missing_prices)
        self.assertEqual(missing_prices, bom_core.metrics(self.doc)["missing"])

    def test_missing_price_not_totalled(self):
        doc={"schemaVersion": 1,"project": "Test",
             "items": [
                 {"id":"1","category":"ระบบขับเคลื่อน",
                  "name":"Motor","qty":2,"unitPrice":100},
                 {"id":"2","category":"ระบบขับเคลื่อน",
                  "name":"Unknown","qty":1,"unitPrice":None},
             ]}
        prices=reports.category_stats(doc["items"])
        self.assertEqual(prices[0][1:],(2,1,200.0))
        self.assertEqual(bom_core.metrics(doc)["known_cost"],200)


if __name__ == "__main__":
    unittest.main()
