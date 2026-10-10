"""Industrial Dark visual design system for the Qt desktop edition."""
import re
from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

COLORS = {
    "bg": "#09111F", "sidebar": "#0C1626", "panel": "#111F32",
    "panel2": "#16273C", "line": "#263C54", "text": "#E7F2FF",
    "muted": "#C4D3E6", "blue": "#36A8FF", "green": "#29D7A3",
    "amber": "#F5BA55", "red": "#FF7891", "purple": "#AB99FF",
}



SCALE_OPTIONS = (1.0, 1.15, 1.3, 1.45)
SCALE_LABELS = ("ปกติ 100%", "อ่านง่าย 115%", "ใหญ่ 130%", "ใหญ่มาก 145%")
FONT_OPTIONS = ("Leelawadee UI", "Tahoma")
DEFAULT_SCALE = 1.15


def _settings():
    return QSettings("CraneVehicle", "BOMManager")


def current_scale():
    try:
        candidate = float(_settings().value("appearance/text_scale", DEFAULT_SCALE))
    except (TypeError, ValueError):
        candidate = DEFAULT_SCALE
    return min(SCALE_OPTIONS, key=lambda available: abs(available - candidate))


def current_font():
    value = str(_settings().value("appearance/font_family", FONT_OPTIONS[0]))
    return value if value in FONT_OPTIONS else FONT_OPTIONS[0]


def save_appearance(scale=None, font_family=None):
    settings = _settings()
    if scale is not None:
        if scale not in SCALE_OPTIONS:
            raise ValueError("Font scale must match a supported preset")
        settings.setValue("appearance/text_scale", str(scale))
    if font_family is not None:
        if font_family not in FONT_OPTIONS:
            raise ValueError("Unknown UI font")
        settings.setValue("appearance/font_family", font_family)
    settings.sync()


def _scale_css(css, zoom):
    return re.sub(r"font-size:\s*(\d+)px",
                  lambda match: f"font-size: {max(12, round(int(match.group(1)) * zoom))}px",
                  css)


