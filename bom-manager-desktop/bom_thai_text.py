"""Thai-safe PDF text: font registration, selective shaping and word wrapping.

Without shaping, ReportLab hides tone marks that sit on an upper vowel
(ชิ้น -> ชิน, ที่ -> ที, ซื้อ -> ซือ). HarfBuzz shaping (uharfbuzz) fixes the
drawing but splits sara am (จำนวน extracts as จํานวน) and uses unmapped glyphs
for raised tone marks, which breaks copy/search. So:

* only words with a tone mark on an upper vowel are shaped;
* raised tone-mark glyphs are mapped back to their Unicode character in the
  PDF ToUnicode table, so shaped words still copy and search correctly;
* lines are broken at Thai word boundaries (PyThaiNLP dictionary, or
  character clusters as a fallback) and drawn by ThaiText.
"""
import os
import re

REGULAR = "CVBOMThai"
BOLD = "CVBOMThai-Bold"

# Tahoma ships with every Windows install, so layout is the same on student
# PCs and the CI build machine. Each pair is (regular, bold).
FONT_PAIRS = (
    (r"C:\Windows\Fonts\tahoma.ttf", r"C:\Windows\Fonts\tahomabd.ttf"),
    (r"C:\Windows\Fonts\LeelawUI.ttf", r"C:\Windows\Fonts\LeelaUIb.ttf"),
    (r"C:\Windows\Fonts\leelawad.ttf", r"C:\Windows\Fonts\leelawdb.ttf"),
    ("/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
     "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf"),
    ("/usr/share/fonts/truetype/thai-tlwg/Garuda.ttf",
     "/usr/share/fonts/truetype/thai-tlwg/Garuda-Bold.ttf"),
)

UPPER_VOWELS = "\u0E31\u0E34\u0E35\u0E36\u0E37\u0E47"
TONE_MARKS = "\u0E48\u0E49\u0E4A\u0E4B\u0E4C"
_STACKED = re.compile("[" + UPPER_VOWELS + "][" + TONE_MARKS + "]")

# One breakable unit when no dictionary is available: a Latin/number run, or
# an optional leading vowel, one character, then combining marks.
_CLUSTER = re.compile(
    r"\s+|[A-Za-z0-9][A-Za-z0-9.,:;/_\-+%()×°'\"]*"
    r"|[\u0E40-\u0E44]?[^\s][\u0E30-\u0E3A\u0E45\u0E47-\u0E4E]*")
# Smallest drawable unit, for splitting a word wider than its cell.
_GRAPHEME = re.compile(r"\s+|[เ-ไ]?[^\s][ะ-ฺๅ็-๎]*")

_registered = None
_word_tokenize = None
_word_engine = None
_fonts_by_face = {}     # PDF face name -> registered TTFont
_variant_chars = {}     # PDF face name -> {glyph id: character}


def register_fonts():
    """Register a Thai regular/bold pair once; return (regular, bold) names."""
    global _registered
    if _registered:
        return _registered
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for regular, bold in FONT_PAIRS:
        if not os.path.isfile(regular):
            continue
        try:
            pdfmetrics.registerFont(TTFont(REGULAR, regular))
            _remember_variants(REGULAR, regular)
            bold_name = REGULAR
            if os.path.isfile(bold):
                pdfmetrics.registerFont(TTFont(BOLD, bold))
                _remember_variants(BOLD, bold)
                bold_name = BOLD
            pdfmetrics.registerFontFamily(REGULAR, normal=REGULAR, bold=bold_name,
                                          italic=REGULAR, boldItalic=bold_name)
            _install_tounicode_fix()
            _registered = (REGULAR, bold_name)
            return _registered
        except Exception:
            continue
    raise RuntimeError("ไม่พบฟอนต์ไทยสำหรับ PDF (เช่น Tahoma ที่ติดตั้งใน Windows)")


def shaping_available():
    try:
        import uharfbuzz  # noqa: F401
        return True
    except ImportError:
        return False


