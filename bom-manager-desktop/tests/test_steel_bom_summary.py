"""Tests for combined BOM overview and structural-steel material takeoff."""
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bom_steel_bom


class SteelBOMTests(unittest.TestCase):
    def setUp(self):
        self.doc = {
            "items": [
                {"id": "1", "category": "ไฟฟ้ากำลัง", "name": "Motor",
                 "qty": 2, "unitPrice": 100},
                {"id": "2", "category": "อิเล็กทรอนิกส์/ควบคุม", "name": "ESP32",
                 "qty": 1, "unitPrice": None},
            ],
            "steel_members": [
                {"id": "S1", "member": "โครงด้านข้าง", "profile": "เหล็กกล่องสี่เหลี่ยม",
                 "size": "25x25x2 mm", "qty": 4, "length_mm": 750,
                 "stock_length_m": 6},
                {"id": "S2", "member": "คานขวาง", "profile": "เหล็กกล่องสี่เหลี่ยม",
                 "size": "25x25x2 mm", "qty": 2, "length_mm": 1250,
                 "stock_length_m": 6},
                {"id": "S3", "member": "ค้ำยัน", "profile": "เหล็กฉาก",
                 "size": "20x20x3 mm", "qty": 2, "length_mm": 1000,
                 "stock_length_m": 6},
            ],
        }

    def test_summary_groups_by_profile_size_and_stock_length(self):
        result = bom_steel_bom.summarize_bom_and_steel(self.doc)
        self.assertEqual(result["bom_items"], 2)
        self.assertEqual(result["bom_known_cost"], Decimal("200"))
        self.assertEqual(result["bom_missing_prices"], 1)
        self.assertEqual(result["steel_pieces"], 8)
        self.assertEqual(result["steel_required_length_m"], Decimal("7.5"))
        self.assertEqual(len(result["steel_groups"]), 2)
        box = next(g for g in result["steel_groups"] if g["profile"] == "เหล็กกล่องสี่เหลี่ยม")
        self.assertEqual(box["pieces"], 6)
        self.assertEqual(box["total_length_m"], Decimal("5.5"))
        self.assertEqual(box["estimated_bars_with_waste"], 1)
        angle = next(g for g in result["steel_groups"] if g["profile"] == "เหล็กฉาก")
        self.assertEqual(angle["estimated_bars_with_waste"], 1)

    def test_waste_allowance_and_price_are_separate_from_bom_budget(self):
        result = bom_steel_bom.summarize_bom_and_steel(
            self.doc, steel_purchase_unit_price="350", waste_percent=20)
        self.assertEqual(result["steel_length_with_waste_m"], Decimal("9.00"))
        self.assertEqual(result["steel_stock_bars"], 3)
        self.assertEqual(result["steel_procurement_length_m"], Decimal("18.0"))
        self.assertEqual(result["steel_cost_estimate"], Decimal("1050"))
        self.assertEqual(result["bom_known_cost"], Decimal("200"))

    def test_invalid_waste_rejected(self):
        with self.assertRaises(ValueError):
            bom_steel_bom.summarize_bom_and_steel(self.doc, waste_percent=101)

    def test_empty_steel_list_is_supported(self):
        result = bom_steel_bom.summarize_bom_and_steel({"items": [], "steel_members": []})
        self.assertEqual(result["steel_groups"], [])
        self.assertEqual(result["steel_pieces"], 0)
        self.assertEqual(result["steel_stock_bars"], 0)
        self.assertIsNone(result["steel_cost_estimate"])


if __name__ == "__main__":
    unittest.main()
