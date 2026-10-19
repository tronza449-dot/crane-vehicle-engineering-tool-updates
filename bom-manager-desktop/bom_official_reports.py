"""Formal engineering BOM PDF / Excel, independent of legacy exports.

Only figures with known prices contribute to budget totals. Blank means unknown.
All report cover metadata is editable and does not imply institutional approval.
"""
from datetime import datetime
from xml.sax.saxutils import escape
import bom_core
import bom_categories
import bom_steel
import bom_steel_bom

# One restrained palette shared by PDF and Excel to match the formal
# academic prototype: navy headings, blue accents, pale-blue table bands.
# Category identity is communicated by labels and grouping, not rainbow fills.
NAVY="#18324F"
BLUE="#3F789E"
GREY="#5E6B78"
PALE="#EEF3F7"
LINE="#D1DCE5"
ROW_ALT="#F7F9FB"
CATEGORY_FILL="#E7F0F6"

# Excel intentionally has its own worksheet-first palette (teal / mist grey).
# PDF remains navy-blue and report-like; the two outputs must not look like
# the same template recolored.
EXCEL_NAVY="#123B4A"
EXCEL_BLUE="#087E8B"
EXCEL_GREY="#5C6F73"
EXCEL_PALE="#E6F3F4"
EXCEL_LINE="#C7D9DC"
EXCEL_ROW_ALT="#F5F9F9"
EXCEL_CATEGORY_FILL="#DDEFF1"
EXCEL_FONT="TH Sarabun New"


def metadata(doc, values=None):
    v=values or {}
    return {
        "project": str(v.get("project") or doc.get("project") or "Crane Vehicle"),
        "author": str(v.get("author") or "ไม่ระบุ"),
        "institution": str(v.get("institution") or "ไม่ระบุ"),
        "advisor": str(v.get("advisor") or "ไม่ระบุ"),
        "document_no": str(v.get("document_no") or "BOM-001"),
        "revision": str(v.get("revision") or "00"),
        "date": str(v.get("date") or datetime.now().strftime("%d/%m/%Y")),
    }


def sorted_items(doc):
    """Keep the manually saved BOM order inside each engineering category.

    Python's stable sort preserves the existing relative order of items with
    the same category, including custom ↑/↓ moves made on another computer.
    """
    return sorted(doc["items"], key=lambda x:
                  bom_categories.sort_key(bom_categories.normalize_category(
                      x.get("category"))))


def price(value):
    return bom_core.decimal_or_none(value)


def category_stats(items):
    result=[]
    for category,count in bom_categories.summary(items):
        rows=[x for x in items if bom_categories.normalize_category(
               x.get("category")) == category]
        missing=sum(price(x.get("unitPrice")) is None for x in rows)
        known=sum((price(x.get("unitPrice")) or 0) *
                  (price(x.get("qty")) or 0) for x in rows)
        result.append((category,count,missing,float(known)))
    return result



def report_quality(items):
    """Count missing fields without guessing values for engineering components."""
    return {
        "part_number_missing": sum(not str(x.get("partNumber") or "").strip() for x in items),
        "supplier_missing": sum(not str(x.get("supplier") or "").strip() for x in items),
        "reference_missing": sum(not str(x.get("link") or "").strip() for x in items),
        "price_missing": sum(price(x.get("unitPrice")) is None for x in items),
    }