def _remember_variants(font_name, path):
    """Find glyphs HarfBuzz substitutes for tone marks/upper vowels.

    These glyphs have no cmap entry, so ReportLab gives them private-use codes.
    Shaping each mark after plain and tall-ascender consonants shows which
    unmapped glyph stands for which character.
    """
    from reportlab.pdfbase import pdfmetrics
    font = pdfmetrics.getFont(font_name)
    face = font.face.name.decode("latin-1")
    _fonts_by_face[face] = font
    if not shaping_available():
        return
    import uharfbuzz as hb
    hb_font = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
    mapped = set(font.face.glyphToChar)

    def shape(text):
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(hb_font, buffer, {"kern": True, "liga": True, "dlig": True})
        return [info.codepoint for info in buffer.glyph_infos]

    variants = {}
    for base in "กปฝฟฬ":
        for upper in ("",) + tuple(UPPER_VOWELS):
            prefix = base + upper
            before = set(shape(prefix))
            for glyph in before - set(shape(base)) - mapped:
                variants.setdefault(glyph, upper)
            for tone in TONE_MARKS:
                for glyph in set(shape(prefix + tone)) - before - mapped:
                    variants.setdefault(glyph, tone)
    _variant_chars[face] = variants


def _install_tounicode_fix():
    from reportlab.pdfbase import ttfonts
    original = ttfonts.makeToUnicodeCMap
    if getattr(original, "thai_variants", False):
        return

    def make(fontname, subset):
        face = fontname.split("+", 1)[-1]
        font = _fonts_by_face.get(face)
        variants = _variant_chars.get(face)
        if font is not None and variants:
            fixed = []
            for value in subset:
                glyph = font.face.charToGlyph.get(value) if 0xE000 <= value <= 0xF8FF else None
                fixed.append(ord(variants[glyph]) if glyph in variants else value)
            subset = fixed
        return original(fontname, subset)

    make.thai_variants = True
    ttfonts.makeToUnicodeCMap = make


def word_engine():
    """'pythainlp' when dictionary word breaking works, else 'cluster'."""
    _load_tokenizer()
    return _word_engine


def _load_tokenizer():
    global _word_tokenize, _word_engine
    if _word_engine is not None:
        return
    try:
        from pythainlp.tokenize import word_tokenize
        word_tokenize("ทดสอบ", engine="newmm")
        _word_tokenize, _word_engine = word_tokenize, "pythainlp"
    except Exception:
        _word_tokenize, _word_engine = None, "cluster"


def _clusters(text):
    return _CLUSTER.findall(text)


_THAI = re.compile("[฀-๿]")
_OPENING = set("([{“‘\"'<")
_CLOSING = set(")]}”’\"',.;:!?%>")


def _glue(parts):
    """Keep Latin/number runs (URLs, part numbers) whole and attach brackets
    and closing punctuation to the neighbouring word."""
    result = []
    for part in parts:
        if not part:
            continue
        if result and not part.isspace() and not result[-1].isspace():
            previous = result[-1]
            latin_run = not _THAI.search(previous) and not _THAI.search(part)
            if (latin_run or previous[-1] in _OPENING
                    or all(ch in _CLOSING for ch in part)):
                result[-1] = previous + part
                continue
        result.append(part)
    return result


def tokens(text):
    """Split one line into breakable tokens; joining them gives the line back."""
    _load_tokenizer()
    if _word_tokenize is not None:
        try:
            result = _word_tokenize(text, engine="newmm", keep_whitespace=True)
            if "".join(result) == text:
                return _glue(result)
        except Exception:
            pass
    return _glue(_clusters(text))


def break_lines(text, font_name, font_size, width):
    """Greedy word wrap for mixed Thai/Latin text at a fixed width in points."""
    from reportlab.pdfbase.pdfmetrics import stringWidth

    def measure(value):
        return stringWidth(value, font_name, font_size)

    limit = max(1.0, width - 0.5)
    lines = []
    for raw in (str(text).splitlines() or [""]):
        line = ""
        for token in tokens(raw):
            if measure((line + token).rstrip()) <= limit:
                line += token
                continue
            if line.strip():
                lines.append(line.rstrip())
            line = ""
            token = token.lstrip()
            # A single word wider than the cell (long URL, part number).
            while token and measure(token) > limit:
                piece = ""
                for cluster in _GRAPHEME.findall(token):
                    if piece and measure(piece + cluster) > limit:
                        break
                    piece += cluster
                lines.append(piece)
                token = token[len(piece):]
            line = token
        lines.append(line.rstrip())
    return lines


