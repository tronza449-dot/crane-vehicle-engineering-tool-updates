"""Windows Industrial Dark entrypoint with packaged EXE smoke-test mode."""
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
    assert len(win.nav_buttons) == 5
    assert win.stack.count() == 5
    assert win.bom_table.columnCount() == 8
    assert len(win.cards) == 6
    if "--capture-preview" in sys.argv:
        filename = Path("output") / "IndustrialDarkPreview.png"
        filename.parent.mkdir(parents=True, exist_ok=True)
        if not win.grab().save(str(filename), "PNG"):
            raise RuntimeError("Failed to save Industrial Dark GUI screenshot")
    win.close()
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv or "--capture-preview" in sys.argv:
        sys.exit(smoke_test())
    sys.exit(main())
