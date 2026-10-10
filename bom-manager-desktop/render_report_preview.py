"""Render and validate actual engineering PDF pages in Windows CI."""
from pathlib import Path
import fitz

FOLDER = Path(__file__).resolve().parent / "output"
SOURCE = FOLDER / "EngineeringBOM_Example.pdf"
TARGETS = [
    (0, "EngineeringBOM_Cover.png"),
    (2, "EngineeringBOM_Table.png"),
]
with fitz.open(str(SOURCE)) as pdf:
    assert len(pdf) >= 9, f"Unexpected number of pages ({len(pdf)}); check annex breaks"
    assert all(abs(page.rect.width - 841.89) < 2 and abs(page.rect.height - 595.28) < 2
               for page in pdf), "Report pages must all use landscape A4"
    for index, name in TARGETS:
        page = pdf[index]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        target = FOLDER / name
        pix.save(str(target))
        assert target.stat().st_size > 10000
        print(name, "bytes", target.stat().st_size, "page", index+1, "of", len(pdf))
