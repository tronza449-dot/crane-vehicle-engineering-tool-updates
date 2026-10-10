"""Build report samples from the checked-in BOM (no user credentials)."""
import json
from pathlib import Path

import bom_official_reports

BASE = Path(__file__).resolve().parent
source = BASE.parent / "bom-manager" / "bom.json"
out = BASE / "output"
out.mkdir(exist_ok=True)
doc = json.loads(source.read_text(encoding="utf-8"))
about = {"author": "ไม่ระบุ (แก้ไขได้ในโปรแกรม)",
         "institution": "ไม่ระบุ (แก้ไขได้ในโปรแกรม)",
         "document_no": "BOM-EXAMPLE", "revision": "DRAFT"}
bom_official_reports.export_pdf(doc, out / "EngineeringBOM_Example.pdf", about)
bom_official_reports.export_excel(doc, out / "EngineeringBOM_Example.xlsx", about)
for suffix in ("pdf","xlsx"):
    file = out / ("EngineeringBOM_Example."+suffix)
    assert file.exists() and file.stat().st_size > 9000
    print(file, file.stat().st_size, "bytes")
