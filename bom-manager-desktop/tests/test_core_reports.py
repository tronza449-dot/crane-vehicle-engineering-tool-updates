"""Check BOM integrity and real output files without starting the Tkinter GUI."""
import csv
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bom_core
import bom_reports


class DataRulesTests(unittest.TestCase):
    def setUp(self):
        self.document = {
            "schemaVersion": 1, "project": "ทดสอบ", "otherField": {"keep": True},
            "items": [
                {"id": "1", "name": "ESP32", "qty": 2, "unitPrice": 125.50,
                 "status": "เลือกแล้ว", "extraKey": "must remain"},
                {"id": "2", "name": "BMS", "qty": 1, "unitPrice": None}
            ],
            "wiring": [{"id": "1", "from": "BMS B+", "to": "Main fuse",
                        "protection": "Fuse pending", "status": "รอตรวจสอบ"}],
            "purchases": [{"id": "1", "itemId": "1", "description": "ESP32", "qty": 2,
                           "unitPrice": 120, "status": "สั่งแล้ว"}]
        }

    def test_metrics_ignore_unknown_price(self):
        m = bom_core.metrics(self.document)
        self.assertEqual(m["known_cost"], 251)
        self.assertEqual(m["missing"], 1)
        self.assertEqual(m["purchase_total"], 240)
        self.assertEqual(m["wires"], 1)

    def test_prevent_bad_items_and_duplicate_ids(self):
        import copy
        dup = copy.deepcopy(self.document)
        dup["items"][1]["id"] = "1"
        with self.assertRaises(bom_core.DataError):
            bom_core.ensure_doc(dup)
        for invalid in ("-1", "NaN", "abc"):
            with self.assertRaises(bom_core.DataError):
                bom_core.valid_qty(invalid)

    def test_csv_with_formula_guard(self):
        self.document["items"][0]["name"] = "=HYPERLINK(\"evil\")"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bom.csv"
            bom_reports.export_csv(self.document, path)
            with open(path, encoding="utf-8-sig", newline="") as f:
                data = list(csv.reader(f))
            self.assertTrue(data[1][2].startswith("'="))
            self.assertEqual(len(data), 3)

    def test_excel_all_tabs_and_formulas(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "output.xlsx"
            bom_reports.export_excel(self.document, path)
            with zipfile.ZipFile(path) as z:
                names = set(z.namelist())
                self.assertIn("xl/worksheets/sheet1.xml", names)
                book = z.read("xl/workbook.xml").decode()
                self.assertIn('name="Wiring"', book)
                self.assertIn('name="Purchasing"', book)
                self.assertIn('name="Summary"', book)
                bom = z.read("xl/worksheets/sheet1.xml").decode()
                self.assertIn("E5*G5", bom)
                self.assertIn("H5", bom)
            self.assertGreater(path.stat().st_size, 4000)

    def test_json_keeps_extra_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "backup.json"
            bom_reports.export_json(self.document, path)
            restored = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(restored["otherField"]["keep"])
            self.assertEqual(restored["items"][0]["extraKey"], "must remain")

    def test_wiring_reference_check(self):
        self.document["wiring"][0]["fromItemId"] = "999"
        issues = bom_core.connection_warnings(self.document)
        self.assertTrue(any("999" in issue for issue in issues))

    def test_real_bom_excel_and_pdf(self):
        raw_path = Path(__file__).resolve().parents[2] / "bom-manager" / "bom.json"
        doc = json.loads(raw_path.read_text(encoding="utf-8"))
        bom_core.ensure_doc(doc)
        with tempfile.TemporaryDirectory() as directory:
            xlsx = Path(directory) / "real.xlsx"
            bom_reports.export_excel(doc, xlsx)
            self.assertGreater(xlsx.stat().st_size, 7000)
            try:
                bom_reports._thai_font()
            except RuntimeError:
                self.skipTest("ไม่มีฟอนต์ไทยในสภาพแวดล้อมทดสอบ")
            pdf = Path(directory) / "real.pdf"
            bom_reports.export_pdf(doc, pdf)
            self.assertTrue(pdf.read_bytes().startswith(b"%PDF"))
            self.assertGreater(pdf.stat().st_size, 2000)


if __name__ == "__main__":
    unittest.main()
