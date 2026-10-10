"""Pure utilities for BOM purchasing, audit and multi-PC conflict reconciliation."""
import copy
from collections import defaultdict
from decimal import Decimal
from urllib.parse import urlparse
import bom_core

_MISSING = object()
_COLLECTIONS = ("items", "wiring", "purchases")


def purchase_progress(doc):
    needed = {str(i["id"]): Decimal(str(i["qty"])) for i in doc.get("items", [])}
    ordered = defaultdict(lambda: Decimal("0"))
    received = defaultdict(lambda: Decimal("0"))
    for order in doc.get("purchases", []):
        key = str(order.get("itemId") or "")
        if key not in needed or order.get("status") == "ยกเลิก":
            continue
        qty = Decimal(str(order.get("qty") or 0))
        ordered[key] += qty
        if order.get("status") == "ได้รับแล้ว":
            received[key] += qty
        elif order.get("status") == "ได้รับบางส่วน":
            amount = Decimal(str(order.get("receivedQty") or 0))
            received[key] += min(max(amount, Decimal("0")), qty)
    return {
        "lines": len(needed),
        "ordered_lines": sum(ordered[k] >= q for k, q in needed.items()),
        "received_lines": sum(received[k] >= q for k, q in needed.items()),
        "remaining_to_order": {k: max(q - ordered[k], Decimal("0")) for k, q in needed.items()},
        "remaining_to_receive": {k: max(q - received[k], Decimal("0")) for k, q in needed.items()},
        "overordered": {k: ordered[k] - q for k, q in needed.items() if ordered[k] > q},
        "known_purchase_total": bom_core.metrics(doc)["purchase_total"],
    }


def audit_bom(doc):
    issues = []
    def add(level, where, message):
        issues.append({"level": level, "where": where, "detail": message})
    try:
        bom_core.ensure_doc(doc)
    except bom_core.DataError as exc:
        return [{"level": "ERROR", "where": "BOM", "detail": str(exc)}]
    names = defaultdict(list)
    pn_values = defaultdict(list)
    ids = {str(item["id"]) for item in doc["items"]}
    for item in doc["items"]:
        ref = str(item["id"])
        name = str(item.get("name") or "").strip()
        pn = str(item.get("partNumber") or "").strip()
        if not name:
            add("ERROR", ref, "ไม่ระบุชื่ออุปกรณ์")
        else:
            names[name.casefold()].append(ref)
        if pn:
            pn_values[pn.casefold()].append(ref)
        else:
            add("WARN", ref, "ไม่มี Part Number")
        if item.get("unitPrice") in (None, ""):
            add("WARN", ref, "ยังไม่ทราบราคา")
        if not str(item.get("supplier") or "").strip():
            add("WARN", ref, "ยังไม่มีผู้ขาย")
        link = str(item.get("link") or "").strip()
        if link and urlparse(link).scheme not in ("http", "https"):
            add("WARN", ref, "ลิงก์สินค้าไม่ใช่ HTTP/HTTPS")
    for label, groups in (("ชื่อ", names), ("Part Number", pn_values)):
        for refs in groups.values():
            if len(refs) > 1:
                add("WARN", ", ".join(refs), label + " ซ้ำ")
    orders = defaultdict(list)
    for order in doc.get("purchases", []):
        ref = str(order.get("itemId") or "")
        if ref and ref not in ids:
            add("ERROR", ref, "การจัดซื้ออ้างอิง BOM ID ที่ไม่มีแล้ว")
        if ref and order.get("status") != "ยกเลิก":
            orders[ref].append(str(order.get("id") or "—"))
        try:
            amount = Decimal(str(order.get("receivedQty") or 0))
            total = Decimal(str(order.get("qty") or 0))
            if amount < 0 or amount > total:
                add("ERROR", ref, "จำนวนรับจริงต้องอยู่ในช่วง 0 ถึงจำนวนสั่ง")
        except Exception:
            add("ERROR", ref, "จำนวนที่รับจริงไม่ถูกต้อง")
    for ref, lines in orders.items():
        if len(lines) > 1:
            add("WARN", ref, "มีการจัดซื้อซ้ำหลายบรรทัด: " + ", ".join(lines))
    for ref, excess in purchase_progress(doc)["overordered"].items():
        add("WARN", ref, "สั่งเกิน: " + str(excess))
    for message in bom_core.connection_warnings(doc):
        add("WARN", "Wiring", message)
    return issues


def merge_docs(base, local, remote, preference="local"):
    """Three-way merge of fields and ID-linked rows with explicit conflicts."""
    if base is None:
        raise ValueError("Missing GitHub ancestor; refuse unsafe merge")
    if preference not in ("local", "remote"):
        raise ValueError("Unknown conflict preference")
    conflicts = []
    def choose(path, b, l, r):
        if l == r:
            chosen = l
        elif l == b:
            chosen = r
        elif r == b:
            chosen = l
        elif l is not _MISSING and r is not _MISSING and isinstance(l, dict) and isinstance(r, dict):
            result = {}
            base_dict = b if isinstance(b, dict) else {}
            for name in sorted(set(base_dict) | set(l) | set(r)):
                value = choose(path + "." + name, base_dict.get(name, _MISSING),
                               l.get(name, _MISSING), r.get(name, _MISSING))
                if value is not _MISSING:
                    result[name] = value
            return result
        else:
            conflicts.append(path)
            chosen = l if preference == "local" else r
        return _MISSING if chosen is _MISSING else copy.deepcopy(chosen)
    result = {}
    for key in sorted(set(base) | set(local) | set(remote)):
        if key not in _COLLECTIONS:
            value = choose(key, base.get(key, _MISSING), local.get(key, _MISSING),
                           remote.get(key, _MISSING))
            if value is not _MISSING:
                result[key] = value
            continue
        def keyed(rows):
            return {str(row.get("id")): row for row in rows}
        bm = keyed(base.get(key, []))
        lm = keyed(local.get(key, []))
        rm = keyed(remote.get(key, []))
        b_order, l_order, r_order = list(bm), list(lm), list(rm)
        lc = [x for x in l_order if x in bm] != [x for x in b_order if x in lm]
        rc = [x for x in r_order if x in bm] != [x for x in b_order if x in rm]
        if lc and rc and [x for x in l_order if x in bm] != [x for x in r_order if x in bm]:
            conflicts.append(key + ".order")
            order = l_order if preference == "local" else r_order
        elif lc:
            order = l_order
        else:
            order = r_order
        order = list(dict.fromkeys(order + r_order + l_order + b_order))
        rows = []
        for row_id in order:
            value = choose(key + "[" + row_id + "]", bm.get(row_id, _MISSING),
                           lm.get(row_id, _MISSING), rm.get(row_id, _MISSING))
            if value is not _MISSING:
                rows.append(value)
        result[key] = rows
    return result, list(dict.fromkeys(conflicts))
