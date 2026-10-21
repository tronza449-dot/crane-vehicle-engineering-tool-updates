"""Formal engineering BOM PDF / Excel, independent of legacy exports.

Design A: formal black-and-white engineering report for university submission.
Only figures with known prices contribute to budget totals. Blank means unknown.
All report cover metadata is editable and does not imply institutional approval.
"""
from datetime import datetime
import math
import unicodedata
from urllib.parse import urlsplit
import bom_core
import bom_categories
import bom_steel
import bom_steel_bom

# Design A palette, shared by PDF and Excel: black ink on white paper with
# light-grey header and group bands so printed copies stay crisp in B/W.
INK = "#000000"
HEAD_FILL = "#E6E6E6"
BAND_FILL = "#F2F2F2"
NOTE_INK = "#404040"
MISSING_FILL = "#EDEDED"
# Excel renders Thai itself; Tahoma is present on every Windows PC.
EXCEL_FONT = "Tahoma"

CATEGORY_DEFINITIONS = {
    "เครื่องกล": "โครงรถ โครงสร้าง ล้อ เครน และตะกร้า",
    "ไฟฟ้ากำลัง": "แบตเตอรี่ มอเตอร์ VESC/ไดรเวอร์ ฟิวส์ คอนแทคเตอร์ สายกำลัง และ DC-DC",
    "อิเล็กทรอนิกส์/ควบคุม": "ESP32 เซนเซอร์ CAN รีโมต RC จอ และวงจรสัญญาณ/ควบคุม",
    "อื่น ๆ": "รายการที่ยังไม่จัดเข้าหมวดหลัก",
}


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


def _quantity_text(value):
    value = price(value) or 0
    return f"{value:,.0f}" if value == value.to_integral_value() else f"{value:,.2f}"


def _money_text(value):
    return "–" if value is None else f"{value:,.2f}"


def _numbered_canvas(decorate):
    """Canvas class that prints 'หน้า x / y' by buffering pages until save."""
    from reportlab.pdfgen.canvas import Canvas

    class NumberedCanvas(Canvas):
        def __init__(self, *args, **kwargs):
            Canvas.__init__(self, *args, **kwargs)
            self._pages = []

        def showPage(self):
            self._pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._pages)
            for state in self._pages:
                self.__dict__.update(state)
                decorate(self, self._pageNumber, total)
                Canvas.showPage(self)
            Canvas.save(self)

    return NumberedCanvas


