"""Stable engineering-system categories for the Crane Vehicle BOM.

Only the category field is reclassified. Component identities, prices,
connections, suppliers, quantities and order records must remain unchanged.
"""
from collections import Counter

CATEGORY_ORDER = (
    "โครงสร้างและเครื่องกล",
    "ระบบขับเคลื่อน",
    "แบตเตอรี่และไฟฟ้ากำลัง",
    "ระบบควบคุมและสื่อสาร",
    "เซนเซอร์และความปลอดภัย",
    "ระบบเครนและวินช์",
    "สายไฟและอุปกรณ์ติดตั้ง",
)
UNCATEGORIZED = "อื่น ๆ / รอจัดหมวด"
CATEGORY_OPTIONS = (*CATEGORY_ORDER, UNCATEGORIZED)

# Exact BOM item IDs in the user's 33-item engineering BOM.
# This is ONLY used for deliberate one-time project migration, never
# for changing category during ordinary loading or editing.
PROJECT_CATEGORY_IDS = {
    "โครงสร้างและเครื่องกล": ("26", "27", "28"),
    "ระบบขับเคลื่อน": ("2", "3"),
    "แบตเตอรี่และไฟฟ้ากำลัง": ("4", "5", "6", "7", "9", "10"),
    "ระบบควบคุมและสื่อสาร": ("1", "11", "14", "15", "18", "19", "20"),
    "เซนเซอร์และความปลอดภัย": ("8", "12", "13", "16", "17", "21"),
    "ระบบเครนและวินช์": ("22", "23", "24", "25"),
    "สายไฟและอุปกรณ์ติดตั้ง": ("29", "30", "31", "32", "33"),
}

ID_TO_CATEGORY = {
    item_id: category
    for category, item_ids in PROJECT_CATEGORY_IDS.items()
    for item_id in item_ids
}
assert len(ID_TO_CATEGORY) == 33, "Each initial BOM ID must be assigned once"


def sort_key(category):
    category = str(category or UNCATEGORIZED)
    try:
        return (CATEGORY_ORDER.index(category), "")
    except ValueError:
        return (len(CATEGORY_ORDER), category.casefold())


def sorted_categories(categories):
    return sorted(set(str(cat or UNCATEGORIZED) for cat in categories), key=sort_key)


def reclassify_project_items(items, *, strict=True):
    """Return a copy of rows changing *only* category, never underlying rows.

    Require all 33 original IDs with no extras when strict=True to protect
    against accidental application to a changed BOM.
    """
    keys = [str(item.get("id")) for item in items]
    if strict and (len(keys) != 33 or len(set(keys)) != 33
                   or set(keys) != set(ID_TO_CATEGORY)):
        raise ValueError("Project category migration requires exactly the 33 original BOM IDs")
    updated = []
    for entry in items:
        row = dict(entry)
        new_cat = ID_TO_CATEGORY.get(str(entry.get("id")))
        if new_cat:
            row["category"] = new_cat
        updated.append(row)
    return updated


def summary(items):
    counts = Counter(str(item.get("category") or UNCATEGORIZED) for item in items)
    return [(cat, counts[cat]) for cat in sorted_categories(counts)]
