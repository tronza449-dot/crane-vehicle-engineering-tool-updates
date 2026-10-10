"""Read BOM rows from XLSX using OOXML, without macros or formula execution."""
import copy
import re
import zipfile
from xml.etree import ElementTree as ET
import bom_core

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
HEADERS = {
    "bom id": "id", "id": "id", "รหัส": "id",
    "ระบบ / หมวด": "category", "หมวด": "category", "หมวดหมู่": "category",
    "part number": "partNumber", "part no.": "partNumber",
    "อุปกรณ์ / รุ่น": "name", "ชื่ออุปกรณ์": "name", "รายการ": "name",
    "จำนวน": "qty", "หน่วย": "unit",
    "ราคา/หน่วย (บาท)": "unitPrice", "ราคาต่อหน่วย": "unitPrice",
    "สถานะ": "status", "ร้านค้า / ผู้ขาย": "supplier",
    "ลิงก์สินค้า": "link", "สเปกทางเทคนิค": "spec",
}


def read_bom_xlsx(filename):
    with zipfile.ZipFile(filename) as archive:
        names = set(archive.namelist())
        if "xl/workbook.xml" not in names:
            raise ValueError("ไม่พบโครงสร้าง XLSX")
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {x.attrib["Id"]: x.attrib["Target"] for x in rels}
        sheets = book.findall("m:sheets/m:sheet", NS)
        if not sheets:
            raise ValueError("ไฟล์ Excel ไม่มีชีต")
        selected = next((s for s in sheets if s.attrib.get("name", "").lower() == "bom"), sheets[0])
        target = targets[selected.attrib["{" + NS["r"] + "}id"]]
        target = target.lstrip("/") if target.startswith("/") else (
            target if target.startswith("xl/") else "xl/" + target)
        shared = []
        if "xl/sharedStrings.xml" in names:
            strings = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for entry in strings.findall("m:si", NS):
                shared.append("".join(t.text or "" for t in entry.findall(".//m:t", NS)))
        xml = ET.fromstring(archive.read(target))
        lines = []
        for row in xml.findall(".//m:sheetData/m:row", NS):
            cells = {}
            for c in row.findall("m:c", NS):
                match = re.match(r"[A-Z]+", c.attrib.get("r", ""))
                if not match:
                    continue
                col = 0
                for ch in match.group():
                    col = col * 26 + ord(ch) - 64
                value = c.find("m:v", NS)
                if c.attrib.get("t") == "inlineStr":
                    text = "".join(t.text or "" for t in c.findall(".//m:t", NS))
                else:
                    text = value.text if value is not None and value.text else ""
                    if c.attrib.get("t") == "s" and text:
                        text = shared[int(text)]
                cells[col - 1] = text
            if cells:
                lines.append(cells)
    mapping, index = None, None
    for n, line in enumerate(lines[:40]):
        found = {col: HEADERS[str(val).strip().casefold()]
                 for col, val in line.items() if str(val).strip().casefold() in HEADERS}
        if "name" in found.values() and "qty" in found.values():
            mapping, index = found, n
            break
    if mapping is None:
        raise ValueError("ไม่พบหัวตารางชื่ออุปกรณ์และจำนวน")
    output = []
    for line in lines[index + 1:]:
        item = {key: str(line.get(col, "")).strip() for col, key in mapping.items()}
        if not item.get("name"):
            continue
        item["qty"] = bom_core.valid_qty(item.get("qty"))
        item["unitPrice"] = bom_core.valid_price(item.get("unitPrice"))
        output.append(item)
    if not output:
        raise ValueError("Excel ไม่มีรายการอุปกรณ์ให้เพิ่ม")
    return output


def add_imported_items(doc, rows):
    """Never replace an existing record or change a referenced BOM ID."""
    result = copy.deepcopy(doc)
    occupied = {str(i["id"]) for i in result["items"]}
    keys = {(str(i.get("name") or "").casefold(),
             str(i.get("partNumber") or "").casefold())
            for i in result["items"]}
    added = 0
    for item in rows:
        identity = (str(item.get("name") or "").casefold(),
                    str(item.get("partNumber") or "").casefold())
        if identity in keys:
            continue
        row = dict(item)
        proposed = str(row.get("id") or "")
        if not proposed or proposed in occupied:
            number = 1
            while str(number) in occupied:
                number += 1
            proposed = str(number)
        row["id"] = proposed
        row.setdefault("category", "อื่น ๆ / รอจัดหมวด")
        row.setdefault("unit", "ชิ้น")
        result["items"].append(row)
        occupied.add(proposed)
        keys.add(identity)
        added += 1
    bom_core.ensure_doc(result)
    return result, added
