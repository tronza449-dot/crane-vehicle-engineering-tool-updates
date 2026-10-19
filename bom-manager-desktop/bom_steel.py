"""Steel cut-list validation and quantity takeoff calculations.

Stock-bar counts are lower-bound estimates based on total length only. They
exclude kerf, unusable offcuts, cutting layout, joints, and fabrication waste.
"""
from decimal import Decimal, InvalidOperation, ROUND_CEILING

# Material is independent of profile/shape: e.g. a square tube may be
# carbon steel or stainless steel. Unknown legacy entries stay explicitly
# unspecified rather than being assigned a guessed grade or density.
DEFAULT_MATERIAL = "วัสดุเดิม/ไม่ระบุเกรด"
MATERIAL_OPTIONS = (
    DEFAULT_MATERIAL,
    "เหล็กคาร์บอน (SS400 / ASTM A36)",
    "เหล็กชุบสังกะสี",
    "สแตนเลส SUS 201",
    "สแตนเลส SUS 304",
    "สแตนเลส SUS 316",
    "อะลูมิเนียม 6061",
    "อะลูมิเนียม 6063",
    "ทองแดง",
    "ทองเหลือง",
    "วัสดุอื่น ๆ",
)

WEIGHT_MODE_LENGTH = "length_based"
WEIGHT_MODE_MANUAL = "manual"
WEIGHT_MODE_OPTIONS = (
    (WEIGHT_MODE_LENGTH, "เหล็กกล่อง/หน้าตัด — คำนวณจากความยาว"),
    (WEIGHT_MODE_MANUAL, "ชิ้นส่วนอื่น — กรอกน้ำหนักต่อชิ้นเอง"),
)


