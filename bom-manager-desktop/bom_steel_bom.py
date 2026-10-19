"""Additive steel take-off and cost summary helpers for the engineering BOM."""
from decimal import Decimal, InvalidOperation, ROUND_CEILING

import bom_categories
import bom_steel


def _decimal(value, label, *, allow_blank=False):
    if value is None or str(value).strip() == "":
        if allow_blank:
            return None
        raise ValueError(f"{label}: กรุณากรอกข้อมูล")
    try:
        result = Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{label}: ต้องเป็นตัวเลข") from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f"{label}: ต้องเป็นเลขตั้งแต่ศูนย์ขึ้นไป")
    return result


def summarize_bom_and_steel(doc, steel_purchase_unit_price=None, waste_percent=0):
    """Return BOM summary, steel totals by section and estimated stock procurement.

    BOM costs remain separate from structural steel costs because the steel
    cut-list describes fabrication material and may overlap with a BOM frame.
    Do not add them automatically to BOM budget; callers may show a separate
    clearly-labelled estimate when price per stock bar is supplied.
    """
    items = doc.get("items", [])
    steel_rows = doc.get("steel_members", [])
    by_category = {}
    known_bom_cost = Decimal("0")
    missing_prices = 0
    for item in items:
        category = bom_categories.normalize_category(item.get("category"))
        entry = by_category.setdefault(category, {"items": 0, "quantity": Decimal("0"),
                                                   "known_cost": Decimal("0"),
                                                   "missing_prices": 0})
        entry["items"] += 1
        qty = _decimal(item.get("qty", 0), "จำนวน BOM")
        entry["quantity"] += qty
        price = _decimal(item.get("unitPrice"), "ราคา BOM", allow_blank=True)
        if price is None:
            entry["missing_prices"] += 1
            missing_prices += 1
        else:
            cost = qty * price
            entry["known_cost"] += cost
            known_bom_cost += cost
    # Equipment mass is entered manually as kg per BOM unit. Never infer a
    # component mass from its name or price; missing weights remain unknown.
    equipment_known_weight = Decimal("0")
    equipment_weighted_items = 0
    equipment_missing_weight_count = 0
    equipment_missing_weight_qty = Decimal("0")
    equipment_weight_rows = []
    for item in items:
        qty = _decimal(item.get("qty", 0), "จำนวน BOM")
        unit_weight = _decimal(item.get("unitWeightKg"), "น้ำหนักต่อหน่วย",
                               allow_blank=True)
        if unit_weight is not None and unit_weight <= 0:
            raise ValueError("น้ำหนักต่อหน่วยต้องมากกว่า 0 kg หรือเว้นว่างหากยังไม่ทราบ")
        line_weight = None if unit_weight is None else qty * unit_weight
        if line_weight is None:
            equipment_missing_weight_count += 1
            equipment_missing_weight_qty += qty
        else:
            equipment_weighted_items += 1
            equipment_known_weight += line_weight
        equipment_weight_rows.append({
            "id": str(item.get("id") or ""),
            "name": str(item.get("name") or ""),
            "qty": qty,
            "unit": str(item.get("unit") or ""),
            "unit_weight_kg": unit_weight,
            "total_weight_kg": line_weight,
        })
    steel = bom_steel.summarize(steel_rows)
    combined_known_weight = equipment_known_weight + steel["known_weight_kg"]
    waste = _decimal(waste_percent, "เปอร์เซ็นต์เผื่อเศษ")
    if waste > 100:
        raise ValueError("เปอร์เซ็นต์เผื่อเศษต้องไม่เกิน 100")
    groups = []
    total_required = Decimal("0")
    total_bars = 0
    total_order_length = Decimal("0")
    for group in steel["groups"]:
        length = group["total_length_m"]
        length_with_waste = length * (Decimal("1") + waste / Decimal("100"))
        stock_value = group.get("stock_length_m")
        if stock_value is not None and length_with_waste > 0:
            stock_length = Decimal(str(stock_value))
            bars = int((length_with_waste / stock_length).to_integral_value(rounding=ROUND_CEILING))
            procurement_length = stock_length * bars
        else:
            # Manual-mass components have no stock-bar length; their weight is
            # still included, but they must not inflate steel procurement.
            bars = 0
            procurement_length = Decimal("0")
        groups.append({**group, "length_with_waste_m": length_with_waste,
                       "estimated_bars_with_waste": bars,
                       "procurement_length_m": procurement_length})
        total_required += length
        total_bars += bars
        total_order_length += procurement_length
    unit_price = _decimal(steel_purchase_unit_price, "ราคาเหล็กต่อท่อน", allow_blank=True)
    steel_cost = (unit_price * total_bars) if unit_price is not None else None
    return {
        "category_summary": by_category,
        "bom_items": len(items),
        "equipment_weight_rows": equipment_weight_rows,
        "equipment_known_weight_kg": equipment_known_weight,
        "equipment_weighted_items": equipment_weighted_items,
        "equipment_missing_weight_count": equipment_missing_weight_count,
        "equipment_missing_weight_qty": equipment_missing_weight_qty,
        "combined_known_weight_kg": combined_known_weight,
        "combined_weight_complete": (
            equipment_missing_weight_count == 0 and
            steel["unknown_weight_length_m"] == 0
        ),
        "bom_known_cost": known_bom_cost,
        "bom_missing_prices": missing_prices,
        "steel_groups": groups,
        "steel_pieces": steel["total_pieces"],
        "steel_known_weight_kg": steel["known_weight_kg"],
        "steel_unknown_weight_length_m": steel["unknown_weight_length_m"],
        "steel_required_length_m": total_required,
        "steel_length_with_waste_m": total_required * (Decimal("1") + waste / Decimal("100")),
        "steel_stock_bars": total_bars,
        "steel_procurement_length_m": total_order_length,
        "steel_cost_estimate": steel_cost,
        "waste_percent": waste,
        "steel_unit_price_per_bar": unit_price,
    }