def export_pdf(doc, destination, options=None):
    """Landscape A4 academic report with cover, category BOM and appendices."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    PageBreak, LongTable, TableStyle)
    from bom_reports import _thai_font
    bom_core.ensure_doc(doc)
    m=metadata(doc,options)
    stats=bom_core.metrics(doc)
    categories=category_stats(doc["items"])
    items=sorted_items(doc)
    quality=report_quality(items)
    font=_thai_font()
    navy=colors.HexColor(NAVY)
    line=colors.HexColor(LINE)
    page=landscape(A4)
    width=page[0]-64
    body=ParagraphStyle("body",fontName=font,fontSize=10,leading=15,
                        textColor=colors.HexColor("#23394D"),wordWrap="CJK",
                        splitLongWords=True)
    small=ParagraphStyle("small",parent=body,fontSize=9,leading=13)
    label=ParagraphStyle("label",parent=body,fontSize=9.5,leading=14,
                         textColor=colors.HexColor(GREY))
    title=ParagraphStyle("title",parent=body,fontSize=21,leading=31,
                         textColor=navy)
    section=ParagraphStyle("section",parent=body,fontSize=15,leading=24,
                           textColor=navy)
    white=ParagraphStyle("white",parent=body,fontSize=9,leading=13,
                         textColor=colors.white,alignment=TA_CENTER)
    centered=ParagraphStyle("centered",parent=body,alignment=TA_CENTER)
    numeric=ParagraphStyle("numeric",parent=body,alignment=TA_RIGHT)
    def P(text,sty=body):
        return Paragraph(escape(str(text if text is not None else "—")).replace("\n","<br/>"),sty)
    def TABLE(headings, rows, widths, category_col=None):
        """Formal table with a clear repeated column header on every page."""
        numeric_cols={i for i,h in enumerate(headings)
                      if any(word in h.casefold() for word in
                             ("จำนวน","ราคา","รวม","ยอด","ไม่มีราคา"))}
        center_cols={i for i,h in enumerate(headings)
                     if h.strip().casefold() in ("id","bom id","ลำดับ","สถานะ")}
        data=[[P(h,white) for h in headings]]
        body_rows=rows or [["ยังไม่มีข้อมูล"]+[""]*(len(headings)-1)]
        data += [[P(value, numeric if col in numeric_cols else
                    centered if col in center_cols else body)
                  for col,value in enumerate(row)] for row in body_rows]
        t=LongTable(data,colWidths=widths,repeatRows=1,hAlign="LEFT",splitByRow=1)
        commands=[
            ("BACKGROUND",(0,0),(-1,0),navy),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),
             [colors.white,colors.HexColor(ROW_ALT)]),
            ("BOX",(0,0),(-1,-1),.65,line),
            ("INNERGRID",(0,0),(-1,-1),.35,line),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),6),
            ("RIGHTPADDING",(0,0),(-1,-1),6),
            ("TOPPADDING",(0,0),(-1,-1),5),
            ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ]
        if category_col is not None and rows:
            # Use the same subtle blue for all engineering categories.
            # Section titles and table borders provide the hierarchy.
            fills={category: colors.HexColor(CATEGORY_FILL)
                   for category in ("เครื่องกล", "ไฟฟ้ากำลัง",
                                    "อิเล็กทรอนิกส์/ควบคุม", "อื่น ๆ")}
            previous=None
            for row_index,row in enumerate(rows,1):
                category=str(row[category_col])
                commands.append(("BACKGROUND",(category_col,row_index),
                                 (category_col,row_index),fills.get(category,colors.white)))
                if category != previous:
                    commands.append(("LINEABOVE",(0,row_index),(-1,row_index),1.1,navy))
                    previous=category
        t.setStyle(TableStyle(commands))
        return t
    # PDF style 1: a clear document cover with a solid navy title panel.
    # This is deliberately a different composition from the Excel workbook.
    # Academic cover: white paper, dark ink, one muted-blue accent.
    # Large solid-color blocks are avoided so the report prints cleanly in B/W.
    cover_kicker=ParagraphStyle("cover_kicker",parent=body,fontSize=9,
        leading=14,textColor=colors.HexColor(BLUE))
    cover_title=ParagraphStyle("cover_title",parent=body,fontSize=22,
        leading=31,textColor=navy)
    cover_subtitle=ParagraphStyle("cover_subtitle",parent=body,fontSize=10,
        leading=16,textColor=colors.HexColor(GREY))
    cover=LongTable([
        [P("ENGINEERING DESIGN DOCUMENT",cover_kicker)],
        [P("รายงานรายการวัสดุและอุปกรณ์",cover_title)],
        [P("BILL OF MATERIALS (BOM)  |  CRANE VEHICLE",cover_subtitle)],
    ],colWidths=[width],hAlign="LEFT")
    cover.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),0.65,colors.HexColor(LINE)),
        ("LINEBEFORE",(0,0),(0,-1),4,colors.HexColor(BLUE)),
        ("LINEBELOW",(0,0),(-1,0),0.6,colors.HexColor(LINE)),
        ("LINEBELOW",(0,-1),(-1,-1),2.2,colors.HexColor(BLUE)),
        ("LEFTPADDING",(0,0),(-1,-1),18),
        ("RIGHTPADDING",(0,0),(-1,-1),18),
        ("TOPPADDING",(0,0),(-1,0),14),
        ("BOTTOMPADDING",(0,0),(-1,0),6),
        ("TOPPADDING",(0,1),(-1,1),5),
        ("BOTTOMPADDING",(0,1),(-1,1),5),
        ("TOPPADDING",(0,2),(-1,2),4),
        ("BOTTOMPADDING",(0,2),(-1,2),15),
    ]))
    story=[cover,Spacer(1,18),
           P("DOCUMENT CONTROL / ข้อมูลควบคุมเอกสาร",section),
           Spacer(1,8)]
    rows=[
        ["โครงการ",m["project"]],
        ["ผู้จัดทำ",m["author"]],
        ["สถาบัน / หน่วยงาน",m["institution"]],
        ["ผู้ตรวจสอบ / อาจารย์ที่ปรึกษา",m["advisor"]],
        ["เลขที่เอกสาร",m["document_no"]],
        ["Revision / วันที่",f'{m["revision"]}  /  {m["date"]}'],
        ["สถานะเอกสาร", "DRAFT / ใช้ประกอบรายงานการออกแบบ ไม่ใช่เอกสารอนุมัติการผลิต"],
        ["รูปแบบอ้างอิง", "ประยุกต์แนวทาง Parts List ของ ISO 7573; ไม่ใช่การรับรองมาตรฐาน"],
    ]
    meta=LongTable([[P(a,label),P(b)] for a,b in rows],colWidths=[150,width-150])
    meta.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1),colors.HexColor(PALE)),
        ("BACKGROUND",(1,0),(1,-1),colors.white),
        ("LINEBELOW",(0,0),(-1,-1),.45,line),
        ("LINEAFTER",(0,0),(0,-1),.6,line),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),12),
        ("RIGHTPADDING",(0,0),(-1,-1),12),
    ]))
    story += [meta,Spacer(1,18),P("สรุปข้อมูลและงบประมาณ",section),Spacer(1,7)]
    story.append(TABLE(["จำนวนรายการ","มีราคาแล้ว","ยังไม่มีราคา","ยอดรวมที่ทราบราคา (บาท)"],[
        [stats["items"],stats["priced"],stats["missing"],
         f'{stats["known_cost"]:,.2f}']],
        [width*.20,width*.20,width*.20,width*.40]))
    story += [Spacer(1,9),P(
        "หมายเหตุ: ราคาไม่ทราบจะแสดงเป็น — ไม่ถือว่าราคาเท่ากับศูนย์ "
        "ยอดรวมยังไม่รวมรายการที่ไม่มีราคา รวมทั้งค่าขนส่ง ภาษี และค่าแรงที่ยังไม่บันทึก",label),
        PageBreak(),P("ตรวจความครบถ้วนและสรุปตามหมวดวิศวกรรม",section),Spacer(1,6),
        P("ตรวจข้อมูลที่ยังขาดก่อนนำรายการไปจัดซื้อหรือใช้เป็นเอกสารอ้างอิง",label),
        Spacer(1,5),
        TABLE(["ไม่มี Part No.","ยังไม่ระบุผู้ขาย","ไม่มีแหล่งอ้างอิง","ยังไม่ทราบราคา"],
              [[quality["part_number_missing"],quality["supplier_missing"],
                quality["reference_missing"],quality["price_missing"]]],
              [width*.25,width*.25,width*.25,width*.25]),
        Spacer(1,14),P("รายการแยกตามระบบวิศวกรรม / CATEGORY DEFINITIONS",section),Spacer(1,6)]
    category_definitions = {
        "เครื่องกล": "โครงรถ โครงสร้าง ล้อ เครน และตะกร้า",
        "ไฟฟ้ากำลัง": "แบตเตอรี่ มอเตอร์ VESC/ไดรเวอร์ ฟิวส์ คอนแทคเตอร์ สายกำลัง และ DC-DC",
        "อิเล็กทรอนิกส์/ควบคุม": "ESP32 เซนเซอร์ CAN รีโมต RC จอ และวงจรสัญญาณ/ควบคุม",
        "อื่น ๆ": "รายการที่ยังไม่จัดเข้าหมวดหลัก",
    }
    story.append(TABLE(
       ["หมวดหลัก","ขอบเขตของหมวด","รายการ","ไม่มีราคา","ยอดรวมที่ทราบ (บาท)"],
       [[c,category_definitions.get(c,""),n,missing,f"{amount:,.2f}"]
        for c,n,missing,amount in categories],
       [width*.21,width*.35,width*.12,width*.12,width*.20]))
    story.append(PageBreak())
    story += [
        P("ทะเบียนรายการวัสดุและอุปกรณ์ / MASTER BOM REGISTER", section),
        P("รายการทั้งหมดเรียงตามหมวดหลัก • ตารางหลักแสดงเฉพาะข้อมูลสำคัญเพื่อให้อ่านง่าย "
          "รายละเอียด Part Number และสเปกอยู่ในภาคผนวก", label),
        Spacer(1, 8),
    ]
    # Separate tables by engineering discipline instead of making users scan
    # a mixed, deeply-columned register. Every table repeats its column header.
    row_number = 1
    for category_index, (category, count, _missing, subtotal) in enumerate(categories):
        if category_index:
            story.append(PageBreak())
        category_items = [item for item in items
                          if bom_categories.normalize_category(item.get("category")) == category]
        master_rows = []
        for item in category_items:
            unitprice = price(item.get("unitPrice"))
            qty = price(item.get("qty")) or 0
            master_rows.append([
                row_number, item.get("id"), item.get("name", ""),
                f'{item.get("qty", "")} {item.get("unit") or ""}'.strip(),
                "—" if unitprice is None else f"{unitprice:,.2f}",
                "—" if unitprice is None else f"{qty * unitprice:,.2f}",
                item.get("status") or "—",
            ])
            row_number += 1
        story.append(P(f"หมวดหลัก: {category}  |  {count} รายการ", section))
        story.append(Spacer(1, 4))
        # Category is repeated on every row as well as in the section heading,
        # so a page break never leaves a reader guessing which group is shown.
        categorized_rows = [[category] + row for row in master_rows]
        story.append(TABLE(
            ["หมวดหลัก", "ลำดับ", "BOM ID", "อุปกรณ์ / รุ่น", "จำนวน / หน่วย",
             "ราคา/หน่วย (บาท)", "รวม (บาท)", "สถานะ"],
            categorized_rows, [90, 36, 56, 245, 75, 90, 90, width - 682],
            category_col=0))
        story.append(Spacer(1, 3))
        story.append(P(
            f"รวมหมวด {category}: {subtotal:,.2f} บาท "
            "(รวมเฉพาะรายการที่ทราบราคา)", label))
        story.append(Spacer(1, 12))
    story += [
        Spacer(1, 4),
        P("หมายเหตุ: BOM ID ใช้อ้างอิงรายการภายในโครงการ • Part No. เป็นรหัสจากผู้ผลิต "
          "เมื่อมีข้อมูล • ช่องราคา — หมายถึงยังไม่ทราบราคา ไม่ใช่ศูนย์บาท", label),
        PageBreak(),
    ]
    story += [P("ภาคผนวก ก. สเปกและแหล่งอ้างอิงอุปกรณ์",section),
              P("Part Number (ถ้ามี) เป็นรหัสผู้ผลิต ส่วน BOM ID เป็นรหัสรายการในโครงการ "
                "• ไฟฟ้ากำลัง: แบตเตอรี่ มอเตอร์ ฟิวส์ คอนแทคเตอร์ และสายจ่ายกำลัง • อิเล็กทรอนิกส์/ควบคุม: ESP32, เซนเซอร์, CAN และวงจรสัญญาณ",label),
              Spacer(1,8)]
    story.append(TABLE(["BOM ID","ชื่ออุปกรณ์ / รุ่น","สเปก / รายละเอียดที่บันทึก",
                        "ผู้ขาย / แหล่งอ้างอิง"],[
        [item.get("id"),item.get("name"),item.get("spec"),
         ("ผู้ขาย: "+str(item.get("supplier") or "ยังไม่ระบุ")+"\n"+
          "ที่มา: "+str(item.get("link") or "ยังไม่ระบุ"))]
        for item in items],[46,201,260,width-507]))
    story.append(PageBreak())
    story += [P("ภาคผนวก ข. ตารางการเดินสาย (Wiring Schedule)",section),
              P("ข้อมูลเบื้องต้น ต้องตรวจสอบแรงดัน กระแส ฟิวส์ และ pinout ก่อนต่อวงจรจริง",label),
              Spacer(1,9)]
    story.append(TABLE(["ID","ต้นทาง","ปลายทาง","สัญญาณ / แรงดัน",
                        "ชนิดสาย","การป้องกัน","สถานะ"],[
        [w.get("id"),w.get("from"),w.get("to"),
         f'{w.get("signal","")}\n{w.get("voltage","")}',
         w.get("cable"),w.get("protection"),w.get("status")]
        for w in doc.get("wiring",[])],[38,135,135,115,105,115,width-643]))
    story.append(PageBreak())
    story += [P("ภาคผนวก ค. รายการจัดซื้อ (Purchasing)",section),Spacer(1,9)]
    story.append(TABLE(["ID","BOM ID","รายการ","ผู้ขาย","จำนวน","รวม (บาท)","สถานะ"],[
        [o.get("id"),o.get("itemId"),o.get("description"),o.get("supplier"),
         o.get("qty"),"—" if price(o.get("unitPrice")) is None
         else f'{(price(o.get("qty")) or 0)*price(o.get("unitPrice")):,.2f}',
         o.get("status")] for o in doc.get("purchases",[])],
        [38,50,228,140,60,113,width-629]))
    story += [Spacer(1,15),P(
        "เอกสารจัดทำจากข้อมูล BOM ณ วันที่ส่งออก ใช้เพื่อประกอบรายงานออกแบบ "
        "ไม่ใช่ใบสั่งซื้อหรือเอกสารที่ผ่านการอนุมัติ",label)]

    # Structural-steel cut list is part of the same shared engineering document.
    # Estimated stock bars are length-only lower bounds, not an optimized cut plan.
    steel_rows = doc.get("steel_members", [])
    steel_totals = bom_steel.summarize(steel_rows)
    story += [
        PageBreak(),
        P("ภาคผนวก ง. รายการตัดเหล็กและวัสดุโครงสร้าง / STEEL CUT LIST", section),
        P("สรุปจำนวนชิ้นและความยาวแยกตามชนิดหน้าตัด ขนาด และความยาวท่อนมาตรฐาน", label),
        Spacer(1, 8),
        TABLE(
            ["วัสดุ / เกรด", "ชนิดหน้าตัด", "ขนาดหน้าตัด", "จำนวนชิ้น",
             "ความยาวรวม (m)", "ท่อนมาตรฐาน (m)", "จำนวนท่อน (ประมาณ)"],
            [[g.get("material", bom_steel.DEFAULT_MATERIAL), g["profile"], g["size"],
              g["pieces"], bom_steel.format_length(g["total_length_m"]),
              f'{g["stock_length_m"]:g}', g["estimated_stock_bars"]]
             for g in steel_totals["groups"]],
            [width*.13, width*.14, width*.14, width*.08,
             width*.15, width*.16, width*.20]),
        Spacer(1, 8),
        P(f'รวมจำนวนชิ้น: {steel_totals["total_pieces"]:,}  |  '
          f'ความยาวรวม: {bom_steel.format_length(steel_totals["total_length_m"])} m  |  '
          f'ท่อนมาตรฐานที่ประมาณ: {steel_totals["estimated_stock_bars"]:,} ท่อน', label),
        Spacer(1, 12),
        P("รายละเอียดชิ้นส่วนสำหรับถอดปริมาณเหล็ก", section),
        Spacer(1, 6),
        TABLE(
            ["ID", "ตำแหน่ง / ชิ้นส่วน", "วัสดุ / เกรด", "ชนิดหน้าตัด",
             "ขนาดหน้าตัด", "จำนวน", "ยาว/ชิ้น (mm)", "รวม (m)",
             "ท่อนมาตรฐาน (m)", "หมายเหตุ"],
            [[r.get("id"), r.get("member"),
              bom_steel.normalize_member(r).get("material", bom_steel.DEFAULT_MATERIAL),
              r.get("profile"), r.get("size"), r.get("qty"), r.get("length_mm"),
              bom_steel.format_length(bom_steel.total_length_m(r)),
              f'{float(r.get("stock_length_m") or 6):g}', r.get("notes")]
             for r in steel_rows],
            [width*.04, width*.13, width*.11, width*.10, width*.10,
             width*.05, width*.08, width*.08, width*.08, width*.23]),
        Spacer(1, 8),
        P("ข้อจำกัดการประมาณ: จำนวนท่อนมาตรฐานคำนวณจากความยาวรวมเท่านั้น "
          "ยังไม่หัก kerf เศษตัด ระยะซ้อน/ต่อ และข้อจำกัดการจัดวางชิ้นตัด "
          "ต้องตรวจแผนตัดจริงก่อนสั่งซื้อเหล็ก", label),
    ]

    # Combined mass roll-up: only manually supplied equipment weights and
    # steel weights with a complete reference measurement are counted.
    mass = bom_steel_bom.summarize_bom_and_steel(doc)
    equipment_rows = []
    for item in sorted_items(doc):
        qty = price(item.get("qty")) or 0
        unit_weight = price(item.get("unitWeightKg"))
        line_weight = qty * unit_weight if unit_weight is not None else None
        equipment_rows.append([
            item.get("id"), item.get("name"),
            f'{qty:g} {item.get("unit") or ""}'.strip(),
            "—" if unit_weight is None else f"{unit_weight:,.3f}",
            "—" if line_weight is None else f"{line_weight:,.3f}",
        ])
    story += [
        PageBreak(),
        P("ภาคผนวก จ. สรุปน้ำหนักอุปกรณ์และโครงสร้าง / TOTAL MASS ROLL-UP", section),
        P("น้ำหนักอุปกรณ์กรอกเองต่อ 1 หน่วย • น้ำหนักเหล็กคำนวณจากความยาวและน้ำหนักอ้างอิงที่กรอกไว้", label),
        Spacer(1, 8),
        TABLE(["น้ำหนักอุปกรณ์ที่ทราบ (kg)", "น้ำหนักโครงเหล็กที่ทราบ (kg)",
               "น้ำหนักรวมที่ทราบ (kg)"], [[
            f'{mass["equipment_known_weight_kg"]:,.3f}' if mass["equipment_weighted_items"] else "—",
            f'{mass["steel_known_weight_kg"]:,.3f}' if mass["steel_known_weight_kg"] else "—",
            f'{mass["combined_known_weight_kg"]:,.3f}' if
            (mass["equipment_weighted_items"] or mass["steel_known_weight_kg"]) else "—",
        ]], [width/3, width/3, width/3]),
        Spacer(1, 7),
        P(f'อุปกรณ์ยังไม่กรอกน้ำหนัก {mass["equipment_missing_weight_count"]} รายการ '
          f'({mass["equipment_missing_weight_qty"]:g} หน่วย) • '
          f'โครงเหล็กยังไม่ทราบน้ำหนัก {bom_steel.format_length(mass["steel_unknown_weight_length_m"])} m. '
          + ("กรอกน้ำหนักครบตามรายการที่บันทึก" if mass["combined_weight_complete"]
             else "น้ำหนักรวมเป็นเฉพาะส่วนที่ทราบ ยังไม่ใช่น้ำหนักจริงครบทุกชิ้น"), label),
        Spacer(1, 12),
        P("ตารางน้ำหนักอุปกรณ์จาก BOM", section), Spacer(1, 5),
        TABLE(["BOM ID", "อุปกรณ์ / รุ่น", "จำนวน / หน่วย",
               "น้ำหนัก/หน่วย (kg)", "น้ำหนักรวม (kg)"],
              equipment_rows,
              [width*.09, width*.39, width*.16, width*.18, width*.18]),
        Spacer(1, 12),
        P("ตารางน้ำหนักโครงสร้างเหล็ก", section), Spacer(1, 5),
        TABLE(["ชิ้นส่วน", "ขนาดหน้าตัด", "จำนวน", "ความยาวรวม (m)",
               "น้ำหนักที่ทราบ (kg)", "ยังไม่ทราบน้ำหนัก (m)"],
              [[g.get("profile"), g.get("size"), g["pieces"],
                bom_steel.format_length(g["total_length_m"]),
                bom_steel.format_length(g["known_weight_kg"], 3),
                bom_steel.format_length(g["unknown_weight_length_m"])]
               for g in mass["steel_groups"]],
              [width*.18, width*.19, width*.10, width*.17, width*.18, width*.18]),
        Spacer(1, 8),
        P("ข้อควรระวัง: หากมีรายการโครงเหล็กเดียวกันถูกใส่เป็นน้ำหนักอุปกรณ์ใน BOM ด้วย "
          "และอยู่ใน Steel Cut List ด้วย จะถูกนับซ้ำ ต้องเว้นน้ำหนัก BOM ของรายการซ้ำหรือไม่รวมรายการนั้น "
          "น้ำหนักที่ยังไม่กรอกจะไม่ถูกเดาและไม่ถูกรวมในผลรวม", label),
    ]

    # Dedicated sign-off page: leave actual signature/date spaces for a printed
    # academic submission. Names come from report options; no approval is implied.
    story += [
        PageBreak(),
        P("การจัดทำและตรวจสอบเอกสาร / PREPARED & REVIEWED",section),
        P("ลงนามหลังจากตรวจสอบรายการอุปกรณ์ จำนวน ราคาอ้างอิง และความครบถ้วนแล้ว",label),
        Spacer(1,14),
    ]
    signoff = LongTable([
        [P("ผู้จัดทำ / PREPARED BY",white),
         P("ผู้ตรวจสอบ / REVIEWED BY",white)],
        [P("ชื่อ-สกุล: "+m["author"]),
         P("ชื่อ-สกุล: "+m["advisor"])],
        [P("ลายมือชื่อ: ........................................................"),
         P("ลายมือชื่อ: ........................................................")],
        [P("วันที่: ........../........../.........."),
         P("วันที่: ........../........../..........")],
    ], colWidths=[width*.5,width*.5], hAlign="LEFT")
    signoff.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),navy),
        ("BACKGROUND",(0,1),(-1,-1),colors.HexColor(PALE)),
        ("BOX",(0,0),(-1,-1),.65,line),
        ("INNERGRID",(0,0),(-1,-1),.4,line),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),13),
        ("RIGHTPADDING",(0,0),(-1,-1),13),
        ("TOPPADDING",(0,0),(-1,-1),14),
        ("BOTTOMPADDING",(0,0),(-1,-1),14),
    ]))
    story += [
        signoff, Spacer(1,18),
        P("สถานะเอกสาร: DRAFT • หน้าลงนามนี้เป็นช่องสำหรับตรวจทานในรายงานการศึกษา "
          "ไม่ใช่การรับรองความปลอดภัยหรือการอนุมัติให้ผลิต",label),
    ]
    template=SimpleDocTemplate(str(destination),pagesize=page,
        leftMargin=32,rightMargin=32,topMargin=60,bottomMargin=46,
        title="Engineering Bill of Materials",author=m["author"],
        subject=m["project"])
    def decoration(canvas,page_doc):
        canvas.saveState()
        # Print-friendly running header: white paper, a fine steel-blue rule,
        # and restrained dark text instead of a full-width dark banner.
        canvas.setStrokeColor(colors.HexColor(BLUE))
        canvas.setLineWidth(1.1 if page_doc.page == 1 else 0.8)
        canvas.line(32,page[1]-25,page[0]-32,page[1]-25)
        if page_doc.page > 1:
            canvas.setFillColor(navy)
            canvas.setFont(font,9)
            canvas.drawString(32,page[1]-20,
                             "ENGINEERING BOM  /  DRAFT")
            canvas.setFillColor(colors.HexColor(GREY))
            canvas.setFont(font,8)
            canvas.drawRightString(page[0]-32,page[1]-20,
                                   m["document_no"][:44])
        canvas.setStrokeColor(line)
        canvas.setLineWidth(0.6)
        canvas.line(32,34,page[0]-32,34)
        canvas.setFillColor(colors.HexColor(GREY))
        canvas.setFont(font,8)
        canvas.drawString(32,21,
            f'Rev. {m["revision"]}  |  {m["date"]}  |  รายงานประกอบการออกแบบ')
        canvas.drawRightString(page[0]-32,21,f"หน้า {page_doc.page}")
        canvas.restoreState()
    template.build(story,onFirstPage=decoration,onLaterPages=decoration)


def export_excel(doc,destination,options=None):
    """Print-ready workbook with Summary, BOM, Specification, Wiring and Purchasing."""
    import xlsxwriter
    bom_core.ensure_doc(doc)
    m=metadata(doc,options)
    stats=bom_core.metrics(doc)
    items=sorted_items(doc)
    categories=category_stats(items)
    quality=report_quality(items)
    wb=xlsxwriter.Workbook(str(destination))
    wb.set_properties({"title":"Engineering Bill of Materials / BOM",
                       "author":m["author"],"subject":m["project"],
                       "comments":"Unknown prices are intentionally blank."})
    def fmt(**kwargs):
        return wb.add_format({"font_name":EXCEL_FONT,"font_size":14,
                              "font_color":"#21384E","valign":"vcenter",**kwargs})
    # Excel style 2: deep teal worksheet bands and mist-grey rows, retained as
    # a distinct formal workbook design. Use the Thai academic font TH Sarabun New.
    # PDF uses the same preferred Thai font with its separate navy-blue design.
    title=fmt(bold=True,font_size=22,font_color="white",bg_color=EXCEL_NAVY,
              valign="vcenter",bottom=4,bottom_color=EXCEL_BLUE)
    subtitle=fmt(font_size=13,font_color=EXCEL_GREY,bg_color=EXCEL_PALE,
                 valign="vcenter")
    bar=fmt(bold=True,font_color="white",bg_color=EXCEL_BLUE,font_size=15,
            bottom=2,bottom_color=EXCEL_NAVY)
    head=fmt(bold=True,font_color="white",bg_color=EXCEL_NAVY,
             align="center",text_wrap=True,font_size=13,border=1,border_color=EXCEL_BLUE,
             valign="vcenter")
    normal=fmt(text_wrap=True,border=1,border_color=EXCEL_LINE)
    alternate=fmt(text_wrap=True,bg_color=EXCEL_ROW_ALT,border=1,border_color=EXCEL_LINE)
    # Keep category styling consistent with the PDF and the agreed prototype:
    # navy table headers, pale-blue category bands, dark navy labels.
    category_colors={
        "เครื่องกล":(EXCEL_ROW_ALT,EXCEL_CATEGORY_FILL,EXCEL_NAVY),
        "ไฟฟ้ากำลัง":(EXCEL_ROW_ALT,EXCEL_CATEGORY_FILL,EXCEL_NAVY),
        "อิเล็กทรอนิกส์/ควบคุม":(EXCEL_ROW_ALT,EXCEL_CATEGORY_FILL,EXCEL_NAVY),
        "อื่น ๆ":(EXCEL_ROW_ALT,EXCEL_CATEGORY_FILL,EXCEL_NAVY),
    }
    category_formats={
        cat:fmt(bold=True,bg_color=palette[1],font_color=palette[2],
                border=1,border_color=EXCEL_LINE)
        for cat,palette in category_colors.items()
    }
    category_row_formats={
        cat:fmt(bg_color=palette[0],text_wrap=True,border=1,border_color=EXCEL_LINE)
        for cat,palette in category_colors.items()
    }
    category_start_formats={
        cat:fmt(bg_color=palette[0],text_wrap=True,border=1,border_color=EXCEL_LINE,
                top=2,top_color=EXCEL_NAVY)
        for cat,palette in category_colors.items()
    }
    category_number_formats={
        cat:fmt(bg_color=palette[0],num_format="#,##0.##",align="center",
                border=1,border_color=EXCEL_LINE)
        for cat,palette in category_colors.items()
    }
    category_money_formats={
        cat:fmt(bg_color=palette[0],num_format="#,##0.00;[Red](#,##0.00)",
                align="right",border=1,border_color=EXCEL_LINE)
        for cat,palette in category_colors.items()
    }
    category_start_number_formats={
        cat:fmt(bg_color=palette[0],num_format="#,##0.##",align="center",
                border=1,border_color=EXCEL_LINE,top=2,top_color=EXCEL_NAVY)
        for cat,palette in category_colors.items()
    }
    category_start_money_formats={
        cat:fmt(bg_color=palette[0],num_format="#,##0.00;[Red](#,##0.00)",
                align="right",border=1,border_color=EXCEL_LINE,top=2,top_color=EXCEL_NAVY)
        for cat,palette in category_colors.items()
    }
    label=fmt(bold=True,font_color=EXCEL_NAVY)
    total_fmt=fmt(bold=True,bg_color=EXCEL_PALE,font_color=EXCEL_NAVY,
                  border=1,border_color=EXCEL_LINE)
    number=fmt(num_format="#,##0.##",align="center",border=1,border_color=EXCEL_LINE)
    money=fmt(num_format="#,##0.00;[Red](#,##0.00)",align="right",
              border=1,border_color=EXCEL_LINE)
    total_money=fmt(bold=True,bg_color=EXCEL_PALE,font_color=EXCEL_NAVY,
                    num_format="#,##0.00;[Red](#,##0.00)",align="right",
                    border=1,border_color=EXCEL_LINE)
    notice=fmt(font_color="#805000",bg_color="#FFF8E8",text_wrap=True)
    def sheet(name,widths,headers=None,wide=False):
        w=wb.add_worksheet(name)
        w.hide_gridlines(2)
        w.set_tab_color(EXCEL_BLUE if name in ("BOM","Summary") else EXCEL_NAVY)
        w.set_landscape();w.set_paper(8 if wide else 9)
        w.fit_to_pages(1,0);w.center_horizontally()
        w.set_margins(.34,.34,.55,.55)
        w.set_header("&C&BENGINEERING BOM | "+m["document_no"])
        w.set_footer("&LRev. "+m["revision"]+" | Engineering Draft&RPage &P / &N")
        for n,width in enumerate(widths):w.set_column(n,n,width)
        w.merge_range(0,0,1,len(widths)-1,
                      "รายงานรายการวัสดุและอุปกรณ์ / ENGINEERING BOM",title)
        w.merge_range(2,0,2,len(widths)-1,
            "โครงการ: "+m["project"]+"  |  No: "+m["document_no"]+
            "  |  Rev: "+m["revision"]+"  |  "+m["date"],subtitle)
        w.set_row(0,25);w.set_row(1,20);w.set_row(2,24)
        if headers:
            section_titles={
                "BOM":"ทะเบียนรายการวัสดุและอุปกรณ์ / MASTER BOM REGISTER",
                "Specification":"รายละเอียดสเปกทางเทคนิค / TECHNICAL SPECIFICATION",
                "Wiring":"ตารางการเดินสาย / WIRING SCHEDULE",
                "Purchasing":"ทะเบียนรายการจัดซื้อ / PURCHASING REGISTER",
                "References":"แหล่งอ้างอิงและการตรวจสอบย้อนกลับ / REFERENCES",
                "Completeness":"ตรวจความครบถ้วนของข้อมูล / COMPLETENESS REVIEW",
                "Steel Summary":"สรุปปริมาณเหล็กตามหน้าตัด / STEEL SUMMARY",
                "Steel Cut List":"รายการตัดเหล็ก / STEEL CUT LIST",
            }
            w.merge_range(4,0,4,len(widths)-1,
                          section_titles.get(name,name+" / ENGINEERING DOCUMENT"),bar)
            for i,h in enumerate(headers):w.write(6,i,h,head)
            w.set_row(6,35);w.freeze_panes(7,2);w.repeat_rows(0,6)
        return w
    count=len(items)
    start=8;end=7+count
    startend=lambda letter: "BOM!$"+letter+"$"+str(start)+":$"+letter+"$"+str(max(start,end))
    summary=sheet("Summary",[34,24,25,24])
    summary.merge_range("A5:D5","ข้อมูลเอกสาร / Document information",bar)
    for row,(key,value) in enumerate([
        ("โครงการ",m["project"]),("ผู้จัดทำ",m["author"]),
        ("สถาบัน / หน่วยงาน",m["institution"]),
        ("ผู้ตรวจสอบ / อาจารย์ที่ปรึกษา",m["advisor"]),
        ("เลขที่เอกสาร",m["document_no"]),("Revision",m["revision"]),
        ("วันที่จัดทำ",m["date"])],7):
        summary.write(row,0,key,label)
        summary.merge_range(row,1,row,3,value,normal)
        summary.set_row(row,26)
    summary.merge_range("A16:D16","สรุปงบประมาณ / Budget",bar)
    for row,key in enumerate(["รายการอุปกรณ์ทั้งหมด","รายการที่มีราคา",
                              "รายการที่ยังไม่มีราคา","ยอดรวมที่ทราบ (บาท)",
                              "ยอดจัดซื้อที่บันทึก (บาท)"],17):
        summary.write(row,0,key,label)
    summary.write_formula(17,1,"=COUNTA("+startend("D")+")",number,count)
    summary.write_formula(18,1,"=COUNT("+startend("G")+")",number,stats["priced"])
    summary.write_formula(19,1,"=B18-B19",number,stats["missing"])
    summary.write_formula(20,1,"=SUM("+startend("H")+")",money,stats["known_cost"])
    summary.write_formula(21,1,"=SUM(Purchasing!G8:G5000)",
                          money,stats["purchase_total"])
    summary.merge_range("A24:D24","ภาพรวมตามหมวดวิศวกรรม",bar)
    for c,h in enumerate(["หมวดระบบ","จำนวน","ไม่มีราคา","ยอดที่ทราบ (บาท)"]):
        summary.write(25,c,h,head)
    for row,(cat,total,missing,amount) in enumerate(categories,26):
        erow=row+1
        summary.write_string(row,0,cat,normal)
        summary.write_formula(row,1,"=COUNTIF("+startend("B")+",A"+str(erow)+")",
                              number,total)
        summary.write_formula(row,2,"=COUNTIFS("+startend("B")+",A"+str(erow)+
                              ","+startend("G")+',""'+")",number,missing)
        summary.write_formula(row,3,"=SUMIF("+startend("B")+",A"+str(erow)+
                              ","+startend("H")+")",money,amount)
        summary.set_row(row,28)
    summary.merge_range("A30:D30","ขอบเขตของหมวดหลัก / CATEGORY DEFINITIONS",bar)
    for row,(cat,description) in enumerate([
        ("เครื่องกล","โครงรถ โครงสร้าง ล้อ เครน และตะกร้า"),
        ("ไฟฟ้ากำลัง","แบตเตอรี่ มอเตอร์ VESC/ไดรเวอร์ ฟิวส์ คอนแทคเตอร์ สายกำลัง และ DC-DC"),
        ("อิเล็กทรอนิกส์/ควบคุม","ESP32 เซนเซอร์ CAN รีโมต RC จอ และวงจรสัญญาณ/ควบคุม"),
    ],30):
        summary.write(row,0,cat,category_formats[cat])
        summary.merge_range(row,1,row,3,description,normal)
        summary.set_row(row,34)
    summary.merge_range("A36:D38",
        "หมายเหตุ: รายการที่ไม่ทราบราคาไม่ถูกถือว่ามีราคา 0 บาท "
        "และยอดรวมยังไม่ใช่งบประมาณสุดท้าย "
        "ไม่รวมค่าจัดส่ง ภาษี และค่าแรงที่ไม่ได้บันทึก",notice)
    summary.print_area("A1:D38")
    bom=sheet("BOM",[11,27,25,46,11,11,20,21,26],
        ["BOM ID","ระบบ / หมวด","Part Number","อุปกรณ์ / รุ่น","จำนวน","หน่วย",
         "ราคา/หน่วย (บาท)","รวม (บาท)","สถานะ"],True)
    details=sheet("Specification",[12,29,50,68,27,36,54],
        ["ID","หมวด","อุปกรณ์ / รุ่น","สเปกทางเทคนิค",
         "Part No.","ร้านค้า / ผู้ขาย","ข้อมูลเพิ่มเติม / ลิงก์"],True)
    previous_category = None
    for idx,item in enumerate(items):
        row=7+idx;erow=row+1
        category=bom_categories.normalize_category(item.get("category"))
        qty=price(item.get("qty")) or 0
        amount=price(item.get("unitPrice"))
        entries=[item.get("id"),category,item.get("partNumber"),item.get("name"),
                 qty,item.get("unit"),amount,None,item.get("status")]
        first_in_group = category != previous_category
        row_fmt = category_start_formats.get(category, normal) if first_in_group else category_row_formats.get(category, normal)
        num_fmt = category_start_number_formats.get(category, number) if first_in_group else category_number_formats.get(category, number)
        money_fmt = category_start_money_formats.get(category, money) if first_in_group else category_money_formats.get(category, money)
        for col,val in enumerate(entries):
            if col==7:
                bom.write_formula(row,col,'=IF(G'+str(erow)+'="","",E'+
                                  str(erow)+'*G'+str(erow)+')',money_fmt,
                                  "" if amount is None else float(qty*amount))
            elif val is None:
                bom.write_blank(row,col,None,row_fmt)
            elif col in (4,6):
                bom.write_number(row,col,float(val),num_fmt if col==4 else money_fmt)
            else:
                bom.write_string(row,col,str(val),
                                 category_formats.get(category,row_fmt) if col==1 else row_fmt)
        bom.set_row(row,43)
        previous_category = category
        extra="\n".join(str(item.get(k)) for k in ("link","connection","notes")
                        if item.get(k))
        values=[item.get("id"),category,item.get("name"),item.get("spec"),
                item.get("partNumber"),item.get("supplier"),extra]
        for col,val in enumerate(values):
            details.write_string(row,col,"" if val is None else str(val),
                                 alternate if idx%2 else normal)
        details.set_row(row,61)
    if count:
        bom.autofilter(6,0,6+count,8)
        details.autofilter(6,0,6+count,6)
        bom.conditional_format(7,6,6+count,6,
                               {"type":"blanks","format":notice})
    total_row=7+count
    bom.merge_range(total_row,0,total_row,6,
                    "รวมมูลค่ารายการที่ทราบราคา (บาท)",total_fmt)
    last_data_excel_row=count+7
    total_formula=("=SUM(H8:H"+str(last_data_excel_row)+")") if count else "=0"
    bom.write_formula(total_row,7,total_formula,
                      total_money,float(stats["known_cost"]))
    bom.set_row(total_row,30)
    bom.print_area(0,0,total_row,8)
    details.print_area(0,0,max(7,6+count),6)
    wiring=sheet("Wiring",[11,32,32,22,20,28,37,25],
        ["ID","ต้นทาง","ปลายทาง","สัญญาณ","แรงดัน",
         "ชนิดสาย","การป้องกัน","สถานะ"],True)
    for n,item in enumerate(doc.get("wiring",[]),7):
        for col,key in enumerate(("id","from","to","signal","voltage",
                                  "cable","protection","status")):
            wiring.write_string(n,col,str(item.get(key) or ""),
                                alternate if n%2 else normal)
        wiring.set_row(n,43)
    wiring.print_area(0,0,max(7,6+len(doc.get("wiring",[]))),7)
    buy=sheet("Purchasing",[11,13,46,34,14,21,21,23],
        ["ID","BOM ID","รายการ","ผู้ขาย","จำนวน",
         "ราคา/หน่วย (บาท)","รวม (บาท)","สถานะ"],True)
    orders=doc.get("purchases",[])
    for n,item in enumerate(orders,7):
        r=n+1;qty=price(item.get("qty")) or 0;amount=price(item.get("unitPrice"))
        for col,key in enumerate(("id","itemId","description","supplier",
                                  "qty","unitPrice","lineTotal","status")):
            if col==6:
                buy.write_formula(n,col,'=IF(F'+str(r)+'="","",E'+str(r)+'*F'+
                                  str(r)+')',money,
                                  None if amount is None else float(qty*amount))
            elif col in (4,5):
                val=qty if col==4 else amount
                if val is None:buy.write_blank(n,col,None,normal)
                else:buy.write_number(n,col,float(val),number if col==4 else money)
            else:buy.write_string(n,col,str(item.get(key) or ""),normal)
        buy.set_row(n,43)
    buy.print_area(0,0,max(7,6+len(orders)),7)
    notes=sheet("Notes",[35,98])
    notes.merge_range("A5:B5","คำแนะนำการใช้รายงาน",bar)
    for row,(labeltext,text) in enumerate([
        ("ประเภทเอกสาร","เอกสารประกอบรายงานออกแบบ ไม่ใช่เอกสารที่อนุมัติให้ผลิต"),
        ("ราคาที่ยังไม่มี","ช่องราคาว่าง = ยังไม่ทราบ ไม่ใช่ศูนย์บาท"),
        ("สูตรคำนวณ","ยอดรวมในชีต BOM และ Purchasing ใช้สูตร Excel"),
        ("การพิมพ์","Summary หน้า A4 แนวนอน, BOM/Specification/Wiring/Purchasing หน้า A3 แนวนอน"),
        ("ความปลอดภัยไฟฟ้า","Wiring เป็นข้อมูลเบื้องต้น ต้องตรวจคู่มือผู้ผลิตก่อนติดตั้งจริง"),
        ("แหล่งข้อมูล","ใช้ข้อมูล ณ วันที่ส่งออก ไม่รวม GitHub Token")
    ],7):
        notes.write(row,0,labeltext,label);notes.write(row,1,text,normal)
        notes.set_row(row,40)
    notes.print_area("A1:B15")

    # Traceability is distinct from a formal manufacturer P/N.
    # Existing project IDs remain unchanged, and missing values remain blank.
    sources=sheet("References",[12,44,25,29,52,36,56],
        ["BOM ID","อุปกรณ์ / รุ่น","Part Number","ผู้ขาย","ลิงก์แหล่งข้อมูล",
         "สถานะการเลือก","หมายเหตุการอ้างอิง"],True)
    sourcefmt=fmt(font_color=EXCEL_BLUE,underline=True,text_wrap=True,
                   border=1,border_color=EXCEL_LINE)
    for idx,item in enumerate(items):
        row=7+idx
        values=[item.get("id"),item.get("name"),item.get("partNumber"),
                item.get("supplier"),item.get("link"),
                item.get("status"),item.get("notes")]
        for col,val in enumerate(values):
            value=str(val or "")
            if col==4 and value.lower().startswith(("https://","http://")):
                try:
                    sources.write_url(row,col,value,sourcefmt,"เปิดแหล่งอ้างอิง")
                except (ValueError,TypeError):
                    sources.write_string(row,col,value,alternate if idx%2 else normal)
            else:
                sources.write_string(row,col,value,alternate if idx%2 else normal)
        sources.set_row(row,54)
    if count:
        sources.autofilter(6,0,6+count,6)
    sources.print_area(0,0,max(7,6+count),6)

    review=sheet("Completeness",[37,28,29,36])
    review.merge_range("A5:D5","รายการข้อมูลที่ต้องตรวจสอบก่อนนำไปจัดซื้อ",bar)
    review.merge_range("A7:D7","DATA QUALITY CHECK / Preliminary design",bar)
    indicators=[
        ("Part Number ไม่ระบุ",quality["part_number_missing"]),
        ("ผู้ขายไม่ระบุ",quality["supplier_missing"]),
        ("ลิงก์อ้างอิงไม่ระบุ",quality["reference_missing"]),
        ("ราคาที่ยังไม่ทราบ",quality["price_missing"]),
    ]
    for row,(name,value) in enumerate(indicators,8):
        review.write(row,0,name,label)
        review.write_number(row,1,value,number)
    review.merge_range("A16:D16","หมายเหตุสำคัญ",bar)
    review.merge_range("A18:D20",
        "รหัส BOM ภายในโครงการ ไม่เท่ากับ Part Number จากผู้ผลิต "
        "ไม่ควรเติม Part Number หรือผู้ขายจากการคาดเดา "
        "เอกสารนี้เป็น DRAFT ไม่ใช่ใบสั่งซื้อหรือเอกสารอนุมัติการผลิต",notice)
    review.merge_range("A23:D23","แนวทางการจัดรายการอุปกรณ์ที่ใช้อ้างอิง",bar)
    review.write_string("A25","ISO 7573:2008 / Technical product documentation - Parts lists",normal)
    review.write_url("B25","https://www.iso.org/standard/43883.html",sourcefmt,"หน้าเอกสาร ISO")
    review.write_string("A26","SOLIDWORKS / BOM columns and part properties",normal)
    review.write_url("B26","https://help.solidworks.com/2021/English/SolidWorks/sldworks/c_Bill_of_Materials_-_Custom_Properties.htm",sourcefmt,"ดูแหล่งอ้างอิง")
    review.write_string("A27","OpenBOM / Parts list data fields and cost context",normal)
    review.write_url("B27","https://www.openbom.com/blog/bill-of-materials-types-formats-and-examples",sourcefmt,"ดูแหล่งอ้างอิง")
    review.print_area("A1:D30")

    summary.merge_range("A41:D41","ตรวจสอบความครบถ้วนของข้อมูล (DRAFT)",bar)
    for row,(name,value) in enumerate(indicators,42):
        summary.write(row,0,name,label)
        summary.write_number(row,1,value,number)
    summary.print_area("A1:D49")

    # Separate one-page sign-off sheet so the Excel report can be printed and
    # signed without disturbing the budget and category-summary worksheet.
    approval = sheet("Approval", [30, 24, 30, 24])
    approval.merge_range("A5:D5",
                         "การจัดทำและตรวจสอบเอกสาร / DOCUMENT SIGN-OFF", bar)
    approval.merge_range("A7:B7", "ผู้จัดทำ / PREPARED BY", bar)
    approval.merge_range("C7:D7", "ผู้ตรวจสอบ / REVIEWED BY", bar)
    approval.merge_range("A8:B8", "ชื่อ-สกุล: " + m["author"], normal)
    approval.merge_range("C8:D8", "ชื่อ-สกุล: " + m["advisor"], normal)
    approval.merge_range("A10:B10", "ลายมือชื่อ / Signature", label)
    approval.merge_range("C10:D10", "ลายมือชื่อ / Signature", label)
    signature_line = fmt(bottom=1, bottom_color=EXCEL_GREY)
    approval.merge_range("A11:B11", " ", signature_line)
    approval.merge_range("C11:D11", " ", signature_line)
    approval.merge_range("A12:B12", "วันที่ / Date: ........../........../..........", normal)
    approval.merge_range("C12:D12", "วันที่ / Date: ........../........../..........", normal)
    approval.set_row(6, 28)
    approval.set_row(7, 34)
    approval.set_row(9, 24)
    approval.set_row(10, 42)
    approval.set_row(11, 30)
    approval.merge_range(
        "A15:D17",
        "สถานะเอกสาร: DRAFT • ใช้ประกอบรายงานการศึกษา "
        "การลงนามเป็นการตรวจทานเอกสาร ไม่ใช่การรับรองความปลอดภัยหรืออนุมัติให้ผลิต",
        notice)
    approval.set_row(14, 28)
    approval.set_row(15, 28)
    approval.set_row(16, 28)
    approval.print_area("A1:D17")
    approval.fit_to_pages(1, 1)
    # Structural-steel takeoff: separate group summary and editable cut list.
    steel_rows = doc.get("steel_members", [])
    steel_totals = bom_steel.summarize(steel_rows)
    steel_summary = sheet("Steel Summary", [23, 28, 29, 16, 22, 22, 24],
        ["วัสดุ / เกรด", "ชนิดหน้าตัด", "ขนาดหน้าตัด", "จำนวนชิ้น",
         "ความยาวรวม (m)", "ท่อนมาตรฐาน (m)", "จำนวนท่อน (ประมาณ)"], True)
    steel_cut = sheet("Steel Cut List", [10, 32, 23, 25, 28, 14, 20, 18, 22, 44],
        ["ID", "ตำแหน่ง / ชิ้นส่วน", "วัสดุ / เกรด", "ชนิดหน้าตัด",
         "ขนาดหน้าตัด", "จำนวนชิ้น", "ยาว/ชิ้น (mm)", "รวมความยาว (m)",
         "ท่อนมาตรฐาน (m)", "หมายเหตุ"], True)
    steel_summary.merge_range(
        5, 0, 5, 6,
        "จำนวนท่อนเป็นค่าประมาณจากความยาวรวม ไม่หัก kerf/เศษตัด/ระยะซ้อน "
        "และไม่ใช่ cutting plan", notice)
    steel_summary.set_row(5, 32)
    steel_length_fmt = fmt(num_format="#,##0.000", align="right",
                           border=1, border_color=EXCEL_LINE)
    for idx, raw in enumerate(steel_rows):
        item = bom_steel.normalize_member(raw)
        row = 7 + idx
        excel_row = row + 1
        values = [item.get("id"), item.get("member"), item.get("material"),
                  item.get("profile"), item.get("size"), item.get("qty"),
                  item.get("length_mm"), None, item.get("stock_length_m"), item.get("notes")]
        rowfmt = alternate if idx % 2 else normal
        for col, value in enumerate(values):
            if col == 7:
                length = float(bom_steel.total_length_m(item))
                steel_cut.write_formula(
                    row, col, f"=F{excel_row}*G{excel_row}/1000",
                    steel_length_fmt, length)
            elif col in (5, 6, 8):
                if value is None:
                    steel_cut.write_blank(row, col, None, rowfmt)
                else:
                    steel_cut.write_number(row, col, float(value),
                                           number if col == 4 else steel_length_fmt)
            else:
                steel_cut.write_string(row, col, "" if value is None else str(value), rowfmt)
        steel_cut.set_row(row, 43)
    cut_last_excel = max(8, 7 + len(steel_rows))
    if steel_rows:
        steel_cut.autofilter(6, 0, 6 + len(steel_rows), 9)
    steel_cut.print_area(0, 0, max(7, 6 + len(steel_rows)), 9)

    if steel_totals["groups"]:
        for idx, group in enumerate(steel_totals["groups"]):
            row = 7 + idx
            excel_row = row + 1
            steel_summary.write_string(row, 0, group["material"], alternate if idx % 2 else normal)
            steel_summary.write_string(row, 1, group["profile"], alternate if idx % 2 else normal)
            steel_summary.write_string(row, 2, group["size"], alternate if idx % 2 else normal)
            cut_qty = "'Steel Cut List'!$F$8:$F$" + str(cut_last_excel)
            cut_material = "'Steel Cut List'!$C$8:$C$" + str(cut_last_excel)
            cut_profile = "'Steel Cut List'!$D$8:$D$" + str(cut_last_excel)
            cut_size = "'Steel Cut List'!$E$8:$E$" + str(cut_last_excel)
            cut_length = "'Steel Cut List'!$H$8:$H$" + str(cut_last_excel)
            cut_stock = "'Steel Cut List'!$I$8:$I$" + str(cut_last_excel)
            steel_summary.write_formula(
                row, 3,
                f"=SUMIFS({cut_qty},{cut_material},A{excel_row},"
                f"{cut_profile},B{excel_row},{cut_size},C{excel_row},"
                f"{cut_stock},F{excel_row})",
                number, group["pieces"])
            steel_summary.write_formula(
                row, 4,
                f"=SUMIFS({cut_length},{cut_material},A{excel_row},"
                f"{cut_profile},B{excel_row},{cut_size},C{excel_row},"
                f"{cut_stock},F{excel_row})",
                steel_length_fmt, float(group["total_length_m"]))
            steel_summary.write_number(row, 5, group["stock_length_m"], steel_length_fmt)
            steel_summary.write_formula(
                row, 6, f"=IF(F{excel_row}>0,ROUNDUP(E{excel_row}/F{excel_row},0),0)",
                number, group["estimated_stock_bars"])
            steel_summary.set_row(row, 32)
        steel_summary.autofilter(6, 0, 6 + len(steel_totals["groups"]), 6)
        steel_total_row = 7 + len(steel_totals["groups"])
        steel_summary.merge_range(steel_total_row, 0, steel_total_row, 2,
                                  "รวมทั้งหมด", total_fmt)
        last_summary_excel = 7 + len(steel_totals["groups"])
        steel_summary.write_formula(
            steel_total_row, 3, f"=SUM(D8:D{last_summary_excel})",
            number, steel_totals["total_pieces"])
        steel_summary.write_formula(
            steel_total_row, 4, f"=SUM(E8:E{last_summary_excel})",
            steel_length_fmt, float(steel_totals["total_length_m"]))
        steel_summary.write_blank(steel_total_row, 5, None, total_fmt)
        steel_summary.write_formula(
            steel_total_row, 6, f"=SUM(G8:G{last_summary_excel})",
            number, steel_totals["estimated_stock_bars"])
        steel_summary.set_row(steel_total_row, 32)
        steel_summary.print_area(0, 0, steel_total_row, 6)
    else:
        steel_summary.write_string(7, 0, "ยังไม่มีข้อมูลโครงสร้างเหล็ก", normal)
        steel_summary.print_area("A1:G8")

    wb.close()
