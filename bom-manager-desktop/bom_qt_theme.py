"""Industrial Dark visual design system for the Qt desktop edition."""
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

COLORS = {
    "bg": "#09111F", "sidebar": "#0C1626", "panel": "#111F32",
    "panel2": "#16273C", "line": "#263C54", "text": "#E7F2FF",
    "muted": "#9CB0C8", "blue": "#36A8FF", "green": "#29D7A3",
    "amber": "#F5BA55", "red": "#FF7891", "purple": "#AB99FF",
}


def apply_theme(app: QApplication):
    app.setFont(QFont("Leelawadee UI", 11))
    app.setStyleSheet(r"""
    QWidget { background: #09111F; color: #E7F2FF;
              font-family: "Leelawadee UI", "Segoe UI", sans-serif; font-size: 14px; }
    QWidget#main, QWidget#content, QWidget#page { background: #09111F; }
    QFrame#sidebar { background: #0C1626; border-right: 1px solid #263C54; }
    QFrame#topbar { background: #0E1B2D; border: 1px solid #263C54;
                    border-radius: 15px; }
    QFrame#panel, QFrame#metric, QFrame#tablePanel, QFrame#formPanel {
        background: #111F32; border: 1px solid #263C54; border-radius: 16px;
    }
    QFrame#metric:hover { border: 1px solid #36A8FF; background: #16273C; }
    QLabel { border: none; background: transparent; }
    QLabel#logo { color: #36A8FF; font-size: 24px; font-weight: 800; }
    QLabel#sideTitle { color: #E7F2FF; font-size: 19px; font-weight: 800; }
    QLabel#sidebarCaption { color: #9CB0C8; font-size: 12px; }
    QLabel#pageTitle { color: #EDF6FF; font-size: 25px; font-weight: 800; }
    QLabel#sectionTitle { color: #E7F2FF; font-size: 17px; font-weight: 700; }
    QLabel#caption { color: #A2B6CF; font-size: 13px; }
    QLabel#kpiValue { font-size: 32px; font-weight: 800; }
    QLabel#kpiName { font-size: 14px; color: #AFC2D8; }
    QLabel#hint { color: #96AFC9; font-size: 12px; }
    QLabel#status { color: #AFC2D8; font-size: 13px; }
    QLabel#badge { color: #29D7A3; background: #163B3B; border-radius: 8px;
                   padding: 5px 11px; font-size: 12px; font-weight: 700; }
    QPushButton {
        background: #1B3049; border: 1px solid #35506B; color: #E7F2FF;
        padding: 11px 17px; border-radius: 10px; font-weight: 700; min-height: 20px;
    }
    QPushButton:hover { background: #254261; border-color: #36A8FF; }
    QPushButton:pressed { background: #16436D; }
    QPushButton:disabled { background: #142237; color: #657C95; border-color: #223448; }
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
        background: transparent; color: #9CB0C8; border: 1px solid transparent;
        text-align: left; padding: 14px 18px; border-radius: 11px; font-size: 15px;
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
        selection-color: white; font-size: 14px;
    }
    QHeaderView::section { background: #1D314A; color: #CBDBED;
                           border: none; border-right: 1px solid #2D435C;
                           border-bottom: 1px solid #35516D;
                           padding: 11px 10px; font-size: 13px; font-weight: 700; }
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
    """)
