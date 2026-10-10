"""Formal engineering BOM PDF / Excel, independent of legacy exports.

Only figures with known prices contribute to budget totals. Blank means unknown.
All report cover metadata is editable and does not imply institutional approval.
"""
from datetime import datetime
from xml.sax.saxutils import escape
import bom_core
import bom_categories

NAVY="#153752"
BLUE="#205983"
GREY="#5B7185"
PALE="#EDF3F8"
LINE="#D5E1EC"


def metadata(doc, values=None):
    v=values or {}
    return {
        "project": str(v.get("project") or doc.get("project") or "Crane Vehicle"),
        "author": str(v.get("author") or "ไม่ระบุ"),
        "institution": str(v.get("institution") or "ไม่ระบุ"),
        "document_no": str(v.get("document_no") or "BOM-001"),
        "revision": str(v.get("revision") or "00"),
        "date": str(v.get("date") or datetime.now().strftime("%d/%m/%Y")),
    }


def sorted_items(doc):
    return sorted(doc["items"], key=lambda x: (
        bom_categories.sort_key(x.get("category")),
        str(x.get("name") or "").casefold(), str(x.get("id") or "")))


def price(value):
    return bom_core.decimal_or_none(value)


def category_stats(items):
    result=[]
    for category,count in bom_categories.summary(items):
        rows=[x for x in items if str(x.get("category") or
               bom_categories.UNCATEGORIZED)==category]
        missing=sum(price(x.get("unitPrice")) is None for x in rows)
        known=sum((price(x.get("unitPrice")) or 0) *
                  (price(x.get("qty")) or 0) for x in rows)
        result.append((category,count,missing,float(known)))
    return result


