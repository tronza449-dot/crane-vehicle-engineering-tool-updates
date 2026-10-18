"""Render and validate actual engineering PDF pages in Windows CI."""
from pathlib import Path
import fitz

FOLDER = Path(__file__).resolve().parent / "output"
SOURCE = FOLDER / "EngineeringBOM_Example.pdf"
with fitz.open(str(SOURCE)) as pdf:
    assert len(pdf) >= 7, f"Unexpectedly short formal report ({len(pdf)} pages)"
    assert all(abs(page.rect.width - 841.89) < 2 and abs(page.rect.height - 595.28) < 2
               for page in pdf), "Report pages must all use landscape A4"
    table_index = next((i for i, page in enumerate(pdf)
                        if "MASTER BOM REGISTER" in page.get_text()), None)
    assert table_index is not None, "The new consolidated BOM table is missing from the PDF"
    assert "BOM ID" in pdf[table_index].get_text(), "The master BOM table must include BOM IDs"
    targets = [(0, "EngineeringBOM_Cover.png"),
               (table_index, "EngineeringBOM_Table.png")]
    for index, name in targets:
        page = pdf[index]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        target = FOLDER / name
        pix.save(str(target))
        assert target.stat().st_size > 10000
        print(name, "bytes", target.stat().st_size, "page", index+1, "of", len(pdf))
