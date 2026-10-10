"""Local report exports; never use GitHub credentials in exported files."""
import csv
import json
import os
from datetime import datetime
from pathlib import Path

import bom_core

BOM_HEADERS = [
    ("id", "ID"), ("category", "หมวดหมู่"), ("name", "อุปกรณ์ / รุ่น"),
    ("spec", "สเปก"), ("qty", "จำนวน"), ("unit", "หน่วย"),
    ("unitPrice", "ราคา/หน่วย (THB)"), ("lineTotal", "รวม (THB)"),
    ("status", "สถานะออกแบบ"), ("supplier", "ร้านค้า"), ("partNumber", "Part No."),
    ("link", "ลิงก์สินค้า"), ("connection", "การต่อ/สายสัญญาณ"), ("notes", "หมายเหตุ"),
]
WIRE_HEADERS = [
    ("id", "ID"), ("from", "ต้นทาง / Terminal"), ("to", "ปลายทาง / Terminal"),
    ("fromItemId", "BOM ID ต้นทาง"), ("toItemId", "BOM ID ปลายทาง"),
    ("signal", "สัญญาณ/ไฟเลี้ยง"), ("voltage", "แรงดัน"),
    ("cable", "ชนิดสาย/ขนาด"), ("protection", "ฟิวส์/การป้องกัน"),
    ("status", "สถานะตรวจสอบ"), ("notes", "หมายเหตุ"),
]
PURCHASE_HEADERS = [
    ("id", "ID"), ("itemId", "BOM ID"), ("description", "รายการสั่งซื้อ"),
    ("supplier", "ผู้ขาย"), ("qty", "จำนวน"), ("unitPrice", "ราคา/หน่วย (THB)"),
    ("lineTotal", "ยอดรวม (THB)"), ("status", "สถานะจัดซื้อ"),
    ("po", "PO/Reference"), ("dueDate", "วันที่คาดว่าจะได้รับ"),
    ("link", "ลิงก์ผู้ขาย"), ("notes", "หมายเหตุ"),
]


def _num(value):
    x = bom_core.decimal_or_none(value)
    return float(x) if x is not None else None


