# Bounded release-blocking smoke checks.
# Do not walk every nested tab or render whole PDF reports here; those run in deep audit.
import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import math
from PySide6.QtWidgets import QApplication, QPushButton, QScrollArea, QGroupBox, QAbstractSpinBox
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
import CraneVehicleEngineeringTool as cvet

print("SMOKE 1/5: QApplication startup", flush=True)
app=QApplication.instance() or QApplication([])
w=cvet.App()
try:
    assert w.windowTitle().find("V"+cvet.APP_VERSION)>=0
    print("SMOKE 2/5: visible navigation", flush=True)
    assert "hardware" not in w._mode_pages, "Hardware I/O must remain outside visible routing"
    assert not any("HARDWARE I/O" in b.text().upper() for b in w.homePage.findChildren(QPushButton))
    for show in (w.show_home_mode,w.show_torque_mode,w.show_electrical_mode,
                 w.show_winch_mode,w.show_stability_mode,w.show_telemetry_mode):
        show()
        QApplication.processEvents()

    print("SMOKE 3/5: engineering calculations", flush=True)
    t=w.torque_results()
    for key in ("T","rpm","Pwheel","Ibatt","Ftraction"):
        assert math.isfinite(float(t[key])), "Drive "+key
    e=w.electrical_results()
    for key in ("Ah","Edesign","Ecycle","Icalc_peak"):
        assert math.isfinite(float(e[key])), "Battery "+key
    assert e["Edesign"]>=0 and e["Ecycle"]>=0
    winch=w.winch_core_results()
    assert winch["up_speed"]>0
    cases=w.stability_fbd_cases()
    assert len(cases)==5, "Expected side L/R + front + rear + slope"

    print("SMOKE: BMS checks use consistent auxiliary-inclusive current references",flush=True)
    bms=w.battery_selection_results()
    rows=w.design_check_rows()
    cont=next(x for x in rows if x[0]=="Main BMS" and x[1]=="Continuous current")
    peak=next(x for x in rows if x[0]=="Main BMS" and x[1]=="Peak current (calculated)")
    winch_peak=next(x for x in rows if x[0]=="Winch BMS" and "Starting/stall" in x[1])
    assert f"{bms['cont_req']:.1f} A" in cont[2],(cont,bms["cont_req"])
    assert f"{bms['peak_calc']:.1f} A" in peak[2],(peak,bms["peak_calc"])
    assert winch_peak[4]=="CHECK", "Missing winch starting/stall data cannot PASS"
    html=w.bms_check_html()
    assert "including auxiliary" in html and "stall/start surge unknown" in html
    print("SMOKE: battery PDF report Step5 Thai formula and Step6 BMS arithmetic",flush=True)
    battery_html=w.battery_report_html()
    report_e=w.electrical_results()
    report_sel=w.battery_selection_results()
    report_aux=max(0.0,report_sel["e"].get("Iaux",0.0))
    assert "พลังงานรวมทั้งหมด = (พลังงานขับเคลื่อนรถต่อ 1 รอบไป–กลับ" in battery_html
    assert "E<sub>total</sub>" in battery_html
    assert "กำลังไฟฟ้าเฉลี่ยของอุปกรณ์เสริม × ระยะเวลาทำงานทั้งหมดในหน่วยชั่วโมง" in battery_html
    assert f"max({report_e['Icalc_up']:.2f}, {report_e.get('Iturn_avg',0.0):.2f}) + {report_aux:.2f} = <b>{report_sel['cont_req']:.2f} A</b>" in battery_html
    assert f"max({report_sel['cont_req']:.2f}, {report_sel['t']['Ibatt']:.2f} + {report_aux:.2f}) = <b>{report_sel['peak_calc']:.2f} A</b>" in battery_html
    assert abs(max(report_e["Icalc_up"],report_e.get("Iturn_avg",0.0),0)+report_aux-report_sel["cont_req"])<1e-8
    assert abs(max(report_sel["cont_req"],report_sel["t"]["Ibatt"]+report_aux)-report_sel["peak_calc"])<1e-8
    print("SMOKE: Thai battery STEP 6 sections",flush=True)
    for label in ("6.1 แยกให้ออกก่อน","6.2 กระแสแต่ละตัวมาจากไหน","6.3 Continuous Current","6.4 Peak Current","6.5 ทำไมสรุปเป็น BMS"):
        assert label in battery_html,("Missing battery explanation",label)
    assert "Ah กับ A ไม่ใช่ค่าเดียวกัน" in battery_html
    assert "ปัดขึ้นทีละ 5 A" in battery_html
    assert "ไม่ใช่กระแสสูงสุดจริงของมอเตอร์" in battery_html
    assert f"ceil({report_sel['cont_req']:.2f} ÷ 5) × 5 = <b>{report_sel['bms_cont']:.0f} A</b>" in battery_html
    assert f"ceil({report_sel['peak_calc']:.2f} ÷ 5) × 5 = <b>{report_sel['bms_peak']:.0f} A</b>" in battery_html
    print("SMOKE: print STEP5/6 report to a real PDF",flush=True)
    from pathlib import Path
    from PySide6.QtGui import QTextDocument, QPageSize, QFont
    from PySide6.QtPrintSupport import QPrinter
    output_path=Path("battery-step56-smoke.pdf").resolve()
    document=QTextDocument()
    document.setDefaultFont(QFont("Noto Sans Thai",10))
    document.setHtml(battery_html)
    printer=QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(str(output_path))
    printer.setPageSize(QPageSize(QPageSize.A4))
    document.print_(printer)
    pdf_content=output_path.read_bytes()
    assert pdf_content[:5]==b"%PDF-" and len(pdf_content)>15000, "PDF report invalid or empty"
    try:
        from PySide6.QtPdf import QPdfDocument
        from PySide6.QtCore import QSize
        reader=QPdfDocument()
        reader.load(str(output_path))
        page_count=reader.pageCount()
        assert 5<=page_count<=20, ("Unusual report page count",page_count)
        for index in (3,4,5):
            if index<page_count:
                page=reader.render(index,QSize(750,1058))
                assert not page.isNull()
                assert page.save(f"battery-step56-page-{index+1}.png","PNG")
        reader.close()
    except ImportError:
        print("QtPdf unavailable: validated physical PDF header and size",flush=True)

    print("SMOKE: simple What-if payload comparison after saved-state restore",flush=True)
    preserved=w.capture_project_state()
    try:
        for obj,value in ((w.mt,300.0),(w.ml,100.0),(w.mb,20.0),
                          (w.slope,11.11),(w.wmass,100.0)):
            obj.blockSignals(True)
            try:obj.setValue(value)
            finally:obj.blockSignals(False)
        w.whatIfShowAdvanced.setChecked(False)
        w.whatIfQuickParam.setCurrentIndex(0)
        w.whatIfQuickValue.setValue(200.0)
        # Deliberately poison the hidden advanced controls with old startup values.
        w.whatIfSlope.setValue(19.0)
        w.whatIfBaseMass.setValue(1500.0)
        base,scenario=w._what_if_comparison_values()
        assert base["payload"]==100.0 and scenario["payload"]==200.0
        assert abs(base["slope"]-11.11)<1e-8 and scenario["slope"]==base["slope"]
        assert scenario["base_mass"]==base["base_mass"]==180.0
        assert abs(sum(scenario[k] for k in ("base_mass","payload","boom_mass"))-400.0)<1e-8
        assert all(scenario[k]==base[k] for k in base if k not in ("payload","winch_load"))
        before=w._evaluate_coupled_scenario(base)
        after=w._evaluate_coupled_scenario(scenario)
        assert before["torque_mass"]==300.0 and after["torque_mass"]==400.0
        assert before["battery_mass"]==300.0 and after["battery_mass"]==400.0
        assert after["torque"]>before["torque"],("torque must rise",before["torque"],after["torque"])
        assert after["drive_cycle_wh"]>before["drive_cycle_wh"]
        assert abs(after["torque"]/before["torque"]-4.0/3.0)<1e-5
        html=w.sensitivity_analysis_html()
        assert "300.0 kg" in html and "400.0 kg" in html
        assert "Driving slope" in html and "11.11" in html
    finally:
        w.apply_project_state(preserved,False)
        w._core_recalculate()
    print("SMOKE 4/5: save/updater widgets", flush=True)
    assert hasattr(w,"updateProgress") and hasattr(w,"updateStageLabel")
    assert hasattr(w,"updatePercentLabel")
    w._set_update_stage("ขั้นตอน 2/4 - ทดสอบ")
    w._set_update_progress(45)
    assert w.updateProgress.value()==45 and w.updatePercentLabel.text()=="45%"
    assert w.updateProgress.isTextVisible()

    print("SMOKE 5/6: responsive Slope UI at laptop and compact resolutions", flush=True)
    assert isinstance(w.slopePage.findChild(QScrollArea,"slopeScrollArea"),QScrollArea)
    assert w.slopeScroll.widget().layout() is not None
    assert w.rampRiseCm.maximumWidth()<=230
    assert w.rampRiseCm.buttonSymbols()==QAbstractSpinBox.UpDownArrows
    assert "color:#182230" in w.rampRiseCm.styleSheet()
    assert w.rampGeomOut.minimumHeight()>=270
    assert w.slopeout.minimumHeight()>=185
    result=w.ramp_geometry_results()
    assert w.slopeSummaryAngle.text()==f'{result["angle"]:.2f}°'
    w.show()
    w.show_stability_mode()
    idx=next(i for i in range(w.stabilityTabs.count()) if w.stabilityTabs.tabText(i)=="Slope")
    w.stabilityTabs.setCurrentIndex(idx)
    print("SMOKE: Final Design lock -> visible warning -> actual mouse click unlock", flush=True)
    w.resize(1366,768)
    QApplication.processEvents()
    w.designLockButton.setChecked(True)
    QApplication.processEvents()
    assert not w.rampRiseCm.isEnabled() and not w.rampUseMainMass.isEnabled()
    assert w.stabilityLockBanner.isVisible(), "User must see why inputs are disabled"
    assert w.stabilityUnlockButton.isVisible() and w.stabilityUnlockButton.isEnabled()
    QTest.mouseClick(w.stabilityUnlockButton,Qt.LeftButton)
    QApplication.processEvents()
    assert not w._design_inputs_locked(), "Click must unlock Final Design"
    assert not w.stabilityLockBanner.isVisible()
    assert w.rampRiseCm.isEnabled() and w.rampRunCm.isEnabled() and w.rampMeasuredCm.isEnabled()
    assert w.rampUseMainMass.isEnabled()
    assert w.slope.isEnabled() and w.hcg.isEnabled() and w.acc.isEnabled()
    assert not w.rampMass.isEnabled(), "Linked mass must not appear manually editable"

    # Simulate a real user unchecking the battery link and typing a value.
    w.slopeScroll.verticalScrollBar().setValue(0)
    QApplication.processEvents()
    print("CHECKBOX_GEO",w.rampUseMainMass.width(),w.rampUseMainMass.sizeHint().width(),
          "checked",w.rampUseMainMass.isChecked(),"enabled",w.rampUseMainMass.isEnabled(),flush=True)
    QTest.mouseClick(w.rampUseMainMass,Qt.LeftButton)
    QApplication.processEvents()
    assert not w.rampUseMainMass.isChecked(), "Main Battery checkbox must respond to a mouse click on its center"
    assert w.rampMass.isEnabled()
    field=w.rampRiseCm.lineEdit()
    QTest.mouseClick(field,Qt.LeftButton)
    QTest.keyClick(field,Qt.Key_A,Qt.ControlModifier)
    QTest.keyClicks(field,"65.0")
    QTest.keyClick(field,Qt.Key_Return)
    QApplication.processEvents()
    assert abs(w.rampRiseCm.value()-65.0)<0.01, "Ramp field must accept real keyboard entry"
    assert "65.0" in w.rampGeomOut.toPlainText()
    # Other inputs remain live when battery mass is linked again.
    QTest.mouseClick(w.rampUseMainMass,Qt.LeftButton)
    QApplication.processEvents()
    assert w.rampUseMainMass.isChecked() and not w.rampMass.isEnabled()
    assert w.rampRiseCm.isEnabled()

    for width,height in ((1366,768),(1024,650)):
        w.resize(width,height)
        QApplication.processEvents()
        assert w.slopeScroll.widget().isVisible()
        assert w.slopeScroll.viewport().height()>120
        # All horizontal content must fit; a hidden horizontal scrollbar may
        # otherwise conceal the entire right half of Ramp Geometry.
        if w.slopeScroll.widget().width()>w.slopeScroll.viewport().width()+3:
            print("SLOPE_WIDTH_OVERFLOW",width,w.slopeScroll.widget().width(),w.slopeScroll.viewport().width(),flush=True)
            for g in w.slopeScroll.widget().findChildren(QGroupBox):
                print("SLOPE_GROUP",g.objectName() or "group","minimum",g.minimumSizeHint().width(),"hint",g.sizeHint().width(),flush=True)
        assert w.slopeScroll.widget().width()<=w.slopeScroll.viewport().width()+3, (
            width,w.slopeScroll.widget().width(),w.slopeScroll.viewport().width()
        )
        assert w.rampRiseCm.lineEdit().text().strip()
        assert w.rampGeomOut.toPlainText().strip()
        shot=w.grab()
        assert not shot.isNull() and shot.width()>0
        assert shot.save(f"slope-ui-{width}.png","PNG")
        if width==1024:
            assert w.slopeScroll.verticalScrollBar().maximum()>0

    fbdIdx=next(i for i in range(w.stabilityTabs.count()) if w.stabilityTabs.tabText(i)=="Engineering FBD")
    w.stabilityTabs.setCurrentIndex(fbdIdx)
    assert isinstance(w.fbdPage.findChild(QScrollArea,"fbdScrollArea"),QScrollArea)
    assert w.fbdScroll.widget().layout() is not None
    for width,height in ((1366,768),(1024,650)):
        w.resize(width,height)
        QApplication.processEvents()
        assert w.forceDiagram.height()>=525, "Diagram may not be crushed by lower explanation panes"
        assert w.fbdScroll.verticalScrollBar().maximum()>0, "Explanations must scroll"
        assert w.fbdScroll.widget().width()<=w.fbdScroll.viewport().width()+3, (
            "FBD overflow",width,w.fbdScroll.widget().width(),w.fbdScroll.viewport().width()
        )
        assert w.grab().save(f"fbd-ui-{width}.png","PNG")
        w.fbdScroll.verticalScrollBar().setValue(w.fbdScroll.verticalScrollBar().maximum())
        QApplication.processEvents()
        assert w.grab().save(f"fbd-ui-bottom-{width}.png","PNG")
        w.fbdScroll.verticalScrollBar().setValue(0)

    print("SMOKE: moment-balance reference example",flush=True)
    reference=dict(mt=300.0,ml=100.0,mb=20.0,W=1.10,WB=1.10,L=1.20,
                   kd=1.20,xC=.15,xCG=0.0,yCG=0.0,req=1.50)
    left=w.side_moment_balance(reference,-90.0,"left")
    right=w.side_moment_balance(reference,90.0,"right")
    front=w.longitudinal_moment_balance(reference,0.0,"front")
    rear=w.longitudinal_moment_balance(reference,-90.0,"rear")
    for case,mo,mr in ((left,774.99,971.19),(right,774.99,971.19),
                       (front,294.30,1039.86),(rear,0.0,1147.77)):
        assert abs(case["mo"]-mo)<.03,("M_O",case)
        assert abs(case["mr"]-mr)<.03,("M_R",case)
    assert left["sf"]<reference["req"] and right["sf"]<reference["req"]
    print("SMOKE: geometry FBD direct rendering regression (6 cases × 2 sizes)", flush=True)
    # Call the actual painter methods, so Python exceptions from QPaintEvent cannot be swallowed by Qt.
    from PySide6.QtGui import QImage, QPainter
    fd=cvet.ForceDiagram(w)
    d=w.inputs()
    original_txt=fd.txt
    recorded=[]
    def tracking_txt(p,x,y,value,*args,**kwargs):
        recorded.append(str(value))
        return original_txt(p,x,y,value,*args,**kwargs)
    fd.txt=tracking_txt
    cases_render=[
        ("geometry",0,90.0),
        ("left",1,-90.0),
        ("right",2,90.0),
        ("front",3,0.0),
        ("rear",4,-90.0),
        ("slope",5,None),
    ]
    for width,height in ((1180,760),(920,590)):
        fd.resize(width,height)
        for name,mode,angle in cases_render:
            fd.setCaseAngle(angle)
            fd.setMode(mode)
            recorded.clear()
            picture=QImage(width,height,QImage.Format_ARGB32_Premultiplied)
            picture.fill(Qt.white)
            painter=QPainter(picture)
            assert painter.isActive(), "FBD QPainter initialization failed"
            try:
                if mode==0:fd.geometry(painter,d)
                elif mode==1:fd.side(painter,d,"left")
                elif mode==2:fd.side(painter,d,"right")
                elif mode==3:fd.longitudinal(painter,d,"front")
                elif mode==4:fd.longitudinal(painter,d,"rear")
                else:fd.slope(painter,d)
            finally:
                painter.end()
            if mode==0:
                assert any("Right tipping axis (+y)" in x for x in recorded), "Top view +y axis label wrong"
                assert any("Left tipping axis (-y)" in x for x in recorded), "Top view -y axis label wrong"
            if mode in (1,2,3,4):
                assert any("R_opp → 0 at tipping" in x for x in recorded), "Missing limit-state reaction note"
                assert any("CRANE PLAN VIEW" in x for x in recorded), "Missing crane plan-view inset"
            assert picture.save(f"fbd-engineering-{name}-{width}.png","PNG"), name
    # Front uses separate boom and load gravity lines at their real x projections;
    # rear +/-90 must collapse those lines only on the MAIN orthographic FBD.
    fd.resize(1180,760)
    fd.setCaseAngle(0.0)
    tracked=[]
    original_arrow=fd.arrow
    def capture_arrow(p,a,b,label="",*args,**kwargs):
        tracked.append((str(label),float(a.x())))
        return original_arrow(p,a,b,label,*args,**kwargs)
    fd.arrow=capture_arrow
    pic=QImage(1180,760,QImage.Format_ARGB32_Premultiplied)
    pic.fill(Qt.white)
    painter=QPainter(pic)
    recorded.clear()
    try:
        fd.longitudinal(painter,reference,"front")
    finally:
        painter.end()
    assert not any("90° TO MAST - OUT OF PLANE (SKETCH ONLY)" in t for t in recorded), "θ=0° must show the actual projected boom"
    boom=next(x for label,x in tracked if label.startswith("W_B = "))
    load=next(x for label,x in tracked if label=="Kdyn·W_L")
    assert load > boom+15,(boom,load)
    assert any("BOOM PROFILE (SCHEMATIC)" in x for x in recorded)
    assert pic.save("fbd-boom-front-reference.png","PNG")
    tracked.clear()
    fd.setCaseAngle(-90.0)
    pic.fill(Qt.white)
    painter=QPainter(pic)
    recorded.clear()
    try:
        fd.longitudinal(painter,reference,"rear")
    finally:
        painter.end()
    assert any("90° TO MAST - OUT OF PLANE (SKETCH ONLY)" in t for t in recorded), "±90° must show 90° L-shape, not an inclined boom"
    assert sum(1 for label,x in tracked if label.startswith("W_B + W_L (same x)"))==1
    assert not any(label.startswith("W_B = ") for label,x in tracked)
    assert pic.save("fbd-boom-rear-reference.png","PNG")
    fd.arrow=original_arrow
    fd.deleteLater()
    print("SMOKE: boom 20kg + payload separate projection regression OK", flush=True)
    print("SMOKE 6/6: close safely", flush=True)
finally:
    w.close()
    QApplication.processEvents()
print("CVET_RELEASE_SMOKE_OK",flush=True)
