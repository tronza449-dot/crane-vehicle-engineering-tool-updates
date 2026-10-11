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
    fd.deleteLater()
    print("SMOKE 6/6: close safely", flush=True)
finally:
    w.close()
    QApplication.processEvents()
print("CVET_RELEASE_SMOKE_OK",flush=True)
