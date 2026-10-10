"""Regression tests for 1.10 purchasing, safe sync, Excel import and quality audit."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bom_advanced as adv
import bom_import_excel as importer
import bom_official_reports


def base():
    return {"schemaVersion": 1, "project": "Test", "currency": "THB",
            "items": [{"id": "1", "category": "ระบบขับเคลื่อน", "name": "Motor",
                       "partNumber": "QS-1500", "qty": 2, "unit": "ตัว",
                       "unitPrice": 4000},
                      {"id": "2", "category": "ระบบขับเคลื่อน", "name": "Controller",
                       "qty": 1, "unitPrice": None}],
            "wiring": [], "purchases": []}


class AdvancedTests(unittest.TestCase):
    def test_merge_disjoint_fields_automatically(self):
        original = base()
        local, remote = copy.deepcopy(original), copy.deepcopy(original)
        local["items"][0]["name"] = "Motor revised"
        remote["items"][0]["qty"] = 3
        merged, conflicts = adv.merge_docs(original, local, remote)
        self.assertEqual(conflicts, [])
        self.assertEqual(merged["items"][0]["name"], "Motor revised")
        self.assertEqual(merged["items"][0]["qty"], 3)

    def test_merge_conflict_is_reported_and_preference_works(self):
        original = base()
        local, remote = copy.deepcopy(original), copy.deepcopy(original)
        local["items"][0]["qty"] = 3
        remote["items"][0]["qty"] = 5
        merged, conflicts = adv.merge_docs(original, local, remote)
        self.assertTrue(any(".qty" in name for name in conflicts))
        self.assertEqual(merged["items"][0]["qty"], 3)
        alternate, _ = adv.merge_docs(original, local, remote, preference="remote")
        self.assertEqual(alternate["items"][0]["qty"], 5)

    def test_three_way_merge_keeps_added_purchase_and_reorder(self):
        original = base()
        local, remote = copy.deepcopy(original), copy.deepcopy(original)
        local["items"].reverse()
        remote["purchases"] = [{"id": "PO1", "itemId": "1",
                                "description": "Motor", "qty": 1, "unitPrice": 3900}]
        merged, conflicts = adv.merge_docs(original, local, remote)
        self.assertFalse(conflicts)
        self.assertEqual([i["id"] for i in merged["items"]], ["2", "1"])
        self.assertEqual(merged["purchases"][0]["itemId"], "1")

    def test_purchasing_shortage_and_partial_received(self):
        doc = base()
        doc["purchases"] = [{"id": "A", "itemId": "1", "qty": 2, "unitPrice": 3900,
                             "status": "ได้รับบางส่วน", "receivedQty": 1},
                            {"id": "B", "itemId": "2", "qty": 1, "unitPrice": 99,
                             "status": "ยกเลิก"}]
        summary = adv.purchase_progress(doc)
        self.assertEqual(summary["ordered_lines"], 1)
        self.assertEqual(summary["received_lines"], 0)
        self.assertEqual(summary["remaining_to_receive"]["1"], 1)
        self.assertEqual(summary["remaining_to_order"]["2"], 1)

    def test_quality_audit_reports_unknown_price_and_references(self):
        doc = base()
        errors = adv.audit_bom(doc)
        self.assertTrue(any("ราคา" in e["detail"] for e in errors))
        self.assertTrue(any("Part Number" in e["detail"] for e in errors))

    def test_exported_excel_can_be_imported_without_overwriting_existing_ids(self):
        doc = base()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "bom.xlsx"
            bom_official_reports.export_excel(doc, target)
            new_rows = importer.read_bom_xlsx(target)
        self.assertEqual(len(new_rows), 2)
        self.assertEqual(new_rows[0]["name"], "Motor")
        self.assertEqual(new_rows[0]["qty"], 2)
        original = copy.deepcopy(doc)
        updated, added = importer.add_imported_items(doc, new_rows)
        self.assertEqual(added, 0)
        self.assertEqual(original, doc)
        self.assertEqual(updated, doc)
        extension = [{"id": "1", "name": "New Sensor", "qty": 1, "unit": "ชิ้น",
                      "category": "เซนเซอร์และความปลอดภัย", "unitPrice": None}]
        newer, added = importer.add_imported_items(doc, extension)
        self.assertEqual(added, 1)
        self.assertEqual(newer["items"][-1]["id"], "3")


if __name__ == "__main__":
    unittest.main()
