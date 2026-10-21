"""Thai PDF text: tone marks must be drawn, copied and wrapped correctly."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import bom_thai_text

# Words whose tone mark sits on an upper vowel (ReportLab used to drop the
# mark), plus sara-am words that HarfBuzz would decompose (copy/search risk).
STACKED = ["ชิ้น", "ที่ปรึกษา", "ซื้อ", "เครื่องกล", "ทั้งสิ้น"]
SARA_AM = ["จำนวน", "น้ำหนัก", "ไฟฟ้ากำลัง", "ลำดับ"]


def thai_font_or_skip(test):
    try:
        return bom_thai_text.register_fonts()
    except RuntimeError:
        test.skipTest("System has no supported Thai PDF font")


class ThaiTextTests(unittest.TestCase):
    def test_only_stacked_words_are_shaped(self):
        for word in STACKED:
            self.assertTrue(any(shaped for _, shaped in bom_thai_text._segments(word)), word)
        for word in SARA_AM:
            self.assertFalse(any(shaped for _, shaped in bom_thai_text._segments(word)), word)

    def test_tokens_rejoin_to_the_original_text(self):
        text = "แบตเตอรี่ขับเคลื่อน (Li-ion 72 V) ที่มา: www.example.com/a-b_c"
        self.assertEqual("".join(bom_thai_text.tokens(text)), text)
        tokens = bom_thai_text.tokens(text)
        self.assertIn("www.example.com/a-b_c", tokens)  # Latin runs stay whole
        self.assertTrue(any(t.startswith("(") and len(t) > 1 for t in tokens))

    def test_wrapping_breaks_between_words_not_inside_them(self):
        regular, _ = thai_font_or_skip(self)
        text = "ผู้ตรวจสอบอาจารย์ที่ปรึกษาโครงการรถไฟฟ้าพร้อมเครน"
        lines = bom_thai_text.break_lines(text, regular, 9, 70)
        self.assertGreater(len(lines), 1)
        self.assertEqual("".join(lines), text)
        if bom_thai_text.word_engine() == "pythainlp":
            self.assertTrue(any("ที่ปรึกษา" in line for line in lines), lines)
        url = "https://www.example.com/" + "x" * 120
        long_lines = bom_thai_text.break_lines(url, regular, 9, 100)
        self.assertEqual("".join(long_lines), url)
        from reportlab.pdfbase.pdfmetrics import stringWidth
        self.assertTrue(all(stringWidth(line, regular, 9) <= 100 for line in long_lines))

    def test_pdf_draws_tone_marks_and_copies_real_text(self):
        regular, _ = thai_font_or_skip(self)
        if not bom_thai_text.shaping_available():
            self.skipTest("uharfbuzz is not installed")
        import fitz
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.platypus import SimpleDocTemplate
        words = STACKED + SARA_AM
        style = ParagraphStyle("t", fontName=regular, fontSize=14, leading=22)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "thai.pdf"

            def header(canvas, _doc):
                canvas.setFont(regular, 10)
                bom_thai_text.draw_string(canvas, 40, 800, "เลขที่เอกสาร วันที่จัดทำ")

            SimpleDocTemplate(str(target)).build(
                [bom_thai_text.paragraph(word, style) for word in words],
                onFirstPage=header)
            with fitz.open(str(target)) as pdf:
                text = pdf[0].get_text()
            for word in words + ["เลขที่เอกสาร", "วันที่จัดทำ"]:
                self.assertIn(word, text)
            self.assertFalse([c for c in text if 0xE000 <= ord(c) <= 0xF8FF],
                             "private-use glyph codes leaked into copied text")

            # The shaped drawing must differ from plain (unshaped) ReportLab
            # output, which hides the tone mark of ชิ้น behind the vowel.
            def render(draw):
                path = Path(folder) / "one.pdf"
                page = rl_canvas.Canvas(str(path), pagesize=(120, 60))
                page.setFont(regular, 30)
                draw(page)
                page.save()
                with fitz.open(str(path)) as pdf:
                    return pdf[0].get_pixmap(dpi=72).samples
            plain = render(lambda c: c.drawString(10, 15, "ชิ้น"))
            shaped = render(lambda c: bom_thai_text.draw_string(c, 10, 15, "ชิ้น"))
            self.assertNotEqual(plain, shaped)


if __name__ == "__main__":
    unittest.main()
