"""Crane Vehicle BOM Manager — Industrial Dark / PySide6 desktop UI.

Retains existing bom.json data, GitHub credential storage, exports and signed-size
SHA256 verified updater. Qt widgets are real/editable, not a screenshot.
"""
import base64
import copy
import json
import os
import shutil
import subprocess
import sys
import time
import threading
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import keyring
from PySide6.QtCore import QThread, Signal, Qt, QRectF, QSettings, QTimer
from PySide6.QtGui import QBrush, QColor, QFont, QPen, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout,
    QFrame, QGraphicsScene, QGraphicsView, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QMainWindow, QMessageBox, QTabWidget,
    QPlainTextEdit, QProgressBar, QPushButton, QScrollArea, QSizePolicy,
    QStackedWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)

import bom_core
import bom_categories
import bom_reports
import bom_official_reports
import bom_debug
import bom_qt_theme as theme
import updater


OWNER = "tronza449-dot"
REPO = "crane-vehicle-engineering-tool-updates"
SERVICE = "CraneVehicleBOMManager"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
BOM_PATH = "bom-manager/bom.json"
BOM_URL = f"{API}/contents/{BOM_PATH}"
VERSION = updater.current_version()

ITEM_FIELDS = [
    ("category", "หมวดอุปกรณ์"), ("name", "อุปกรณ์ / รุ่น"),
    ("partNumber", "Part Number"), ("spec", "รายละเอียด / สเปก"),
    ("qty", "จำนวน"), ("unit", "หน่วย"), ("unitPrice", "ราคา/หน่วย (บาท)"),
    ("status", "สถานะการเลือก"), ("supplier", "ร้านค้า / ผู้ขาย"),
    ("link", "ลิงก์สินค้า"), ("connection", "การต่อ / GPIO / สื่อสาร"),
    ("notes", "หมายเหตุ"),
]
WIRE_FIELDS = [
    ("from", "ต้นทาง / Terminal"), ("to", "ปลายทาง / Terminal"),
    ("fromItemId", "BOM ID ต้นทาง"), ("toItemId", "BOM ID ปลายทาง"),
    ("signal", "สัญญาณ"), ("voltage", "แรงดัน"),
    ("cable", "ชนิด / ขนาดสาย"), ("protection", "ฟิวส์ / การป้องกัน"),
    ("status", "สถานะ"), ("notes", "หมายเหตุ"),
]
PURCHASE_FIELDS = [
    ("itemId", "BOM ID อ้างอิง"), ("description", "รายการสั่งซื้อ"),
    ("supplier", "ผู้ขาย"), ("qty", "จำนวน"),
    ("unitPrice", "ราคา/หน่วย (บาท)"), ("status", "สถานะ"),
    ("po", "เลขอ้างอิง PO"), ("dueDate", "กำหนดรับ YYYY-MM-DD"),
    ("link", "ลิงก์ร้านค้า"), ("notes", "หมายเหตุ"),
]
FIELD_SET = {"items": ITEM_FIELDS, "wiring": WIRE_FIELDS, "purchases": PURCHASE_FIELDS}
WIRE_STATUS = ["รอตรวจสอบ", "ตรวจสอบแล้ว", "แก้ไขแบบ", "ยกเลิก"]
PURCHASE_STATUS = ["วางแผน", "ขอราคา", "สั่งแล้ว", "ได้รับแล้ว", "ยกเลิก"]
MULTILINE = {"spec", "connection", "notes"}


def money(value):
    return "—" if value is None or str(value).strip() == "" else f"{float(value):,.2f}"


def github_api(method="GET", payload=None, token=None, url=BOM_URL):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "CraneVehicleBOMManager/Qt",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def friendly_error(exc):
    if isinstance(exc, HTTPError):
        if exc.code in (409, 412, 422):
            return "GitHub มีข้อมูลใหม่กว่าที่โหลดไว้ (conflict)\nกรุณาสำรอง JSON ก่อน แล้วโหลดล่าสุดเพื่อตรวจความแตกต่าง"
        if exc.code == 401:
            return "GitHub Token ไม่ถูกต้องหรือหมดอายุ (401)"
        if exc.code == 403:
            return "GitHub ไม่อนุญาต หรือเกิน Rate Limit (403)\nตรวจสิทธิ์ Contents: Read and write"
        return f"GitHub HTTP {exc.code}: {exc.reason}"
    if isinstance(exc, URLError):
        return "ไม่สามารถเชื่อมต่ออินเทอร์เน็ตหรือ GitHub ได้"
    return str(exc)


class Job(QThread):
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, work, parent=None, reporter=None, context="background"):
        super().__init__(parent)
        self.work = work
        self.reporter = reporter
        self.context = context

    def run(self):
        try:
            self.succeeded.emit(self.work())
        except Exception as exc:
            if self.reporter:
                self.reporter.exception(self.context, "JOB_EXCEPTION", exc)
            self.failed.emit(friendly_error(exc))


