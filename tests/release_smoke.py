# Bounded release-blocking smoke checks.
# Do not walk every nested tab or render whole PDF reports here; those run in deep audit.
import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import math
from PySide6.QtWidgets import QApplication, QPushButton, QScrollArea, QGroupBox
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
    assert w.rampGeomOut.minimumHeight()>=270
    assert w.slopeout.minimumHeight()>=185
    result=w.ramp_geometry_results()
    assert w.slopeSummaryAngle.text()==f'{result["angle"]:.2f}°'
    w.show()
    w.show_stability_mode()
    idx=next(i for i in range(w.stabilityTabs.count()) if w.stabilityTabs.tabText(i)=="Slope")
    w.stabilityTabs.setCurrentIndex(idx)
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
                print("SLOPE_GROUP",g.title()[:90],"minimum",g.minimumSizeHint().width(),"hint",g.sizeHint().width(),flush=True)
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

    print("SMOKE 6/6: close safely", flush=True)
finally:
    w.close()
    QApplication.processEvents()
print("CVET_RELEASE_SMOKE_OK",flush=True)
