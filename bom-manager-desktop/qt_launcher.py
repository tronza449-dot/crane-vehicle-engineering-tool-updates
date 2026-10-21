"""Windows Minimal Engineering entrypoint with packaged EXE smoke-test mode."""
import json
import os
import sys
import tempfile
from pathlib import Path

from bom_qt import main


def smoke_test():
    """Verify packaged PySide6 can load all pages without any GitHub access.

    Tests run after unit tests in the same Windows runner. Give the EXE a
    clean local profile so a test-created dirty draft cannot trigger the
    unsaved-changes confirmation dialog and stall the smoke test.
    """
    os.environ["LOCALAPPDATA"] = tempfile.mkdtemp(prefix="bom-manager-smoke-")
    os.environ["BOM_MANAGER_DISABLE_STARTUP_UPDATE_CHECK"] = "1"
    trace_path = Path("output") / "smoke_trace.log"
    trace_path.parent.mkdir(parents=True, exist_ok=True)

    def trace(stage):
        with trace_path.open("a", encoding="utf-8") as stream:
            stream.write(stage + "\n")
            stream.flush()

    trace("start")
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtCore import Qt
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    from bom_qt import BOMWindow
    from bom_qt_theme import apply_theme
    app = QApplication([])
    trace("QApplication ready")
    apply_theme(app)
    trace("theme ready")
    win = BOMWindow(auto_load=False)
    trace("BOMWindow constructed")
    # CI may provide real project data for a faithful screenshot.
    source = Path.cwd().parent / "bom-manager" / "bom.json"
    if source.exists():
        import bom_core
        doc = json.loads(source.read_text(encoding="utf-8"))
        bom_core.ensure_doc(doc)
        win.payload = doc
    win.render_all()
    trace("initial render complete")
    win.resize(1480, 890)
    win.show()
    app.processEvents()
    trace("window shown and events processed")
    # These assertions describe the current Minimal Engineering UI.
    # Keep them aligned with actual widgets so stale preview checks cannot
    # hang a windowed EXE behind an unhandled-assertion dialog.
    try:
        assert len(win.nav_buttons) == 7, f"navigation buttons: {len(win.nav_buttons)}"
        assert win.stack.count() == 7, f"page count: {win.stack.count()}"
        assert win.bom_table.columnCount() == 11, (
            f"BOM table columns: {win.bom_table.columnCount()}")
        assert len(win.cards) == 6, f"dashboard metric cards: {len(win.cards)}"
        import bom_categories
        assert len(win.category_buttons) == len(bom_categories.CATEGORY_ORDER), (
            f"category buttons: {len(win.category_buttons)}")
        assert win.update_btn.parentWidget().objectName() == "topbar", (
            "update button is not inside topbar")
        assert win.update_btn.isEnabled(), "update button is disabled"
        assert win.install_btn.isHidden()  # displayed only when update found
    except BaseException:
        import traceback
        trace("UI assertion failed:")
        trace(traceback.format_exc())
        win.dirty = False
        win.busy = False
        win.downloading = False
        win.close()
        app.quit()
        return 1
    win.show_page(6)
    trace("debug page shown")
    assert win.debug_checks.rowCount() >= 3
    assert win.debug_events.columnCount() == 5
    win.show_page(0)
    app.processEvents()
    trace("dashboard restored")
    if "--capture-preview" in sys.argv:
        folder = Path("output")
        folder.mkdir(parents=True, exist_ok=True)

        # Dedicated Cut List preview uses representative materials to verify
        # wrapped headers and the material/shape distinction in the real EXE.
        win.payload["steel_members"] = [
            {"id": "S1", "member": "เสาโครง", "material": "เหล็กคาร์บอน (SS400 / ASTM A36)",
             "profile": "เหล็กกล่องสี่เหลี่ยม", "size": "50×50×2 mm",
             "qty": 4, "length_mm": 1000, "stock_length_m": 6,
             "weight_reference_length_m": "", "weight_reference_kg": "",
             "notes": "ตัวอย่างจากแบบ"},
            {"id": "S2", "member": "คานฐาน", "material": "สแตนเลส SUS 304",
             "profile": "เหล็กกล่องแบน", "size": "50×25×2 mm",
             "qty": 6, "length_mm": 1250, "stock_length_m": 6,
             "weight_reference_length_m": "", "weight_reference_kg": "",
             "notes": "ตรวจเกรดก่อนสั่งซื้อ"},
            {"id": "S3", "member": "ขายึด", "material": "อะลูมิเนียม 6061",
             "profile": "เหล็กฉาก", "size": "30×30×3 mm",
             "qty": 2, "length_mm": 300, "stock_length_m": 6,
             "weight_reference_length_m": "", "weight_reference_kg": "",
             "notes": "ตัวอย่าง"},
        ]
        win.render_all()
        app.processEvents()

        def snapshot(name):
            app.processEvents()
            if not win.grab().save(str(folder / name), "PNG"):
                raise RuntimeError("Could not capture " + name)

        win.show_page(0)
        snapshot("MinimalDashboardPreview.png")
        trace("dashboard screenshot saved")
        win.show_page(1)
        snapshot("MinimalBOMPreview.png")
        trace("BOM screenshot saved")
        win.show_page(2)
        snapshot("TotalMassRegisterPreview.png")
        trace("steel Cut List screenshot saved")
        win.show_page(5)
        snapshot("MinimalReportsPreview.png")
        trace("reports screenshot saved")
        win.show_page(6)
        snapshot("DebugReportPreview.png")
        trace("debug screenshot saved")

        # Show a real editable Qt item form without submitting/changing BOM data.
        from bom_qt import RecordDialog, ITEM_FIELDS
        item_dialog = RecordDialog("เพิ่มอุปกรณ์", ITEM_FIELDS,
                                   {"category": "ระบบขับเคลื่อน"}, win)
        item_dialog.show()
        app.processEvents()
        trace("item editor shown")
        if not item_dialog.grab().save(str(folder / "MinimalFormPreview.png"), "PNG"):
            raise RuntimeError("Could not capture MinimalFormPreview.png")
        item_dialog.close()
        trace("item editor screenshot saved")

        # Accessibility option is also verified on the packaged executable.
        win.font_scale_selector.setCurrentIndex(2)
        trace("font zoom increased")
        win.show_page(1)
        snapshot("ReadableBOMPreview.png")
        trace("readability screenshot saved")
        win.font_scale_selector.setCurrentIndex(1)
        win.show_page(0)
    # The packaged EXE must keep Thai PDF shaping and word breaking; a missing
    # bundled module silently falls back to broken tone marks otherwise.
    import bom_official_reports
    import bom_thai_text
    report_folder = Path("output")
    report_folder.mkdir(parents=True, exist_ok=True)
    bom_official_reports.export_pdf(win.payload, report_folder / "PackagedReport.pdf")
    trace(f"packaged report exported: shaping={bom_thai_text.shaping_available()} "
          f"words={bom_thai_text.word_engine()}")
    if not bom_thai_text.shaping_available() or bom_thai_text.word_engine() != "pythainlp":
        trace("Thai PDF text support is missing from the packaged EXE")
        win.dirty = False
        win.close()
        app.quit()
        return 1
    # A preview test must never prompt to save test-only edits.
    win.dirty = False
    win.busy = False
    win.downloading = False
    trace("closing main window")
    win.close()
    app.quit()
    trace("smoke test complete")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv or "--capture-preview" in sys.argv:
        sys.exit(smoke_test())
    sys.exit(main())