def export_pdf(doc, destination, options=None):
    """A4 formal black-and-white engineering report (design A).

    Portrait pages hold document control, summaries, the master BOM and the
    sign-off; wide appendices use landscape pages. Every table repeats its
    header row on each page, and Thai text is shaped and wrapped by word.
    """
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, LongTable,
                                    NextPageTemplate, PageBreak, PageTemplate,
                                    Spacer, TableStyle)
    import bom_thai_text
    bom_core.ensure_doc(doc)
    m=metadata(doc,options)
    stats=bom_core.metrics(doc)
    items=sorted_items(doc)
    categories=category_stats(items)
    quality=report_quality(items)
    regular, bold = bom_thai_text.register_fonts()
    ink=colors.HexColor(INK)
    head_fill=colors.HexColor(HEAD_FILL)
    band_fill=colors.HexColor(BAND_FILL)
    portrait_size=A4
    landscape_size=landscape(A4)
    margin=50
    width=portrait_size[0]-2*margin
    wide=landscape_size[0]-2*margin

    body=ParagraphStyle("a-body",fontName=regular,fontSize=9,leading=13.5,textColor=ink)
    strong=ParagraphStyle("a-strong",parent=body,fontName=bold)
    numeric=ParagraphStyle("a-numeric",parent=body,alignment=TA_RIGHT)
    numeric_strong=ParagraphStyle("a-numeric-strong",parent=strong,alignment=TA_RIGHT)
    centered=ParagraphStyle("a-centered",parent=body,alignment=TA_CENTER)
    heading=ParagraphStyle("a-heading",parent=strong,alignment=TA_CENTER)
    caption=ParagraphStyle("a-caption",parent=strong,fontSize=10,leading=15,
                           spaceBefore=6,spaceAfter=5)
    section=ParagraphStyle("a-section",parent=strong,fontSize=12,leading=18,spaceAfter=4)
    note=ParagraphStyle("a-note",parent=body,fontSize=8,leading=12,
                        textColor=colors.HexColor(NOTE_INK))
    title=ParagraphStyle("a-title",parent=strong,fontSize=18,leading=27,alignment=TA_CENTER)
    subtitle=ParagraphStyle("a-subtitle",parent=body,fontSize=10,leading=15,alignment=TA_CENTER)
    kicker=ParagraphStyle("a-kicker",parent=note,alignment=TA_CENTER)

    def P(text,style=body):
        return bom_thai_text.paragraph("—" if text is None else str(text),style)

    def TABLE(headings,rows,widths,numeric_cols=(),center_cols=(),kinds=None):
        """Grid table. kinds maps a row index to ("band",) for a full-width
        group label or ("total", last_label_col, grand) for a total row."""
        kinds=dict(kinds or {})
        if not rows:
            rows=[["ยังไม่มีข้อมูล"]+[""]*(len(headings)-1)]
            kinds={0:("empty",)}
        data=[[P(h,heading) for h in headings]]
        commands=[
            ("GRID",(0,0),(-1,-1),0.4,ink),
            ("LINEBELOW",(0,0),(-1,0),1.0,ink),
            ("BACKGROUND",(0,0),(-1,0),head_fill),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),4),
            ("RIGHTPADDING",(0,0),(-1,-1),4),
            ("TOPPADDING",(0,0),(-1,-1),3),
            ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ]
        for index,row in enumerate(rows):
            r=index+1
            kind=kinds.get(index,("row",))
            if kind[0] in ("band","empty"):
                data.append([P(row[0],strong if kind[0]=="band" else body)]+
                            [""]*(len(headings)-1))
                commands.append(("SPAN",(0,r),(-1,r)))
                if kind[0]=="band":
                    commands.append(("BACKGROUND",(0,r),(-1,r),band_fill))
            elif kind[0]=="total":
                last_label=kind[1]
                data.append([P(row[0],numeric_strong)]+[""]*last_label+
                            [P(v,numeric_strong) if v not in (None,"") else ""
                             for v in row[last_label+1:]])
                commands.append(("SPAN",(0,r),(last_label,r)))
                if kind[2]:
                    commands += [("LINEABOVE",(0,r),(-1,r),1.2,ink),
                                 ("LINEBELOW",(0,r),(-1,r),1.2,ink)]
            else:
                data.append([P(value,numeric if col in numeric_cols else
                               centered if col in center_cols else body)
                             for col,value in enumerate(row)])
        table=LongTable(data,colWidths=widths,repeatRows=1,hAlign="LEFT")
        table.setStyle(TableStyle(commands))
        return table

    def numbered(caption_text,table,note_text=None):
        parts=[P(caption_text,caption),table]
        if note_text:
            parts += [Spacer(1,3),P(note_text,note)]
        return parts

    # ── Page 1: title, document control and summaries (portrait) ──
    story=[P("ENGINEERING DESIGN DOCUMENT",kicker),
           P("รายงานรายการวัสดุและอุปกรณ์",title),
           P("BILL OF MATERIALS (BOM)",subtitle),Spacer(1,12),
           P("ข้อมูลควบคุมเอกสาร / DOCUMENT CONTROL",section)]
    control_rows=[
        ("โครงการ",m["project"],"เลขที่เอกสาร",m["document_no"]),
        ("ผู้จัดทำ",m["author"],"วันที่จัดทำ",m["date"]),
        ("ผู้ตรวจสอบ / อาจารย์ที่ปรึกษา",m["advisor"],"ฉบับแก้ไข",m["revision"]),
    ]
    spanning_rows=[
        ("สถาบัน / หน่วยงาน",m["institution"]),
        ("สถานะเอกสาร","DRAFT / ใช้ประกอบรายงานการออกแบบ ไม่ใช่เอกสารอนุมัติการผลิต"),
        ("รูปแบบอ้างอิง","ประยุกต์แนวทาง Parts List ของ ISO 7573; ไม่ใช่การรับรองมาตรฐาน"),
    ]
    control=LongTable(
        [[P(a,strong),P(b),P(c,strong),P(d)] for a,b,c,d in control_rows]+
        [[P(a,strong),P(b),"",""] for a,b in spanning_rows],
        colWidths=[150,width-150-72-90,72,90],hAlign="LEFT")
    control_style=[("GRID",(0,0),(-1,-1),0.5,ink),
                   ("BACKGROUND",(0,0),(0,-1),band_fill),
                   ("BACKGROUND",(2,0),(2,len(control_rows)-1),band_fill),
                   ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                   ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),4)]
    for r in range(len(control_rows),len(control_rows)+len(spanning_rows)):
        control_style.append(("SPAN",(1,r),(3,r)))
    control.setStyle(TableStyle(control_style))
    story += [control,Spacer(1,8)]

    story += numbered(
        "ตารางที่ 1  สรุปข้อมูลและงบประมาณ",
        TABLE(["จำนวนรายการ","มีราคาแล้ว","ยังไม่มีราคา","ยอดรวมที่ทราบราคา (บาท)"],
              [[stats["items"],stats["priced"],stats["missing"],
                _money_text(stats["known_cost"])]],
              [width*.2,width*.2,width*.2,width*.4],numeric_cols=(3,),center_cols=(0,1,2)),
        "หมายเหตุ: ราคาที่ยังไม่ทราบแสดงเป็น “–” ไม่ถือว่าเท่ากับศูนย์ ยอดรวมยังไม่รวมรายการ"
        "ที่ไม่มีราคา ค่าขนส่ง ภาษี และค่าแรงที่ยังไม่บันทึก")

    known_total=sum(x[3] for x in categories)
    category_rows=[[i,c,CATEGORY_DEFINITIONS.get(c,""),n,missing,_money_text(amount),
                    "–" if not known_total else f"{amount/known_total*100:,.1f}%"]
                   for i,(c,n,missing,amount) in enumerate(categories,1)]
    category_rows.append(["รวม","","",stats["items"],stats["missing"],
                          _money_text(known_total),"100.0%" if known_total else "–"])
    story += numbered(
        "ตารางที่ 2  สรุปค่าใช้จ่ายตามหมวดหลัก / CATEGORY DEFINITIONS",
        TABLE(["ลำดับ","หมวดหลัก","ขอบเขตของหมวด","รายการ","ไม่มีราคา",
               "ยอดรวม (บาท)","สัดส่วน"],category_rows,
              [34,92,width-34-92-46-50-72-48,46,50,72,48],
              numeric_cols=(5,6),center_cols=(0,3,4),
              kinds={len(category_rows)-1:("total",2,True)}))
    story += numbered(
        "ตารางที่ 3  ความครบถ้วนของข้อมูล",
        TABLE(["ไม่มี Part No.","ยังไม่ระบุผู้ขาย","ไม่มีแหล่งอ้างอิง","ยังไม่ทราบราคา"],
              [[quality["part_number_missing"],quality["supplier_missing"],
                quality["reference_missing"],quality["price_missing"]]],
              [width/4]*4,center_cols=(0,1,2,3)),
        "ตรวจข้อมูลที่ยังขาดก่อนนำรายการไปจัดซื้อหรือใช้เป็นเอกสารอ้างอิง")

    # ── Master BOM register: one continuous table grouped by category ──
    bom_rows=[]
    kinds={}
    number=1
    for category,count,_missing,subtotal in categories:
        kinds[len(bom_rows)]=("band",)
        bom_rows.append([f"หมวดหลัก: {category}  ({count} รายการ)"])
        for item in items:
            if bom_categories.normalize_category(item.get("category")) != category:
                continue
            unit_price=price(item.get("unitPrice"))
            qty=price(item.get("qty")) or 0
            bom_rows.append([number,item.get("id"),item.get("name",""),
                             _quantity_text(qty),item.get("unit") or "–",
                             _money_text(unit_price),
                             _money_text(None if unit_price is None else qty*unit_price)])
            number+=1
        kinds[len(bom_rows)]=("total",5,False)
        bom_rows.append([f"รวมหมวด {category}","","","","","",_money_text(subtotal)])
    kinds[len(bom_rows)]=("total",5,True)
    bom_rows.append(["รวมทั้งสิ้น (เฉพาะรายการที่ทราบราคา)","","","","","",
                     _money_text(stats["known_cost"])])
    story += [PageBreak()]
    story += numbered(
        "ตารางที่ 4  ทะเบียนรายการวัสดุและอุปกรณ์ / MASTER BOM REGISTER",
        TABLE(["ลำดับ","BOM ID","รายการ / รุ่น","จำนวน","หน่วย",
               "ราคา/หน่วย (บาท)","ราคารวม (บาท)"],bom_rows,
              [34,44,width-34-44-42-40-68-74,42,40,68,74],
              numeric_cols=(3,5,6),center_cols=(0,1,4),kinds=kinds),
        "หมายเหตุ: BOM ID เป็นรหัสรายการภายในโครงการ • Part No. สเปก ผู้ขาย และสถานะ"
        "อยู่ในภาคผนวก ก • “–” ในช่องราคา หมายถึงยังไม่ทราบราคา ไม่ใช่ศูนย์บาท")

    # ── Appendices on landscape pages ──
    story += [NextPageTemplate("landscape"),PageBreak(),
              P("ภาคผนวก ก  สเปกและแหล่งอ้างอิงอุปกรณ์",section),
              P("Part Number (ถ้ามี) เป็นรหัสผู้ผลิต ส่วน BOM ID เป็นรหัสรายการในโครงการ",note),
              Spacer(1,6)]
    def source_text(link):
        # Print the domain only; the Excel workbook keeps the full clickable URL.
        link=str(link or "").strip()
        if link.lower().startswith(("https://","http://")):
            return urlsplit(link).netloc or link
        return link or "ยังไม่ระบุ"

    story.append(TABLE(
        ["BOM ID","อุปกรณ์ / รุ่น","Part No.","สเปก / รายละเอียด","สถานะการเลือก",
         "ผู้ขาย / แหล่งอ้างอิง"],
        [[item.get("id"),item.get("name"),item.get("partNumber") or "–",
          item.get("spec") or "–",item.get("status") or "–",
          "ผู้ขาย: "+str(item.get("supplier") or "ยังไม่ระบุ")+"\n"+
          "ที่มา: "+source_text(item.get("link"))] for item in items],
        [46,160,72,236,108,wide-622],center_cols=(0,)))

    story += [PageBreak(),P("ภาคผนวก ข  ตารางการเดินสาย (Wiring Schedule)",section),
              P("ข้อมูลเบื้องต้น ต้องตรวจสอบแรงดัน กระแส ฟิวส์ และ pinout ก่อนต่อวงจรจริง",note),
              Spacer(1,6)]
    story.append(TABLE(
        ["ID","ต้นทาง","ปลายทาง","สัญญาณ / แรงดัน","ชนิดสาย","การป้องกัน","สถานะ"],
        [[w.get("id"),w.get("from"),w.get("to"),
          f'{w.get("signal","")}\n{w.get("voltage","")}'.strip(),
          w.get("cable"),w.get("protection"),w.get("status")]
         for w in doc.get("wiring",[])],
        [36,150,150,110,100,110,wide-656],center_cols=(0,)))

    purchase_rows=[]
    for order in doc.get("purchases",[]):
        unit_price=price(order.get("unitPrice"))
        qty=price(order.get("qty")) or 0
        purchase_rows.append([order.get("id"),order.get("itemId"),order.get("description"),
                              order.get("supplier") or "–",_quantity_text(qty),
                              _money_text(unit_price),
                              _money_text(None if unit_price is None else qty*unit_price),
                              order.get("status")])
    purchase_kinds={}
    if purchase_rows:
        purchase_kinds[len(purchase_rows)]=("total",5,True)
        purchase_rows.append(["รวมยอดจัดซื้อที่ทราบราคา","","","","","",
                              _money_text(stats["purchase_total"]),""])
    story += [Spacer(1,14),P("ภาคผนวก ค  รายการจัดซื้อ (Purchasing)",section),Spacer(1,4),
              TABLE(["ID","BOM ID","รายการ","ผู้ขาย","จำนวน","ราคา/หน่วย (บาท)",
                     "รวม (บาท)","สถานะ"],purchase_rows,
                    [36,50,wide-36-50-130-50-80-84-90,130,50,80,84,90],
                    numeric_cols=(4,5,6),center_cols=(0,1,7),kinds=purchase_kinds),
              Spacer(1,4),
              P("เอกสารจัดทำจากข้อมูล BOM ณ วันที่ส่งออก ใช้เพื่อประกอบรายงานออกแบบ "
                "ไม่ใช่ใบสั่งซื้อหรือเอกสารที่ผ่านการอนุมัติ",note)]

    # Structural-steel cut list is part of the same shared engineering document.
    # Estimated stock bars are length-only lower bounds, not an optimized cut plan.
    steel_rows = doc.get("steel_members", [])
    steel_totals = bom_steel.summarize(steel_rows)
    stock_label = lambda value: "—" if value is None else f"{float(value):g}"

    def mode_text(row):
        return ("กรอกน้ำหนักเอง" if row.get("weight_mode") == bom_steel.WEIGHT_MODE_MANUAL
                else "ตามความยาว")

    steel_summary_rows = [
        [mode_text(g), g.get("material", bom_steel.DEFAULT_MATERIAL), g["profile"], g["size"],
         g["pieces"], ("—" if g.get("weight_mode") == bom_steel.WEIGHT_MODE_MANUAL
                       and not g["total_length_m"] else
                       bom_steel.format_length(g["total_length_m"])),
         stock_label(g.get("stock_length_m")),
         bom_steel.format_length(g["known_weight_kg"], 3),
         g["estimated_stock_bars"]]
        for g in steel_totals["groups"]
    ]

    def steel_detail_values(raw):
        item = bom_steel.normalize_member(raw)
        manual = item.get("weight_mode") == bom_steel.WEIGHT_MODE_MANUAL
        length_display = (
            bom_steel.format_length(bom_steel.total_length_m(item))
            if item.get("length_mm") is not None else "—")
        mass = bom_steel.total_weight_kg(item)
        link = str(item.get("link") or "").strip()
        # Keep a printable domain in the narrow PDF table; the Excel workbook
        # retains the complete clickable URL for procurement follow-up.
        link_display = (urlsplit(link).netloc
                        if link.lower().startswith(("https://", "http://")) else link)
        return [
            item.get("id"), item.get("member"), mode_text(item),
            item.get("material", bom_steel.DEFAULT_MATERIAL), item.get("profile"),
            item.get("size"), item.get("qty"),
            item.get("length_mm") if item.get("length_mm") is not None else "—",
            length_display,
            (bom_steel.format_length(item.get("manual_unit_weight_kg"), 3)
             if manual else "—"),
            ("—" if mass is None else bom_steel.format_length(mass, 3)),
            stock_label(item.get("stock_length_m")), link_display or "—",
            item.get("notes"),
        ]

    steel_reference_rows = []
    for raw in steel_rows:
        link = str(raw.get("link") or "").strip()
        if not link:
            continue
        domain = (urlsplit(link).netloc
                  if link.lower().startswith(("https://", "http://")) else link)
        steel_reference_rows.append([raw.get("id", "—"), raw.get("member", "—"), domain or "—"])

    story += [
        PageBreak(),
        P("ภาคผนวก ง  รายการตัดเหล็กและน้ำหนักชิ้นส่วน / STEEL CUT LIST", section),
        P("โหมดตามความยาวใช้สำหรับเหล็กกล่อง/หน้าตัด • โหมดกรอกน้ำหนักเองใช้กับแผ่นยึด "
          "ขายึด ฐานมอเตอร์ และชิ้นส่วนที่ไม่คิดเป็นความยาวท่อนมาตรฐาน", note),
        Spacer(1, 6),
        TABLE(["วิธีน้ำหนัก", "วัสดุ / เกรด", "ชนิดหน้าตัด", "ขนาดหน้าตัด", "จำนวนชิ้น",
               "ความยาวรวม (m)", "ท่อนมาตรฐาน (m)", "น้ำหนักที่ทราบ (kg)",
               "จำนวนท่อน (ประมาณ)"],
              steel_summary_rows,
              [wide*.105, wide*.12, wide*.12, wide*.12, wide*.07,
               wide*.12, wide*.11, wide*.12, wide*.115],
              numeric_cols=(4, 5, 6, 7, 8)),
        Spacer(1, 4),
        P(f'รวมจำนวนชิ้น: {steel_totals["total_pieces"]:,}  |  '
          f'ความยาวที่ระบุ: {bom_steel.format_length(steel_totals["total_length_m"])} m  |  '
          f'น้ำหนักโครงสร้างที่ทราบ: {bom_steel.format_length(steel_totals["known_weight_kg"], 3)} kg  |  '
          f'ท่อนมาตรฐานที่ประมาณ: {steel_totals["estimated_stock_bars"]:,} ท่อน', note),
        P("รายละเอียดชิ้นส่วนสำหรับถอดปริมาณ", caption),
        TABLE(["ID", "ตำแหน่ง / ชิ้นส่วน", "วิธีน้ำหนัก", "วัสดุ / เกรด", "ชนิดหน้าตัด",
               "ขนาด", "จำนวน", "ยาว/ชิ้น (mm)", "รวม (m)", "น้ำหนัก/ชิ้น (kg)",
               "น้ำหนักรวม (kg)", "ท่อนมาตรฐาน (m)", "ลิงก์สินค้า", "หมายเหตุ"],
              [steel_detail_values(r) for r in steel_rows],
              [wide*.035, wide*.105, wide*.075, wide*.085, wide*.08, wide*.07,
               wide*.055, wide*.06, wide*.055, wide*.07, wide*.07, wide*.065,
               wide*.075, wide*.08],
              numeric_cols=(6, 7, 8, 9, 10, 11), center_cols=(0,)),
        P("แหล่งอ้างอิงสินค้า / PRODUCT REFERENCES", caption),
        TABLE(["ID", "ชิ้นส่วน", "โดเมนสินค้า / แหล่งอ้างอิง"], steel_reference_rows,
              [wide*.08, wide*.30, wide*.62], center_cols=(0,)),
        Spacer(1, 4),
        P("ข้อจำกัดการประมาณ: จำนวนท่อนมาตรฐานคำนวณเฉพาะรายการที่มีความยาวและท่อนมาตรฐาน "
          "ไม่หัก kerf เศษตัด ระยะซ้อน/ต่อ หรือข้อจำกัดการจัดวางชิ้นตัด "
          "น้ำหนักที่กรอกเองจะคูณจำนวนชิ้นโดยตรงและไม่ถูกรวมเป็นความยาวเหล็ก", note),
    ]

    # Combined mass roll-up: only manually supplied equipment weights and
    # steel weights with a complete reference measurement are counted.
    mass = bom_steel_bom.summarize_bom_and_steel(doc)
    equipment_rows = []
    for item in items:
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
        P("ภาคผนวก จ  สรุปน้ำหนักอุปกรณ์และโครงสร้าง / TOTAL MASS ROLL-UP", section),
        P("น้ำหนักอุปกรณ์กรอกเองต่อ 1 หน่วย • โครงสร้างคำนวณได้ทั้งจากความยาว/น้ำหนักอ้างอิง "
          "หรือจากน้ำหนักต่อชิ้นที่ผู้ใช้กรอกเอง", note),
        Spacer(1, 6),
        TABLE(["น้ำหนักอุปกรณ์ที่ทราบ (kg)", "น้ำหนักโครงเหล็กที่ทราบ (kg)",
               "น้ำหนักรวมที่ทราบ (kg)"], [[
            f'{mass["equipment_known_weight_kg"]:,.3f}' if mass["equipment_weighted_items"] else "—",
            f'{mass["steel_known_weight_kg"]:,.3f}' if mass["steel_known_weight_kg"] else "—",
            f'{mass["combined_known_weight_kg"]:,.3f}' if
            (mass["equipment_weighted_items"] or mass["steel_known_weight_kg"]) else "—",
        ]], [wide/3, wide/3, wide/3], numeric_cols=(0, 1, 2)),
        Spacer(1, 4),
        P(f'อุปกรณ์ยังไม่กรอกน้ำหนัก {mass["equipment_missing_weight_count"]} รายการ '
          f'({mass["equipment_missing_weight_qty"]:g} หน่วย) • '
          f'โครงเหล็กยังไม่ทราบน้ำหนัก {bom_steel.format_length(mass["steel_unknown_weight_length_m"])} m • '
          + ("กรอกน้ำหนักครบตามรายการที่บันทึก" if mass["combined_weight_complete"]
             else "น้ำหนักรวมเป็นเฉพาะส่วนที่ทราบ ยังไม่ใช่น้ำหนักจริงครบทุกชิ้น"), note),
        P("ตารางน้ำหนักอุปกรณ์จาก BOM", caption),
        TABLE(["BOM ID", "อุปกรณ์ / รุ่น", "จำนวน / หน่วย",
               "น้ำหนัก/หน่วย (kg)", "น้ำหนักรวม (kg)"],
              equipment_rows,
              [wide*.09, wide*.43, wide*.14, wide*.17, wide*.17],
              numeric_cols=(3, 4), center_cols=(0, 2)),
        P("ตารางน้ำหนักโครงสร้างเหล็กและชิ้นส่วน", caption),
        TABLE(["วิธีน้ำหนัก", "ชิ้นส่วน / หน้าตัด", "ขนาด", "จำนวน", "ความยาวรวม (m)",
               "น้ำหนักที่ทราบ (kg)", "ยังไม่ทราบน้ำหนัก (m)"],
              [[mode_text(g), g.get("profile"), g.get("size"), g["pieces"],
                ("—" if g.get("weight_mode") == bom_steel.WEIGHT_MODE_MANUAL
                 and not g["total_length_m"] else
                 bom_steel.format_length(g["total_length_m"])),
                bom_steel.format_length(g["known_weight_kg"], 3),
                bom_steel.format_length(g["unknown_weight_length_m"])]
               for g in mass["steel_groups"]],
              [wide*.13, wide*.19, wide*.16, wide*.08, wide*.14, wide*.15, wide*.15],
              numeric_cols=(3, 4, 5, 6)),
        Spacer(1, 4),
        P("ข้อควรระวัง: หากรายการโครงเหล็กเดียวกันถูกใส่น้ำหนักทั้งใน BOM และใน Steel Cut List "
          "จะถูกนับซ้ำ น้ำหนักที่ยังไม่กรอกจะไม่ถูกเดาและไม่ถูกรวมในผลรวม", note),
    ]

    # Sign-off page leaves real signature/date space for a printed academic
    # submission. Names come from report options; no approval is implied.
    signoff = LongTable([
        [P("ผู้จัดทำ / PREPARED BY",heading), P("ผู้ตรวจสอบ / REVIEWED BY",heading)],
        [P("ชื่อ-สกุล: "+m["author"]), P("ชื่อ-สกุล: "+m["advisor"])],
        [P("ลายมือชื่อ: ........................................................"),
         P("ลายมือชื่อ: ........................................................")],
        [P("วันที่: ........../........../.........."),
         P("วันที่: ........../........../..........")],
    ], colWidths=[width*.5,width*.5], hAlign="LEFT")
    signoff.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,ink),
        ("BACKGROUND",(0,0),(-1,0),head_fill),
        ("LINEBELOW",(0,0),(-1,0),1.0,ink),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),12),
        ("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,1),(-1,-1),14),
        ("BOTTOMPADDING",(0,1),(-1,-1),14),
    ]))
    story += [
        NextPageTemplate("portrait"),PageBreak(),
        P("การจัดทำและตรวจสอบเอกสาร / PREPARED & REVIEWED",section),
        P("ลงนามหลังจากตรวจสอบรายการอุปกรณ์ จำนวน ราคาอ้างอิง และความครบถ้วนแล้ว",note),
        Spacer(1,12),KeepTogether([signoff]),Spacer(1,14),
        P("สถานะเอกสาร: DRAFT • หน้าลงนามนี้เป็นช่องสำหรับตรวจทานในรายงานการศึกษา "
          "ไม่ใช่การรับรองความปลอดภัยหรือการอนุมัติให้ผลิต",note),
    ]

    def decorate(canvas,number,total):
        page_width,page_height=canvas._pagesize
        canvas.saveState()
        canvas.setFillColor(ink)
        canvas.setStrokeColor(ink)
        canvas.setFont(bold,9)
        bom_thai_text.draw_string(canvas,margin,page_height-34,
                                  "รายงานรายการวัสดุและอุปกรณ์ (Bill of Materials)")
        canvas.setFont(regular,8.5)
        bom_thai_text.draw_string(
            canvas,page_width-margin,page_height-34,
            f'เลขที่เอกสาร {m["document_no"][:40]}  |  ฉบับแก้ไข {m["revision"][:12]}',"right")
        canvas.setLineWidth(0.8)
        canvas.line(margin,page_height-40,page_width-margin,page_height-40)
        canvas.setLineWidth(0.5)
        canvas.line(margin,40,page_width-margin,40)
        bom_thai_text.draw_string(canvas,margin,28,
                                  f'โครงการ: {m["project"][:70]}  |  วันที่จัดทำ {m["date"]}')
        bom_thai_text.draw_string(canvas,page_width-margin,28,
                                  f"หน้า {number} / {total}","right")
        canvas.restoreState()

    def frame(size,name):
        return Frame(margin,50,size[0]-2*margin,size[1]-50-56,id=name,
                     leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)

    template=BaseDocTemplate(
        str(destination),pagesize=portrait_size,
        title="Engineering Bill of Materials",author=m["author"],subject=m["project"],
        pageTemplates=[
            PageTemplate(id="portrait",frames=[frame(portrait_size,"portrait")],
                         pagesize=portrait_size),
            PageTemplate(id="landscape",frames=[frame(landscape_size,"landscape")],
                         pagesize=landscape_size),
        ])
    template.build(story,canvasmaker=_numbered_canvas(decorate))


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
        return wb.add_format({"font_name":EXCEL_FONT,"font_size":10,
                              "font_color":INK,"valign":"vcenter",**kwargs})
    # Design A: black text, thin black grid, light-grey header and group bands.
    # Prints cleanly in black and white on A4.
    title=fmt(bold=True,font_size=14,align="center",bottom=2)
    subtitle=fmt(font_color=NOTE_INK,align="center",text_wrap=True)
    bar=fmt(bold=True,font_size=11,bg_color=BAND_FILL,border=1,border_color=INK)
    head=fmt(bold=True,bg_color=HEAD_FILL,align="center",text_wrap=True,
             border=1,border_color=INK,bottom=2)
    # Wrapped text is centred vertically like the numbers; row heights are
    # estimated per row.
    normal=fmt(text_wrap=True,border=1,border_color=INK)
    alternate=normal
    band=fmt(bold=True,bg_color=BAND_FILL,border=1,border_color=INK)
    label=fmt(bold=True)
    total_fmt=fmt(bold=True,align="right",border=1,border_color=INK)
    # General shows 35 and 2.5 without the trailing "35." of #,##0.##
    number=fmt(num_format="General",align="center",border=1,border_color=INK)
    money=fmt(num_format="#,##0.00;-#,##0.00",align="right",
              border=1,border_color=INK)
    mass_number=fmt(num_format="#,##0.000",align="right",
                    border=1,border_color=INK)
    total_mass=fmt(bold=True,num_format="#,##0.000",align="right",
                   border=1,border_color=INK)
    total_money=fmt(bold=True,num_format="#,##0.00;-#,##0.00",align="right",
                    border=1,border_color=INK)
    grand_label=fmt(bold=True,align="right",border=1,border_color=INK,top=6,bottom=6)
    grand_money=fmt(bold=True,num_format="#,##0.00;-#,##0.00",align="right",
                    border=1,border_color=INK,top=6,bottom=6)
    notice=fmt(italic=True,font_color=NOTE_INK,text_wrap=True,valign="top")
    missing_price=wb.add_format({"bg_color":MISSING_FILL})
    def sheet(name,widths,headers=None,wide=False):
        w=wb.add_worksheet(name)
        w.hide_gridlines(2)
        w.set_paper(9)  # A4; wide registers print landscape
        if wide:
            w.set_landscape()
        w.fit_to_pages(1,0);w.center_horizontally()
        w.set_margins(.4,.4,.6,.6)
        w.set_header("&L&8"+m["project"].replace("&","&&")+
                     "&R&8เลขที่เอกสาร "+m["document_no"].replace("&","&&")+
                     " | ฉบับแก้ไข "+m["revision"].replace("&","&&"))
        w.set_footer("&L&8รายงานรายการวัสดุและอุปกรณ์ (DRAFT)&R&8หน้า &P / &N")
        # Widths were tuned for TH Sarabun 14; Tahoma 10 needs about 72%.
        for n,width in enumerate(widths):w.set_column(n,n,round(width*.72,1))
        w.merge_range(0,0,1,len(widths)-1,
                      "รายงานรายการวัสดุและอุปกรณ์ / ENGINEERING BOM",title)
        w.merge_range(2,0,2,len(widths)-1,
            "โครงการ: "+m["project"]+"  |  เลขที่เอกสาร: "+m["document_no"]+
            "  |  ฉบับแก้ไข: "+m["revision"]+"  |  วันที่จัดทำ: "+m["date"],subtitle)
        # Narrow portrait sheets need two lines for the project subtitle.
        w.set_row(0,18);w.set_row(1,12);w.set_row(2,18 if wide else 30)
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
                "Mass Summary":"สรุปน้ำหนักรวมอุปกรณ์และโครงสร้าง / TOTAL MASS ROLL-UP",
            }
            w.merge_range(4,0,4,len(widths)-1,
                          section_titles.get(name,name+" / ENGINEERING DOCUMENT"),bar)
            for i,h in enumerate(headers):w.write(6,i,h,head)
            # Multi-line Thai/English column titles need room to wrap.
            w.set_row(6,32);w.freeze_panes(7,2);w.repeat_rows(6)
        return w

    def fitted_row_height(values, widths, minimum=18, line_height=14, padding=6):
        """Estimate wrapped Excel row height for mixed Thai/English text."""
        max_lines = 1
        for col, value in enumerate(values):
            if value is None:
                continue
            width = max(5.0, float(widths[col]) if col < len(widths) else 12.0)
            # Conservative: Excel wraps URLs at / and - leaving short lines,
            # and clipped text is worse than a little white space.
            capacity = max(4.0, width * 0.66)
            parts = str(value).splitlines() or [""]
            lines = 0
            for part in parts:
                display_width = sum(
                    0.0 if unicodedata.combining(ch) else
                    2.0 if unicodedata.east_asian_width(ch) in ("F", "W") else 1.0
                    for ch in part)
                lines += max(1, int(math.ceil(display_width / capacity)))
            max_lines = max(max_lines, lines)
        # Stay below Excel's 409 pt row-height limit, while giving long notes
        # enough room instead of forcing them into the old fixed 34–43 pt rows.
        return min(360, max(minimum, max_lines * line_height + padding))

    count=len(items)
    # BOM sheet rows: one band row and one subtotal row per category around
    # the items. Ranges below span all of them; band/subtotal rows leave the
    # category, name and price columns empty, so COUNTIF/SUMIF skip them.
    start=8;end=7+count+2*len(categories)
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
    # SUBTOTAL ignores the per-category SUBTOTAL rows inside the range.
    summary.write_formula(20,1,"=SUBTOTAL(9,"+startend("H")+")",money,stats["known_cost"])
    summary.write_formula(21,1,"=SUBTOTAL(9,Purchasing!G8:G5000)",
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
    for row,cat in enumerate(bom_categories.CATEGORY_ORDER,30):
        description=CATEGORY_DEFINITIONS[cat]
        summary.write(row,0,cat,band)
        summary.merge_range(row,1,row,3,description,normal)
        summary.set_row(row, fitted_row_height([cat, description], [34, 73], minimum=20))
    summary.merge_range("A36:D38",
        "หมายเหตุ: รายการที่ไม่ทราบราคาไม่ถูกถือว่ามีราคา 0 บาท "
        "และยอดรวมยังไม่ใช่งบประมาณสุดท้าย "
        "ไม่รวมค่าจัดส่ง ภาษี และค่าแรงที่ไม่ได้บันทึก",notice)
    summary.print_area("A1:D38")
    bom=sheet("BOM",[11,27,25,46,11,11,20,21,26,19,19],
        ["BOM ID","ระบบ / หมวด","Part Number","อุปกรณ์ / รุ่น","จำนวน","หน่วย",
         "ราคา/หน่วย (บาท)","รวม (บาท)","สถานะ","น้ำหนัก/หน่วย (kg)",
         "น้ำหนักรวม (kg)"],True)
    details=sheet("Specification",[12,29,50,68,27,36,54],
        ["ID","หมวด","อุปกรณ์ / รุ่น","สเปกทางเทคนิค",
         "Part No.","ร้านค้า / ผู้ขาย","ข้อมูลเพิ่มเติม / ลิงก์"],True)
    bom_widths=[11,27,25,46,11,11,20,21,26,19,19]
    row=7
    for category,category_count,_missing,subtotal in categories:
        # Group band: label in column A only, so the importer (which needs a
        # name in column D) and the COUNTIF/SUMIF ranges ignore it.
        bom.merge_range(row,0,row,10,
                        f"หมวดหลัก: {category}  ({category_count} รายการ)",band)
        bom.set_row(row,20)
        row+=1
        first=row
        for item in items:
            if bom_categories.normalize_category(item.get("category")) != category:
                continue
            erow=row+1
            qty=price(item.get("qty")) or 0
            amount=price(item.get("unitPrice"))
            unit_weight=price(item.get("unitWeightKg"))
            entries=[item.get("id"),category,item.get("partNumber"),item.get("name"),
                     qty,item.get("unit"),amount,None,item.get("status"),
                     unit_weight,None]
            for col,val in enumerate(entries):
                if col==7:
                    bom.write_formula(row,col,'=IF(G'+str(erow)+'="","",E'+
                                      str(erow)+'*G'+str(erow)+')',money,
                                      "" if amount is None else float(qty*amount))
                elif col==10:
                    bom.write_formula(row,col,'=IF(J'+str(erow)+'="","",E'+
                                      str(erow)+'*J'+str(erow)+')',mass_number,
                                      "" if unit_weight is None else float(qty*unit_weight))
                elif val is None:
                    bom.write_blank(row,col,None,mass_number if col==9 else
                                    money if col==6 else normal)
                elif col in (4,6,9):
                    bom.write_number(row,col,float(val),
                                     number if col==4 else money if col==6 else mass_number)
                else:
                    bom.write_string(row,col,str(val),normal)
            bom.set_row(row, fitted_row_height(entries, bom_widths, minimum=20))
            row+=1
        bom.merge_range(row,0,row,6,f"รวมหมวด {category}",total_fmt)
        bom.write_formula(row,7,f"=SUBTOTAL(9,H{first+1}:H{row})",total_money,subtotal)
        for col in (8,9,10):
            bom.write_blank(row,col,None,normal)
        bom.set_row(row,20)
        row+=1
    total_row=row
    bom.merge_range(total_row,0,total_row,6,
                    "รวมทั้งสิ้น (เฉพาะรายการที่ทราบราคา)",grand_label)
    total_formula=f"=SUBTOTAL(9,H8:H{total_row})" if count else "=0"
    bom.write_formula(total_row,7,total_formula,
                      grand_money,float(stats["known_cost"]))
    for col in (8,9,10):
        bom.write_blank(total_row,col,None,grand_label)
    bom.set_row(total_row,22)
    bom.write_string(total_row+2,0,
        "หมายเหตุ: ช่องราคาสีเทา = ยังไม่ทราบราคา (ไม่ใช่ 0 บาท) • ราคารวมและยอดรวมคำนวณด้วยสูตร "
        "แก้จำนวนหรือราคาแล้วยอดจะเปลี่ยนเอง",notice)
    if count:
        bom.autofilter(6,0,total_row-1,10)
        # Shade unknown prices on item rows only (column D holds the name).
        bom.conditional_format(7,6,total_row-1,6,
                               {"type":"formula","criteria":'=AND($D8<>"",$G8="")',
                                "format":missing_price})
    bom.print_area(0,0,total_row+2,10)

    for idx,item in enumerate(items):
        row=7+idx
        category=bom_categories.normalize_category(item.get("category"))
        extra="\n".join(str(item.get(k)) for k in ("link","connection","notes")
                        if item.get(k))
        values=[item.get("id"),category,item.get("name"),item.get("spec"),
                item.get("partNumber"),item.get("supplier"),extra]
        for col,val in enumerate(values):
            details.write_string(row,col,"" if val is None else str(val),normal)
        details.set_row(row, fitted_row_height(
            values, [12,29,50,68,27,36,54], minimum=20))
    if count:
        details.autofilter(6,0,6+count,6)
    details.print_area(0,0,max(7,6+count),6)
    wiring=sheet("Wiring",[11,32,32,22,20,28,37,25],
        ["ID","ต้นทาง","ปลายทาง","สัญญาณ","แรงดัน",
         "ชนิดสาย","การป้องกัน","สถานะ"],True)
    for n,item in enumerate(doc.get("wiring",[]),7):
        for col,key in enumerate(("id","from","to","signal","voltage",
                                  "cable","protection","status")):
            wiring.write_string(n,col,str(item.get(key) or ""),
                                alternate if n%2 else normal)
        wiring.set_row(n, fitted_row_height(
            [item.get(k) for k in ("id","from","to","signal","voltage",
                                   "cable","protection","status")],
            [11,32,32,22,20,28,37,25], minimum=20))
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
                # Cached value must be "" (not None) or Excel repairs the sheet.
                buy.write_formula(n,col,'=IF(F'+str(r)+'="","",E'+str(r)+'*F'+
                                  str(r)+')',money,
                                  "" if amount is None else float(qty*amount))
            elif col in (4,5):
                val=qty if col==4 else amount
                if val is None:buy.write_blank(n,col,None,money if col==5 else normal)
                else:buy.write_number(n,col,float(val),number if col==4 else money)
            else:buy.write_string(n,col,str(item.get(key) or ""),normal)
        buy.set_row(n, fitted_row_height(
            [item.get(k) for k in ("id","itemId","description","supplier",
                                   "qty","unitPrice","lineTotal","status")],
            [11,13,46,34,14,21,21,23], minimum=20))
    buy_total=7+len(orders)
    if orders:
        buy.autofilter(6,0,buy_total-1,7)
        buy.merge_range(buy_total,0,buy_total,5,"รวมยอดจัดซื้อที่ทราบราคา (บาท)",grand_label)
        buy.write_formula(buy_total,6,f"=SUBTOTAL(9,G8:G{buy_total})",grand_money,
                          float(stats["purchase_total"]))
        buy.write_blank(buy_total,7,None,grand_label)
    buy.print_area(0,0,max(7,buy_total),7)
    notes=sheet("Notes",[35,98])
    notes.merge_range("A5:B5","คำแนะนำการใช้รายงาน",bar)
    for row,(labeltext,text) in enumerate([
        ("ประเภทเอกสาร","เอกสารประกอบรายงานออกแบบ ไม่ใช่เอกสารที่อนุมัติให้ผลิต"),
        ("ราคาที่ยังไม่มี","ช่องราคาว่าง = ยังไม่ทราบ ไม่ใช่ศูนย์บาท"),
        ("สูตรคำนวณ","ยอดรวมในชีต BOM และ Purchasing ใช้สูตร Excel"),
        ("การพิมพ์","กระดาษ A4 ทุกชีต: Summary/Notes/Completeness/Approval แนวตั้ง, "
                    "ตารางกว้าง (BOM, Specification, Wiring, Purchasing, เหล็ก, น้ำหนัก) แนวนอน"),
        ("ความปลอดภัยไฟฟ้า","Wiring เป็นข้อมูลเบื้องต้น ต้องตรวจคู่มือผู้ผลิตก่อนติดตั้งจริง"),
        ("แหล่งข้อมูล","ใช้ข้อมูล ณ วันที่ส่งออก ไม่รวม GitHub Token")
    ],7):
        notes.write(row,0,labeltext,label);notes.write(row,1,text,normal)
        notes.set_row(row, fitted_row_height([labeltext, text], [35, 98], minimum=20))
    notes.print_area("A1:B15")

    # Traceability is distinct from a formal manufacturer P/N.
    # Existing project IDs remain unchanged, and missing values remain blank.
    sources=sheet("References",[12,44,25,29,52,36,56],
        ["BOM ID","อุปกรณ์ / รุ่น","Part Number","ผู้ขาย","ลิงก์แหล่งข้อมูล",
         "สถานะการเลือก","หมายเหตุการอ้างอิง"],True)
    sourcefmt=fmt(underline=True,text_wrap=True,
                   border=1,border_color=INK)
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
        sources.set_row(row, fitted_row_height(
            values, [12,44,25,29,52,36,56], minimum=20))
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
    signature_line = fmt(bottom=1, bottom_color=INK)
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
    steel_summary = sheet("Steel Summary", [18, 23, 28, 29, 16, 22, 22, 24],
        ["วิธีน้ำหนัก", "วัสดุ / เกรด", "ชนิดหน้าตัด", "ขนาดหน้าตัด", "จำนวนชิ้น",
         "ความยาวรวม (m)", "ท่อนมาตรฐาน (m)", "จำนวนท่อน (ประมาณ)"], True)
    steel_cut = sheet("Steel Cut List",
        [10, 32, 20, 23, 25, 28, 14, 20, 18, 22, 44, 20, 20, 20, 22, 20, 44],
        ["ID", "ตำแหน่ง / ชิ้นส่วน", "วิธีน้ำหนัก", "วัสดุ / เกรด", "ชนิดหน้าตัด",
         "ขนาดหน้าตัด", "จำนวนชิ้น", "ยาว/ชิ้น (mm)", "รวมความยาว (m)",
         "ท่อนมาตรฐาน (m)", "หมายเหตุ", "อ้างอิงยาว (m)", "อ้างอิงหนัก (kg)",
         "น้ำหนัก/เมตร (kg/m)", "น้ำหนัก/ชิ้น (kg)", "น้ำหนักรวม (kg)",
         "ลิงก์สินค้า"], True)
    steel_summary.merge_range(
        5, 0, 5, 7,
        "จำนวนท่อนประมาณเฉพาะรายการที่มีความยาวและท่อนมาตรฐาน ไม่หัก kerf/เศษตัด/ระยะซ้อน "
        "ส่วนชิ้นส่วนโหมดกรอกน้ำหนักเองจะรวม kg โดยไม่ถูกนับเป็นท่อนเหล็ก", notice)
    steel_summary.set_row(5, 32)
    steel_length_fmt = fmt(num_format="#,##0.000", align="right",
                           border=1, border_color=INK)
    steel_link_fmt = fmt(underline=1, text_wrap=True,
                         border=1, border_color=INK)
    for idx, raw in enumerate(steel_rows):
        item = bom_steel.normalize_member(raw)
        row = 7 + idx
        excel_row = row + 1
        manual = item.get("weight_mode") == bom_steel.WEIGHT_MODE_MANUAL
        rate = bom_steel.weight_per_m(item)
        steel_line_mass = bom_steel.total_weight_kg(item)
        mode_text = "กรอกน้ำหนักเอง" if manual else "ตามความยาว"
        values = [
            item.get("id"), item.get("member"), mode_text, item.get("material"),
            item.get("profile"), item.get("size"), item.get("qty"),
            item.get("length_mm"), None, item.get("stock_length_m"), item.get("notes"),
            item.get("weight_reference_length_m"), item.get("weight_reference_kg"),
            None, item.get("manual_unit_weight_kg"), None, item.get("link"),
        ]
        rowfmt = alternate if idx % 2 else normal
        for col, value in enumerate(values):
            if col == 16:
                link = str(value or "").strip()
                if link.lower().startswith(("https://", "http://")):
                    steel_cut.write_url(row, col, link, steel_link_fmt,
                                        string="เปิดลิงก์สินค้า")
                else:
                    steel_cut.write_string(row, col, link, rowfmt)
            elif col == 8:
                length = (float(bom_steel.total_length_m(item))
                          if item.get("length_mm") is not None else "")
                steel_cut.write_formula(
                    row, col, f'=IF(H{excel_row}="","",G{excel_row}*H{excel_row}/1000)',
                    steel_length_fmt, length)
            elif col == 13:
                steel_cut.write_formula(
                    row, col,
                    f'=IF(AND(L{excel_row}<>"",M{excel_row}<>""),M{excel_row}/L{excel_row},"")',
                    mass_number, "" if rate is None else float(rate))
            elif col == 15:
                steel_cut.write_formula(
                    row, col,
                    f'=IF(C{excel_row}="กรอกน้ำหนักเอง",G{excel_row}*O{excel_row},'
                    f'IF(AND(I{excel_row}<>"",N{excel_row}<>""),I{excel_row}*N{excel_row},""))',
                    mass_number, "" if steel_line_mass is None else float(steel_line_mass))
            elif col in (6, 7, 9, 11, 12, 14):
                if value is None or value == "":
                    steel_cut.write_blank(row, col, None,
                                          mass_number if col in (11, 12, 14) else rowfmt)
                else:
                    fmt_value = (number if col == 6 else
                                 mass_number if col in (11, 12, 14) else steel_length_fmt)
                    steel_cut.write_number(row, col, float(value), fmt_value)
            else:
                steel_cut.write_string(row, col, "" if value is None else str(value), rowfmt)
        steel_cut.set_row(row, fitted_row_height(
            values, [10,32,20,23,25,28,14,20,18,22,44,20,20,20,22,20,44],
            minimum=20))
    cut_last_excel = max(8, 7 + len(steel_rows))
    if steel_rows:
        steel_cut.autofilter(6, 0, 6 + len(steel_rows), 16)
    steel_cut.print_area(0, 0, max(7, 6 + len(steel_rows)), 16)

    # Combined mass roll-up worksheet. BOM and cut-list sources remain the
    # editable inputs; this sheet summarizes only weights that are known.
    mass_data = bom_steel_bom.summarize_bom_and_steel(doc)
    mass_sheet = sheet("Mass Summary",
        [20, 12, 42, 13, 13, 22, 22, 29],
        ["ประเภท", "ID", "อุปกรณ์ / ชิ้นส่วน", "จำนวน", "หน่วย",
         "น้ำหนักอ้างอิง (kg/ชิ้น หรือ kg/m)", "น้ำหนักรวม (kg)", "หมายเหตุ"], True)
    mass_sheet.write_string(3, 0, "อุปกรณ์ BOM (kg)", label)
    mass_sheet.write_formula(3, 1,
        '=IF(COUNT(BOM!K8:K' + str(max(8, end)) + ')=0,"",SUM(BOM!K8:K' +
        str(max(8, end)) + '))',
        total_mass, "" if mass_data["equipment_weighted_items"] == 0
        else float(mass_data["equipment_known_weight_kg"]))
    mass_sheet.write_string(3, 2, "โครงเหล็ก (kg)", label)
    mass_sheet.write_formula(3, 3,
        '=IF(COUNT(\'Steel Cut List\'!P8:P' + str(max(8, 7 + len(steel_rows))) +
        ')=0,"",SUM(\'Steel Cut List\'!P8:P' + str(max(8, 7 + len(steel_rows))) + '))',
        total_mass, "" if mass_data["steel_known_weight_kg"] == 0
        else float(mass_data["steel_known_weight_kg"]))
    mass_sheet.write_string(3, 4, "น้ำหนักรวมที่ทราบ (kg)", label)
    mass_sheet.write_formula(3, 5, '=IF(COUNT(B4,D4)=0,"",SUM(B4,D4))',
        total_mass, "" if not (mass_data["equipment_weighted_items"] or
                               mass_data["steel_known_weight_kg"])
        else float(mass_data["combined_known_weight_kg"]))
    mass_sheet.merge_range(5, 0, 5, 7,
        "รวมเฉพาะน้ำหนักที่กรอกไว้ • น้ำหนักที่ไม่ทราบจะแสดงว่างและไม่ถูกเดา", notice)
    for idx, item in enumerate(items):
        row = 7 + idx
        excel_row = row + 1
        qty = price(item.get("qty")) or 0
        unit_weight = price(item.get("unitWeightKg"))
        line_weight = None if unit_weight is None else qty * unit_weight
        values = ["อุปกรณ์ BOM", item.get("id"), item.get("name"), qty,
                  item.get("unit") or "", unit_weight, None,
                  "ยังไม่ทราบน้ำหนัก" if unit_weight is None else ""]
        for col, value in enumerate(values):
            if col == 6:
                mass_sheet.write_formula(
                    row, col, f'=IF(F{excel_row}="","",D{excel_row}*F{excel_row})',
                    mass_number, "" if line_weight is None else float(line_weight))
            elif value is None or value == "":
                mass_sheet.write_blank(row, col, None,
                                       mass_number if col in (3, 5) else normal)
            elif col == 3:
                mass_sheet.write_number(row, col, float(value), number)
            elif col == 5:
                mass_sheet.write_number(row, col, float(value), mass_number)
            else:
                mass_sheet.write_string(row, col, str(value),
                                         alternate if idx % 2 else normal)
        mass_sheet.set_row(row, fitted_row_height(
            values, [20,12,42,13,13,22,22,29], minimum=20))
    steel_header_row = 7 + len(items) + 2
    mass_sheet.merge_range(steel_header_row, 0, steel_header_row, 7,
                           "รายการโครงสร้างเหล็ก / STEEL FRAME", bar)
    subhead_row = steel_header_row + 1
    for col, heading in enumerate(["ประเภท", "ID", "อุปกรณ์ / ชิ้นส่วน", "จำนวน", "หน่วย",
                                   "น้ำหนักต่อหน่วย / เมตร (kg)", "น้ำหนักรวม (kg)", "หมายเหตุ"]):
        mass_sheet.write(subhead_row, col, heading, head)
    for idx, raw in enumerate(steel_rows):
        item = bom_steel.normalize_member(raw)
        rate = bom_steel.weight_per_m(item)
        manual = item.get("weight_mode") == bom_steel.WEIGHT_MODE_MANUAL
        unit_mass = item.get("manual_unit_weight_kg") if manual else rate
        line_weight = bom_steel.total_weight_kg(item)
        row = subhead_row + 1 + idx
        source_excel_row = 8 + idx
        values = ["โครงเหล็ก", item.get("id"), item.get("member"), item.get("qty"),
                  "ชิ้น", unit_mass, None,
                  ("น้ำหนักต่อชิ้นที่กรอกเอง" if manual else
                   "ยังไม่ทราบน้ำหนัก" if line_weight is None else "")]
        for col, value in enumerate(values):
            if col == 6:
                formula = f'=IF(\'Steel Cut List\'!P{source_excel_row}="","",\'Steel Cut List\'!P{source_excel_row})'
                mass_sheet.write_formula(
                    row, col, formula, mass_number,
                    "" if line_weight is None else float(line_weight))
            elif value is None or value == "":
                mass_sheet.write_blank(row, col, None,
                                       mass_number if col == 5 else normal)
            elif col == 3:
                mass_sheet.write_number(row, col, float(value), number)
            elif col == 5:
                mass_sheet.write_number(row, col, float(value), mass_number)
            else:
                mass_sheet.write_string(row, col, str(value),
                                         alternate if idx % 2 else normal)
        mass_sheet.set_row(row, 20)
    mass_last = max(subhead_row + len(steel_rows), 7 + len(items))
    mass_sheet.print_area(0, 0, mass_last, 7)

    if steel_totals["groups"]:
        for idx, group in enumerate(steel_totals["groups"]):
            row = 7 + idx
            excel_row = row + 1
            mode_text = ("กรอกน้ำหนักเอง" if group.get("weight_mode") == bom_steel.WEIGHT_MODE_MANUAL
                         else "ตามความยาว")
            steel_summary.write_string(row, 0, mode_text, alternate if idx % 2 else normal)
            steel_summary.write_string(row, 1, group["material"], alternate if idx % 2 else normal)
            steel_summary.write_string(row, 2, group["profile"], alternate if idx % 2 else normal)
            steel_summary.write_string(row, 3, group["size"], alternate if idx % 2 else normal)
            cut_qty = "'Steel Cut List'!$G$8:$G$" + str(cut_last_excel)
            cut_mode = "'Steel Cut List'!$C$8:$C$" + str(cut_last_excel)
            cut_material = "'Steel Cut List'!$D$8:$D$" + str(cut_last_excel)
            cut_profile = "'Steel Cut List'!$E$8:$E$" + str(cut_last_excel)
            cut_size = "'Steel Cut List'!$F$8:$F$" + str(cut_last_excel)
            cut_length = "'Steel Cut List'!$I$8:$I$" + str(cut_last_excel)
            cut_stock = "'Steel Cut List'!$J$8:$J$" + str(cut_last_excel)
            criteria = (f"{cut_mode},A{excel_row},{cut_material},B{excel_row},"
                        f"{cut_profile},C{excel_row},{cut_size},D{excel_row},"
                        f"{cut_stock},G{excel_row}")
            steel_summary.write_formula(
                row, 4, f"=SUMIFS({cut_qty},{criteria})",
                number, group["pieces"])
            steel_summary.write_formula(
                row, 5,
                f'=IF(A{excel_row}="กรอกน้ำหนักเอง","",SUMIFS({cut_length},{criteria}))',
                steel_length_fmt,
                "" if group.get("weight_mode") == bom_steel.WEIGHT_MODE_MANUAL
                and not group["total_length_m"] else float(group["total_length_m"]))
            if group.get("stock_length_m") is None:
                steel_summary.write_blank(row, 6, None, steel_length_fmt)
            else:
                steel_summary.write_number(row, 6, group["stock_length_m"], steel_length_fmt)
            steel_summary.write_formula(
                row, 7, f"=IF(G{excel_row}>0,ROUNDUP(F{excel_row}/G{excel_row},0),0)",
                number, group["estimated_stock_bars"])
            steel_summary.set_row(row, fitted_row_height(
                [mode_text, group["material"], group["profile"], group["size"],
                 group["pieces"], group["total_length_m"], group.get("stock_length_m"),
                 group["estimated_stock_bars"]],
                [18,23,28,29,16,22,22,24], minimum=20))
        steel_summary.autofilter(6, 0, 6 + len(steel_totals["groups"]), 7)
        steel_total_row = 7 + len(steel_totals["groups"])
        steel_summary.merge_range(steel_total_row, 0, steel_total_row, 3,
                                  "รวมทั้งหมด", total_fmt)
        last_summary_excel = 7 + len(steel_totals["groups"])
        steel_summary.write_formula(
            steel_total_row, 4, f"=SUM(E8:E{last_summary_excel})",
            number, steel_totals["total_pieces"])
        steel_summary.write_formula(
            steel_total_row, 5, f"=SUM(F8:F{last_summary_excel})",
            steel_length_fmt, float(steel_totals["total_length_m"]))
        steel_summary.write_blank(steel_total_row, 6, None, total_fmt)
        steel_summary.write_formula(
            steel_total_row, 7, f"=SUM(H8:H{last_summary_excel})",
            number, steel_totals["estimated_stock_bars"])
        steel_summary.set_row(steel_total_row, 32)
        steel_summary.print_area(0, 0, steel_total_row, 7)
    else:
        steel_summary.write_string(7, 0, "ยังไม่มีข้อมูลโครงสร้างเหล็ก", normal)
        steel_summary.print_area("A1:H8")

    # Guard the workbook packager against a malformed cell format. A bad
    # format must never make the complete Excel export unusable.
    for worksheet in wb.worksheets():
        for row_index, row_cells in worksheet.table.items():
            for col_index, cell in list(row_cells.items()):
                cell_format = getattr(cell, "format", None)
                if cell_format is not None and not callable(
                        getattr(cell_format, "_get_xf_index", None)):
                    print(
                        "WARNING: invalid Excel cell format; applying safe fallback: "
                        f"sheet={worksheet.name!r}, row={row_index + 1}, "
                        f"column={col_index + 1}, type={type(cell_format).__name__}"
                    )
                    if hasattr(cell, "_replace"):
                        row_cells[col_index] = cell._replace(format=normal)
                    else:
                        cell.format = normal
    wb.close()
