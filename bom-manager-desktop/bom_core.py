"""Pure BOM business rules. No GUI or network dependencies.

Compatible with the existing schemaVersion=1 web BOM: unfamiliar keys and
existing item fields are never removed or automatically fabricated.
"""
from collections import Counter
from decimal import Decimal, InvalidOperation


class DataError(ValueError):
    pass


def decimal_or_none(value):
    if value is None or str(value).strip() == "":
        return None
    try:
        result = Decimal(str(value).replace(",", ""))
    except (InvalidOperation, ValueError) as exc:
        raise DataError("ราคา/จำนวนต้องเป็นตัวเลข") from exc
    if not result.is_finite() or result < 0:
        raise DataError("ราคา/จำนวนต้องไม่ติดลบและต้องเป็นตัวเลขที่จำกัด")
    return result


def valid_qty(value):
    result = decimal_or_none(value)
    if result is None or result == 0:
        raise DataError("จำนวนต้องมากกว่า 0")
    return float(result) if result != result.to_integral_value() else int(result)


def valid_price(value):
    result = decimal_or_none(value)
    return None if result is None else float(result)


def ensure_doc(doc):
    if not isinstance(doc, dict) or not isinstance(doc.get("items"), list):
        raise DataError("ไฟล์ BOM ต้องมี items เป็นรายการ")
    for list_key in ("wiring", "purchases"):
        if list_key in doc and not isinstance(doc[list_key], list):
            raise DataError(f"{list_key} ต้องเป็นรายการ")
    for wiring in doc.get("wiring", []):
        if not isinstance(wiring, dict):
            raise DataError("พบ Wiring ที่ไม่ใช่ข้อมูลรายการ")
    for order in doc.get("purchases", []):
        if not isinstance(order, dict):
            raise DataError("พบข้อมูลจัดซื้อที่ไม่ใช่รายการ")
        valid_qty(order.get("qty"))
        decimal_or_none(order.get("unitPrice"))
    seen = set()
    for item in doc["items"]:
        if not isinstance(item, dict):
            raise DataError("พบรายการอุปกรณ์รูปแบบผิด")
        key = str(item.get("id", "")).strip()
        if not key or key in seen:
            raise DataError(f"รหัสอุปกรณ์ซ้ำ/ว่าง: {key!r}")
        seen.add(key)
        valid_qty(item.get("qty"))
        decimal_or_none(item.get("unitPrice"))
    return doc


def next_id(rows):
    occupied = {str(x.get("id")) for x in rows}
    candidate = 1
    while str(candidate) in occupied:
        candidate += 1
    return str(candidate)


def metrics(doc):
    items = doc.get("items", [])
    count = len(items)
    total_qty = Decimal("0")
    known_cost = Decimal("0")
    priced = 0
    cats = Counter()
    for item in items:
        qty = decimal_or_none(item.get("qty")) or Decimal("0")
        total_qty += qty
        cats[str(item.get("category") or "ไม่ระบุ")] += 1
        price = decimal_or_none(item.get("unitPrice"))
        if price is not None:
            priced += 1
            known_cost += qty * price
    purchases = doc.get("purchases", [])
    ordered_total = Decimal("0")
    for order in purchases:
        price = decimal_or_none(order.get("unitPrice"))
        qty = decimal_or_none(order.get("qty")) or Decimal("0")
        if price is not None:
            ordered_total += price * qty
    return {"items": count, "quantity": total_qty, "priced": priced,
            "missing": count - priced, "known_cost": known_cost,
            "purchase_count": len(purchases), "purchase_total": ordered_total,
            "wires": len(doc.get("wiring", [])), "categories": cats}


def connection_warnings(doc):
    """Non-certifying automated checks; manual electrical verification remains essential."""
    item_ids = {str(x.get("id")) for x in doc.get("items", [])}
    issues = []
    for i, wire in enumerate(doc.get("wiring", []), start=1):
        if not isinstance(wire, dict):
            issues.append(f"สาย #{i}: โครงสร้างข้อมูลไม่ถูกต้อง")
            continue
        if not str(wire.get("from", "")).strip() or not str(wire.get("to", "")).strip():
            issues.append(f"สาย #{i}: ต้องระบุต้นทางและปลายทาง")
        for field in ("fromItemId", "toItemId"):
            ref = str(wire.get(field, "")).strip()
            if ref and ref not in item_ids:
                issues.append(f"สาย #{i}: อุปกรณ์อ้างอิง {ref} ไม่มีใน BOM")
        if not str(wire.get("protection", "")).strip():
            issues.append(f"สาย #{i}: ยังไม่ระบุการป้องกัน/ฟิวส์ (ถ้าจำเป็น)")
    return issues


def normalize_dialog_values(values):
    result = dict(values)
    result["qty"] = valid_qty(result.get("qty"))
    result["unitPrice"] = valid_price(result.get("unitPrice"))
    if not str(result.get("name", "")).strip():
        raise DataError("กรุณากรอกชื่ออุปกรณ์")
    return result
