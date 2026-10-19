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
    steel = bom_steel.summarize(steel_rows)
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
        stock_length = Decimal(str(group["stock_length_m"]))
        bars = int((length_with_waste / stock_length).to_integral_value(rounding=ROUND_CEILING))
        groups.append({**group, "length_with_waste_m": length_with_waste,
                       "estimated_bars_with_waste": bars,
                       "procurement_length_m": stock_length * bars})
        total_required += length
        total_bars += bars
        total_order_length += stock_length * bars
    unit_price = _decimal(steel_purchase_unit_price, "ราคาเหล็กต่อท่อน", allow_blank=True)
    steel_cost = (unit_price * total_bars) if unit_price is not None else None
    return {
        "category_summary": by_category,
        "bom_items": len(items),
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