PROFILE_OPTIONS = (
    "เหล็กกล่องสี่เหลี่ยม",
    "เหล็กกล่องแบน",
    "เหล็กฉาก",
    "เหล็กตัวซี",
    "เหล็กตัวไอ/เอช",
    "เหล็กแบน",
    "ท่อเหล็กกลม",
    "เหล็กเส้น",
    "เพลากลม",
    "เพลาสี่เหลี่ยม",
    "เหล็กตัวที",
    "ชิ้นส่วนอื่น",
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
    """Validate a cut-list row in either length-based or manual-mass mode.

    Legacy rows without weight_mode retain the original length-based behaviour.
    Manual-mass rows need a quantity and kg per piece; length and stock-bar
    fields may be blank because a plate, bracket, purchased assembly, or other
    non-tubular component may not be described by a cut length.
    """
    row = dict(values)
    member = str(row.get("member") or "").strip()
    material = str(row.get("material") or DEFAULT_MATERIAL).strip()
    mode = str(row.get("weight_mode") or WEIGHT_MODE_LENGTH).strip()
    if mode not in (WEIGHT_MODE_LENGTH, WEIGHT_MODE_MANUAL):
        raise SteelDataError("กรุณาเลือกโหมดน้ำหนักที่รองรับ")
    profile = str(row.get("profile") or "").strip()
    if not profile and mode == WEIGHT_MODE_MANUAL:
        profile = "ชิ้นส่วนอื่น"
    size = str(row.get("size") or "").strip()
    if not size and mode == WEIGHT_MODE_MANUAL:
        size = "ไม่ระบุขนาด"
    if not member:
        raise SteelDataError("กรุณาระบุตำแหน่งหรือชื่อชิ้นส่วน")
    if not profile:
        raise SteelDataError("กรุณาเลือกชนิดหน้าตัด")
    if not size:
        raise SteelDataError("กรุณาระบุขนาดหน้าตัด เช่น 25×25×2 mm")
    qty = _positive(row.get("qty"), "จำนวนชิ้น")
    if qty != qty.to_integral_value():
        raise SteelDataError("จำนวนชิ้นต้องเป็นจำนวนเต็ม")

    manual_raw = row.get("manual_unit_weight_kg")
    if mode == WEIGHT_MODE_MANUAL:
        manual_weight = _positive(manual_raw, "น้ำหนักต่อชิ้น (kg)")
        length_raw = row.get("length_mm")
        length_mm = (_positive(length_raw, "ความยาวต่อชิ้น (mm)")
                     if length_raw is not None and str(length_raw).strip() else None)
        stock_raw = row.get("stock_length_m")
        stock_length = (_positive(stock_raw, "ความยาวเหล็กมาตรฐาน (m)")
                        if stock_raw is not None and str(stock_raw).strip() else None)
        if length_mm is not None and stock_length is not None and length_mm > stock_length * 1000:
            raise SteelDataError(
                "ความยาวชิ้นงานมากกว่าท่อนมาตรฐานที่เลือก "
                "ให้ตรวจความยาวหรือเปลี่ยนความยาวท่อนมาตรฐาน")
        row.update({
            "member": member, "material": material, "profile": profile, "size": size,
            "weight_mode": mode, "qty": int(qty),
            "length_mm": (float(length_mm) if length_mm is not None and
                          length_mm != length_mm.to_integral_value()
                          else int(length_mm) if length_mm is not None else None),
            "stock_length_m": float(stock_length) if stock_length is not None else None,
            "weight_reference_length_m": None,
            "weight_reference_kg": None,
            "manual_unit_weight_kg": float(manual_weight),
            "link": str(row.get("link") or "").strip(),
            "notes": str(row.get("notes") or "").strip(),
        })
        return row

    length_mm = _positive(row.get("length_mm"), "ความยาวต่อชิ้น (mm)")
    stock_length_m = _positive(row.get("stock_length_m") or 6, "ความยาวเหล็กมาตรฐาน (m)")
    reference_length_raw = row.get("weight_reference_length_m")
    reference_weight_raw = row.get("weight_reference_kg")
    has_reference_length = (reference_length_raw is not None and
                            str(reference_length_raw).strip() != "")
    has_reference_weight = (reference_weight_raw is not None and
                            str(reference_weight_raw).strip() != "")
    if has_reference_length and has_reference_weight:
        reference_length = _positive(reference_length_raw, "ความยาวอ้างอิงน้ำหนัก (m)")
        reference_weight = _positive(reference_weight_raw, "น้ำหนักอ้างอิง (kg)")
    elif has_reference_length or has_reference_weight:
        raise SteelDataError(
            "การคำนวณน้ำหนักต้องกรอกทั้งความยาวอ้างอิง (m) และน้ำหนักของความยาวนั้น (kg)")
    else:
        reference_length = None
        reference_weight = None
    if length_mm > stock_length_m * Decimal("1000"):
        raise SteelDataError(
            "ความยาวชิ้นงานมากกว่าท่อนมาตรฐานที่เลือก "
            "ให้ตรวจความยาวหรือเปลี่ยนความยาวท่อนมาตรฐาน")
    row.update({
        "member": member,
        "material": material,
        "profile": profile,
        "size": size,
        "weight_mode": mode,
        "qty": int(qty),
        "length_mm": float(length_mm) if length_mm != length_mm.to_integral_value()
        else int(length_mm),
        "stock_length_m": float(stock_length_m),
        "weight_reference_length_m": (
            float(reference_length) if reference_length is not None else None),
        "weight_reference_kg": (
            float(reference_weight) if reference_weight is not None else None),
        "manual_unit_weight_kg": None,
        "link": str(row.get("link") or "").strip(),
        "notes": str(row.get("notes") or "").strip(),
    })
    return row

def total_length_m(row):
    """Total required length for one cut-list row, in metres (zero if not applicable)."""
    normalized = normalize_member(row)
    if normalized["length_mm"] is None:
        return Decimal("0")
    qty = Decimal(str(normalized["qty"]))
    length_mm = Decimal(str(normalized["length_mm"]))
    return qty * length_mm / Decimal("1000")


def weight_per_m(row):
    """Calculate kg/m from the user's measured reference length and weight.

    Returns None when no weight reference was provided. No steel density or
    profile weight is guessed from the nominal dimensions.
    """
    reference = normalize_member(row)
    if reference["weight_mode"] == WEIGHT_MODE_MANUAL:
        return None
    length = reference.get("weight_reference_length_m")
    weight = reference.get("weight_reference_kg")
    if length is None or weight is None:
        return None
    return Decimal(str(weight)) / Decimal(str(length))


def total_weight_kg(row):
    """Return known total mass, using either kg/m or the user's kg-per-piece."""
    normalized = normalize_member(row)
    if normalized["weight_mode"] == WEIGHT_MODE_MANUAL:
        return Decimal(str(normalized["qty"])) * Decimal(
            str(normalized["manual_unit_weight_kg"]))
    rate = weight_per_m(normalized)
    if rate is None:
        return None
    return total_length_m(normalized) * rate


def summarize(rows):
    """Aggregate length and known/unknown mass by profile, size, and stock length."""
    groups = {}
    total_pieces = 0
    total_length = Decimal("0")
    for raw in rows or []:
        row = normalize_member(raw)
        stock_value = row["stock_length_m"]
        stock_key = Decimal(str(stock_value)) if stock_value is not None else None
        key = (row["weight_mode"], row["material"], row["profile"], row["size"], stock_key)
        group = groups.setdefault(key, {
            "weight_mode": row["weight_mode"],
            "material": row["material"],
            "profile": row["profile"], "size": row["size"],
            "stock_length_m": float(stock_value) if stock_value is not None else None,
            "pieces": 0, "total_length_m": Decimal("0"),
            "known_weight_kg": Decimal("0"),
            "unknown_weight_length_m": Decimal("0"),
        })
        row_length = total_length_m(row)
        group["pieces"] += row["qty"]
        group["total_length_m"] += row_length
        if row["weight_mode"] == WEIGHT_MODE_MANUAL:
            group["known_weight_kg"] += total_weight_kg(row)
        else:
            rate = weight_per_m(row)
            if rate is None:
                group["unknown_weight_length_m"] += row_length
            else:
                group["known_weight_kg"] += row_length * rate
        total_pieces += row["qty"]
        total_length += row_length

    result = []
    total_stock_bars = 0
    total_known_weight = Decimal("0")
    total_unknown_weight_length = Decimal("0")
    for key in sorted(groups, key=lambda x: (
            x[0], x[1].casefold(), x[2].casefold(), x[3].casefold(),
            x[4].casefold(), x[5] if x[5] is not None else Decimal("0"))):
        group = groups[key]
        stock_length = group["stock_length_m"]
        if stock_length is not None and group["total_length_m"] > 0:
            group["estimated_stock_bars"] = int(
                (group["total_length_m"] / Decimal(str(stock_length)))
                .to_integral_value(rounding=ROUND_CEILING))
        else:
            group["estimated_stock_bars"] = 0
        total_stock_bars += group["estimated_stock_bars"]
        total_known_weight += group["known_weight_kg"]
        total_unknown_weight_length += group["unknown_weight_length_m"]
        result.append(group)
    return {
        "groups": result,
        "total_pieces": total_pieces,
        "total_length_m": total_length,
        "estimated_stock_bars": total_stock_bars,
        "known_weight_kg": total_known_weight,
        "unknown_weight_length_m": total_unknown_weight_length,
    }


def format_length(value, places=3):
    return f"{float(value):,.{places}f}"
