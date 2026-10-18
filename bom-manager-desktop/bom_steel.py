"""Steel cut-list validation and quantity takeoff calculations.

Stock-bar counts are lower-bound estimates based on total length only. They
exclude kerf, unusable offcuts, cutting layout, joints, and fabrication waste.
"""
from decimal import Decimal, InvalidOperation, ROUND_CEILING

PROFILE_OPTIONS = (
    "เหล็กกล่องสี่เหลี่ยม",
    "เหล็กกล่องแบน",
    "เหล็กฉาก",
    "เหล็กตัวซี",
    "เหล็กตัวไอ/เอช",
    "เหล็กแบน",
    "ท่อเหล็กกลม",
    "เหล็กเส้น",
    "อื่น ๆ",
)


class SteelDataError(ValueError):
    """Invalid structural-steel cut-list row."""


def _positive(value, label):
    try:
        number = Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError, AttributeError) as exc:
        raise SteelDataError(f"{label} ต้องเป็นตัวเลข") from exc
    if not number.is_finite() or number <= 0:
        raise SteelDataError(f"{label} ต้องมากกว่า 0")
    return number


def normalize_member(values):
    """Validate and normalize an editable cut-list row."""
    row = dict(values)
    member = str(row.get("member") or "").strip()
    profile = str(row.get("profile") or "").strip()
    size = str(row.get("size") or "").strip()
    if not member:
        raise SteelDataError("กรุณาระบุตำแหน่งหรือชื่อชิ้นส่วน")
    if not profile:
        raise SteelDataError("กรุณาเลือกชนิดหน้าตัดเหล็ก")
    if not size:
        raise SteelDataError("กรุณาระบุขนาดหน้าตัด เช่น 25×25×2 mm")
    qty = _positive(row.get("qty"), "จำนวนชิ้น")
    if qty != qty.to_integral_value():
        raise SteelDataError("จำนวนชิ้นต้องเป็นจำนวนเต็ม")
    length_mm = _positive(row.get("length_mm"), "ความยาวต่อชิ้น (mm)")
    stock_length_m = _positive(row.get("stock_length_m") or 6, "ความยาวเหล็กมาตรฐาน (m)")
    row.update({
        "member": member,
        "profile": profile,
        "size": size,
        "qty": int(qty),
        "length_mm": float(length_mm) if length_mm != length_mm.to_integral_value()
        else int(length_mm),
        "stock_length_m": float(stock_length_m),
        "notes": str(row.get("notes") or "").strip(),
    })
    return row


def total_length_m(row):
    """Total required length for one cut-list row, in metres."""
    qty = _positive(row.get("qty"), "จำนวนชิ้น")
    length_mm = _positive(row.get("length_mm"), "ความยาวต่อชิ้น (mm)")
    return qty * length_mm / Decimal("1000")


def summarize(rows):
    """Aggregate pieces and length by profile, section size, and stock length."""
    groups = {}
    total_pieces = 0
    total_length = Decimal("0")
    for raw in rows or []:
        row = normalize_member(raw)
        key = (row["profile"], row["size"], Decimal(str(row["stock_length_m"])))
        group = groups.setdefault(key, {
            "profile": row["profile"], "size": row["size"],
            "stock_length_m": float(row["stock_length_m"]),
            "pieces": 0, "total_length_m": Decimal("0"),
        })
        group["pieces"] += row["qty"]
        group["total_length_m"] += total_length_m(row)
        total_pieces += row["qty"]
        total_length += total_length_m(row)

    result = []
    total_stock_bars = 0
    for key in sorted(groups, key=lambda x: (x[0].casefold(), x[1].casefold(), x[2])):
        group = groups[key]
        group["estimated_stock_bars"] = int(
            (group["total_length_m"] / Decimal(str(group["stock_length_m"])))
            .to_integral_value(rounding=ROUND_CEILING))
        total_stock_bars += group["estimated_stock_bars"]
        result.append(group)
    return {
        "groups": result,
        "total_pieces": total_pieces,
        "total_length_m": total_length,
        "estimated_stock_bars": total_stock_bars,
    }


def format_length(value, places=3):
    return f"{float(value):,.{places}f}"