class Card(QFrame):
    clicked = Signal()

    def __init__(self, label, value="—", tint="#36A8FF", symbol="▣", parent=None):
        super().__init__(parent)
        self.setObjectName("metric")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(142)
        box = QVBoxLayout(self)
        box.setContentsMargins(20, 15, 20, 17)
        box.setSpacing(6)
        top = QHBoxLayout()
        icon = QLabel(symbol)
        icon.setFont(QFont("Segoe UI Symbol", 19))
        icon.setStyleSheet(f"color:{tint};")
        top.addWidget(icon)
        top.addStretch()
        arrow = QLabel("↗")
        arrow.setStyleSheet("color: #8EAAC9; font-size: 18px;")
        top.addWidget(arrow)
        box.addLayout(top)
        caption = QLabel(label)
        caption.setObjectName("kpiName")
        caption.setWordWrap(True)
        box.addWidget(caption)
        self.figure = QLabel(value)
        self.figure.setObjectName("kpiValue")
        self.figure.setStyleSheet(f"color: {tint};")
        box.addWidget(self.figure)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class RecordDialog(QDialog):
    def __init__(self, title, fields, values=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(640, 580)
        self.resize(770, 650)
        self.values = values or {}
        self.widgets = {}
        outer = QVBoxLayout(self)
        outer.setSpacing(14)
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        outer.addWidget(heading)
        self.tabs = None
        is_bom = title in ("เพิ่มอุปกรณ์", "แก้ไขอุปกรณ์")
        groups = {}
        if is_bom:
            self.tabs = QTabWidget()
            for name, keys in (
                ("ข้อมูลหลัก", ("category", "name", "partNumber", "qty", "unit", "status")),
                ("สเปกและการเชื่อมต่อ", ("spec", "connection")),
                ("ราคาและร้านค้า", ("unitPrice", "supplier", "link")),
                ("หมายเหตุ", ("notes",)),
            ):
                page = QWidget()
                layout = QFormLayout(page)
                layout.setContentsMargins(17, 18, 17, 18)
                layout.setFieldGrowthPolicy(
                    QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
                layout.setVerticalSpacing(16)
                layout.setHorizontalSpacing(17)
                for field in keys:
                    groups[field] = layout
                self.tabs.addTab(page, name)
            outer.addWidget(self.tabs, 1)
        else:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            content = QWidget()
            form = QFormLayout(content)
            form.setFieldGrowthPolicy(
                QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
            form.setVerticalSpacing(13)
            form.setHorizontalSpacing(18)
        for key, label in fields:
            val = self.values.get(key)
            if key == "category":
                control = QComboBox()
                control.setEditable(False)
                control.addItems(list(bom_categories.CATEGORY_OPTIONS))
                # Keep categories from older BOM files selectable, never discard them.
                categories_in_document = []
                if parent is not None and hasattr(parent, "payload"):
                    categories_in_document = bom_categories.sorted_categories(
                        item.get("category") for item in
                        parent.payload.get("items", []))
                for category in categories_in_document:
                    if control.findText(category) < 0:
                        control.addItem(category)
                current = str(val or bom_categories.UNCATEGORIZED)
                if control.findText(current) < 0:
                    control.addItem(current)
                control.setCurrentText(current)
                control.setToolTip("คลิกเลือกหมวดอุปกรณ์จากรายการ ไม่ต้องพิมพ์เอง")
            elif key == "itemId" and "จัดซื้อ" in title:
                control = QComboBox()
                control.setEditable(False)
                control.addItem("— เลือกอุปกรณ์จาก BOM —", "")
                for bom_item in (parent.payload.get("items", []) if parent else []):
                    item_id = str(bom_item.get("id") or "").strip()
                    if item_id:
                        control.addItem(
                            f'{item_id}  |  {bom_item.get("name") or "ไม่ระบุชื่อ"}', item_id)
                old_id = str(val or "").strip()
                matched = control.findData(old_id)
                if matched == -1 and old_id:
                    control.addItem(f"{old_id}  |  รายการอ้างอิงเก่า", old_id)
                    matched = control.findData(old_id)
                control.setCurrentIndex(max(0, matched))
                control.setToolTip("เลือกรายการอุปกรณ์ แล้วโปรแกรมจะดึงรายละเอียดจาก BOM อัตโนมัติ")
            elif key in MULTILINE:
                control = QPlainTextEdit()
                control.setPlainText("" if val is None else str(val))
                control.setMinimumHeight(85)
            elif key == "status" and title.startswith(("เพิ่มจุดต่อ", "แก้ไขจุดต่อ")):
                control = QComboBox()
                control.addItems(WIRE_STATUS)
                control.setCurrentText(str(val or WIRE_STATUS[0]))
            elif key == "status" and "จัดซื้อ" in title:
                control = QComboBox()
                control.addItems(PURCHASE_STATUS)
                control.setCurrentText(str(val or PURCHASE_STATUS[0]))
            else:
                control = QLineEdit("" if val is None else str(val))
                if key == "unitPrice":
                    control.setPlaceholderText("เว้นว่างหากยังไม่ทราบราคา")
                if key == "qty":
                    control.setPlaceholderText("จำนวนต้องมากกว่า 0")
            self.widgets[key] = control
            (groups.get(key) if is_bom else form).addRow(QLabel(label), control)
        if "จัดซื้อ" in title and "itemId" in self.widgets:
            self.widgets["itemId"].currentIndexChanged.connect(
                lambda _: self._fill_purchase_from_bom(parent))
            summary = QLabel(
                "เลือกรายการจาก BOM ด้านบนเพื่อดึงข้อมูลตั้งต้น จากนั้นแก้จำนวน "
                "ราคา และผู้ขายตามใบเสนอราคาจริงได้")
            summary.setWordWrap(True)
            summary.setObjectName("hint")
            form.addRow(summary)
        if not is_bom:
            scroll.setWidget(content)
            outer.addWidget(scroll, 1)
        actions = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        actions.button(QDialogButtonBox.StandardButton.Save).setText("บันทึกข้อมูล")
        actions.button(QDialogButtonBox.StandardButton.Cancel).setText("ยกเลิก")
        actions.accepted.connect(self.accept)
        actions.rejected.connect(self.reject)
        outer.addWidget(actions)

    def _fill_purchase_from_bom(self, owner):
        """Copy BOM values into the purchase draft, never editing the BOM row."""
        if owner is None or not hasattr(owner, "payload"):
            return
        item_id = str(self.widgets["itemId"].currentData() or "")
        if not item_id:
            return
        item = next((entry for entry in owner.payload.get("items", [])
                     if str(entry.get("id")) == item_id), None)
        if item is None:
            return
        for field, source in (("description", "name"), ("qty", "qty"),
                              ("unitPrice", "unitPrice"), ("supplier", "supplier"),
                              ("link", "link")):
            widget = self.widgets.get(field)
            if isinstance(widget, QLineEdit):
                value = item.get(source)
                widget.setText("" if value is None else str(value))

    def get_values(self):
        data = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, QPlainTextEdit):
                val = widget.toPlainText()
            elif isinstance(widget, QComboBox):
                val = (str(widget.currentData() or "") if key == "itemId"
                       else widget.currentText())
            else:
                val = widget.text()
            data[key] = val.strip()
        return data


class ReportOptionsDialog(QDialog):
    """Simple report metadata form; saved in app settings, not in BOM JSON."""
    FIELDS = (
        ("author", "ผู้จัดทำ"),
        ("institution", "มหาวิทยาลัย / สถาบัน"),
        ("document_no", "เลขที่เอกสาร"),
        ("revision", "Revision"),
    )

    def __init__(self, document, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ตั้งค่ารายงานสำหรับส่งอาจารย์")
        self.setMinimumWidth(530)
        settings = QSettings("CraneVehicle", "BOMManager")
        self.inputs = {}
        form = QVBoxLayout(self)
        form.setContentsMargins(23, 23, 23, 23)
        title = QLabel("จัดทำรายงาน BOM แบบทางการ")
        title.setObjectName("sectionTitle")
        form.addWidget(title)
        hint = QLabel("กรอกข้อมูลหน้ารายงานครั้งเดียว โปรแกรมจะจำค่าไว้สำหรับครั้งถัดไป")
        hint.setObjectName("caption")
        hint.setWordWrap(True)
        form.addWidget(hint)
        grid = QFormLayout()
        grid.setVerticalSpacing(13)
        for key,label in self.FIELDS:
            default = "BOM-001" if key == "document_no" else "00" if key == "revision" else ""
            control = QLineEdit(str(settings.value("report/"+key, default)))
            control.setMinimumWidth(305)
            if key in ("author", "institution"):
                control.setPlaceholderText("กรอกข้อมูลสำหรับหน้ารายงาน")
            self.inputs[key] = control
            grid.addRow(label, control)
        form.addLayout(grid)
        note = QLabel("ใช้ข้อมูล BOM ปัจจุบัน ราคาที่ยังไม่ทราบจะแสดงเป็น — "
                      "และไม่ถูกรวมเป็นราคาศูนย์")
        note.setWordWrap(True)
        note.setObjectName("hint")
        form.addWidget(note)
        controls = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel)
        controls.button(QDialogButtonBox.StandardButton.Ok).setText("ต่อไป: เลือกที่บันทึก")
        controls.button(QDialogButtonBox.StandardButton.Cancel).setText("ยกเลิก")
        controls.accepted.connect(self.accept)
        controls.rejected.connect(self.reject)
        form.addWidget(controls)

    def values(self):
        settings = QSettings("CraneVehicle", "BOMManager")
        result = {key:control.text().strip() for key,control in self.inputs.items()}
        for key,value in result.items():
            settings.setValue("report/"+key, value)
        settings.sync()
        return result


class BOMWindow(QMainWindow):
    def __init__(self, auto_load=True, debugger=None):
        super().__init__()
        self.debugger = debugger or bom_debug.DebugReporter(version=VERSION)
        self.setWindowTitle(f"Crane Vehicle BOM Manager — Minimal Engineering v{VERSION}")
        self.resize(1580, 960)
        self.setMinimumSize(1180, 750)
        self.payload = {"schemaVersion": 1, "project": "รถไฟฟ้าพร้อมเครน",
                        "currency": "THB", "items": []}
        self.sha = None
        self.dirty = False
        self.revision = 0
        self.edit_dialog_active = False
        self.busy = False
        self.jobs = set()
        try:
            self.token = keyring.get_password(SERVICE, "github-token")
        except Exception as exc:
            self.token = None
            self.debugger.exception("credentials", "CREDENTIAL_READ_FAILED", exc)
        if self.token:
            self.debugger.register_secret(self.token)
        self.update_info = None
        self.downloading = False
        self.cancel_download = threading.Event()
        self.cache_path = self._cache_path()
        self.nav_buttons = []
        self.zoom_factor = theme.current_scale()
        self.last_git_ok = None
        self.last_github_sync_at = None
        self.sync_paused_conflict = False
        self.auto_sync_enabled = QSettings("CraneVehicle", "BOMManager").value(
            "sync/auto_enabled", True, type=bool)
        self.auto_sync_delay_ms = 90_000  # debounce bursts of user edits
        self.auto_sync_timer = QTimer(self)
        self.auto_sync_timer.setSingleShot(True)
        self.auto_sync_timer.timeout.connect(self._autosync_if_needed)
        self.auto_sync_retry_timer = QTimer(self)
        self.auto_sync_retry_timer.setInterval(180_000)
        self.auto_sync_retry_timer.timeout.connect(self._autosync_if_needed)
        self.auto_sync_retry_timer.start()
        # GitHub is the shared source of truth across PCs. Poll only when
        # this machine has no unsynced edits, to avoid overwriting a draft.
        self.remote_refresh_timer = QTimer(self)
        self.remote_refresh_timer.setInterval(120_000)
        self.remote_refresh_timer.timeout.connect(self._refresh_remote_if_clean)
        self.remote_refresh_timer.start()
        self._make_ui()
        self._setup_readability()
        self._read_cache()
        self.render_all()
        # A crash leaves a durable local draft. Retry safely using GitHub SHA,
        # never replace a recovered dirty draft with a remote download.
        if self.dirty:
            self._schedule_auto_sync()
        self.debugger.event("INFO", "application", "APP_STARTED",
                            f"Minimal Engineering desktop v{VERSION} started")
        if auto_load:
            if self.dirty:
                self.set_status("กู้คืนข้อมูลฉบับร่างที่ยังไม่ได้บันทึก GitHub — กรุณาตรวจสอบก่อนโหลดทับ")
            else:
                self.load_remote(silent=True)
            # Start update checking after event loop has begun; network is in a worker.
            QTimer.singleShot(1500, lambda: self.check_version(silent=True))

    @staticmethod
    def _cache_path():
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".local" / "share")
        folder = Path(base) / "CraneVehicleBOMManager"
        folder.mkdir(parents=True, exist_ok=True)
        return folder / "draft.json"

    def _read_cache(self):
        try:
            data = json.loads(self.cache_path.read_text(encoding="utf-8"))
            bom_core.ensure_doc(data["payload"])
            self.payload = data["payload"]
            self.sha = data.get("sha")
            self.dirty = bool(data.get("dirty"))
        except (OSError, KeyError, TypeError, ValueError):
            return

    def _write_cache(self):
        temp = self.cache_path.with_suffix(".tmp")
        data = {"payload": self.payload, "sha": self.sha, "dirty": self.dirty,
                "savedAt": datetime.now(timezone.utc).isoformat()}
        try:
            with open(temp, "w", encoding="utf-8") as output:
                json.dump(data, output, ensure_ascii=False, indent=2)
                output.flush()
                os.fsync(output.fileno())
            os.replace(temp, self.cache_path)
        except OSError as exc:
            self.set_status(f"เตือน: เก็บฉบับร่างในเครื่องไม่สำเร็จ: {exc}")

    def _button(self, text, callback, role=None):
        widget = QPushButton(text)
        if role:
            widget.setObjectName(role)
        widget.clicked.connect(callback)
        return widget

    @staticmethod
    def _label(text, object_name=None):
        label = QLabel(text)
        if object_name:
            label.setObjectName(object_name)
        return label

    def _make_ui(self):
        root = QWidget()
        root.setObjectName("main")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(282)
        self.sidebar_frame = sidebar
        left = QVBoxLayout(sidebar)
        left.setContentsMargins(17, 26, 17, 20)
        left.setSpacing(10)
        left.addWidget(self._label("◈   BOM Manager", "logo"))
        left.addWidget(self._label("CRANE VEHICLE PROJECT", "sidebarCaption"))
        left.addSpacing(18)
        left.addWidget(self._label("เมนูหลัก / WORKSPACE", "sidebarCaption"))
        labels = [
            "⌂    หน้าหลัก",
            "▤    รายการอุปกรณ์ (BOM)",
            "⌁    สายไฟและการเชื่อมต่อ",
            "▣    จัดซื้อและราคา",
            "⇩    รายงาน (PDF / Excel)",
            "⚙    ตรวจสอบระบบ",
        ]
        for i, name in enumerate(labels):
            button = self._button(name, lambda _checked=False, n=i: self.show_page(n))
            button.setObjectName("nav")
            button.setProperty("active", i == 0)
            button.setMinimumHeight(48)
            left.addWidget(button)
            self.nav_buttons.append(button)
        left.addStretch()
        left.addWidget(self._label("การแสดงผล / READABILITY", "sidebarCaption"))
        left.addWidget(self._label("ขนาดตัวอักษร", "caption"))
        self.font_scale_selector = QComboBox()
        for value, caption in zip(theme.SCALE_OPTIONS, theme.SCALE_LABELS):
            self.font_scale_selector.addItem(caption, value)
        self.font_scale_selector.setCurrentIndex(
            theme.SCALE_OPTIONS.index(theme.current_scale()))
        self.font_scale_selector.currentIndexChanged.connect(self.change_font_scale)
        self.font_scale_selector.setToolTip("ปรับตัวอักษรทั้งโปรแกรม และจำค่าครั้งถัดไป")
        left.addWidget(self.font_scale_selector)
        left.addWidget(self._label("ฟอนต์ภาษาไทย", "caption"))
        self.font_family_selector = QComboBox()
        self.font_family_selector.addItems(list(theme.FONT_OPTIONS))
        self.font_family_selector.setCurrentText(theme.current_font())
        self.font_family_selector.currentTextChanged.connect(self.change_font_family)
        left.addWidget(self.font_family_selector)
        left.addWidget(self._label("Ctrl + / Ctrl -  ปรับขนาด", "sidebarCaption"))
        left.addSpacing(13)
        left.addWidget(self._label("SYSTEM STATUS", "sidebarCaption"))
        self.connection = self._label("●  ใช้งานในเครื่องได้", "sideStatus")
        left.addWidget(self.connection)
        version = self._label(f"Minimal Engineering  ·  v{VERSION}", "sidebarCaption")
        left.addWidget(version)
        layout.addWidget(sidebar)

        content = QWidget()
        content.setObjectName("content")
        right = QVBoxLayout(content)
        right.setContentsMargins(25, 22, 25, 16)
        right.setSpacing(15)
        top = QFrame()
        top.setObjectName("topbar")
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(20, 15, 20, 15)
        top_layout.setSpacing(8)
        heading_row = QHBoxLayout()
        heading_row.setSpacing(16)
        titles = QVBoxLayout()
        titles.setSpacing(4)
        titles.addWidget(self._label("BOM Manager  /  Engineering Workspace", "sectionTitle"))
        self.top_project_label = self._label("กำลังโหลดข้อมูลโครงการ…", "caption")
        titles.addWidget(self.top_project_label)
        self.cloud_header_status = self._label(
            "GitHub Cloud: กำลังตรวจสอบการเชื่อมต่อ", "caption")
        titles.addWidget(self.cloud_header_status)
        heading_row.addLayout(titles, 1)

        # Keep the updater available on EVERY page, not hidden under Reports/GitHub.
        update_controls = QVBoxLayout()
        update_controls.setSpacing(5)
        update_heading = QHBoxLayout()
        update_heading.setSpacing(9)
        self.version_label = self._label(f"เวอร์ชัน v{VERSION}", "caption")
        update_heading.addWidget(self.version_label)
        self.update_btn = self._button("ตรวจสอบอัปเดต", self.check_version)
        self.update_btn.setToolTip("ตรวจสอบเวอร์ชันใหม่จาก GitHub")
        update_heading.addWidget(self.update_btn)
        update_controls.addLayout(update_heading)
        self.install_btn = self._button("ดาวน์โหลดและอัปเดต", self.install_update, "success")
        self.install_btn.setEnabled(False)
        self.install_btn.setVisible(False)
        self.install_btn.setToolTip("จะเปิดได้เมื่อพบ BOM Manager เวอร์ชันใหม่")
        update_controls.addWidget(self.install_btn)
        heading_row.addLayout(update_controls)
        top_layout.addLayout(heading_row)
        action_row = QHBoxLayout()
        action_row.setSpacing(9)
        action_row.addStretch()
        action_row.addWidget(self._button("+ เพิ่มอุปกรณ์",
                                           lambda: self.edit_record("items"), "primary"))
        action_row.addWidget(self._button("ส่งออก PDF / Excel",
                                           lambda: self.show_page(4)))
        action_row.addWidget(self._button("รับข้อมูล GitHub ล่าสุด",
                                           self.load_remote))
        self.sync_btn = self._button("ซิงก์ข้อมูลตอนนี้", self.sync_now, "primary")
        self.sync_btn.setToolTip(
            "หากมีข้อมูลแก้ไขจะบันทึกไป GitHub; หากไม่มีจะดึงข้อมูลใหม่จาก GitHub")
        action_row.addWidget(self.sync_btn)
        top_layout.addLayout(action_row)
        right.addWidget(top)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._scrolling_dashboard(self._build_dashboard()))
        self.stack.addWidget(self._build_bom())
        self.stack.addWidget(self._build_wiring())
        self.stack.addWidget(self._build_purchases())
        self.stack.addWidget(self._scrolling_dashboard(self._build_sync()))
        self.stack.addWidget(self._build_diagnostics())
        right.addWidget(self.stack, 1)

        footer = QHBoxLayout()
        self.status = self._label("พร้อมใช้งาน", "status")
        footer.addWidget(self.status, 1)
        self.data_status = self._label("GitHub · ยังไม่ได้โหลด", "status")
        footer.addWidget(self.data_status)
        right.addLayout(footer)
        layout.addWidget(content, 1)

    @staticmethod
    def _scrolling_dashboard(page):
        """Keep the enlarged dashboard usable on 768px-high laptops."""
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.Shape.NoFrame)
        area.setStyleSheet("QScrollArea { border: 0; background: #F5F8FC; }")
        area.setWidget(page)
        return area

    def _setup_readability(self):
        for shortcut, slot in (
            ("Ctrl++", self.increase_font_scale),
            ("Ctrl+=", self.increase_font_scale),
            ("Ctrl+-", self.decrease_font_scale),
            ("Ctrl+0", self.reset_font_scale),
        ):
            action = QShortcut(QKeySequence(shortcut), self)
            action.activated.connect(slot)
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(lambda: self.show_page(4))
        self._apply_readability_metrics()

    def _apply_readability_metrics(self):
        """Spacing follows text zoom to prevent Thai glyph clipping in rows."""
        zoom = self.zoom_factor
        self.sidebar_frame.setFixedWidth(round(245 * zoom))
        row_h = round(53 * zoom)
        header_h = round(49 * zoom)
        for table in (self.category_table, self.bom_table, self.wire_table,
                      self.purchase_table, self.debug_checks, self.debug_events):
            table.verticalHeader().setDefaultSectionSize(row_h)
            table.horizontalHeader().setFixedHeight(header_h)
        for card in self.cards.values():
            card.setMinimumHeight(round(112 * zoom))
        for button in getattr(self, "category_buttons", {}).values():
            button.setMinimumHeight(round(67 * zoom))

    def change_font_scale(self, index):
        if index < 0:
            return
        scale = self.font_scale_selector.itemData(index)
        if scale is None:
            return
        self.zoom_factor = float(scale)
        theme.save_appearance(scale=self.zoom_factor)
        theme.apply_theme(QApplication.instance(), scale=self.zoom_factor)
        self._apply_readability_metrics()

    def change_font_family(self, family):
        if family not in theme.FONT_OPTIONS:
            return
        theme.save_appearance(font_family=family)
        theme.apply_theme(QApplication.instance(), scale=self.zoom_factor,
                          font_family=family)
        self._apply_readability_metrics()

    def increase_font_scale(self):
        index = self.font_scale_selector.currentIndex()
        if index < self.font_scale_selector.count()-1:
            self.font_scale_selector.setCurrentIndex(index+1)

    def decrease_font_scale(self):
        index = self.font_scale_selector.currentIndex()
        if index > 0:
            self.font_scale_selector.setCurrentIndex(index-1)

    def reset_font_scale(self):
        self.font_scale_selector.setCurrentIndex(
            theme.SCALE_OPTIONS.index(theme.DEFAULT_SCALE))

    def _page(self, title, caption):
        page = QWidget()
        page.setObjectName("page")
        box = QVBoxLayout(page)
        box.setContentsMargins(1, 3, 1, 2)
        box.setSpacing(14)
        box.addWidget(self._label(title, "pageTitle"))
        box.addWidget(self._label(caption, "caption"))
        return page, box

    def _panel(self, title, parent_layout, stretch=0):
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 17, 18, 19)
        layout.setSpacing(12)
        layout.addWidget(self._label(title, "sectionTitle"))
        parent_layout.addWidget(panel, stretch)
        return layout

    @staticmethod
    def _table(headers, stretch_col=0):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(58)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setSectionResizeMode(
            stretch_col, QHeaderView.ResizeMode.Stretch)
        table.setSortingEnabled(False)
        return table

    def filter_category(self, category):
        self.show_page(1)
        self.search.clear()
        self.price_filter.setCurrentText("ทุกราคา")
        if self.category.findText(category) >= 0:
            self.category.setCurrentText(category)
        else:
            self.category.setCurrentIndex(0)
            self.set_status(f"ยังไม่มีอุปกรณ์ในหมวด {category}")

    def _build_dashboard(self):
        page, body = self._page(
            "ภาพรวมโครงการ", "PROJECT OVERVIEW   /   จำนวนอุปกรณ์ ราคา และความครบถ้วนของข้อมูล")

        hero = QFrame()
        hero.setObjectName("hero")
        line = QHBoxLayout(hero)
        line.setContentsMargins(23, 19, 23, 19)
        heading = QVBoxLayout()
        heading.setSpacing(6)
        heading.addWidget(self._label("CRANE VEHICLE  /  ENGINEERING BOM", "caption"))
        self.hero_project_label = self._label("โครงการรถขนซากสัตว์พร้อมเครน", "heroTitle")
        self.hero_project_label.setWordWrap(True)
        heading.addWidget(self.hero_project_label)
        heading.addWidget(self._label(
            "ดูข้อมูลอุปกรณ์ในระบบ แก้ไขรายการ แล้วส่งออกรายงาน PDF / Excel",
            "heroSubtitle"))
        line.addLayout(heading, 1)
        quick = QVBoxLayout()
        quick.addWidget(self._button("เปิดรายการอุปกรณ์  →",
                                     lambda: self.show_page(1), "primary"))
        quick.addWidget(self._button("ส่งออกรายงาน", lambda: self.show_page(4)))
        line.addLayout(quick)
        body.addWidget(hero)

        board = QGridLayout()
        board.setHorizontalSpacing(12)
        board.setVerticalSpacing(12)
        metrics = [
            ("items", "อุปกรณ์ทั้งหมด", "#1768D2", "▣", "items"),
            ("priced", "มีราคาแล้ว", "#13835C", "✓", "priced"),
            ("missing", "ยังไม่มีราคา", "#B74A37", "!", "missing"),
            ("known_cost", "มูลค่าที่ทราบ (บาท)", "#7652BB", "฿", "priced"),
            ("wires", "รายการเชื่อมต่อสาย", "#377FB5", "⌁", "wiring"),
            ("purchase_count", "รายการจัดซื้อ", "#A46B20", "▤", "purchases"),
        ]
        self.cards = {}
        for index, (key, label, tint, symbol, target) in enumerate(metrics):
            card = Card(label, tint=tint, symbol=symbol)
            card.clicked.connect(lambda t=target: self.show_metric(t))
            self.cards[key] = card
            if index < 4:
                board.addWidget(card, 0, index)
            else:
                board.addWidget(card, 1, (index-4)*2, 1, 2)
        for column in range(4):
            board.setColumnStretch(column, 1)
        body.addLayout(board)

        panel = self._panel("หมวดอุปกรณ์   ·   เลือกเพื่อดูรายการ", body, stretch=1)
        tabs = QTabWidget()
        self.category_tabs = tabs
        categories_page = QWidget()
        grid = QGridLayout(categories_page)
        grid.setContentsMargins(11, 13, 11, 13)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        self.category_buttons = {}
        for i, category in enumerate(bom_categories.CATEGORY_ORDER):
            button = self._button(
                category, lambda _checked=False, cat=category: self.filter_category(cat),
                "categoryAction")
            button.setMinimumHeight(68)
            button.setToolTip("เปิดรายการหมวด " + category)
            grid.addWidget(button, i//4, i%4)
            self.category_buttons[category] = button
        for column in range(4):
            grid.setColumnStretch(column, 1)
        tabs.addTab(categories_page, "หมวดทั้งหมด")
        detail_page = QWidget()
        details_layout = QVBoxLayout(detail_page)
        self.category_table = self._table(["หมวดอุปกรณ์", "จำนวนรายการ"], 0)
        self.category_table.setColumnWidth(1, 150)
        self.category_table.cellDoubleClicked.connect(self.open_category_from_dashboard)
        self.category_table.setToolTip("ดับเบิลคลิกหมวดเพื่อเปิดรายการ")
        details_layout.addWidget(self.category_table)
        tabs.addTab(detail_page, "ดูเป็นตาราง")
        panel.addWidget(tabs, 1)

        quality = self._panel("ความครบถ้วนของข้อมูลราคา", body)
        progress = QHBoxLayout()
        self.price_label = self._label("กรอกราคาแล้ว 0 รายการ", "caption")
        progress.addWidget(self.price_label)
        self.price_progress = QProgressBar()
        self.price_progress.setTextVisible(False)
        progress.addWidget(self.price_progress, 1)
        quality.addLayout(progress)
        self.budget_note = self._label(
            "ยอดรวมที่ทราบราคา ไม่รวมรายการที่ยังไม่มีราคา", "hint")
        self.budget_note.setWordWrap(True)
        quality.addWidget(self.budget_note)
        return page

    def _table_panel(self, body, title):
        return self._panel(title, body, stretch=1)

    def _build_bom(self):
        page, body = self._page(
            "รายการอุปกรณ์ (BOM)",
            "เลือกอุปกรณ์ ตรวจสอบ Part Number และราคา หรือดับเบิลคลิกเพื่อแก้ไข")

        actions = QHBoxLayout()
        actions.addWidget(self._button("+ เพิ่มอุปกรณ์", lambda: self.edit_record("items"), "primary"))
        actions.addWidget(self._button("แก้ไขรายการ", lambda: self.edit_record("items", True)))
        actions.addWidget(self._button("ลบที่เลือก", lambda: self.delete_record("items"), "danger"))
        actions.addStretch()
        actions.addWidget(self._button("ออกเอกสาร PDF / Excel",
                                       lambda: self.show_page(4)))
        body.addLayout(actions)

        filters = self._panel("ค้นหาและกรองรายการ", body)
        search_row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("ค้นหาชื่ออุปกรณ์ / รุ่น / Part Number / รหัส BOM…")
        self.search.textChanged.connect(self.render_bom)
        search_row.addWidget(self.search, 4)
        self.category = QComboBox()
        self.category.addItem("ทุกหมวด")
        self.category.currentIndexChanged.connect(self.render_bom)
        search_row.addWidget(self.category, 2)
        filters.addLayout(search_row)
        filter_row = QHBoxLayout()
        self.price_filter = QComboBox()
        self.price_filter.addItems(["ทุกราคา", "มีราคา", "ไม่มีราคา"])
        self.price_filter.currentIndexChanged.connect(self.render_bom)
        filter_row.addWidget(self.price_filter)
        self.group_mode = QComboBox()
        self.group_mode.addItems(["จัดกลุ่มตามระบบ", "แสดงรายการต่อเนื่อง"])
        self.group_mode.currentIndexChanged.connect(self.render_bom)
        self.group_mode.setToolTip("ปรับรูปแบบแสดงผล โดยไม่เปลี่ยนรายการหรือหมวดจริง")
        filter_row.addWidget(self.group_mode)
        self.visible_count_label = self._label("กำลังโหลดรายการ…", "caption")
        filter_row.addWidget(self.visible_count_label)
        filter_row.addStretch()
        filters.addLayout(filter_row)

        table_box = self._table_panel(body, "รายการวัสดุและอุปกรณ์")
        self.bom_table = self._table(
            ["BOM ID", "ชื่ออุปกรณ์ / รุ่น", "หมวดระบบ", "Part Number",
             "จำนวน", "หน่วย", "ราคา/หน่วย (บาท)", "รวม (บาท)", "สถานะ"], 1)
        for i, w in {0: 84, 2: 170, 3: 140, 4: 74, 5: 65,
                     6: 132, 7: 135, 8: 160}.items():
            self.bom_table.setColumnWidth(i, w)
        self.bom_table.setToolTip("เลือกแถวแล้วกดแก้ไขรายการ หรือดับเบิลคลิก")
        self.bom_table.cellDoubleClicked.connect(
            lambda *_: self.edit_record("items", True))
        table_box.addWidget(self.bom_table)
        footer = QHBoxLayout()
        footer.addWidget(self._label(
            "ราคา “—” หมายถึงยังไม่มีข้อมูล ไม่ใช่ราคา 0 บาท", "hint"))
        footer.addStretch()
        footer.addWidget(self._button("สร้างรายการจัดซื้อจากที่เลือก",
                                      self.purchase_selected))
        table_box.addLayout(footer)
        return page

    def _build_wiring(self):
        page, body = self._page("Wiring Manager", "WIRING & TERMINAL SCHEDULE  /  แบบร่าง ต้องตรวจสอบก่อนประกอบ")
        actions = QHBoxLayout()
        actions.addWidget(self._button("+ เพิ่มจุดต่อ", lambda: self.edit_record("wiring"), "primary"))
        actions.addWidget(self._button("แก้ไข", lambda: self.edit_record("wiring", True)))
        actions.addWidget(self._button("ลบ", lambda: self.delete_record("wiring"), "danger"))
        actions.addStretch()
        actions.addWidget(self._button("ตรวจสอบข้อมูล", self.check_wiring))
        actions.addWidget(self._button("ดูแผนภาพ", self.preview_wiring))
        actions.addWidget(self._button("ส่งออก Draw.io", lambda: self.export("drawio")))
        body.addLayout(actions)
        section = self._table_panel(body, "รายการสายและขั้วต่อ")
        self.wire_table = self._table(
            ["ID", "ต้นทาง", "ปลายทาง", "สัญญาณ", "แรงดัน", "ขนาดสาย", "การป้องกัน", "สถานะ"], 1)
        for i, w in {0: 65, 2: 175, 3: 145, 4: 100, 5: 160, 6: 155, 7: 125}.items():
            self.wire_table.setColumnWidth(i, w)
        self.wire_table.cellDoubleClicked.connect(lambda *_: self.edit_record("wiring", True))
        section.addWidget(self.wire_table)
        body.addWidget(self._label(
            "ข้อควรระวัง: ยังไม่ใช่วงจรรับรองความปลอดภัย ต้องตรวจขั้วต่อ กระแส แรงดัน และฟิวส์จากคู่มือจริง", "hint"))
        return page

    def _build_purchases(self):
        page, body = self._page("จัดซื้อ / Purchasing", "PROCUREMENT TRACKER  /  วางแผน ซื้อ และรับสินค้า")
        actions = QHBoxLayout()
        actions.addWidget(self._button("+ เลือกอุปกรณ์จาก BOM", lambda: self.edit_record("purchases"), "primary"))
        actions.addWidget(self._button("แก้ไข", lambda: self.edit_record("purchases", True)))
        actions.addWidget(self._button("ลบ", lambda: self.delete_record("purchases"), "danger"))
        info = self._label("เลือกรายการจาก BOM ในหน้าต่างใหม่ แล้วตรวจราคา/จำนวนสั่งซื้อจริง", "hint")
        info.setWordWrap(True)
        actions.addStretch()
        self.purchase_total = self._label("ยอดรวมจัดซื้อ: —", "sectionTitle")
        actions.addWidget(self.purchase_total)
        body.addLayout(actions)
        body.addWidget(info)
        section = self._table_panel(body, "Purchase Orders / รายการสั่งซื้อ")
        self.purchase_table = self._table(
            ["BOM ID", "รายการ", "ผู้ขาย", "จำนวน", "ราคา/หน่วย", "ยอดรวม", "สถานะ", "PO", "กำหนดรับ"], 1)
        for i, w in {0: 76, 2: 145, 3: 68, 4: 100, 5: 120, 6: 120, 7: 110, 8: 116}.items():
            self.purchase_table.setColumnWidth(i, w)
        self.purchase_table.cellDoubleClicked.connect(lambda *_: self.edit_record("purchases", True))
        section.addWidget(self.purchase_table)
        return page

    def _build_sync(self):
        page, body = self._page(
            "รายงานและการจัดเก็บข้อมูล",
            "ส่งออกเอกสารสำหรับใส่รายงาน หรือจัดการข้อมูล GitHub")
        body.addWidget(self._label(
            "ขั้นตอนง่าย ๆ : เลือก PDF หรือ Excel → กรอกชื่อผู้จัดทำ / สถาบัน → เลือกที่บันทึก",
            "caption"))
        group = self._panel("1  ส่งออกรายงานแบบทางการ (แนะนำสำหรับส่งอาจารย์)", body)
        text = self._label(
            "รายงานมีส่วนหัวโครงการ เลขที่เอกสาร Revision สรุปงบประมาณ "
            "และ BOM แยกหมวด พร้อมข้อมูลสเปก Wiring และจัดซื้อ", "caption")
        text.setWordWrap(True)
        group.addWidget(text)
        export_cards = QGridLayout()
        export_cards.setHorizontalSpacing(13)
        for column, (heading, description, title, action, role) in enumerate((
            ("PDF สำหรับรายงาน", "เอกสาร A4 มีเลขหน้า ภาคผนวก และ Revision",
             "สร้าง PDF", lambda: self.export("pdf"), "primary"),
            ("Excel ตรวจสอบข้อมูล", "ตาราง BOM พร้อมสูตรและชีตสเปก / แหล่งอ้างอิง",
             "สร้าง Excel", lambda: self.export("xlsx"), "success"),
            ("ชุดเอกสารรายงาน", "สร้างไฟล์ PDF และ Excel พร้อมกันในโฟลเดอร์เดียว",
             "สร้างทั้งสองไฟล์", self.export_report_pair, None),
        )):
            card = QFrame()
            card.setObjectName("formPanel")
            stack = QVBoxLayout(card)
            stack.setContentsMargins(17, 16, 17, 16)
            stack.setSpacing(10)
            stack.addWidget(self._label(heading, "sectionTitle"))
            description_label = self._label(description, "caption")
            description_label.setWordWrap(True)
            stack.addWidget(description_label)
            stack.addStretch()
            stack.addWidget(self._button(title, action, role))
            export_cards.addWidget(card, 0, column)
            export_cards.setColumnStretch(column, 1)
        group.addLayout(export_cards)
        text = self._label(
            "PDF: A4 แนวนอน พร้อมเลขหน้าและภาคผนวก  |  "
            "Excel: แยกชีตสรุป อุปกรณ์ สเปก สายไฟ และจัดซื้อ พร้อมสูตรคำนวณ", "hint")
        text.setWordWrap(True)
        group.addWidget(text)

        group = self._panel("2  บันทึกและซิงก์ GitHub", body)
        row = QHBoxLayout()
        row.addWidget(self._button("ซิงก์ข้อมูลตอนนี้", self.sync_now, "primary"))
        row.addWidget(self._button("โหลดข้อมูลล่าสุด", self.load_remote))
        row.addWidget(self._button("บันทึก GitHub", self.save_remote))
        row.addWidget(self._button("ตั้งค่า Token", self.configure_token))
        row.addWidget(self._button("ประวัติการแก้ไข", self.show_history))
        group.addLayout(row)
        sync_settings = QHBoxLayout()
        self.auto_sync_toggle = QCheckBox("Auto Save ไป GitHub เมื่อแก้ไขรายการ")
        self.auto_sync_toggle.setToolTip(
            "บันทึกฉบับร่างในเครื่องทันที และซิงก์หลังหยุดแก้ไขประมาณ 90 วินาที "
            "หากเน็ตหลุดจะเก็บฉบับร่างไว้และลองใหม่โดยไม่ทับข้อมูลเครื่องอื่น")
        self.auto_sync_toggle.setChecked(self.auto_sync_enabled)
        self.auto_sync_toggle.toggled.connect(self.set_auto_sync)
        sync_settings.addWidget(self.auto_sync_toggle)
        self.sync_state = self._label("บันทึกในเครื่อง · ยังไม่ซิงก์", "status")
        sync_settings.addWidget(self.sync_state)
        sync_settings.addStretch()
        group.addLayout(sync_settings)
        guide = self._label(
            "ฉบับร่างเก็บในเครื่องทันทีเพื่อกู้คืนหากไฟดับ · Auto Save ส่งขึ้น GitHub "
            "หลังหยุดแก้ไข ~90 วินาที · อีกเครื่องจะตรวจดึงข้อมูลใหม่ทุก 2 นาที "
            "เมื่อไม่มีข้อมูลแก้ไขค้าง · หากข้อมูลชนกันจะหยุดซิงก์ ไม่ทับงานของเครื่องอื่น", "hint")
        guide.setWordWrap(True)
        group.addWidget(guide)

        group = self._panel("3  เครื่องมืออื่นและสำรองข้อมูล", body)
        row = QHBoxLayout()
        for kind, title in [("csv","CSV"), ("json","JSON Backup"),
                            ("drawio","Draw.io")]:
            row.addWidget(self._button(title,
                                       lambda _checked=False, k=kind: self.export(k)))
        row.addWidget(self._button("นำเข้า JSON Backup", self.import_backup))
        row.addWidget(self._button("เปิดโฟลเดอร์ฉบับร่าง", self.open_cache_dir))
        group.addLayout(row)
        group.addWidget(self._label(
            "ตรวจสอบเวอร์ชันหรืออัปเดตโปรแกรมได้จากมุมขวาบนทุกหน้า", "hint"))
        body.addWidget(self._label(
            "ข้อควรทราบ: ข้อมูลราคาที่ไม่ครบจะไม่ถูกคิดเป็นศูนย์ "
            "และรายงานไม่มีลายเซ็นอนุมัติที่ไม่ได้ให้ข้อมูล", "hint"))
        body.addStretch(1)
        return page


    def _build_diagnostics(self):
        page, body = self._page(
            "Debug Report / ตรวจสอบระบบ",
            "DIAGNOSTICS  /  ตรวจสถานะโปรแกรมและส่งออกรายงานแบบไม่เปิดเผย GitHub Token")
        row = QHBoxLayout()
        row.addWidget(self._button("ตรวจสอบระบบตอนนี้", self.refresh_diagnostics, "primary"))
        row.addWidget(self._button("ทดสอบเชื่อมต่อ GitHub", self.debug_check_github))
        row.addWidget(self._button("ส่งออก Debug Report (.json)", self.export_debug))
        row.addStretch()
        body.addLayout(row)
        summary = self._panel("สถานะการตรวจสอบ", body)
        self.debug_summary = self._label("กำลังเตรียมข้อมูล", "caption")
        summary.addWidget(self.debug_summary)
        self.debug_checks = self._table(["ตรวจสอบ", "ผล", "รายละเอียด"], 2)
        self.debug_checks.setMaximumHeight(260)
        self.debug_checks.setColumnWidth(0, 205)
        self.debug_checks.setColumnWidth(1, 90)
        summary.addWidget(self.debug_checks)
        events = self._panel("บันทึกเหตุการณ์ล่าสุด (เก็บเฉพาะข้อมูลเทคนิค)", body, stretch=1)
        self.debug_events = self._table(["เวลา UTC", "ระดับ", "ระบบ", "รหัส", "รายละเอียด"], 4)
        self.debug_events.setColumnWidth(0, 178)
        self.debug_events.setColumnWidth(1, 75)
        self.debug_events.setColumnWidth(2, 125)
        self.debug_events.setColumnWidth(3, 195)
        events.addWidget(self.debug_events)
        extra = QHBoxLayout()
        extra.addWidget(self._button("เปิดโฟลเดอร์ Log", self.open_log_dir))
        extra.addWidget(self._button("ล้าง Log ในเครื่อง", self.clear_debug_logs, "danger"))
        extra.addStretch()
        events.addLayout(extra)
        body.addWidget(self._label(
            "ความเป็นส่วนตัว: รายงานไม่มี GitHub Token, รายละเอียด BOM รายชิ้น หรือรหัสผ่าน "
            "· บันทึกเฉพาะสรุปจำนวนรายการและเหตุการณ์ระบบ · ไม่อัปโหลดรายงานอัตโนมัติ", "hint"))
        return page

    def _debug_state(self):
        return {
            "dirty": self.dirty,
            "remote_loaded": self.sha is not None,
            "github_token_present": bool(self.token),
            "github_connected": self.last_git_ok,
        }

    def refresh_diagnostics(self):
        data = self.debugger.snapshot(self.payload, **self._debug_state())
        checks = data["checks"]
        self.debug_checks.setRowCount(len(checks))
        for i, item in enumerate(checks):
            color = {"PASS": "#29D7A3", "WARN": "#F5BA55",
                     "FAIL": "#FF7891"}.get(item["status"], "#AFC2D8")
            for col, key in enumerate(("name", "status", "detail")):
                cell = QTableWidgetItem(item[key])
                if key == "status":
                    cell.setForeground(QBrush(QColor(color)))
                self.debug_checks.setItem(i, col, cell)
        logs = data["events"]
        self.debug_events.setRowCount(len(logs))
        for i, item in enumerate(reversed(logs)):
            values = [item.get(k, "") for k in
                      ("timestamp", "level", "area", "code", "message")]
            for col, value in enumerate(values):
                cell = QTableWidgetItem(value)
                if col == 1:
                    cell.setForeground(QBrush(QColor(
                        "#FF7891" if value == "ERROR" else
                        "#F5BA55" if value == "WARN" else "#AFC2D8")))
                self.debug_events.setItem(i, col, cell)
        errors = sum(e.get("level") == "ERROR" for e in logs)
        warns = sum(x["status"] == "WARN" for x in checks)
        fails = sum(x["status"] == "FAIL" for x in checks)
        self.debug_summary.setText(
            f"ระบบ: {len(checks)} รายการตรวจสอบ · FAIL {fails} / WARN {warns} "
            f"· เหตุการณ์ {len(logs)} รายการ (ERROR {errors}) · "
            f"{'ข้อมูลยังไม่บันทึก GitHub' if self.dirty else 'ข้อมูลไม่มีการแก้ไขค้าง'}")
        return data

    def debug_check_github(self):
        self.set_status("กำลังทดสอบ GitHub API โดยไม่ส่งข้อมูล BOM…")
        def success(_):
            self.last_git_ok = True
            self.debugger.event("INFO", "github", "CONNECTIVITY_OK",
                                "GitHub API ตอบกลับสำเร็จ")
            self.set_status("ตรวจสอบ GitHub API ผ่าน")
            self.refresh_diagnostics()
        def failed(msg):
            self.last_git_ok = False
            self.debugger.event("ERROR", "github", "CONNECTIVITY_FAILED", msg)
            self._message_error(msg)
            self.refresh_diagnostics()
        self._job(lambda: github_api("GET", token=self.token, url=API),
                  success, failed, context="github")

    def export_debug(self):
        filename = f"BOM_Debug_Report_v{VERSION}.json"
        path, _ = QFileDialog.getSaveFileName(
            self, "บันทึก Debug Report", filename, "JSON report (*.json)")
        if not path:
            return
        try:
            self.debugger.export_json(path, self.payload, **self._debug_state())
        except Exception as exc:
            self.debugger.exception("diagnostics", "REPORT_EXPORT_FAILED", exc)
            self._message_error("ส่งออก Debug Report ไม่สำเร็จ")
            return
        self.refresh_diagnostics()
        self.set_status("สร้าง Debug Report เรียบร้อย (ไม่ได้อัปโหลด GitHub)")
        QMessageBox.information(self, "ส่งออก Debug Report สำเร็จ",
                                "ไฟล์ถูกบันทึกไว้ในเครื่องตามที่คุณเลือก\n"
                                "ตรวจเนื้อหาก่อนส่งให้ผู้อื่นได้")

    def open_log_dir(self):
        path = self.debugger.folder
        try:
            path.mkdir(parents=True, exist_ok=True)
            if sys.platform == "win32":
                os.startfile(str(path))
            else:
                webbrowser.open(path.as_uri())
        except OSError as exc:
            self._message_error(f"เปิดโฟลเดอร์ Log ไม่สำเร็จ: {type(exc).__name__}")

    def clear_debug_logs(self):
        if QMessageBox.question(self, "ยืนยันล้าง Log",
                "ลบบันทึกข้อผิดพลาดเก่าในเครื่องหรือไม่?\n"
                "ข้อมูล BOM และ GitHub จะไม่ถูกลบ") != QMessageBox.StandardButton.Yes:
            return
        self.debugger.clear_logs()
        self.debugger.event("INFO", "diagnostics", "LOGS_CLEARED",
                            "ล้าง Log เก่าในเครื่องแล้ว")
        self.refresh_diagnostics()

    def show_page(self, number):
        self.stack.setCurrentIndex(number)
        if number == 5:
            self.refresh_diagnostics()
        for i, button in enumerate(self.nav_buttons):
            button.setProperty("active", number == i)
            button.style().unpolish(button)
            button.style().polish(button)

    def show_metric(self, target):
        if target == "wiring":
            self.show_page(2)
        elif target == "purchases":
            self.show_page(3)
        else:
            self.show_page(1)
            self.search.clear()
            self.category.setCurrentIndex(0)
            self.price_filter.setCurrentText(
                "ไม่มีราคา" if target == "missing" else "มีราคา" if target == "priced" else "ทุกราคา")

    def set_status(self, message):
        self.status.setText(message)

    def render_all(self):
        self.render_dashboard()
        self.render_bom()
        self.render_wiring()
        self.render_purchases()
        self.top_project_label.setText(str(self.payload.get("project") or "ยังไม่ได้ตั้งชื่อโครงการ"))
        self.hero_project_label.setText(str(self.payload.get("project") or "ยังไม่ได้ตั้งชื่อโครงการ"))
        if hasattr(self, "debug_checks"):
            self.refresh_diagnostics()
        sync_text = ("รอซิงก์ GitHub" if self.dirty else
                     "ข้อมูลซิงก์ GitHub แล้ว" if self.sha else
                     "ข้อมูลอยู่ในเครื่อง")
        self.data_status.setText(
            f"{sync_text}  •  {len(self.payload.get('items', []))} รายการ")
        self._refresh_sync_state()

    def render_dashboard(self):
        info = bom_core.metrics(self.payload)
        for key in ("items", "priced", "missing", "wires", "purchase_count"):
            self.cards[key].figure.setText(str(info[key]))
        self.cards["known_cost"].figure.setText(money(info["known_cost"]))
        cats = [(cat, info["categories"][cat]) for cat in
                bom_categories.sorted_categories(info["categories"].keys())]
        self.category_table.setRowCount(len(cats))
        for row, (category, count) in enumerate(cats):
            self.category_table.setItem(row, 0, QTableWidgetItem(category))
            self.category_table.setItem(row, 1, QTableWidgetItem(str(count)))
        self.category_table.clearSelection()
        for cat, button in self.category_buttons.items():
            count = info["categories"].get(cat, 0)
            button.setText(f"{cat}\n{count} รายการ")
        percent = int(round(100 * info["priced"] / max(info["items"], 1)))
        self.price_label.setText(f"กรอกราคาแล้ว {info['priced']}/{info['items']} รายการ  ·  {percent}%")
        self.price_progress.setValue(percent)
        self.budget_note.setText(
            f"ยอดรวมที่ทราบราคา {money(info['known_cost'])} บาท · ยังไม่มีราคา {info['missing']} รายการ "
            "· ยอดนี้ยังไม่ใช่งบประมาณสุดท้าย")

    def open_category_from_dashboard(self, row, _column):
        cell = self.category_table.item(row, 0)
        if cell:
            self.show_page(1)
            self.search.clear()
            self.price_filter.setCurrentText("ทุกราคา")
            self.category.setCurrentText(cell.text())

    def render_bom(self):
        values = self.payload.get("items", [])
        selected = self.category.currentText()
        cats = bom_categories.sorted_categories(
            x.get("category") or bom_categories.UNCATEGORIZED for x in values)
        if self.category.count() != len(cats) + 1 or any(
                self.category.itemText(i + 1) != name for i, name in enumerate(cats)):
            self.category.blockSignals(True)
            self.category.clear()
            self.category.addItems(["ทุกหมวด"] + cats)
            self.category.setCurrentText(selected if selected in cats else "ทุกหมวด")
            self.category.blockSignals(False)
        query = self.search.text().strip().casefold()
        cat = self.category.currentText()
        price_filter = self.price_filter.currentText()
        entries = []
        for index, item in enumerate(values):
            item_cat = str(item.get("category") or bom_categories.UNCATEGORIZED)
            if cat != "ทุกหมวด" and item_cat != cat:
                continue
            has_price = item.get("unitPrice") is not None and str(item.get("unitPrice")).strip() != ""
            if price_filter == "มีราคา" and not has_price:
                continue
            if price_filter == "ไม่มีราคา" and has_price:
                continue
            if query and query not in " ".join(str(x or "") for x in item.values()).casefold():
                continue
            entries.append((index, item))
        self.bom_table.clearSpans()
        grouped = self.group_mode.currentIndex() == 0
        if grouped:
            entries.sort(key=lambda x: (bom_categories.sort_key(x[1].get("category")),
                                        str(x[1].get("name") or "").casefold()))
            display = []
            previous = None
            for index, item in entries:
                item_cat = str(item.get("category") or bom_categories.UNCATEGORIZED)
                if item_cat != previous:
                    count = sum(1 for _, row in entries if str(
                        row.get("category") or bom_categories.UNCATEGORIZED) == item_cat)
                    display.append(("heading", item_cat, count))
                    previous = item_cat
                display.append(("item", index, item))
        else:
            display = [("item", index, item) for index, item in entries]
        self.bom_table.setRowCount(len(display))
        self.visible_count_label.setText(
            f"แสดง {len(entries)} จาก {len(values)} รายการ")
        for i, row in enumerate(display):
            if row[0] == "heading":
                header = QTableWidgetItem(f"▣  {row[1]}    ·    {row[2]} รายการ")
                header.setBackground(QBrush(QColor("#E7F1FC")))
                header.setForeground(QBrush(QColor("#174F8C")))
                font = header.font()
                font.setBold(True)
                header.setFont(font)
                header.setFlags(Qt.ItemFlag.NoItemFlags)
                self.bom_table.setItem(i, 0, header)
                self.bom_table.setSpan(i, 0, 1, self.bom_table.columnCount())
                self.bom_table.setRowHeight(i, round(48*self.zoom_factor))
                continue
            _, index, item = row
            qty = item.get("qty", 0)
            price = item.get("unitPrice")
            columns = [item.get("id", ""), item.get("name", ""),
                       item.get("category", ""), item.get("partNumber", "") or "—",
                       qty, item.get("unit", ""), money(price),
                       money(float(qty) * float(price)) if price is not None else "—",
                       item.get("status", "")]
            for col, val in enumerate(columns):
                cell = QTableWidgetItem(str(val if val is not None else ""))
                cell.setData(Qt.ItemDataRole.UserRole, index)
                if col in (4, 6, 7):
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignVCenter |
                                          Qt.AlignmentFlag.AlignRight)
                if col in (6, 7) and price is None:
                    cell.setForeground(QBrush(QColor("#A86521")))
                if col == 8 and "ยัง" in str(val):
                    cell.setForeground(QBrush(QColor("#A86521")))
                self.bom_table.setItem(i, col, cell)
        self.bom_table.clearSelection()

    def render_wiring(self):
        rows = self.payload.get("wiring", [])
        self._fill_table(self.wire_table, rows, [
            "id", "from", "to", "signal", "voltage", "cable", "protection", "status"])

    def render_purchases(self):
        rows = self.payload.get("purchases", [])
        self.purchase_table.setRowCount(len(rows))
        for row, entry in enumerate(rows):
            qty = float(entry.get("qty") or 0)
            price = entry.get("unitPrice")
            cols = [entry.get("itemId", ""), entry.get("description", ""),
                    entry.get("supplier", ""), entry.get("qty", ""),
                    money(price), money(qty * float(price)) if price is not None else "—",
                    entry.get("status", ""), entry.get("po", ""),
                    entry.get("dueDate", "")]
            for col, value in enumerate(cols):
                item = QTableWidgetItem(str(value if value is not None else ""))
                item.setData(Qt.ItemDataRole.UserRole, row)
                self.purchase_table.setItem(row, col, item)
        self.purchase_table.clearSelection()
        total = bom_core.metrics(self.payload)["purchase_total"]
        self.purchase_total.setText(f"ยอดรวมที่มีราคา: ฿ {money(total)}")

    @staticmethod
    def _fill_table(table, rows, keys):
        table.setRowCount(len(rows))
        for i, entry in enumerate(rows):
            for col, key in enumerate(keys):
                item = QTableWidgetItem(str(entry.get(key) or ""))
                item.setData(Qt.ItemDataRole.UserRole, i)
                table.setItem(i, col, item)
        table.clearSelection()

    def _selected_index(self, kind):
        table = {"items": self.bom_table,
                 "wiring": self.wire_table,
                 "purchases": self.purchase_table}[kind]
        row = table.currentRow()
        if row < 0:
            QMessageBox.information(self, "เลือกรายการ", "กรุณาเลือกรายการจากตารางก่อน")
            return None
        item = table.item(row, 0)
        original_index = item.data(Qt.ItemDataRole.UserRole) if item else None
        if original_index is None:
            QMessageBox.information(self, "เลือกอุปกรณ์", "กรุณาเลือกแถวอุปกรณ์ ไม่ใช่แถวชื่อหมวด")
            return None
        return int(original_index)

    def _refresh_sync_state(self):
        if not hasattr(self, "sync_state"):
            return
        if self.sync_paused_conflict:
            state = "ข้อมูลชนกัน · หยุด Auto Save จนกว่าจะตรวจสอบ"
        elif not self.dirty:
            state = ("ซิงก์ GitHub แล้ว · ตรวจข้อมูลใหม่ทุก 2 นาที"
                     if self.sha and self.last_git_ok is True else
                     "ใช้ข้อมูลในเครื่อง · GitHub ติดต่อไม่ได้" if
                     self.last_git_ok is False else
                     "มีข้อมูลในเครื่อง · กำลังตรวจ GitHub" if self.sha else
                     "ข้อมูลในเครื่อง · รอโหลด GitHub")
        elif not self.auto_sync_enabled:
            state = "บันทึกในเครื่อง · Auto Save GitHub ปิด"
        elif not self.token:
            state = "บันทึกในเครื่อง · รอตั้งค่า GitHub Token"
        elif not self.sha:
            state = "บันทึกในเครื่อง · ต้องโหลด GitHub ก่อน"
        elif self.busy:
            state = "บันทึกในเครื่อง · รอซิงก์"
        else:
            state = "บันทึกในเครื่อง · รอซิงก์ GitHub อัตโนมัติ"
        self.sync_state.setText(state)
        if hasattr(self, "cloud_header_status"):
            updated = (self.last_github_sync_at.astimezone().strftime("%d/%m %H:%M")
                       if self.last_github_sync_at else "ยังไม่เคยซิงก์ในรอบนี้")
            self.cloud_header_status.setText(
                "GitHub Cloud: " + state + "  |  ล่าสุด: " + updated)

    def sync_now(self):
        """One button: push local edits or pull new edits from other PCs."""
        if self.sync_paused_conflict:
            QMessageBox.warning(
                self, "มีข้อมูลจากหลายเครื่องชนกัน",
                "โปรแกรมเก็บฉบับร่างไว้ในเครื่องแล้ว ไม่สามารถซิงก์ทับได้ทันที\n"
                "ให้ส่งออก JSON Backup แล้วตรวจสอบข้อมูล GitHub ล่าสุดก่อน")
            return
        if self.dirty:
            self.save_remote()
        else:
            self.load_remote(silent=False)

    def set_auto_sync(self, enabled):
        self.auto_sync_enabled = bool(enabled)
        QSettings("CraneVehicle", "BOMManager").setValue(
            "sync/auto_enabled", self.auto_sync_enabled)
        if self.auto_sync_enabled:
            self._schedule_auto_sync()
        else:
            self.auto_sync_timer.stop()
        self._refresh_sync_state()

    def _schedule_auto_sync(self):
        if (self.auto_sync_enabled and self.dirty and
                not self.sync_paused_conflict and self.token and self.sha):
            self.auto_sync_timer.start(self.auto_sync_delay_ms)
        self._refresh_sync_state()

    def _autosync_if_needed(self):
        if not (self.auto_sync_enabled and self.dirty and self.token
                and self.sha and not self.sync_paused_conflict):
            self._refresh_sync_state()
            return
        if self.busy or self.downloading or self.edit_dialog_active:
            # Another network job or an open editor: retry after changes settle.
            self.auto_sync_timer.start(60_000)
            return
        self.save_remote(automatic=True)

    def _refresh_remote_if_clean(self):
        """Fetch changed GitHub documents across PCs without clobbering drafts."""
        if (self.busy or self.downloading or self.dirty or
                self.edit_dialog_active or self.sync_paused_conflict):
            return
        current_sha = self.sha
        if current_sha is None:
            self.load_remote(silent=True)
            return
        self.busy = True

        def work():
            remote = github_api("GET", token=self.token)
            if remote["sha"] == current_sha:
                return None
            document = json.loads(
                base64.b64decode(remote["content"]).decode("utf-8-sig"))
            bom_core.ensure_doc(document)
            return document, remote["sha"]

        def success(result):
            self.busy = False
            if result is None:
                self.last_git_ok = True
                self.last_github_sync_at = datetime.now(timezone.utc)
                self._refresh_sync_state()
                return
            # A user may edit while the request is in flight; preserve it.
            if self.dirty or self.edit_dialog_active or self.sha != current_sha:
                self._refresh_sync_state()
                return
            self.payload, self.sha = result
            self.last_github_sync_at = datetime.now(timezone.utc)
            self.last_git_ok = True
            self.revision += 1
            self._write_cache()
            self.render_all()
            self.debugger.event("INFO", "github", "REMOTE_REFRESH",
                                "พบ BOM เวอร์ชันใหม่จาก GitHub และอัปเดตในเครื่องแล้ว")
            self.set_status("รับข้อมูลใหม่จาก GitHub แล้ว · ทุกเครื่องใช้ข้อมูลชุดเดียวกัน")

        def failed(message):
            self.busy = False
            self.last_git_ok = False
            self._refresh_sync_state()
            # Silent refresh failures must not interrupt editing.
            self.debugger.event("WARNING", "github", "REMOTE_REFRESH_FAILED",
                                "ตรวจสอบข้อมูลใหม่จาก GitHub ไม่สำเร็จ")
        self._job(work, success, failed, context="github")


    def changed(self):
        self.dirty = True
        self.revision += 1
        self._write_cache()
        self.debugger.event("INFO", "bom", "LOCAL_DRAFT_UPDATED",
                            "ฉบับร่างถูกแก้ไขและบันทึกในเครื่อง")
        self.render_all()
        self._schedule_auto_sync()
        self.set_status("บันทึกในเครื่องแล้ว · "+(
            "จะซิงก์ GitHub อัตโนมัติ" if self.auto_sync_enabled
            else "Auto Save GitHub ปิดอยู่"))

    def edit_record(self, kind, existing=False, defaults=None):
        data = self.payload.setdefault(kind, [])
        index = self._selected_index(kind) if existing else None
        if existing and index is None:
            return
        prev = data[index] if index is not None else {}
        row = {**(defaults or {}), **prev}
        if kind == "items" and index is None:
            row.setdefault("category", bom_categories.UNCATEGORIZED)
            row.setdefault("qty", 1)
        title = {
            "items": ("แก้ไขอุปกรณ์" if existing else "เพิ่มอุปกรณ์"),
            "wiring": ("แก้ไขจุดต่อสาย" if existing else "เพิ่มจุดต่อสาย"),
            "purchases": ("แก้ไขการจัดซื้อ" if existing else "เพิ่มการจัดซื้อ"),
        }[kind]
        dlg = RecordDialog(title, FIELD_SET[kind], row, self)
        self.edit_dialog_active = True
        try:
            accepted = dlg.exec() == QDialog.DialogCode.Accepted
        finally:
            self.edit_dialog_active = False
        if not accepted:
            return
        values = dlg.get_values()
        try:
            if kind == "items":
                values = bom_core.normalize_dialog_values(values)
            elif kind == "wiring":
                if not values["from"] or not values["to"]:
                    raise bom_core.DataError("ต้องระบุจุดต้นทางและปลายทาง")
            else:
                if not values.get("itemId") and index is None:
                    raise bom_core.DataError("กรุณาเลือกอุปกรณ์จากรายการ BOM ก่อนบันทึกการจัดซื้อ")
                if values.get("itemId") and not any(
                    str(i.get("id")) == values["itemId"] for i in
                    self.payload.get("items", [])):
                    if index is None:
                        raise bom_core.DataError("ไม่พบ BOM ID ที่เลือก กรุณาเลือกใหม่")
                if not values["description"]:
                    raise bom_core.DataError("ต้องกรอกชื่ออุปกรณ์ที่สั่งซื้อ")
                values["qty"] = bom_core.valid_qty(values["qty"])
                values["unitPrice"] = bom_core.valid_price(values["unitPrice"])
                if values.get("dueDate"):
                    datetime.strptime(values["dueDate"], "%Y-%m-%d")
        except (ValueError, bom_core.DataError) as exc:
            QMessageBox.warning(self, "ข้อมูลไม่ถูกต้อง", str(exc))
            return
        if index is None:
            data.append({"id": bom_core.next_id(data), **values})
        else:
            data[index] = {**prev, **values}
        self.changed()

    def delete_record(self, kind):
        index = self._selected_index(kind)
        if index is None:
            return
        if QMessageBox.question(self, "ยืนยันลบ", "ต้องการลบรายการที่เลือกหรือไม่?") != QMessageBox.StandardButton.Yes:
            return
        del self.payload[kind][index]
        self.changed()

    def purchase_selected(self):
        index = self._selected_index("items")
        if index is None:
            return
        item = self.payload["items"][index]
        self.show_page(3)
        self.edit_record("purchases", defaults={
            "itemId": str(item.get("id") or ""),
            "description": str(item.get("name") or ""),
            "supplier": str(item.get("supplier") or ""),
            "qty": item.get("qty", 1),
            "unitPrice": item.get("unitPrice"),
            "link": str(item.get("link") or ""),
            "status": PURCHASE_STATUS[0],
        })

    def check_wiring(self):
        issues = bom_core.connection_warnings(self.payload)
        text = ("\n".join(issues[:20]) + f"\n... อีก {max(0, len(issues)-20)} รายการ"
                if issues else "ไม่พบปัญหาโครงสร้างข้อมูลที่ตรวจโดยอัตโนมัติ")
        QMessageBox.information(
            self, "ตรวจสอบ Wiring", text +
            "\n\nผลตรวจนี้ไม่ใช่การรับรองวงจรและพิกัดอุปกรณ์ทางไฟฟ้า")

    def preview_wiring(self):
        dialog = QDialog(self)
        dialog.resize(1120, 740)
        dialog.setWindowTitle("Wiring Connection View — Engineering Draft")
        layout = QVBoxLayout(dialog)
        layout.addWidget(self._label(
            "แสดงแต่ละจุดต่อแยกแถวเพื่อลดเส้นทับ ไม่ใช่ผังวงจรที่ผ่านการรับรอง", "caption"))
        scene = QGraphicsScene(dialog)
        wires = self.payload.get("wiring", [])
        for index, wire in enumerate(wires):
            y = 42 + index * 122
            scene.addRect(QRectF(15, y, 270, 62),
                          QPen(QColor("#35719C"), 1.4), QBrush(QColor("#172E48")))
            scene.addRect(QRectF(790, y, 270, 62),
                          QPen(QColor("#35719C"), 1.4), QBrush(QColor("#172E48")))
            for x, value in ((25, wire.get("from") or "ไม่ระบุต้นทาง"),
                             (800, wire.get("to") or "ไม่ระบุปลายทาง")):
                label = scene.addText(str(value), QFont("Leelawadee UI", 11))
                label.setDefaultTextColor(QColor("#E7F2FF"))
                label.setTextWidth(245)
                label.setPos(x, y+13)
            scene.addLine(285, y+33, 788, y+33, QPen(QColor("#36A8FF"), 2.4))
            scene.addLine(777, y+26, 789, y+33, QPen(QColor("#36A8FF"), 2.4))
            scene.addLine(777, y+40, 789, y+33, QPen(QColor("#36A8FF"), 2.4))
            description = " / ".join(str(wire.get(k) or "—")
                                     for k in ("signal", "voltage", "cable", "protection"))
            line = scene.addText(description, QFont("Leelawadee UI", 9))
            line.setDefaultTextColor(QColor("#AFC2D8"))
            line.setTextWidth(490)
            line.setPos(290, y-10)
        if not wires:
            line = scene.addText("ยังไม่มีรายการสาย กรุณาเพิ่มจุดต่อใน Wiring Manager", QFont("Leelawadee UI", 12))
            line.setDefaultTextColor(QColor("#AFC2D8"))
        scene.setSceneRect(0, 0, 1080, max(420, len(wires)*122+110))
        view = QGraphicsView(scene)
        view.setRenderHint(__import__("PySide6.QtGui", fromlist=["QPainter"]).QPainter.RenderHint.Antialiasing)
        layout.addWidget(view, 1)
        layout.addWidget(self._button("ปิด", dialog.accept))
        dialog.exec()

    def _job(self, task, on_success, on_error=None, context="background"):
        job = Job(task, self, reporter=self.debugger, context=context)
        self.jobs.add(job)
        job.succeeded.connect(on_success)
        def job_failed(message):
            self.debugger.event("ERROR", context, "BACKGROUND_JOB_FAILED", message)
            (on_error or self._message_error)(message)
            if hasattr(self, "debug_events"):
                self.refresh_diagnostics()
        job.failed.connect(job_failed)
        job.finished.connect(lambda j=job: self.jobs.discard(j))
        job.start()

    def _message_error(self, text):
        self.set_status("ไม่สำเร็จ: " + text.splitlines()[0])
        QMessageBox.warning(self, "เกิดข้อผิดพลาด", text)

    def configure_token(self):
        from PySide6.QtWidgets import QInputDialog, QLineEdit as _LineEdit
        token, ok = QInputDialog.getText(
            self, "GitHub Token",
            "Fine-grained token สำหรับ Repository นี้เท่านั้น\nสิทธิ์ Contents: Read and write",
            _LineEdit.EchoMode.Password)
        if not ok:
            return
        token = token.strip()
        if not token:
            QMessageBox.warning(self, "Token ว่าง", "กรุณากรอก GitHub Token")
            return
        self.debugger.register_secret(token)
        self.set_status("กำลังตรวจสิทธิ์ GitHub Token…")
        def success(_result):
            try:
                keyring.set_password(SERVICE, "github-token", token)
            except Exception as exc:
                self.debugger.exception("credentials", "CREDENTIAL_SAVE_FAILED", exc)
                self._message_error("ไม่สามารถบันทึก Token ใน Windows Credential Manager")
                return
            self.token = token
            self.debugger.event("INFO", "credentials", "TOKEN_CONFIGURED",
                                "ตั้งค่า GitHub Credential เรียบร้อย")
            self.set_status("ตรวจ Token และเก็บใน Windows Credential Manager แล้ว")
            self._schedule_auto_sync()
            QMessageBox.information(self, "เชื่อม GitHub สำเร็จ", "บันทึก GitHub Token อย่างปลอดภัยแล้ว")
        self._job(lambda: github_api("GET", token=token), success, context="github")

    def _backup_local_draft(self):
        """Keep an independent recovery copy before a deliberate remote overwrite."""
        backup_dir = self.cache_path.parent / "recovery"
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            path = backup_dir / f"BOM_local_draft_{stamp}.json"
            # Write directly with fsync before allowing GitHub to replace local data.
            with open(path, "x", encoding="utf-8") as output:
                json.dump(self.payload, output, ensure_ascii=False, indent=2)
                output.flush()
                os.fsync(output.fileno())
            return path
        except OSError as exc:
            self.debugger.exception("cache", "RECOVERY_BACKUP_FAILED", exc)
            self._message_error("ไม่สามารถสำรองฉบับร่างก่อนโหลด GitHub ได้ "
                                "จึงยกเลิกการโหลดเพื่อป้องกันข้อมูลสูญหาย")
            return None

    def load_remote(self, silent=False):
        if self.busy:
            return
        # Never silently discard recovered crash data during automatic refresh.
        if self.dirty:
            if silent or QMessageBox.question(
                    self, "มีฉบับร่างค้างอยู่",
                    "ข้อมูลที่แก้ในเครื่องยังไม่ได้บันทึกขึ้น GitHub\n"
                    "ต้องการโหลดข้อมูล GitHub ทับฉบับร่างหรือไม่?\n"
                    "ควรส่งออก JSON Backup ก่อนโหลดทับ"
            ) != QMessageBox.StandardButton.Yes:
                return
            backup = self._backup_local_draft()
            if backup is None:
                return
            self.debugger.event("INFO", "cache", "LOCAL_DRAFT_BACKED_UP",
                                "สำรองฉบับร่างก่อนโหลดข้อมูล GitHub")
        starting_revision = self.revision
        self.busy = True
        self.set_status("กำลังโหลด BOM จาก GitHub…")
        def work():
            raw = github_api("GET", token=self.token)
            content = base64.b64decode(raw["content"]).decode("utf-8-sig")
            document = json.loads(content)
            bom_core.ensure_doc(document)
            return document, raw["sha"]
        def success(result):
            self.busy = False
            if self.revision != starting_revision:
                # Editing started while remote data was in flight.
                self.sync_paused_conflict = True
                self._write_cache()
                self._refresh_sync_state()
                self.set_status("ตรวจพบการแก้ไขระหว่างโหลด GitHub "
                                "· เก็บฉบับร่างในเครื่องไว้ ไม่โหลดทับ")
                return
            self.payload, self.sha = result
            self.last_github_sync_at = datetime.now(timezone.utc)
            self.last_git_ok = True
            self.debugger.event("INFO", "github", "BOM_LOADED",
                                "โหลดข้อมูล BOM จาก GitHub สำเร็จ")
            self.dirty = False
            self.sync_paused_conflict = False
            self.auto_sync_timer.stop()
            self.revision += 1
            self._write_cache()
            self.render_all()
            self.set_status("โหลดข้อมูลล่าสุดจาก GitHub สำเร็จ")
        def failed(message):
            self.busy = False
            self.last_git_ok = False
            self.set_status("ใช้ข้อมูลฉบับร่างในเครื่อง · โหลด GitHub ไม่สำเร็จ")
            if not silent:
                self._message_error(message)
        self._job(work, success, failed, context="github")

    def save_remote(self, checked=False, *, automatic=False):
        """Save one snapshot using GitHub optimistic concurrency.

        Automatic saves never open modal dialogs. A remote edit from another
        machine pauses auto sync, keeping the durable local draft unchanged.
        """
        if self.busy or self.downloading:
            if not automatic:
                QMessageBox.information(self, "กำลังทำงาน",
                                        "กรุณารอการเชื่อมต่อ GitHub ก่อนหน้าเสร็จ")
            return
        try:
            bom_core.ensure_doc(self.payload)
        except bom_core.DataError as exc:
            if automatic:
                self.set_status(f"รอแก้ข้อมูล BOM ก่อน Auto Save: {exc}")
            else:
                self._message_error(str(exc))
            return
        if not self.token:
            if not automatic:
                QMessageBox.information(self, "ยังไม่มี Token",
                                        "กรุณาตั้งค่า GitHub Token ก่อนบันทึก")
                self.configure_token()
            self._refresh_sync_state()
            return
        if not self.sha:
            if not automatic:
                QMessageBox.warning(self, "ยังไม่มี GitHub SHA",
                                    "ต้องโหลดข้อมูล GitHub อย่างน้อยหนึ่งครั้งก่อนบันทึก")
            self._refresh_sync_state()
            return
        if automatic and (not self.auto_sync_enabled or
                          not self.dirty or self.sync_paused_conflict):
            return
        if not automatic and QMessageBox.question(
                self, "บันทึก GitHub Commit",
                f"บันทึก BOM {len(self.payload['items'])} รายการ "
                "พร้อม Wiring และ Purchasing หรือไม่?"
        ) != QMessageBox.StandardButton.Yes:
            return

        self.busy = True
        self.sync_btn.setEnabled(False)
        self.auto_sync_timer.stop()
        self._refresh_sync_state()
        rev = self.revision
        snapshot = copy.deepcopy(self.payload)
        snapshot["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        expected_sha = self.sha
        body = base64.b64encode(
            json.dumps(snapshot, ensure_ascii=False, indent=2).encode("utf-8")
        ).decode("ascii")
        saved_token = self.token

        def work():
            # Check against the live GitHub file before each attempted push.
            # GitHub PUT's SHA also protects against a race after this GET.
            remote = github_api("GET", token=saved_token)
            if remote.get("sha") != expected_sha:
                return {"conflict": True, "remote_sha": remote.get("sha")}
            result = github_api("PUT", {
                "message": ("Auto Save BOM" if automatic else "Save BOM") +
                           f" from Desktop v{VERSION}",
                "branch": "main", "sha": expected_sha, "content": body,
            }, token=saved_token)
            return {"conflict": False, "result": result}

        def conflict_detected():
            self.sync_paused_conflict = True
            self.last_git_ok = False
            self._write_cache()
            self._refresh_sync_state()
            text = ("ข้อมูลบน GitHub เปลี่ยนจากเครื่องอื่นแล้ว "
                    "ระบบหยุด Auto Save เพื่อป้องกันการบันทึกทับ "
                    "ฉบับร่างในเครื่องยังอยู่ครบ กรุณาส่งออก JSON Backup "
                    "แล้วตรวจสอบ/โหลดข้อมูล GitHub ล่าสุดก่อนซิงก์อีกครั้ง")
            self.debugger.event("WARNING", "github", "AUTO_SYNC_CONFLICT", text)
            self.set_status(text)
            if not automatic:
                QMessageBox.warning(self, "GitHub ข้อมูลชนกัน", text)

        def finish(data):
            self.busy = False
            self.sync_btn.setEnabled(True)
            if data.get("conflict"):
                conflict_detected()
                return
            result = data["result"]
            self.sha = result["content"]["sha"]
            self.last_github_sync_at = datetime.now(timezone.utc)
            self.sync_paused_conflict = False
            self.last_git_ok = True
            self.debugger.event(
                "INFO", "github",
                "AUTO_SYNC_OK" if automatic else "BOM_COMMITTED",
                "Auto Save GitHub สำเร็จ" if automatic else "บันทึก GitHub Commit สำเร็จ")
            if rev == self.revision:
                self.payload = snapshot
                self.dirty = False
            else:
                # Newer edits were made while the network was working.
                self.dirty = True
            self._write_cache()
            self.render_all()
            self.set_status("ซิงก์ GitHub สำเร็จ" +
                            (" · มีข้อมูลแก้ไขใหม่รอซิงก์" if self.dirty else ""))
            if self.dirty:
                self._schedule_auto_sync()

        def failed(message):
            self.busy = False
            self.sync_btn.setEnabled(True)
            if ("conflict" in message.casefold() or
                    "ข้อมูลใหม่กว่าที่โหลดไว้" in message):
                conflict_detected()
                return
            self.last_git_ok = False
            self._write_cache()
            self._refresh_sync_state()
            self.debugger.event(
                "WARNING", "github", "AUTO_SYNC_RETRY" if automatic else "SYNC_FAILED",
                "GitHub Sync ไม่สำเร็จ; เก็บข้อมูลไว้ในเครื่องและจะลองอีกครั้ง")
            if automatic:
                self.set_status("GitHub ไม่พร้อม · เก็บฉบับร่างในเครื่องแล้ว "
                                "· จะลองซิงก์ใหม่อัตโนมัติ")
            else:
                self._message_error(message)

        self._job(work, finish, failed, context="github")

    def show_history(self):
        self.set_status("กำลังอ่าน GitHub Commit History…")
        def display(data):
            dlg = QDialog(self)
            dlg.setWindowTitle("ประวัติ GitHub Commit — BOM")
            dlg.resize(950, 590)
            l = QVBoxLayout(dlg)
            history = self._table(["Commit", "วันที่", "รายละเอียด"], 2)
            history.setColumnWidth(0, 145)
            history.setColumnWidth(1, 200)
            history.setRowCount(len(data))
            for i, entry in enumerate(data):
                row = [entry.get("sha", "")[:12],
                       entry.get("commit", {}).get("author", {}).get("date", ""),
                       entry.get("commit", {}).get("message", "").splitlines()[0]]
                for j, text in enumerate(row):
                    history.setItem(i, j, QTableWidgetItem(text))
            l.addWidget(history)
            def open_commit():
                row = history.currentRow()
                if 0 <= row < len(data):
                    webbrowser.open(data[row]["html_url"])
            l.addWidget(self._button("เปิด Commit ที่เลือก", open_commit))
            self.set_status(f"พบประวัติการเปลี่ยนแปลง {len(data)} Commit")
            dlg.exec()
        self._job(lambda: github_api(
            "GET", token=self.token,
            url=f"{API}/commits?path=bom-manager%2Fbom.json&per_page=30"), display)

    def _report_options(self):
        dialog = ReportOptionsDialog(self.payload, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        return dialog.values()

    def export_report_pair(self):
        options = self._report_options()
        if options is None:
            return
        folder = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์บันทึกรายงาน PDF + Excel")
        if not folder:
            return
        base = Path(folder) / ("Engineering_BOM_Report_v" + VERSION)
        try:
            bom_official_reports.export_pdf(self.payload, base.with_suffix(".pdf"), options)
            bom_official_reports.export_excel(self.payload, base.with_suffix(".xlsx"), options)
            self.debugger.event("INFO", "export", "OFFICIAL_PAIR_EXPORTED",
                                "บันทึกรายงาน PDF และ Excel แล้ว")
            self.set_status("ส่งออกรายงานทางการครบทั้ง PDF และ Excel")
            QMessageBox.information(self, "ส่งออกรายงานสำเร็จ",
                                    "สร้าง PDF และ Excel ในโฟลเดอร์ที่เลือกแล้ว")
        except Exception as exc:
            self.debugger.exception("export", "OFFICIAL_PAIR_FAILED", exc)
            self._message_error("ส่งออกรายงานไม่สำเร็จ กรุณาตรวจ Debug Report")

    def export(self, kind):
        formats = {
            "xlsx": ("Excel files (*.xlsx)", bom_official_reports.export_excel),
            "pdf": ("PDF files (*.pdf)", bom_official_reports.export_pdf),
            "csv": ("CSV files (*.csv)", bom_reports.export_csv),
            "json": ("JSON backup (*.json)", bom_reports.export_json),
            "drawio": ("Draw.io (*.drawio)", bom_reports.export_drawio),
        }
        if kind not in formats:
            return
        options = None
        if kind in ("xlsx", "pdf"):
            options = self._report_options()
            if options is None:
                return
        filters, func = formats[kind]
        name = ("Engineering_BOM_Report" if kind in ("xlsx","pdf") else
                "CraneVehicle_BOM") + "_v" + VERSION + "." + kind
        path, _ = QFileDialog.getSaveFileName(self, "ส่งออกรายงาน",
                                              name, filters)
        if not path:
            return
        try:
            if kind in ("xlsx","pdf"):
                func(self.payload, path, options)
            else:
                func(self.payload, path)
            self.debugger.event("INFO", "export", "EXPORT_OK",
                                f"ส่งออกรายงานประเภท {kind} สำเร็จ")
            self.set_status("ส่งออกสำเร็จ: " + path)
            QMessageBox.information(self, "ส่งออกสำเร็จ",
                                    "บันทึกไฟล์แล้ว:\n" + path)
        except Exception as exc:
            self.debugger.exception("export", "EXPORT_FAILED", exc)
            self._message_error(f"ส่งออก {kind} ไม่สำเร็จ: {type(exc).__name__}")


    def import_backup(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือก JSON Backup", "", "JSON files (*.json)")
        if not path:
            return
        try:
            document = json.loads(Path(path).read_text(encoding="utf-8-sig"))
            bom_core.ensure_doc(document)
        except (OSError, ValueError) as exc:
            self.debugger.exception("import", "IMPORT_FAILED", exc)
            self._message_error("นำเข้า JSON ไม่สำเร็จ กรุณาดู Debug Report")
            return
        if QMessageBox.question(
                self, "ยืนยันนำเข้า Backup",
                f"นำเข้า BOM {len(document['items'])} รายการหรือไม่?\n"
                "ข้อมูลใหม่จะอยู่เป็นฉบับร่างในเครื่อง ยังไม่ Commit ขึ้น GitHub") != QMessageBox.StandardButton.Yes:
            return
        self.payload = document
        self.debugger.event("INFO", "import", "BACKUP_IMPORTED", "นำเข้า JSON Backup แล้ว")
        self.changed()
        self.show_page(1)

    def open_cache_dir(self):
        folder = self.cache_path.parent
        if sys.platform == "win32":
            os.startfile(str(folder))
        else:
            webbrowser.open(folder.as_uri())

    def check_version(self, silent=False):
        if self.downloading or not self.update_btn.isEnabled():
            return
        self.update_btn.setEnabled(False)
        self.set_status("กำลังตรวจสอบเวอร์ชันใหม่จาก GitHub…")
        def success(info):
            self.update_btn.setEnabled(True)
            self.update_info = info
            self.debugger.event("INFO", "updater", "VERSION_CHECK_OK",
                                "พบเวอร์ชันใหม่" if info else "ใช้เวอร์ชันล่าสุด")
            self.install_btn.setEnabled(info is not None)
            self.install_btn.setVisible(info is not None)
            self.version_label.setText(
                f"มี v{info['version']} ใหม่" if info else f"เวอร์ชัน v{VERSION} • ล่าสุด")
            self.set_status(f"พบเวอร์ชันใหม่ v{info['version']}" if info
                            else f"BOM Manager v{VERSION} เป็นเวอร์ชันล่าสุด")
            if info and not silent:
                QMessageBox.information(self, "พบเวอร์ชันใหม่",
                                        f"พร้อมอัปเดตจาก v{VERSION} เป็น v{info['version']}")
        def failed(msg):
            self.update_btn.setEnabled(True)
            self.set_status("ตรวจเวอร์ชันไม่ได้ · " + msg.splitlines()[0])
            if not silent:
                self._message_error(msg)
        self._job(lambda: updater.find_update(VERSION), success, failed, context="updater")

    def install_update(self):
        if self.downloading or not self.update_info or self.busy:
            return
        if self.dirty:
            QMessageBox.warning(self, "ยังไม่ได้บันทึก GitHub",
                                "กรุณาบันทึก BOM ที่แก้ไขขึ้น GitHub ก่อนอัปเดต")
            return
        if sys.platform != "win32" or not getattr(sys, "frozen", False):
            QMessageBox.warning(self, "ติดตั้งอัตโนมัติไม่ได้",
                                "การติดตั้งอัปเดตรองรับโปรแกรม .exe ที่ติดตั้งบน Windows เท่านั้น")
            return
        info = self.update_info
        if QMessageBox.question(
                self, "ยืนยันอัปเดต",
                f"ดาวน์โหลดและติดตั้ง BOM Manager v{info['version']} หรือไม่?\n"
                "ไฟล์จะผ่านการตรวจขนาดและ SHA256 ก่อนเปิดตัวติดตั้ง") != QMessageBox.StandardButton.Yes:
            return
        from PySide6.QtWidgets import QProgressDialog
        progress = QProgressDialog("กำลังดาวน์โหลดตัวติดตั้ง…", "ยกเลิก", 0, 100, self)
        progress.setWindowTitle("BOM Manager Update")
        progress.setMinimumDuration(0)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.downloading = True
        self.cancel_download.clear()
        self.install_btn.setEnabled(False)
        progress.canceled.connect(self.cancel_download.set)

        class UpdaterJob(QThread):
            amount = Signal(int)
            succeeded = Signal(object)
            failed = Signal(str)
            def run(inner):
                try:
                    def percent(done, size):
                        inner.amount.emit(min(100, int(done * 100 / max(1, size))))
                    path = updater.download_update(
                        info, progress=percent, cancelled=self.cancel_download)
                    inner.succeeded.emit(path)
                except Exception as exc:
                    self.debugger.exception("updater", "INSTALLER_DOWNLOAD_FAILED", exc)
                    inner.failed.emit(friendly_error(exc))
        job = UpdaterJob(self)
        self.jobs.add(job)
        job.amount.connect(progress.setValue)
        def end():
            self.downloading = False
            progress.close()
            self.install_btn.setEnabled(True)
        def done(path):
            end()
            try:
                subprocess.Popen([str(path), "/NORESTART"], cwd=str(path.parent),
                                 close_fds=True)
            except Exception as exc:
                shutil.rmtree(path.parent, ignore_errors=True)
                self._message_error(str(exc))
                return
            self.debugger.event("INFO", "updater", "INSTALLER_STARTED",
                                "ดาวน์โหลดและเปิดตัวติดตั้งอัปเดตแล้ว")
            self.set_status("เปิดตัวติดตั้งแล้ว · กำลังปิดเวอร์ชันเก่า")
            QApplication.instance().quit()
        def failed(msg):
            end()
            if "ยกเลิก" not in msg:
                self._message_error(msg)
        job.succeeded.connect(done)
        job.failed.connect(failed)
        job.finished.connect(lambda j=job: self.jobs.discard(j))
        job.start()

    def closeEvent(self, event):
        if self.busy or self.downloading:
            QMessageBox.information(self, "ยังทำงานอยู่",
                                    "กรุณารอการเชื่อมต่อ/ดาวน์โหลดให้เสร็จก่อนปิด")
            event.ignore()
            return
        if self.dirty:
            self._write_cache()
            if QMessageBox.question(
                    self, "ยังไม่บันทึก GitHub",
                    "มีฉบับร่างที่ยังไม่ได้บันทึกขึ้น GitHub\n"
                    "โปรแกรมเก็บฉบับร่างในเครื่องแล้ว ต้องการปิดหรือไม่?") != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        event.accept()


def main():
    # Qt 6 is per-monitor DPI aware. Keep fractional Windows display scaling
    # accurate so glyphs are rasterized for the real device scale.
    from PySide6.QtGui import QGuiApplication
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    reporter = bom_debug.DebugReporter(version=VERSION)
    bom_debug.install_hooks(reporter)
    app = QApplication(sys.argv)
    app.setApplicationName("Crane Vehicle BOM Manager")
    theme.apply_theme(app)
    window = BOMWindow(debugger=reporter)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
