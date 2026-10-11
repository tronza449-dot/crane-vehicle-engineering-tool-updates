# Bounded release-blocking smoke checks.
# Do not walk every nested tab or render whole PDF reports here; those run in deep audit.
import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import math
from PySide6.QtWidgets import QApplication, QPushButton
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

    print("SMOKE 5/5: close safely", flush=True)
finally:
    w.close()
    QApplication.processEvents()
print("CVET_RELEASE_SMOKE_OK",flush=True)
