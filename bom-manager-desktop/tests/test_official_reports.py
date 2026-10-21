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
import bom_categories

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
            "advisor": "อาจารย์ทดสอบ",
            "document_no": "ENG-BOM-2026-01",
            "revision": "A",
            "date": "18/10/2026",
        }

    def test_category_totals_match_budget(self):
        rows = reports.category_stats(self.doc["items"])
        stats = bom_core.metrics(self.doc)
        # Reports must include *every* live BOM item, including additions
        # after the original 33-item baseline, without changing user data.
        self.assertEqual(sum(x[1] for x in rows), len(self.doc["items"]))
        self.assertEqual(sum(x[2] for x in rows), stats["missing"])
        self.assertAlmostEqual(sum(x[3] for x in rows), float(stats["known_cost"]))
        self.assertEqual(len(rows), len({bom_categories.normalize_category(
            x.get("category")) for x in self.doc["items"]}))
        self.assertLessEqual({x[0] for x in rows},
                             set(bom_categories.CATEGORY_OPTIONS))

    def test_shared_bom_uses_only_major_categories(self):
        categories = {item.get("category") for item in self.doc["items"]}
        self.assertTrue(categories.issubset(set(bom_categories.CATEGORY_OPTIONS)))
        self.assertEqual(categories, {"เครื่องกล", "ไฟฟ้ากำลัง", "อิเล็กทรอนิกส์/ควบคุม"})
        # The shared BOM may grow as the project evolves; category shape is
        # fixed, but the number of legitimate records is not.
        self.assertGreaterEqual(len(self.doc["items"]), 33)

    def test_legacy_labels_collapse_to_three_major_categories(self):
        items = [
            {"id":"1","category":"โครงสร้างและเครื่องกล"},
            {"id":"2","category":"แบตเตอรี่และไฟฟ้า"},
            {"id":"3","category":"ระบบควบคุมและสื่อสาร"},
            {"id":"4","category":"ระบบเครนและวินช์"},
            {"id":"5","category":"unrecognized imported label"},
        ]
        self.assertEqual(
            [bom_categories.normalize_category(x["category"]) for x in items],
            ["เครื่องกล", "ไฟฟ้ากำลัง", "อิเล็กทรอนิกส์/ควบคุม", "เครื่องกล", "อื่น ๆ"])
        self.assertEqual(
            {category for category, _ in bom_categories.summary(items)},
            {"เครื่องกล", "ไฟฟ้ากำลัง", "อิเล็กทรอนิกส์/ควบคุม", "อื่น ๆ"})

    def test_custom_item_order_is_preserved_in_formal_reports(self):
        # Names are deliberately reverse alphabetical, as a user-arranged BOM.
        doc = {"items": [
            {"id": "20", "category": "ระบบขับเคลื่อน", "name": "Z Motor"},
            {"id": "5", "category": "ระบบขับเคลื่อน", "name": "A Motor"},
            {"id": "6", "category": "แบตเตอรี่และไฟฟ้า",
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
            self.assertIn("xl/worksheets/sheet9.xml", names)
            wb = xlsx.read("xl/workbook.xml").decode("utf-8")
            for tab in ("Summary","BOM","Specification","Wiring","Purchasing",
                        "Notes","References","Completeness","Approval",
                        "Steel Summary","Steel Cut List","Mass Summary"):
                self.assertIn('name="'+tab+'"', wb)
            summary = xlsx.read("xl/worksheets/sheet1.xml").decode("utf-8")
            detail = xlsx.read("xl/worksheets/sheet2.xml").decode("utf-8")
            self.assertIn("COUNTIFS", summary)
            self.assertIn("SUMIF", summary)
            shared = xlsx.read("xl/sharedStrings.xml").decode("utf-8")
            self.assertIn("MASTER BOM REGISTER", shared)
            self.assertIn("ไฟฟ้ากำลัง", shared)
            self.assertIn("CATEGORY DEFINITIONS", shared)
            self.assertIn("อิเล็กทรอนิกส์/ควบคุม", shared)
            self.assertIn("ผู้ตรวจสอบ / อาจารย์ที่ปรึกษา", shared)
            self.assertIn("อาจารย์ทดสอบ", shared)
            self.assertIn("ผู้จัดทำ / PREPARED BY", shared)
            self.assertIn("ผู้ตรวจสอบ / REVIEWED BY", shared)
            self.assertIn("18/10/2026", shared)
            # Row 8 is the first category band, so the first item is row 9.
            # Each category adds a band row and a SUBTOTAL row; the grand
            # total uses SUBTOTAL so category subtotals are not counted twice.
            categories = len(reports.category_stats(self.doc["items"]))
            last_row = 7 + len(self.doc["items"]) + 2 * categories
            self.assertIn(f"SUBTOTAL(9,H8:H{last_row})", detail)
            self.assertIn("SUBTOTAL(9,BOM!$H$8:$H$" + str(last_row), summary)
            self.assertIn("COUNTA", summary)
            self.assertIn("IF(G9", detail)
            self.assertIn("E9*G9", detail)
            self.assertIn("IF(J9", detail)
            self.assertIn("E9*J9", detail)
            self.assertIn("หมวดหลัก: เครื่องกล", shared)
            self.assertIn("รวมหมวด เครื่องกล", shared)
            mass_sheet = xlsx.read("xl/worksheets/sheet12.xml").decode("utf-8")
            self.assertIn("SUM(BOM!K8:K", mass_sheet)
            self.assertIn("Steel Cut List", mass_sheet)
            self.assertIn("น้ำหนักรวม (kg)", shared)
            self.assertIn("น้ำหนัก/หน่วย (kg)", shared)
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
            self.assertEqual(len(formula_cells),
                             2 * len(self.doc["items"]) + categories + 1)
            # Each BOM row has price and mass formulas, plus one subtotal per
            # category and the price grand total.
            # Cached formula values must never be the text "None": Excel then
            # reports the workbook as damaged and repairs it.
            for part in names:
                if part.startswith("xl/worksheets/sheet"):
                    self.assertNotIn("<v>None</v>", xlsx.read(part).decode("utf-8"), part)
            blank_inputs = sum(reports.price(x.get("unitPrice")) is None
                               for x in self.doc["items"])
            self.assertGreater(blank_inputs,0)
            self.assertIn("xl/styles.xml", names)
            self.assertIn("autoFilter", xlsx.read("xl/worksheets/sheet7.xml").decode())
            review = xlsx.read("xl/worksheets/sheet8.xml").decode("utf-8")
            self.assertIn("mergeCell", review)
            approval = xlsx.read("xl/worksheets/sheet9.xml").decode("utf-8")
            self.assertIn("mergeCell", approval)
            self.assertIn("pageSetup", approval)
            self.assertIn("printOptions", approval)

    def test_excel_uses_design_a_black_and_white_print_style(self):
        # Design A (chosen by the user): black ink, light-grey header and
        # group bands, Tahoma, A4 paper. No colour fills from older designs.
        self.assertEqual(reports.INK, "#000000")
        self.assertEqual(reports.HEAD_FILL, "#E6E6E6")
        self.assertEqual(reports.BAND_FILL, "#F2F2F2")
        self.assertEqual(reports.EXCEL_FONT, "Tahoma")
        file = Path(self.temp.name) / "palette.xlsx"
        reports.export_excel(self.doc, file, self.metadata)
        with zipfile.ZipFile(file) as xlsx:
            styles = xlsx.read("xl/styles.xml").decode("utf-8").upper()
            self.assertIn("FFE6E6E6", styles)   # table header fill
            self.assertIn("FFF2F2F2", styles)   # category band fill
            self.assertIn("TAHOMA", styles)
            for old_colour in ("FF123B4A", "FF087E8B", "FFDDEFF1", "FF18324F"):
                self.assertNotIn(old_colour, styles)
            for part in xlsx.namelist():
                if part.startswith("xl/worksheets/sheet"):
                    sheet = xlsx.read(part).decode("utf-8")
                    self.assertIn('paperSize="9"', sheet, part)  # A4 everywhere

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
        import fitz
        with fitz.open(str(pdf)) as exported:
            self.assertGreaterEqual(len(exported), 7)
            # A4 throughout: portrait main report, landscape appendices.
            sizes = {(round(page.rect.width), round(page.rect.height)) for page in exported}
            self.assertEqual(sizes, {(595, 842), (842, 595)})
            self.assertIn("หน้า 1 / " + str(len(exported)), exported[0].get_text())
            # The revised PDF must be white-paper friendly: no solid navy cover
            # panel or full-width dark running header on interior pages.
            cover_pix = exported[0].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
            cover_corner = cover_pix.pixel(cover_pix.width - 45, 90)
            self.assertTrue(all(channel >= 230 for channel in cover_corner),
                            f"Cover background should be white/light, got {cover_corner}")
            interior_pix = exported[1].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
            header_corner = interior_pix.pixel(10, 10)
            self.assertTrue(all(channel >= 230 for channel in header_corner),
                            f"Interior header should not be a dark full-width band: {header_corner}")
            report_text = " ".join(page.get_text() for page in exported)
            self.assertIn("ENGINEERING DESIGN DOCUMENT", report_text)
            self.assertIn("DOCUMENT CONTROL", report_text)
            self.assertIn("BILL OF MATERIALS (BOM)", report_text)
            self.assertIn("MASTER BOM REGISTER", report_text)
            self.assertIn("ไฟฟ้ากำลัง", report_text)
            self.assertIn("CATEGORY DEFINITIONS", report_text)
            self.assertIn("อิเล็กทรอนิกส์/ควบคุม", report_text)
            self.assertIn("ผู้ตรวจสอบ / อาจารย์ที่ปรึกษา", report_text)
            self.assertIn("อาจารย์ทดสอบ", report_text)
            self.assertIn("18/10/2026", report_text)
            self.assertIn("PREPARED & REVIEWED", report_text)
            self.assertIn("ผู้จัดทำ / PREPARED BY", report_text)
            self.assertIn("ผู้ตรวจสอบ / REVIEWED BY", report_text)
            self.assertIn("ลายมือชื่อ", report_text)
            signoff = exported[-1].get_text()
            self.assertIn("PREPARED & REVIEWED", signoff)
            self.assertIn("อาจารย์ทดสอบ", signoff)
            # The master register is visibly divided into top-level system groups.
            self.assertIn("MASTER BOM REGISTER", report_text)
            self.assertIn("TOTAL MASS ROLL-UP", report_text)
            self.assertIn("น้ำหนัก/หน่วย (kg)", report_text)
            self.assertIn("น้ำหนักรวมที่ทราบ (kg)", report_text)
            self.assertIn("รายการ", report_text)
            self.assertIn("หมวดหลัก: เครื่องกล", report_text)
            self.assertIn("หมวดหลัก: ไฟฟ้ากำลัง", report_text)
            self.assertIn("หมวดหลัก: อิเล็กทรอนิกส์/ควบคุม", report_text)
            for heading in ("หมวดหลัก: เครื่องกล", "หมวดหลัก: ไฟฟ้ากำลัง",
                            "หมวดหลัก: อิเล็กทรอนิกส์/ควบคุม"):
                pages = [page.get_text() for page in exported if heading in page.get_text()]
                self.assertTrue(pages, f"Missing grouped table title: {heading}")
                self.assertTrue(any("BOM ID" in page_text for page_text in pages),
                                f"Column header did not repeat with {heading}")


    def test_mass_rollup_in_pdf_and_excel_uses_entered_weights(self):
        import copy
        from decimal import Decimal
        from bom_steel_bom import summarize_bom_and_steel
        doc = copy.deepcopy(self.doc)
        # Isolate this example from optional weights already stored in the live BOM.
        # The expected 6.50 kg is specifically 2 units × 3.25 kg per unit.
        for item in doc["items"]:
            item["unitWeightKg"] = None
        doc["items"][0]["qty"] = 2
        doc["items"][0]["unitWeightKg"] = 3.25
        doc["steel_members"] = [{
            "id": "S1", "member": "Frame rail", "material": "SS400",
            "profile": "เหล็กกล่องสี่เหลี่ยม", "size": "40x40x2 mm",
            "qty": 2, "length_mm": 500, "stock_length_m": 6,
            "weight_reference_length_m": 6, "weight_reference_kg": 12,
        }]
        result = summarize_bom_and_steel(doc)
        self.assertEqual(result["equipment_known_weight_kg"], Decimal("6.50"))
        self.assertEqual(result["steel_known_weight_kg"], Decimal("2"))
        self.assertEqual(result["combined_known_weight_kg"], Decimal("8.50"))
        xlsx = Path(self.temp.name) / "mass.xlsx"
        reports.export_excel(doc, xlsx, self.metadata)
        with zipfile.ZipFile(xlsx) as book:
            workbook = book.read("xl/workbook.xml").decode("utf-8")
            self.assertIn('name="Mass Summary"', workbook)
            bom_xml = book.read("xl/worksheets/sheet2.xml").decode("utf-8")
            self.assertIn("E9*J9", bom_xml)  # row 8 is the category band
            cut_xml = book.read("xl/worksheets/sheet11.xml").decode("utf-8")
            self.assertIn("M8/L8", cut_xml)
            self.assertIn("I8*N8", cut_xml)
            mass_xml = book.read("xl/worksheets/sheet12.xml").decode("utf-8")
            self.assertIn("SUM(B4,D4)", mass_xml)
        try:
            from bom_reports import _thai_font
            _thai_font()
        except RuntimeError:
            self.skipTest("System has no supported Thai PDF font")
        pdf = Path(self.temp.name) / "mass.pdf"
        reports.export_pdf(doc, pdf, self.metadata)
        import fitz
        with fitz.open(str(pdf)) as exported:
            text = " ".join(page.get_text() for page in exported)
            self.assertIn("TOTAL MASS ROLL-UP", text)
            self.assertIn("8.500", text)
            self.assertIn("3.250", text)

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


    def test_excel_long_thai_description_gets_tall_wrapped_row(self):
        doc = {
            "schemaVersion": 1, "project": "ทดสอบข้อความหลายบรรทัด",
            "items": [{
                "id": "LONG-1", "category": "เครื่องกล",
                "name": ("โครงสร้างเหล็กกล่องสำหรับฐานเครน พร้อมจุดยึดมอเตอร์ "
                         "และแผ่นรองรับอุปกรณ์ " * 5),
                "spec": ("รายละเอียดสเปกสำหรับใช้ในรายงานอาจารย์ ต้องอ่านได้ครบทุกบรรทัด "
                         "โดยไม่ซ้อนกับรายการถัดไป " * 4),
                "qty": 2, "unit": "ชิ้น", "unitPrice": 100,
            }],
            "wiring": [], "purchases": [], "steel_members": [],
        }
        file = Path(self.temp.name) / "long-row.xlsx"
        reports.export_excel(doc, file, self.metadata)
        with zipfile.ZipFile(file) as book:
            sheet = ET.fromstring(book.read("xl/worksheets/sheet2.xml"))
            ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            row = sheet.find(".//x:row[@r='9']", ns)  # row 8 is the category band
            self.assertIsNotNone(row)
            self.assertTrue(row.attrib.get("customHeight") == "1")
            self.assertGreaterEqual(float(row.attrib["ht"]), 100.0,
                                    "Long Thai BOM descriptions must not overlap rows")
            # Wrapped cells use top alignment so each line remains inside its row.
            styles = ET.fromstring(book.read("xl/styles.xml"))
            self.assertIsNotNone(styles.find(".//x:alignment[@wrapText='1']", ns))

if __name__ == "__main__":
    unittest.main()
