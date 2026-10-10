"""Minimal Engineering — readable light workspace with a restrained navy sidebar.

Only the presentation layer changes. BOM/JSON, GitHub auth and calculations are
independent of this module. Font zoom and family persist across app upgrades.
"""
import re
from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

COLORS = {
    "bg": "#F5F8FC", "sidebar": "#10243D", "panel": "#FFFFFF",
    "panel2": "#F0F5FA", "line": "#DCE5EF", "text": "#172D45",
    "muted": "#60738A", "blue": "#1768D2", "green": "#13835C",
    "amber": "#9D6415", "red": "#B73B4D", "purple": "#7652BB",
}

SCALE_OPTIONS = (1.0, 1.15, 1.3, 1.45)
SCALE_LABELS = ("ปกติ 100%", "อ่านง่าย 115%", "ใหญ่ 130%", "ใหญ่มาก 145%")
FONT_OPTIONS = ("Tahoma", "Leelawadee UI")
DEFAULT_SCALE = 1.15


def _settings():
    return QSettings("CraneVehicle", "BOMManager")


def current_scale():
    try:
        candidate = float(_settings().value("appearance/text_scale", DEFAULT_SCALE))
    except (TypeError, ValueError):
        candidate = DEFAULT_SCALE
    return min(SCALE_OPTIONS, key=lambda candidate_scale: abs(candidate_scale-candidate))


def current_font():
    font_name = str(_settings().value("appearance/font_family", FONT_OPTIONS[0]))
    return font_name if font_name in FONT_OPTIONS else FONT_OPTIONS[0]


def save_appearance(scale=None, font_family=None):
    settings = _settings()
    if scale is not None:
        if scale not in SCALE_OPTIONS:
            raise ValueError("Unsupported text scale")
        settings.setValue("appearance/text_scale", str(scale))
    if font_family is not None:
        if font_family not in FONT_OPTIONS:
            raise ValueError("Unsupported font")
        settings.setValue("appearance/font_family", font_family)
    settings.sync()


def _scale_css(css, zoom):
    return re.sub(r"font-size:\s*(\d+)px",
                  lambda match: "font-size: %dpx" %
                  max(12, round(int(match.group(1))*zoom)), css)


