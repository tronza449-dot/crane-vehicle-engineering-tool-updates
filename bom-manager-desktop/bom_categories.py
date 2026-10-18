"""Small, stable BOM categories for engineering reports and everyday editing.

Legacy labels are normalized for display/export, and an explicit migration helper
can change only category fields while preserving every other BOM value.
"""
from collections import Counter

CATEGORY_ORDER = ("เครื่องกล", "ไฟฟ้ากำลัง", "อิเล็กทรอนิกส์/ควบคุม")
UNCATEGORIZED = "อื่น ๆ"
CATEGORY_OPTIONS = (*CATEGORY_ORDER, UNCATEGORIZED)

LEGACY_CATEGORY_MAP = {
    # Old detailed labels -> three clear top-level engineering disciplines.
    "โครงสร้างและเครื่องกล": "เครื่องกล",
    "โครงสร้างเครื่องกล": "เครื่องกล",
    "ระบบเครนและวินช์": "เครื่องกล",
    "Mechanical": "เครื่องกล",
    "ระบบขับเคลื่อน": "ไฟฟ้ากำลัง",
    "ขับเคลื่อน/พลังงาน": "ไฟฟ้ากำลัง",
    "แบตเตอรี่และไฟฟ้ากำลัง": "ไฟฟ้ากำลัง",
    "สายไฟและอุปกรณ์ติดตั้ง": "ไฟฟ้ากำลัง",
    "สายไฟ/อุปกรณ์ประกอบ": "ไฟฟ้ากำลัง",
    "วินช์/เครน": "ไฟฟ้ากำลัง",
    "ไฟฟ้า": "ไฟฟ้ากำลัง",
    "Electrical": "ไฟฟ้ากำลัง",
    "Power": "ไฟฟ้ากำลัง",
    "ระบบควบคุมและสื่อสาร": "อิเล็กทรอนิกส์/ควบคุม",
    "เซนเซอร์และความปลอดภัย": "อิเล็กทรอนิกส์/ควบคุม",
    "อิเล็กทรอนิกส์และระบบควบคุม": "อิเล็กทรอนิกส์/ควบคุม",
    "อิเล็กทรอนิกส์และควบคุม": "อิเล็กทรอนิกส์/ควบคุม",
    "อิเล็กทรอนิกส์": "อิเล็กทรอนิกส์/ควบคุม",
    "Electronics": "อิเล็กทรอนิกส์/ควบคุม",
    "Uncategorized": UNCATEGORIZED,
    "อื่น ๆ / รอจัดหมวด": UNCATEGORIZED,
}

# Original 33-item baseline only. These IDs are used by the explicit, strict
# migration helper, never as a rule for classifying newly created BOM items.
PROJECT_CATEGORY_IDS = {
    "เครื่องกล": ("26", "27", "28"),
    "ไฟฟ้ากำลัง": ("3", "4", "5", "6", "7", "9", "10", "16", "22", "23",
                  "25", "29", "30", "31", "33"),
    "อิเล็กทรอนิกส์/ควบคุม": ("1", "2", "8", "11", "12", "13", "14", "15",
                              "17", "18", "19", "20", "21", "24", "32"),
}
ID_TO_CATEGORY = {
    item_id: category
    for category, item_ids in PROJECT_CATEGORY_IDS.items()
    for item_id in item_ids
}
assert len(ID_TO_CATEGORY) == 33, "Each baseline BOM ID must be assigned once"


def normalize_category(category):
    """Return one of the three major categories or 'อื่น ๆ' for unknown labels."""
    raw = str(category or "").strip()
    if raw in CATEGORY_OPTIONS:
        return raw
    return LEGACY_CATEGORY_MAP.get(raw, UNCATEGORIZED)


def sort_key(category):
    normalized = normalize_category(category)
    try:
        return (CATEGORY_ORDER.index(normalized), "")
    except ValueError:
        return (len(CATEGORY_ORDER), normalized.casefold())


def sorted_categories(categories):
    present = {normalize_category(category) for category in categories}
    return [category for category in CATEGORY_ORDER if category in present] + (
        [UNCATEGORIZED] if UNCATEGORIZED in present else [])


def reclassify_project_items(items, *, strict=True):
    """Return a copy of the original baseline rows with only category changed.

    The strict ID guard prevents applying a baseline migration to an unrelated
    or modified project. This function intentionally does not infer new items.
    """
    keys = [str(item.get("id")) for item in items]
    if strict and (len(keys) != 33 or len(set(keys)) != 33
                   or set(keys) != set(ID_TO_CATEGORY)):
        raise ValueError("Project category migration requires exactly the 33 original BOM IDs")
    updated = []
    for entry in items:
        row = dict(entry)
        target = ID_TO_CATEGORY.get(str(entry.get("id")))
        if target:
            row["category"] = target
        else:
            row["category"] = normalize_category(entry.get("category"))
        updated.append(row)
    return updated


def summary(items):
    counts = Counter(normalize_category(item.get("category")) for item in items)
    return [(category, counts[category]) for category in sorted_categories(counts)]
