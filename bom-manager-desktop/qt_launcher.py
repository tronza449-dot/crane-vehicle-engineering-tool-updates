"""Windows Minimal Engineering entrypoint with packaged EXE smoke-test mode."""
import json
import sys
from pathlib import Path

from bom_qt import main


def smoke_test():
    """Verify packaged PySide6 can load all pages without any GitHub access."""
    from PySide6.QtWidgets import QApplication
    from bom_qt import BOMWindow
    from bom_qt_theme import apply_theme
    app = QApplication([])
    apply_theme(app)
    win = BOMWindow(auto_load=False)
    # CI may provide real project data for a faithful screenshot.
    source = Path.cwd().parent / "bom-manager" / "bom.json"
    if source.exists():
        import bom_core
        doc = json.loads(source.read_text(encoding="utf-8"))
        bom_core.ensure_doc(doc)
        win.payload = doc
    win.render_all()
    win.resize(1480, 890)
    win.show()
    app.processEvents()
    assert len(win.nav_buttons) == 6
    assert win.stack.count() == 6
    assert win.bom_table.columnCount() == 9
    assert len(win.cards) == 6
    assert len(win.category_buttons) == 7
    assert win.update_btn.parentWidget().objectName() == "topbar"
    assert win.update_btn.isEnabled()
    assert win.install_btn.isHidden()  # displayed only when update found
    win.show_page(5)
    assert win.debug_checks.rowCount() >= 3
    assert win.debug_events.columnCount() == 5
    win.show_page(0)
    app.processEvents()
    if "--capture-preview" in sys.argv:
        folder = Path("output")
        folder.mkdir(parents=True, exist_ok=True)

        def snapshot(name):
            app.processEvents()
            if not win.grab().save(str(folder / name), "PNG"):
                raise RuntimeError("Could not capture " + name)

        win.show_page(0)
        snapshot("MinimalDashboardPreview.png")
        win.show_page(1)
        snapshot("MinimalBOMPreview.png")
        win.show_page(4)
        snapshot("MinimalReportsPreview.png")
        win.show_page(5)
        snapshot("DebugReportPreview.png")

        # Show a real editable Qt item form without submitting/changing BOM data.
        from bom_qt import RecordDialog, ITEM_FIELDS
        item_dialog = RecordDialog("เพิ่มอุปกรณ์", ITEM_FIELDS,
                                   {"category": "ระบบขับเคลื่อน"}, win)
        item_dialog.show()
        app.processEvents()
        if not item_dialog.grab().save(str(folder / "MinimalFormPreview.png"), "PNG"):
            raise RuntimeError("Could not capture MinimalFormPreview.png")
        item_dialog.close()

        # Accessibility option is also verified on the packaged executable.
        win.font_scale_selector.setCurrentIndex(2)
        win.show_page(1)
        snapshot("ReadableBOMPreview.png")
        win.font_scale_selector.setCurrentIndex(1)
        win.show_page(0)
    win.close()
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv or "--capture-preview" in sys.argv:
        sys.exit(smoke_test())
    sys.exit(main())