def apply_theme(app: QApplication, scale=None, font_family=None):
    """Apply high-contrast style and preserve existing font preferences."""
    scale = current_scale() if scale is None else scale
    if scale not in SCALE_OPTIONS:
        raise ValueError("Unsupported text scale")
    font_family = current_font() if font_family is None else font_family
    if font_family not in FONT_OPTIONS:
        raise ValueError("Unsupported font")
    font = QFont(font_family, max(11, round(12 * scale)))
    # Thai script needs proper shaping; use Windows font hinting and AA.
    font.setWeight(QFont.Weight.Medium)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
    css = r"""
    QWidget { background: #F5F8FC; color: #172D45;
              font-family: "Tahoma"; font-weight: 500;
              font-size: 16px; }
    QWidget#main, QWidget#content, QWidget#page { background: #F5F8FC; }
    QFrame#sidebar { background: #10243D; border: 0; }
    QFrame#topbar { background: #FFFFFF; border: 1px solid #DCE5EF;
                    border-radius: 14px; }
    QFrame#panel, QFrame#metric, QFrame#tablePanel, QFrame#formPanel,
    QFrame#categoryCard, QFrame#hero {
        background: #FFFFFF; border: 1px solid #DCE5EF; border-radius: 14px;
    }
    QFrame#metric:hover, QFrame#categoryCard:hover {
        background: #F6FAFF; border: 1px solid #9BC4F6;
    }
    QFrame#hero { background: #EAF3FF; border: 1px solid #D0E3FC; }
    QLabel { border: 0; background: transparent; }
    QLabel#logo { color: #FFFFFF; font-size: 24px; font-weight: 800; }
    QLabel#sidebarCaption { color: #D6E5F5; font-size: 13px; font-weight: 600; }
    QLabel#pageTitle { color: #142C46; font-size: 26px; font-weight: 800; }
    QLabel#sectionTitle { color: #193652; font-size: 18px; font-weight: 700; }
    QLabel#caption { color: #344B63; font-size: 14px; font-weight: 600; }
    QLabel#kpiValue { color: #153653; font-size: 31px; font-weight: 800; }
    QLabel#kpiName { color: #3A526B; font-size: 14px; font-weight: 600; }
    QLabel#hint { color: #43596E; font-size: 14px; font-weight: 500; }
    QLabel#status { color: #43596E; font-size: 13px; font-weight: 600; }
    QLabel#sideStatus { color: #9DF3C6; font-size: 13px; font-weight: 700; }
    QLabel#badge { color: #16724F; background: #E4F6ED; border-radius: 8px;
                   padding: 4px 10px; font-size: 12px; font-weight: 700; }
    QLabel#heroTitle { color: #133B70; font-size: 22px; font-weight: 800; }
    QLabel#heroSubtitle { color: #2C526E; font-size: 14px; font-weight: 600; }
    QLabel#categoryCount { color: #1768D2; font-size: 20px; font-weight: 800; }

    QPushButton {
        background: #FFFFFF; border: 1px solid #D2DDE8; color: #263E55;
        padding: 9px 14px; border-radius: 9px; font-weight: 600; min-height: 23px;
    }
    QPushButton:hover { background: #EFF6FF; border: 1px solid #91B9EA; color: #134F9D; }
    QPushButton:pressed { background: #DCEBFF; }
    QPushButton:disabled { background: #F1F4F8; border-color: #E1E7EF;
                           color: #8698AA; }
    QPushButton#primary { background: #1768D2; border-color: #1768D2; color: #FFFFFF; }
    QPushButton#primary:hover { background: #0D55B2; border-color: #0D55B2; color: white; }
    QPushButton#success { background: #137F62; border-color: #137F62; color: #FFFFFF; }
    QPushButton#success:hover { background: #096D52; border-color: #096D52; color: white; }
    QPushButton#danger { background: #FFFFFF; border-color: #E5C1C7; color: #A93146; }
    QPushButton#danger:hover { background: #FFF0F2; color: #A12034; }
    QPushButton#nav {
        background: transparent; color: #C8D8EC; border: 1px solid transparent;
        text-align: left; padding: 11px 15px; border-radius: 9px;
        font-size: 14px; font-weight: 600; min-height: 22px;
    }
    QPushButton#nav:hover { background: #203B5B; color: #FFFFFF; }
    QPushButton#nav[active="true"] {
        background: #1768D2; color: #FFFFFF; border: 1px solid #1768D2;
        font-weight: 800;
    }
    QPushButton#categoryAction {
        background: #F7FAFE; border: 1px solid #E0E8F2; color: #224664;
        text-align: left; border-radius: 9px; padding: 11px;
    }
    QPushButton#categoryAction:hover {
        background: #E8F2FF; border: 1px solid #98C2F3; color: #1456A4;
    }
    QLineEdit, QComboBox, QPlainTextEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
        background: #FFFFFF; color: #1B3852; border: 1px solid #CCD9E6;
        padding: 8px 11px; border-radius: 8px; min-height: 26px;
        selection-background-color: #1768D2;
        selection-color: white; font-weight: 600;
    }
    QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus, QTextEdit:focus {
        border: 1px solid #1768D2; background: #FFFFFF;
    }
    QComboBox::drop-down { border: 0; width: 29px; }
    QComboBox QAbstractItemView {
        background: #FFFFFF; color: #172D45; border: 1px solid #CFDCE9;
        selection-background-color: #D8E9FF; selection-color: #143C69;
    }
    QTableWidget, QTableView {
        background: #FFFFFF; alternate-background-color: #F7FAFD;
        gridline-color: #E7EDF3; border: 1px solid #DFE8F0; border-radius: 8px;
        selection-background-color: #D9EBFF; selection-color: #163856;
        font-size: 15px; font-weight: 500;
    }
    QTableWidget::item:hover, QTableView::item:hover { background: #EFF6FF; }
    QHeaderView::section {
        background: #EDF3F9; color: #2D4A64;
        border: none; border-right: 1px solid #E0E8F0;
        border-bottom: 1px solid #D1DDEA; padding: 12px 9px;
        font-size: 14px; font-weight: 700;
    }
    QTableCornerButton::section { background: #EDF3F9; border: 0; }
    QProgressBar { background: #E4EBF2; color: #173E60;
                   border: 0; border-radius: 6px; min-height: 12px; }
    QProgressBar::chunk { background: #18A174; border-radius: 6px; }
    QScrollBar:vertical { background: #F3F6FA; width: 12px; }
    QScrollBar::handle:vertical { background: #C4D1DF; border-radius: 6px; min-height: 28px; }
    QScrollBar:horizontal { background: #F3F6FA; height: 12px; }
    QScrollBar::handle:horizontal { background: #C4D1DF; border-radius: 6px; min-width: 28px; }
    QScrollBar::add-line, QScrollBar::sub-line { height: 0; width: 0; }
    QTabWidget::pane { background: #FFFFFF; border: 1px solid #DCE5EF;
                       border-radius: 10px; padding: 9px; }
    QTabBar::tab { background: #F2F6FA; color: #54718B; border: 1px solid #E0E8F0;
                   padding: 12px 18px; margin-right: 5px; border-radius: 8px; }
    QTabBar::tab:selected { background: #E6F1FF; color: #1768D2;
                            border-color: #A2C7F2; font-weight: 800; }
    QDialog, QMessageBox { background: #FFFFFF; }
    QDialogButtonBox { background: transparent; }
    QToolTip { background: #173652; color: #FFFFFF; border: 1px solid #507595; }
    QSplitter::handle { background: #DFE7F1; }
    /* Scoped sidebar controls retain contrast on a navy background. */
    QFrame#sidebar QLabel#caption { color: #E2EDF8; font-weight: 600; }
    QFrame#sidebar QLabel#status { color: #D1DEEB; }
    QFrame#sidebar QComboBox { background: #1B3552; color: #EFF7FF;
                              border: 1px solid #385775; }
    QFrame#sidebar QComboBox QAbstractItemView {
        background: #1B3552; color: #FFFFFF;
        selection-background-color: #1768D2;
    }
    """
    # Qt stylesheets accept one explicit font-family; a CSS fallback list can
    # resolve unexpectedly and make text appear inconsistent on Windows.
    css=css.replace('font-family: "Tahoma";', f'font-family: "{font_family}";')
    app.setStyleSheet(_scale_css(css,scale))
    return {"scale":scale, "font_family":font_family}