def _segments(text):
    """Group a line into (text, needs_shaping) runs."""
    runs = []
    for token in tokens(text):
        shaped = bool(_STACKED.search(token))
        if runs and runs[-1][1] == shaped:
            runs[-1][0] += token
        else:
            runs.append([token, shaped])
    return runs


def _shape(run, font_name, font_size):
    """Shape directly: canvas.drawString(shaping=True) needs python-bidi."""
    if not shaping_available():
        return run
    try:
        from reportlab.pdfbase.pdfmetrics import getFont
        from reportlab.pdfbase.ttfonts import shapeStr
        if not getFont(font_name).shapable:
            return run
        return shapeStr(run, font_name, font_size)
    except (ImportError, AttributeError):
        return run


def _draw_runs(canvas, x, y, text, font_name, font_size):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    for run, shaped in _segments(text):
        canvas.drawString(x, y, _shape(run, font_name, font_size) if shaped else run)
        x += stringWidth(run, font_name, font_size)


def draw_string(canvas, x, y, text, align="left"):
    """Canvas text for running headers/footers; x is the anchor for align."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    text = str(text)
    font_name, font_size = canvas._fontname, canvas._fontsize
    width = stringWidth(text, font_name, font_size)
    start = {"left": x, "right": x - width, "center": x - width / 2}[align]
    _draw_runs(canvas, start, y, text, font_name, font_size)


def _flowable_class():
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.platypus.flowables import Flowable

    class ThaiText(Flowable):
        """Plain-text flowable: Thai word wrap, selective shaping, alignment."""

        def __init__(self, text, style):
            Flowable.__init__(self)
            self.text = "" if text is None else str(text)
            self.style = style
            self.spaceBefore = style.spaceBefore
            self.spaceAfter = style.spaceAfter
            self._lines = [self.text]
            self.width = self.height = 0

        def wrap(self, availWidth, availHeight):
            style = self.style
            self._lines = break_lines(self.text, style.fontName, style.fontSize, availWidth)
            self.width = availWidth
            self.height = len(self._lines) * style.leading
            return availWidth, self.height

        def split(self, availWidth, availHeight):
            self.wrap(availWidth, availHeight)
            fit = int(availHeight // self.style.leading)
            if fit <= 0:
                return []
            if fit >= len(self._lines):
                return [self]
            first = ThaiText("\n".join(self._lines[:fit]), self.style)
            rest = ThaiText("\n".join(self._lines[fit:]), self.style)
            first.spaceAfter = 0
            rest.spaceBefore = 0
            return [first, rest]

        def draw(self):
            style = self.style
            canvas = self.canv
            canvas.saveState()
            canvas.setFillColor(style.textColor)
            canvas.setFont(style.fontName, style.fontSize)
            # Centre glyphs in each leading band so stacked marks stay inside cells.
            first_baseline = self.height - (style.leading - style.fontSize) / 2 - style.fontSize * 0.9
            for index, line in enumerate(self._lines):
                y = first_baseline - index * style.leading
                line_width = stringWidth(line, style.fontName, style.fontSize)
                if style.alignment == TA_RIGHT:
                    x = self.width - line_width
                elif style.alignment == TA_CENTER:
                    x = (self.width - line_width) / 2
                else:
                    x = 0
                _draw_runs(canvas, x, y, line, style.fontName, style.fontSize)
            canvas.restoreState()

    return ThaiText


_ThaiText = None


def paragraph(text, style):
    """Return a Thai-safe flowable for plain (non-markup) text."""
    global _ThaiText
    if _ThaiText is None:
        _ThaiText = _flowable_class()
    return _ThaiText(text, style)