def csv_safe(value):
    text = "" if value is None else str(value)
    # Protect spreadsheet applications from formula execution on imported CSV.
    if text and text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def export_csv(doc, destination):
    bom_core.ensure_doc(doc)
    with open(destination, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([x[1] for x in BOM_HEADERS])
        for item in doc["items"]:
            qty = _num(item.get("qty")) or 0
            price = _num(item.get("unitPrice"))
            row = dict(item)
            row["lineTotal"] = round(qty * price, 2) if price is not None else None
            writer.writerow([csv_safe(row.get(key)) for key, _ in BOM_HEADERS])


def export_json(doc, destination):
    bom_core.ensure_doc(doc)
    with open(destination, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")


def export_excel(doc, destination):
    """Four-tab XLSX with explicit formulas for subtotals and budget summary."""
    import xlsxwriter
    bom_core.ensure_doc(doc)
    workbook = xlsxwriter.Workbook(str(destination))
    workbook.set_properties({"title": "Crane Vehicle BOM Manager", "comments": "ราคาเบื้องต้น ยังไม่ใช่ใบสั่งซื้อ"})
    navy = "#133451"
    title_fmt = workbook.add_format({"bold": True, "font_size": 18, "font_color": navy})
    subtitle_fmt = workbook.add_format({"font_size": 10, "font_color": "#65778B"})
    header_fmt = workbook.add_format({"bold": True, "bg_color": navy, "font_color": "white",
                                      "text_wrap": True, "valign": "vcenter", "border": 0})
    input_fmt = workbook.add_format({"valign": "top", "text_wrap": True})
    qty_fmt = workbook.add_format({"num_format": "#,##0.##", "valign": "top"})
    money_fmt = workbook.add_format({"num_format": '#,##0.00;[Red](#,##0.00)', "valign": "top"})
    label_fmt = workbook.add_format({"bold": True, "font_color": navy})
    hint_fmt = workbook.add_format({"font_color": "#9C6B13", "text_wrap": True})

    def build_sheet(sheet_name, headers, rows, widths, price_col=None, qty_col=None, total_col=None):
        sheet = workbook.add_worksheet(sheet_name)
        sheet.set_tab_color(navy)
        sheet.freeze_panes(4, 2)
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.write(0, 0, sheet_name, title_fmt)
        sheet.write(1, 0, f"โครงการ: {doc.get('project','')} | สกุลเงิน THB", subtitle_fmt)
        for col, (_key, name) in enumerate(headers):
            sheet.write(3, col, name, header_fmt)
            sheet.set_column(col, col, widths.get(col, 18))
        sheet.set_row(3, 32)
        for i, entry in enumerate(rows, start=4):
            excel_row = i + 1
            for col, (key, _name) in enumerate(headers):
                if col == total_col:
                    pletter = xlsxwriter.utility.xl_col_to_name(price_col)
                    qletter = xlsxwriter.utility.xl_col_to_name(qty_col)
                    sheet.write_formula(i, col,
                        f'=IF({pletter}{excel_row}="","",{qletter}{excel_row}*{pletter}{excel_row})',
                        money_fmt)
                    continue
                val = entry.get(key)
                if val is None:
                    sheet.write_blank(i, col, None, input_fmt)
                elif col == qty_col or col == price_col:
                    n = _num(val)
                    if n is None:
                        sheet.write_blank(i, col, None, input_fmt)
                    else:
                        sheet.write_number(i, col, n, money_fmt if col == price_col else qty_fmt)
                else:
                    sheet.write_string(i, col, str(val), input_fmt)
            sheet.set_row(i, 29)
        last = max(4, len(rows) + 3)
        sheet.autofilter(3, 0, last, len(headers) - 1)
        sheet.print_title_rows(0, 3)
        return sheet

    items = doc["items"]
    bom = build_sheet("BOM", BOM_HEADERS, items,
                      {0: 9, 1: 24, 2: 42, 3: 50, 4: 10, 5: 12,
                       6: 20, 7: 20, 8: 25, 9: 23, 10: 16, 11: 42, 12: 50, 13: 45},
                      price_col=6, qty_col=4, total_col=7)
    wire = build_sheet("Wiring", WIRE_HEADERS, doc.get("wiring", []),
                       {0: 9, 1: 30, 2: 30, 3: 16, 4: 16, 5: 22, 6: 16,
                        7: 25, 8: 29, 9: 22, 10: 48})
    wire.write(len(doc.get("wiring", [])) + 6, 0,
               "หมายเหตุ: ตาราง Wiring เป็นบันทึกแบบร่าง ต้องตรวจ pinout, fuse, current และ voltage rating ก่อนประกอบ", hint_fmt)
    orders = doc.get("purchases", [])
    buy = build_sheet("Purchasing", PURCHASE_HEADERS, orders,
                      {0: 9, 1: 12, 2: 40, 3: 28, 4: 10, 5: 20, 6: 20,
                       7: 22, 8: 20, 9: 20, 10: 45, 11: 45},
                      price_col=5, qty_col=4, total_col=6)
    sheet = workbook.add_worksheet("Summary")
    sheet.set_column("A:A", 38)
    sheet.set_column("B:B", 23)
    sheet.set_column("C:C", 72)
    sheet.write("A1", "ภาพรวม BOM / Budget", title_fmt)
    sheet.write("A3", "จำนวนรายการทั้งหมด", label_fmt)
    sheet.write_formula("B3", "=COUNTA(BOM!C5:C1048576)")
    sheet.write("A4", "จำนวนรายการที่มีราคา", label_fmt)
    sheet.write_formula("B4", "=COUNT(BOM!G5:G1048576)")
    sheet.write("A5", "จำนวนรายการที่ยังไม่ทราบราคา", label_fmt)
    sheet.write_formula("B5", "=B3-B4")
    sheet.write("A6", "ยอดรวม BOM ที่ทราบราคา (THB)", label_fmt)
    sheet.write_formula("B6", "=SUM(BOM!H5:H1048576)", money_fmt)
    sheet.write("A7", "ยอดรวมรายการจัดซื้อ (THB)", label_fmt)
    sheet.write_formula("B7", "=SUM(Purchasing!G5:G1048576)", money_fmt)
    sheet.write("A9", "ข้อควรทราบ", label_fmt)
    sheet.write("C9", "ยอดรวม BOM ยังไม่ใช่งบประมาณสุดท้าย เพราะมีรายการที่ยังไม่ทราบราคา", hint_fmt)
    sheet.write("C10", "ราคาไม่รวมค่าจัดส่ง/ภาษี/งานผลิต เว้นแต่บันทึกไว้เป็นรายการแยก", hint_fmt)
    sheet.write("C11", "ข้อมูล Wiring ไม่ใช่ผังวงจรที่รับรองความปลอดภัย", hint_fmt)
    sheet.freeze_panes(2, 0)
    workbook.close()


def _thai_font():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    paths = [
        r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\LeelawUI.ttf",
        r"C:\Windows\Fonts\LeelawadeeUI.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
        "/usr/share/fonts/truetype/thai-tlwg/Garuda.ttf",
    ]
    for font in paths:
        if os.path.isfile(font):
            try:
                pdfmetrics.registerFont(TTFont("CVBOMThai", font))
                return "CVBOMThai"
            except Exception:
                pass
    raise RuntimeError("ไม่พบฟอนต์ไทยสำหรับ PDF (เช่น Tahoma ที่ติดตั้งใน Windows)")


def export_pdf(doc, destination):
    bom_core.ensure_doc(doc)
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
    from xml.sax.saxutils import escape

    font = _thai_font()
    style = ParagraphStyle("CVBOM", fontName=font, fontSize=8.3, leading=13,
                           alignment=TA_LEFT, wordWrap="CJK")
    header = ParagraphStyle("CVBOMHeader", parent=style, fontSize=9,
                            textColor=colors.white, leading=14)
    title = ParagraphStyle("CVBOMTitle", parent=style, fontSize=18,
                           textColor=colors.HexColor("#133451"), leading=27)
    small = ParagraphStyle("CVBOMSmall", parent=style, fontSize=8, leading=11)
    doc_pdf = SimpleDocTemplate(str(destination), pagesize=landscape(A4),
                                rightMargin=31, leftMargin=31,
                                topMargin=34, bottomMargin=34)
    story = [Paragraph("CRANE VEHICLE — BOM MANAGER", title),
             Paragraph(f"โครงการ: {escape(str(doc.get('project','')))} | "
                       f"ส่งออกเมื่อ {datetime.now().strftime('%d/%m/%Y %H:%M')}", style),
             Spacer(1, 13)]

    def p(value):
        return Paragraph(escape(str(value if value is not None else "—")).replace("\n", "<br/>"), style)

    def table_section(title_text, headings, rows, widths):
        story.append(Paragraph(title_text, title))
        body = [[Paragraph(x, header) for x in headings]]
        body.extend([[p(x) for x in row] for row in rows])
        if len(body) == 1:
            body.append([p("ยังไม่มีข้อมูล")] + [p("") for _ in range(len(headings)-1)])
        tab = LongTable(body, colWidths=widths, repeatRows=1, hAlign="LEFT")
        tab.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#133451")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ("GRID", (0, 0), (-1, -1), .25, colors.HexColor("#D5E0E8")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(tab)
        story.append(Spacer(1, 18))

    summary = bom_core.metrics(doc)
    story.append(Paragraph(
        f"ทั้งหมด {summary['items']} รายการ | มีราคา {summary['priced']} รายการ | "
        f"ยังไม่มีราคา {summary['missing']} รายการ | "
        f"รวมราคาที่ทราบ {summary['known_cost']:,.2f} บาท", style))
    story.append(Paragraph("ยอดประมาณการยังไม่รวมรายการที่ไม่ทราบราคาและค่าใช้จ่ายอื่น", small))
    story.append(Spacer(1, 15))
    table_section("รายการวัสดุและอุปกรณ์ (BOM)",
                  ["ID", "หมวด", "อุปกรณ์ / สเปก", "จำนวน", "ราคา/หน่วย", "รวม", "สถานะ"],
                  [[i.get("id",""), i.get("category",""),
                    f"{i.get('name','')}\n{i.get('spec','')}",
                    f"{i.get('qty','')} {i.get('unit','')}",
                    "—" if _num(i.get("unitPrice")) is None else f"{_num(i.get('unitPrice')):,.2f}",
                    "—" if _num(i.get("unitPrice")) is None else f"{_num(i.get('unitPrice'))*(_num(i.get('qty')) or 0):,.2f}",
                    i.get("status","")] for i in doc["items"]],
                  [38, 108, 255, 66, 85, 80, 112])
    table_section("ตาราง Wiring (Draft — ต้องตรวจสอบก่อนใช้งาน)",
                  ["ID", "ต้นทาง", "ปลายทาง", "สัญญาณ/แรงดัน", "ขนาดสาย", "การป้องกัน", "สถานะ"],
                  [[w.get("id",""), w.get("from",""), w.get("to",""),
                    f"{w.get('signal','')}\n{w.get('voltage','')}", w.get("cable",""),
                    w.get("protection",""), w.get("status","")] for w in doc.get("wiring",[])],
                  [38, 133, 133, 105, 110, 113, 112])
    table_section("รายการจัดซื้อ",
                  ["ID", "BOM", "อุปกรณ์", "ผู้ขาย", "จำนวน", "รวม", "สถานะ"],
                  [[o.get("id",""), o.get("itemId",""), o.get("description",""),
                    o.get("supplier",""), o.get("qty",""),
                    "—" if _num(o.get("unitPrice")) is None else f"{(_num(o.get('qty')) or 0)*_num(o.get('unitPrice')):,.2f}",
                    o.get("status","")] for o in doc.get("purchases",[])],
                  [38, 48, 265, 142, 65, 95, 111])
    def footer(canvas, document):
        canvas.setFont(font, 7.5)
        canvas.setFillColor(colors.HexColor("#526579"))
        canvas.drawString(31, 18, "BOM Manager — Engineering draft / ไม่ใช่เอกสารอนุมัติทางไฟฟ้า")
        canvas.drawRightString(landscape(A4)[0]-31, 18, f"หน้า {document.page}")
    doc_pdf.build(story, onFirstPage=footer, onLaterPages=footer)



def export_drawio(doc, destination):
    """Create an editable, non-crossing row-per-connection diagrams.net drawing.

    This is a terminal schedule visualisation, NOT a certified electrical schematic.
    Rows are deliberately independent; no guessed electrical net connections.
    """
    from xml.etree.ElementTree import Element, SubElement, ElementTree
    bom_core.ensure_doc(doc)
    mx = Element("mxfile", {"host": "app.diagrams.net", "type": "device"})
    diagram = SubElement(mx, "diagram", {"id": "bom-wiring", "name": "Wiring Connections"})
    graph = SubElement(diagram, "mxGraphModel", {
        "dx": "1180", "dy": "760", "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1",
        "page": "1", "pageScale": "1", "pageWidth": "1300",
        "pageHeight": str(max(900, 170 + len(doc.get("wiring", [])) * 125))})
    root = SubElement(graph, "root")
    SubElement(root, "mxCell", {"id": "0"})
    SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    def vertex(cell_id, value, x, y, width, height, style):
        cell = SubElement(root, "mxCell", {"id": str(cell_id), "value": str(value),
                                          "style": style, "vertex": "1", "parent": "1"})
        SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y),
                                        "width": str(width), "height": str(height),
                                        "as": "geometry"})
        return cell

    vertex("title", "BOM WIRING — DRAFT (verify ratings and pinouts before wiring)",
           30, 16, 1160, 38,
           "text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;fontSize=18;fontStyle=1;fontColor=#193B58;")
    wires = doc.get("wiring", [])
    for idx, wire in enumerate(wires):
        y = 100 + idx * 125
        sid, tid = f"source_{idx}", f"target_{idx}"
        left = wire.get("from", "") or "(not specified)"
        right = wire.get("to", "") or "(not specified)"
        vertex(sid, left, 30, y, 305, 52,
               "rounded=1;whiteSpace=wrap;html=1;align=center;fillColor=#E9F1F8;strokeColor=#6F92B2;fontSize=13;")
        vertex(tid, right, 885, y, 305, 52,
               "rounded=1;whiteSpace=wrap;html=1;align=center;fillColor=#E9F1F8;strokeColor=#6F92B2;fontSize=13;")
        note = " | ".join(str(wire.get(x) or "—") for x in
                          ("signal", "voltage", "cable", "protection"))
        vertex(f"label_{idx}", f"{wire.get('id', idx+1)}  {note}",
               355, y - 7, 505, 36,
               "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=11;fontColor=#4C5B69;")
        edge = SubElement(root, "mxCell", {
            "id": f"edge_{idx}", "edge": "1", "parent": "1",
            "source": sid, "target": tid,
            "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
                     "html=1;endArrow=block;endFill=1;strokeColor=#567DA0;strokeWidth=2;"
        })
        SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})
    ElementTree(mx).write(destination, encoding="utf-8", xml_declaration=True)