def apply_theme(app: QApplication, scale=None, font_family=None):
    """Set readable Thai typography throughout tables, forms, navigation and dialogs."""
    scale = current_scale() if scale is None else scale
    if scale not in SCALE_OPTIONS:
        raise ValueError("Unsupported zoom")
    font_family = current_font() if font_family is None else font_family
    if font_family not in FONT_OPTIONS:
        raise ValueError("Unsupported font")
    app.setFont(QFont(font_family, max(11, round(12 * scale))))
    css = r"""
    QWidget { background: #09111F; color: #F1F7FE;
              font-family: "Leelawadee UI", "Segoe UI", sans-serif; font-size: 17px; }
    QWidget#main, QWidget#content, QWidget#page { background: #09111F; }
    QFrame#sidebar { background: #0C1626; border-right: 1px solid #263C54; }
    QFrame#topbar { background: #0E1B2D; border: 1px solid #263C54;
                    border-radius: 15px; }
    QFrame#panel, QFrame#metric, QFrame#tablePanel, QFrame#formPanel {
        background: #111F32; border: 1px solid #263C54; border-radius: 16px;
    }
    QFrame#metric:hover { border: 1px solid #36A8FF; background: #16273C; }
    QLabel { border: none; background: transparent; }
    QLabel#logo { color: #36A8FF; font-size: 26px; font-weight: 800; }
    QLabel#sideTitle { color: #E7F2FF; font-size: 22px; font-weight: 800; }
    QLabel#sidebarCaption { color: #C4D3E6; font-size: 14px; }
    QLabel#pageTitle { color: #EDF6FF; font-size: 28px; font-weight: 800; }
    QLabel#sectionTitle { color: #E7F2FF; font-size: 20px; font-weight: 700; }
    QLabel#caption { color: #C7D7E9; font-size: 15px; }
    QLabel#kpiValue { font-size: 34px; font-weight: 800; }
    QLabel#kpiName { font-size: 17px; color: #D4E0F0; }
    QLabel#hint { color: #C4D3E6; font-size: 14px; }
    QLabel#status { color: #D4E0F0; font-size: 15px; }
    QLabel#badge { color: #29D7A3; background: #163B3B; border-radius: 8px;
                   padding: 5px 11px; font-size: 14px; font-weight: 700; }
    QPushButton {
        background: #1B3049; border: 1px solid #35506B; color: #E7F2FF;
        padding: 12px 17px; border-radius: 10px; font-weight: 700; min-height: 20px;
    }
    QPushButton:hover { background: #254261; border-color: #36A8FF; }
    QPushButton:pressed { background: #16436D; }
    QPushButton:disabled { background: #142237; color: #94A8BD; border-color: #223448; }
    QPushButton#primary {
        background: #0877C7; color: white; border: 1px solid #26ACFF;
    }
    QPushButton#primary:hover { background: #1294EB; }
    QPushButton#success {
        background: #075D50; color: #CBFFEA; border: 1px solid #16896D;
    }
    QPushButton#danger {
        background: #482637; color: #FFDDE5; border: 1px solid #844257;
    }
    QPushButton#nav {
        background: transparent; color: #C4D3E6; border: 1px solid transparent;
        text-align: left; padding: 15px 18px; border-radius: 11px; font-size: 17px;
        font-weight: 600;
    }
    QPushButton#nav:hover { background: #172942; color: #EEF6FF; }
    QPushButton#nav[active="true"] {
        background: #163858; color: #55BBFF; border: 1px solid #27577A;
        border-left: 4px solid #36A8FF; font-weight: 800;
    }
    QLineEdit, QComboBox, QPlainTextEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
        background: #101D2E; color: #F1F7FF; border: 1px solid #34506C;
        padding: 9px 12px; border-radius: 9px; min-height: 23px;
        selection-background-color: #187BC0;
    }
    QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus, QTextEdit:focus {
        border: 1px solid #42B5FF; background: #12263B;
    }
    QComboBox::drop-down { border: none; width: 28px; }
    QComboBox QAbstractItemView { background: #122238; color: #EFF5FF;
                                   selection-background-color: #1E6094; }
    QTableWidget, QTableView {
        background: #101D2F; alternate-background-color: #142339;
        gridline-color: #243A52; border: 1px solid #263C54;
        border-radius: 9px; selection-background-color: #1B5789;
        selection-color: white; font-size: 17px;
    }
    QHeaderView::section { background: #1D314A; color: #CBDBED;
                           border: none; border-right: 1px solid #2D435C;
                           border-bottom: 1px solid #35516D;
                           padding: 15px 10px; font-size: 15px; font-weight: 700; }
    QTableCornerButton::section { background: #1D314A; border: none; }
    QProgressBar { background: #20344A; border: none; border-radius: 5px;
                   color: white; text-align: center; min-height: 10px; }
    QProgressBar::chunk { background: #29D7A3; border-radius: 5px; }
    QScrollBar:vertical { background: #0C1A2B; width: 11px; }
    QScrollBar::handle:vertical { background: #344D68; border-radius: 5px; min-height: 25px; }
    QScrollBar:horizontal { background: #0C1A2B; height: 11px; }
    QScrollBar::handle:horizontal { background: #344D68; border-radius: 5px; min-width: 25px; }
    QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
    QDialog { background: #0C192B; }
    QDialogButtonBox { background: transparent; }
    QMessageBox { background: #0C192B; }
    QToolTip { background: #14263D; color: white; border: 1px solid #3E638A; }
    QSplitter::handle { background: #253950; }
    """
    css = css.replace('"Leelawadee UI", "Segoe UI", sans-serif',
                      f'"{font_family}", "Leelawadee UI", "Segoe UI", sans-serif')
    app.setStyleSheet(_scale_css(css, scale))
    return {"scale": scale, "font_family": font_family}