def export_pdf(doc, destination, options=None):
    """Landscape A4 academic report with cover, category BOM and appendices."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    PageBreak, LongTable, TableStyle)
    from bom_reports import _thai_font
    bom_core.ensure_doc(doc)
    m=metadata(doc,options)
    stats=bom_core.metrics(doc)
    categories=category_stats(doc["items"])
    items=sorted_items(doc)
    font=_thai_font()
    navy=colors.HexColor(NAVY)
    line=colors.HexColor(LINE)
    page=landscape(A4)
    width=page[0]-64
    body=ParagraphStyle("body",fontName=font,fontSize=8.5,leading=14,
                        textColor=colors.HexColor("#23394D"),wordWrap="CJK",
                        splitLongWords=True)
    small=ParagraphStyle("small",parent=body,fontSize=8,leading=12)
    label=ParagraphStyle("label",parent=body,fontSize=9,leading=15,
                         textColor=colors.HexColor(GREY))
    title=ParagraphStyle("title",parent=body,fontSize=19,leading=29,
                         textColor=navy)
    section=ParagraphStyle("section",parent=body,fontSize=14,leading=22,
                           textColor=navy)
    white=ParagraphStyle("white",parent=body,fontSize=8,leading=12,
                         textColor=colors.white)
    def P(text,sty=body):
        return Paragraph(escape(str(text if text is not None else "—")).replace("\n","<br/>"),sty)
    def TABLE(headings,rows,widths):
        data=[[P(h,white) for h in headings]]
        data += [[P(x) for x in row] for row in (rows or [
            ["ยังไม่มีข้อมูล"]+[""]*(len(headings)-1)])]
        t=LongTable(data,colWidths=widths,repeatRows=1,hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),navy),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),
             [colors.white,colors.HexColor("#F3F7FB")]),
            ("LINEBELOW",(0,0),(-1,0),1,navy),
            ("LINEBELOW",(0,1),(-1,-1),.35,line),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LEFTPADDING",(0,0),(-1,-1),6),
            ("RIGHTPADDING",(0,0),(-1,-1),6),
            ("TOPPADDING",(0,0),(-1,-1),7),
            ("BOTTOMPADDING",(0,0),(-1,-1),7),
        ]))
        return t
    story=[
        Spacer(1,22),P("ENGINEERING DESIGN DOCUMENT",label),
        Spacer(1,9),P("รายงานรายการวัสดุและอุปกรณ์",title),
        P("BILL OF MATERIALS (BOM) / CRANE VEHICLE",section),
        Spacer(1,22),
    ]
    rows=[
        ["โครงการ",m["project"]],
        ["ผู้จัดทำ",m["author"]],
        ["สถาบัน / หน่วยงาน",m["institution"]],
        ["เลขที่เอกสาร",m["document_no"]],
        ["Revision / วันที่",f'{m["revision"]}  /  {m["date"]}'],
        ["สถานะ", "รายงานประกอบการออกแบบ - ไม่ใช่เอกสารอนุมัติการผลิต"],
    ]
    meta=LongTable([[P(a,label),P(b)] for a,b in rows],colWidths=[150,width-150])
    meta.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor(PALE)),
        ("LINEBELOW",(0,0),(-1,-1),.4,line),
        ("TOPPADDING",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),12),
    ]))
    story += [meta,Spacer(1,18),P("สรุปข้อมูลและงบประมาณ",section),Spacer(1,7)]
    story.append(TABLE(["จำนวนรายการ","มีราคาแล้ว","ยังไม่มีราคา","ยอดรวมที่ทราบราคา (บาท)"],[
        [stats["items"],stats["priced"],stats["missing"],
         f'{stats["known_cost"]:,.2f}']],
        [width*.20,width*.20,width*.20,width*.40]))
    story += [Spacer(1,12),P(
        "หมายเหตุ: ราคาไม่ทราบจะแสดงเป็น — ไม่ถือว่าราคาเท่ากับศูนย์ "
        "ยอดรวมยังไม่รวมรายการที่ไม่มีราคา รวมทั้งค่าขนส่ง ภาษี และค่าแรงที่ยังไม่บันทึก",label),
        PageBreak(),P("รายการแยกตามระบบวิศวกรรม",section),Spacer(1,6)]
    story.append(TABLE(["ระบบ / หมวดหมู่","รายการ","ไม่มีราคา","ยอดรวมที่ทราบ (บาท)"],
       [[c,n,missing,f"{amount:,.2f}"] for c,n,missing,amount in categories],
       [width*.44,width*.16,width*.17,width*.23]))
    story.append(PageBreak())
    for category,num,missing,known in categories:
        story += [P("ภาคผนวก ก. รายการวัสดุและอุปกรณ์",label),
                  P(category,section),
                  P(f"จำนวน {num} รายการ | ยังไม่มีราคา {missing} | "
                    f"มูลค่าที่ทราบ {known:,.2f} บาท",label),Spacer(1,9)]
        members=[x for x in items if str(x.get("category") or
                     bom_categories.UNCATEGORIZED)==category]
        rows=[]
        for k,item in enumerate(members,1):
            unitprice=price(item.get("unitPrice"))
            qty=price(item.get("qty")) or 0
            rows.append([k,item.get("id"),f'{item.get("name","")}\n{item.get("spec","")}',
                         item.get("qty"),item.get("unit"),
                         "—" if unitprice is None else f"{unitprice:,.2f}",
                         "—" if unitprice is None else f"{qty*unitprice:,.2f}",
                         item.get("status")])
        story.append(TABLE(["ลำดับ","ID","อุปกรณ์ / รายละเอียด","จำนวน",
             "หน่วย","ราคา/หน่วย","รวม (บาท)","สถานะ"],
             rows,[34,36,275,51,45,80,84,width-605]))
        story += [Spacer(1,12),P("ราคาไม่ทราบแสดงเป็น — และไม่รวมในยอดงบประมาณ",label),
                  PageBreak()]
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
    template=SimpleDocTemplate(str(destination),pagesize=page,
        leftMargin=32,rightMargin=32,topMargin=60,bottomMargin=46,
        title="Engineering Bill of Materials",author=m["author"],
        subject=m["project"])
    def decoration(canvas,page_doc):
        canvas.saveState()
        canvas.setFillColor(navy)
        canvas.rect(0,page[1]-34,page[0],34,stroke=0,fill=1)
        canvas.setFillColor(colors.white);canvas.setFont(font,9)
        canvas.drawString(32,page[1]-22,"ENGINEERING BOM  |  "+m["document_no"])
        canvas.setStrokeColor(line);canvas.line(32,34,page[0]-32,34)
        canvas.setFillColor(colors.HexColor(GREY));canvas.setFont(font,8)
        canvas.drawString(32,21,f'Rev. {m["revision"]}  |  {m["date"]}  |  รายงานประกอบการออกแบบ')
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
    wb=xlsxwriter.Workbook(str(destination))
    wb.set_properties({"title":"Engineering Bill of Materials / BOM",
                       "author":m["author"],"subject":m["project"],
                       "comments":"Unknown prices are intentionally blank."})
    def fmt(**kwargs):
        return wb.add_format({"font_name":"Tahoma","font_size":11,
                              "font_color":"#21384E","valign":"vcenter",**kwargs})
    title=fmt(bold=True,font_size=18,font_color=NAVY)
    subtitle=fmt(font_size=10,font_color=GREY)
    bar=fmt(bold=True,font_color="white",bg_color=NAVY,font_size=12)
    head=fmt(bold=True,font_color="white",bg_color=NAVY,
             align="center",text_wrap=True,font_size=10)
    normal=fmt(text_wrap=True,bottom=1,bottom_color=LINE)
    alternate=fmt(text_wrap=True,bg_color="#F2F6FA",bottom=1,bottom_color=LINE)
    category_fmt=fmt(bold=True,bg_color="#E4F0F8",font_color=NAVY)
    label=fmt(bold=True,font_color=NAVY)
    number=fmt(num_format="#,##0.##",align="center")
    money=fmt(num_format="#,##0.00;[Red](#,##0.00)",align="right")
    notice=fmt(font_color="#986015",bg_color="#FFF4E5",text_wrap=True)
    def sheet(name,widths,headers=None,wide=False):
        w=wb.add_worksheet(name)
        w.hide_gridlines(2)
        w.set_tab_color(BLUE if name=="BOM" else NAVY)
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
            w.merge_range(4,0,4,len(widths)-1,name+" / Design documentation",bar)
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
    summary.write_formula(17,1,"=COUNTA("+startend("C")+")",number,count)
    summary.write_formula(18,1,"=COUNT("+startend("F")+")",number,stats["priced"])
    summary.write_formula(19,1,"=B18-B19",number,stats["missing"])
    summary.write_formula(20,1,"=SUM("+startend("G")+")",money,stats["known_cost"])
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
                              ","+startend("F")+',""'+")",number,missing)
        summary.write_formula(row,3,"=SUMIF("+startend("B")+",A"+str(erow)+
                              ","+startend("G")+")",money,amount)
        summary.set_row(row,28)
    summary.merge_range("A36:D38",
        "หมายเหตุ: รายการที่ไม่ทราบราคาไม่ถูกถือว่ามีราคา 0 บาท "
        "และยอดรวมยังไม่ใช่งบประมาณสุดท้าย "
        "ไม่รวมค่าจัดส่ง ภาษี และค่าแรงที่ไม่ได้บันทึก",notice)
    summary.print_area("A1:D38")
    bom=sheet("BOM",[11,27,48,11,11,20,20,26],
        ["ID","ระบบ / หมวด","อุปกรณ์ / รุ่น","จำนวน","หน่วย",
         "ราคา/หน่วย (บาท)","รวม (บาท)","สถานะ"],True)
    details=sheet("Specification",[12,29,50,68,27,36,54],
        ["ID","หมวด","อุปกรณ์ / รุ่น","สเปกทางเทคนิค",
         "Part No.","ร้านค้า / ผู้ขาย","ข้อมูลเพิ่มเติม / ลิงก์"],True)
    for idx,item in enumerate(items):
        row=7+idx;erow=row+1
        category=item.get("category") or bom_categories.UNCATEGORIZED
        qty=price(item.get("qty")) or 0
        amount=price(item.get("unitPrice"))
        entries=[item.get("id"),category,item.get("name"),
                 qty,item.get("unit"),amount,None,item.get("status")]
        for col,val in enumerate(entries):
            style=alternate if idx%2 else normal
            if col==6:
                bom.write_formula(row,col,'=IF(F'+str(erow)+'="","",D'+
                                  str(erow)+'*F'+str(erow)+')',money,
                                  "" if amount is None else float(qty*amount))
            elif val is None:
                bom.write_blank(row,col,None,style)
            elif col in (3,5):
                bom.write_number(row,col,float(val),number if col==3 else money)
            else:
                bom.write_string(row,col,str(val),category_fmt if col==1 else style)
        bom.set_row(row,43)
        extra="\n".join(str(item.get(k)) for k in ("link","connection","notes")
                        if item.get(k))
        values=[item.get("id"),category,item.get("name"),item.get("spec"),
                item.get("partNumber"),item.get("supplier"),extra]
        for col,val in enumerate(values):
            details.write_string(row,col,"" if val is None else str(val),
                                 alternate if idx%2 else normal)
        details.set_row(row,61)
    if count:
        bom.autofilter(6,0,6+count,7)
        details.autofilter(6,0,6+count,6)
        bom.conditional_format(7,5,6+count,5,
                               {"type":"blanks","format":notice})
    bom.print_area(0,0,max(7,6+count),7)
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
    wb.close()
