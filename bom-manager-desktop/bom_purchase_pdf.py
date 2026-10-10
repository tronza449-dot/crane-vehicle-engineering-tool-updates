"""Draft Purchase Order PDF for a single supplier and PO reference."""
from decimal import Decimal
from xml.sax.saxutils import escape


def export_po_pdf(doc, orders, filename, vat_percent=7.0):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
    from bom_reports import _thai_font
    if not orders:
        raise ValueError("ยังไม่มีรายการจัดซื้อให้ส่งออก")
    if any(o.get("status") == "ยกเลิก" for o in orders):
        raise ValueError("ไม่สามารถนำรายการยกเลิกไปออกใบสั่งซื้อ")
    suppliers = {str(o.get("supplier") or "").strip() for o in orders}
    if len(suppliers) != 1:
        raise ValueError("ใบสั่งซื้อหนึ่งฉบับต้องมีผู้ขายเดียวกัน")
    total = Decimal("0")
    vat_rate = Decimal(str(vat_percent)) / 100
    if vat_rate < 0 or vat_rate > 1:
        raise ValueError("VAT ต้องอยู่ระหว่าง 0 ถึง 100")
    font = _thai_font()
    body = ParagraphStyle("po", fontName=font, fontSize=9.2, leading=15, textColor=colors.HexColor("#203449"))
    small = ParagraphStyle("po-small", parent=body, fontSize=8.5, leading=13)
    bold = ParagraphStyle("po-bold", parent=body, fontSize=12, leading=18)
    def p(txt, style=body):
        return Paragraph(escape(str(txt or "—")).replace("\n", "<br/>"), style)
    flow = [p("PURCHASE ORDER / ใบสั่งซื้อ (DRAFT)", bold), Spacer(1, 9)]
    supplier = next(iter(suppliers)) or "ยังไม่ระบุผู้ขาย"
    first = orders[0]
    reference = str(first.get("po") or "ยังไม่ระบุเลข PO")
    flow += [p("โครงการ: " + str(doc.get("project") or "BOM Manager")),
             p("ผู้ขาย: " + supplier), p("เลขที่ PO: " + reference),
             p("สถานะเอกสาร: ฉบับร่าง ยังไม่ใช่เอกสารอนุมัติ"), Spacer(1, 18)]
    rows = [[p("ลำดับ", small), p("BOM ID", small), p("รายการ", small),
             p("จำนวน", small), p("ราคา/หน่วย", small), p("รวม", small)]]
    for index, order in enumerate(orders, 1):
        qty = Decimal(str(order.get("qty") or 0))
        if order.get("unitPrice") in (None, ""):
            raise ValueError("ใบสั่งซื้อมีรายการที่ยังไม่ได้ระบุราคา")
        price = Decimal(str(order["unitPrice"]))
        amount = qty * price
        total += amount
        rows.append([p(index, small), p(order.get("itemId"), small),
                     p(order.get("description"), small), p(str(qty), small),
                     p(f"{price:,.2f}", small), p(f"{amount:,.2f}", small)])
    table = LongTable(rows, colWidths=[41, 56, 216, 58, 81, 80], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCEAF5")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C4D4E2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    vat = total * vat_rate
    flow.extend([table, Spacer(1, 15),
                 p(f"ยอดก่อนภาษี: {total:,.2f} บาท"),
                 p(f"VAT {vat_percent:g}%: {vat:,.2f} บาท"),
                 p(f"ยอดรวม: {total + vat:,.2f} บาท", bold),
                 Spacer(1, 30),
                 p("ผู้จัดทำ: ____________________       ผู้อนุมัติ: ____________________"),
                 p("หมายเหตุ: ตรวจสอบผู้ขาย รายละเอียด ภาษี และเงื่อนไขการชำระเงินจริงก่อนใช้งาน", small)])
    document = SimpleDocTemplate(str(filename), pagesize=A4, rightMargin=30,
                                 leftMargin=30, topMargin=35, bottomMargin=35)
    document.build(flow)
    return {"subtotal": total, "vat": vat, "total": total + vat}
