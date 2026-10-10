"""Web BOM categories must be picked from a safe dropdown, not typed."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CategoryDropdownWebTest(unittest.TestCase):
    def test_category_input_is_a_non_text_dropdown(self):
        html = (ROOT / "bom-manager" / "index.html").read_text(encoding="utf-8")
        self.assertIn('select class="category-pick" data-k="category"', html)
        self.assertNotIn('<input data-k="category"', html)
        self.assertIn("...engineeringCategoryOrder,'อื่น ๆ / รอจัดหมวด'", html)
        self.assertIn("select[data-k=\"category\"]", html)
        self.assertIn("item.category=el.value;markDirty(row);render()", html)
        self.assertIn("category:'อื่น ๆ / รอจัดหมวด',name:'รายการใหม่'", html)


if __name__ == "__main__":
    unittest.main()
