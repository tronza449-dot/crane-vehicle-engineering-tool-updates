"""BOM Manager v1.2 UI: dashboard, BOM, wiring, purchasing, exports, sync.

Wraps the original app to preserve the existing GitHub updater/token workflow.
"""
import base64
import json
import os
import threading
import tkinter as tk
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from urllib.request import Request, urlopen

import bom_core
import bom_reports


WIRE_FIELDS = [
    ("from", "ต้นทาง / Terminal"), ("to", "ปลายทาง / Terminal"),
    ("fromItemId", "BOM ID ต้นทาง"), ("toItemId", "BOM ID ปลายทาง"),
    ("signal", "ชื่อสัญญาณ/วงจร"), ("voltage", "แรงดัน/ประเภทวงจร"),
    ("cable", "ชนิดสาย/ขนาดหน้าตัด"), ("protection", "ฟิวส์/การป้องกัน"),
    ("status", "สถานะ"), ("notes", "หมายเหตุ"),
]
PURCHASE_FIELDS = [
    ("itemId", "BOM ID อ้างอิง"), ("description", "อุปกรณ์ที่สั่งซื้อ"),
    ("supplier", "ร้านค้า/ผู้ขาย"), ("qty", "จำนวน"),
    ("unitPrice", "ราคา/หน่วย (THB)"), ("status", "สถานะ"),
    ("po", "เลขอ้างอิง PO/Order"), ("dueDate", "วันคาดรับ YYYY-MM-DD"),
    ("link", "ลิงก์ร้านค้า"), ("notes", "หมายเหตุ"),
]
PURCHASE_STATUS = ("วางแผน", "ขอราคา", "สั่งแล้ว", "ได้รับแล้ว", "ยกเลิก")
WIRE_STATUS = ("รอตรวจสอบ", "ตรวจสอบแล้ว", "แก้ไขแบบ", "ยกเลิก")


class DetailDialog(tk.Toplevel):
    def __init__(self, parent, title, fields, values=None, options=None):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.result = None
        self.fields = fields
        self.vars = {}
        self.geometry("720x600")
        self.minsize(510, 420)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        shell = ttk.Frame(self)
        shell.grid(row=0, column=0, sticky="nsew")
        canvas = tk.Canvas(shell, highlightthickness=0)
        vs = ttk.Scrollbar(shell, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vs.set)
        canvas.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")
        body = ttk.Frame(canvas, padding=16)
        window = canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window, width=e.width))
        body.columnconfigure(1, weight=1)
        values = values or {}
        options = options or {}
        for i, (key, label) in enumerate(fields):
            ttk.Label(body, text=label).grid(row=i, column=0, padx=(0, 14), pady=6, sticky="nw")
            if key in ("notes", "spec", "connection"):
                widget = tk.Text(body, height=4, wrap="word")
                widget.insert("1.0", str(values.get(key) or ""))
                widget.grid(row=i, column=1, sticky="ew", pady=5)
                self.vars[key] = widget
            else:
                var = tk.StringVar(value="" if values.get(key) is None else str(values.get(key)))
                if key in options:
                    widget = ttk.Combobox(body, textvariable=var, values=options[key], state="readonly")
                    if not var.get():
                        var.set(options[key][0])
                else:
                    widget = ttk.Entry(body, textvariable=var)
                widget.grid(row=i, column=1, sticky="ew", pady=5)
                self.vars[key] = var
        buttons = ttk.Frame(self, padding=(10, 6, 10, 12))
        buttons.grid(row=1, column=0, sticky="ew")
        ttk.Button(buttons, text="บันทึก", command=self.accept).pack(side="right", padx=4)
        ttk.Button(buttons, text="ยกเลิก", command=self.destroy).pack(side="right")
        self.bind("<Escape>", lambda _e: self.destroy())
        self.wait_visibility()
        self.grab_set()
        self.focus_set()

    def accept(self):
        result = {}
        for key, _label in self.fields:
            widget = self.vars[key]
            result[key] = (widget.get("1.0", "end-1c") if isinstance(widget, tk.Text)
                           else widget.get()).strip()
        self.result = result
        self.destroy()


def make_app(BaseApp, ItemDialog, api_request, app_version, api_url, service, item_fields):
    class BOMManagerPlus(BaseApp):
        def __init__(self):
            self.cache_file = self._cache_folder() / "draft.json"
            self._cached_state = self._read_cache()
            self._first_load = True
            super().__init__()
            self.title("Crane Vehicle BOM Manager — v" + app_version)
            self.geometry("1440x850")
            self.protocol("WM_DELETE_WINDOW", self._close_app)
            self.bind_all("<Control-s>", lambda e: self.save_remote())
            self.bind_all("<Control-e>", lambda e: self.export_excel())
            self.bind_all("<Control-f>", self._focus_search)

        @staticmethod
        def _cache_folder():
            home = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".local" / "share")
            path = Path(home) / "CraneVehicleBOMManager"
            path.mkdir(parents=True, exist_ok=True)
            return path

        def _read_cache(self):
            try:
                with open(self.cache_file, encoding="utf-8") as f:
                    snapshot = json.load(f)
                bom_core.ensure_doc(snapshot["payload"])
                return snapshot
            except (OSError, ValueError, KeyError, TypeError):
                return None

        def _persist_cache(self):
            snapshot = {"payload": self.payload, "sha": self.file_sha,
                        "dirty": bool(self.dirty),
                        "time": datetime.now(timezone.utc).isoformat()}
            tmp = self.cache_file.with_suffix(".tmp")
            try:
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(snapshot, f, ensure_ascii=False, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, self.cache_file)
                self._cached_state = snapshot
            except OSError as exc:
                self.status_var.set(f"บันทึกฉบับร่างในเครื่องไม่ได้: {exc}")

        def _focus_search(self, _event):
            self.tabs.select(self.bom_tab)
            self.search_entry.focus_set()

        def _close_app(self):
            if self._remote_busy:
                messagebox.showinfo("กำลังเชื่อมต่อ GitHub", "โปรดดำเนินการโหลด/บันทึกให้เสร็จก่อนปิด", parent=self)
                return
            self._persist_cache()
            if self.dirty and not messagebox.askyesno(
                    "ยังไม่ได้บันทึก GitHub",
                    "มีการแก้ไขที่ยังไม่บันทึกขึ้น GitHub\n"
                    "โปรแกรมเก็บฉบับร่างไว้ในเครื่องแล้ว ต้องการปิดหรือไม่?", parent=self):
                return
            self.destroy()

        def _build_ui(self):
            style = ttk.Style(self)
            if "clam" in style.theme_names():
                style.theme_use("clam")
            style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=(17, 10))
            style.configure("Treeview", font=("Segoe UI", 10), rowheight=31)
            style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
            style.configure("Header.TLabel", font=("Segoe UI", 17, "bold"), foreground="#173853")
            style.configure("Metric.TLabel", font=("Segoe UI", 17, "bold"), foreground="#173853")
            style.configure("Hint.TLabel", foreground="#65788B")
            self.configure(background="#F4F7FB")

            top = ttk.Frame(self, padding=(14, 12))
            top.pack(fill="x")
            ttk.Label(top, text="CRANE VEHICLE · BOM MANAGER", style="Header.TLabel").pack(side="left")
            ttk.Button(top, text="ตั้งค่า GitHub Token", command=self.configure_token).pack(side="right", padx=4)
            ttk.Button(top, text="โหลดจาก GitHub", command=self.load_remote).pack(side="right", padx=4)
            ttk.Button(top, text="บันทึกขึ้น GitHub", command=self.save_remote).pack(side="right", padx=4)
            version_row = ttk.Frame(self, padding=(14, 0, 14, 10))
            version_row.pack(fill="x")
            ttk.Label(version_row, text=f"v{app_version}  •  Windows Desktop", style="Hint.TLabel").pack(side="left")
            ttk.Label(version_row, textvariable=self.update_status_var, style="Hint.TLabel").pack(side="left", padx=16)
            self.check_update_button = ttk.Button(version_row, text="ตรวจสอบเวอร์ชัน", command=self.check_updates)
            self.check_update_button.pack(side="right", padx=4)
            self.install_update_button = ttk.Button(version_row, text="อัปเดตตอนนี้",
                                                     command=self.install_update, state="disabled")
            self.install_update_button.pack(side="right", padx=4)

            self.tabs = ttk.Notebook(self)
            self.tabs.pack(fill="both", expand=True, padx=12, pady=(0, 7))
            self.home_tab = ttk.Frame(self.tabs, padding=14)
            self.bom_tab = ttk.Frame(self.tabs, padding=8)
            self.wire_tab = ttk.Frame(self.tabs, padding=8)
            self.buy_tab = ttk.Frame(self.tabs, padding=8)
            self.sync_tab = ttk.Frame(self.tabs, padding=12)
            for tab, name in [(self.home_tab, "ภาพรวม"), (self.bom_tab, "BOM อุปกรณ์"),
                              (self.wire_tab, "Wiring Manager"), (self.buy_tab, "จัดซื้อ"),
                              (self.sync_tab, "GitHub / ส่งออก")]:
                self.tabs.add(tab, text=name)
            self._build_dashboard()
            self._build_bom()
            self._build_wiring()
            self._build_purchasing()
            self._build_sync()

            footer = ttk.Frame(self, padding=(13, 5, 13, 9))
            footer.pack(fill="x")
            self.total_label = ttk.Label(footer, text="ยอดรวมที่ทราบ: —", font=("Segoe UI", 10, "bold"))
            self.total_label.pack(side="left")
            ttk.Label(footer, textvariable=self.status_var, style="Hint.TLabel").pack(side="right")

        def _build_dashboard(self):
            ttk.Label(self.home_tab, text="ภาพรวมโครงการ / Budget", style="Header.TLabel").pack(anchor="w", pady=(0, 12))
            row = ttk.Frame(self.home_tab)
            row.pack(fill="x")
            self.kpi_vars = {}
            tiles = [("items", "รายการอุปกรณ์"), ("priced", "รายการมีราคา"),
                     ("missing", "รายการยังไม่มีราคา"), ("known_cost", "ยอดรวมที่ทราบ (THB)"),
                     ("wires", "จุดต่อสาย"), ("purchase_count", "รายการจัดซื้อ")]
            for idx, (key, label) in enumerate(tiles):
                tile = ttk.LabelFrame(row, text=label, padding=14)
                tile.grid(row=idx // 3, column=idx % 3, sticky="nsew", padx=5, pady=7)
                self.kpi_vars[key] = tk.StringVar(value="—")
                ttk.Label(tile, textvariable=self.kpi_vars[key], style="Metric.TLabel").pack(anchor="w")
            for idx in range(3):
                row.columnconfigure(idx, weight=1)
            ttk.Label(self.home_tab, text="การกระจายอุปกรณ์ตามหมวด", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(25, 8))
            self.category_tree = ttk.Treeview(self.home_tab, columns=("category", "count"), show="headings", height=9)
            self.category_tree.heading("category", text="หมวด")
            self.category_tree.heading("count", text="จำนวนรายการ")
            self.category_tree.column("category", width=360)
            self.category_tree.column("count", width=110, anchor="center")
            self.category_tree.pack(fill="both", expand=True)
            self.warning_var = tk.StringVar()
            ttk.Label(self.home_tab, textvariable=self.warning_var, style="Hint.TLabel",
                      wraplength=1160).pack(anchor="w", pady=(10, 0))

        @staticmethod
        def _table(parent, columns, headings, widths):
            frame = ttk.Frame(parent)
            frame.pack(fill="both", expand=True)
            tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
            for column in columns:
                tree.heading(column, text=headings.get(column, column))
                tree.column(column, width=widths.get(column, 120),
                            anchor="center" if column in {"id", "qty", "unit", "unitPrice", "lineTotal", "voltage", "itemId"} else "w")
            yscroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            xscroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            tree.grid(row=0, column=0, sticky="nsew")
            yscroll.grid(row=0, column=1, sticky="ns")
            xscroll.grid(row=1, column=0, sticky="ew")
            return tree

        def _build_bom(self):
            controls = ttk.Frame(self.bom_tab, padding=(0, 0, 0, 9))
            controls.pack(fill="x")
            ttk.Label(controls, text="ค้นหา:").pack(side="left")
            self.search_entry = ttk.Entry(controls, textvariable=self.search_var, width=30)
            self.search_entry.pack(side="left", padx=6)
            self.search_var.trace_add("write", lambda *_: self.refresh_table())
            self.category_var = tk.StringVar(value="ทุกหมวด")
            self.cat_combo = ttk.Combobox(controls, textvariable=self.category_var,
                                          state="readonly", width=27, values=["ทุกหมวด"])
            self.cat_combo.pack(side="left", padx=6)
            self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
            ttk.Button(controls, text="+ เพิ่มอุปกรณ์", command=self.add_item).pack(side="left", padx=3)
            ttk.Button(controls, text="แก้ไข", command=self.edit_item).pack(side="left", padx=3)
            ttk.Button(controls, text="ลบ", command=self.delete_item).pack(side="left", padx=3)
            ttk.Button(controls, text="สร้างรายการจัดซื้อจากที่เลือก", command=self.buy_selected_bom).pack(side="right", padx=3)
            columns = ("category", "name", "qty", "unit", "unitPrice", "lineTotal", "status")
            self.tree = self._table(self.bom_tab, columns,
                                    {"category": "กลุ่ม", "name": "อุปกรณ์ / รุ่น",
                                     "qty": "จำนวน", "unit": "หน่วย", "unitPrice": "ราคา/หน่วย",
                                     "lineTotal": "รวม (บาท)", "status": "สถานะออกแบบ"},
                                    {"category": 220, "name": 470, "qty": 85, "unit": 90,
                                     "unitPrice": 130, "lineTotal": 130, "status": 280})
            self.tree.bind("<Double-1>", lambda e: self.edit_item())
            ttk.Label(self.bom_tab,
                      text="หมายเหตุ: ช่องราคาว่างไม่นับเป็น 0 บาทในการประเมินงบประมาณ",
                      style="Hint.TLabel").pack(anchor="w", pady=(6, 0))

        def _build_wiring(self):
            controls = ttk.Frame(self.wire_tab, padding=(0, 0, 0, 9))
            controls.pack(fill="x")
            ttk.Button(controls, text="+ เพิ่มสาย/จุดต่อ", command=self.add_wire).pack(side="left", padx=4)
            ttk.Button(controls, text="แก้ไขจุดต่อ", command=self.edit_wire).pack(side="left", padx=4)
            ttk.Button(controls, text="ลบจุดต่อ", command=self.delete_wire).pack(side="left", padx=4)
            ttk.Button(controls, text="ตรวจสอบข้อมูล", command=self.check_wiring).pack(side="right", padx=4)
            columns = ("id", "from", "to", "signal", "voltage", "cable", "protection", "status")
            self.wiring_tree = self._table(self.wire_tab, columns,
                                          {"id": "ID", "from": "ต้นทาง / Terminal",
                                           "to": "ปลายทาง / Terminal", "signal": "สัญญาณ",
                                           "voltage": "แรงดัน", "cable": "ชนิด/ขนาดสาย",
                                           "protection": "ฟิวส์/การป้องกัน", "status": "สถานะ"},
                                          {"id": 55, "from": 230, "to": 230, "signal": 190,
                                           "voltage": 140, "cable": 180, "protection": 220,
                                           "status": 150})
            self.wiring_tree.bind("<Double-1>", lambda e: self.edit_wire())
            ttk.Label(self.wire_tab,
                      text="ข้อมูลเดินสายเป็นฉบับร่าง ไม่ใช่วงจรรับรอง — ต้องตรวจแรงดัน พิกัดกระแส ขั้วต่อ ฟิวส์ และคู่มืออุปกรณ์จริง",
                      style="Hint.TLabel").pack(anchor="w", pady=(7, 0))

        def _build_purchasing(self):
            controls = ttk.Frame(self.buy_tab, padding=(0, 0, 0, 9))
            controls.pack(fill="x")
            ttk.Button(controls, text="+ เพิ่มรายการจัดซื้อ", command=self.add_purchase).pack(side="left", padx=4)
            ttk.Button(controls, text="แก้ไขการจัดซื้อ", command=self.edit_purchase).pack(side="left", padx=4)
            ttk.Button(controls, text="ลบรายการ", command=self.delete_purchase).pack(side="left", padx=4)
            self.purchase_label = tk.StringVar(value="ยอดรวมรายการจัดซื้อ: 0 บาท")
            ttk.Label(controls, textvariable=self.purchase_label,
                      font=("Segoe UI", 11, "bold")).pack(side="right", padx=8)
            columns = ("itemId", "description", "supplier", "qty", "unitPrice",
                       "lineTotal", "status", "po", "dueDate")
            self.purchase_tree = self._table(self.buy_tab, columns,
                                             {"itemId": "BOM ID", "description": "รายการ",
                                              "supplier": "ผู้ขาย", "qty": "จำนวน",
                                              "unitPrice": "ราคา/หน่วย", "lineTotal": "รวม",
                                              "status": "สถานะจัดซื้อ", "po": "PO",
                                              "dueDate": "กำหนดรับ"},
                                             {"itemId": 75, "description": 330, "supplier": 220,
                                              "qty": 80, "unitPrice": 120, "lineTotal": 130,
                                              "status": 150, "po": 130, "dueDate": 130})
            self.purchase_tree.bind("<Double-1>", lambda e: self.edit_purchase())
            ttk.Label(self.buy_tab,
                      text="รายการจัดซื้อแยกจากสถานะการเลือกอุปกรณ์ใน BOM — ยอดจัดซื้ออาจแตกต่างจากประมาณการ",
                      style="Hint.TLabel").pack(anchor="w", pady=(7, 0))

        def _build_sync(self):
            ttk.Label(self.sync_tab, text="GitHub Sync / สำรองข้อมูล / รายงาน", style="Header.TLabel").pack(anchor="w", pady=(0, 15))
            top = ttk.LabelFrame(self.sync_tab, text="ข้อมูล GitHub", padding=12)
            top.pack(fill="x", pady=7)
            ttk.Button(top, text="โหลดล่าสุด", command=self.load_remote).pack(side="left", padx=5)
            ttk.Button(top, text="บันทึกเป็น GitHub Commit", command=self.save_remote).pack(side="left", padx=5)
            ttk.Button(top, text="ประวัติ Commit", command=self.show_history).pack(side="left", padx=5)
            ttk.Button(top, text="เปิดหน้า Repository", command=lambda: webbrowser.open(
                "https://github.com/tronza449-dot/crane-vehicle-engineering-tool-updates/tree/main/bom-manager")).pack(side="left", padx=5)
            export = ttk.LabelFrame(self.sync_tab, text="ส่งออกข้อมูล", padding=12)
            export.pack(fill="x", pady=7)
            for name, action in [("Excel (.xlsx)", self.export_excel),
                                 ("PDF Report", self.export_pdf),
                                 ("CSV (BOM)", self.export_csv),
                                 ("JSON สำรอง", self.export_json)]:
                ttk.Button(export, text=name, command=action).pack(side="left", padx=6)
            restore = ttk.LabelFrame(self.sync_tab, text="กู้คืน/สำรองข้อมูล", padding=12)
            restore.pack(fill="x", pady=7)
            ttk.Button(restore, text="นำเข้า JSON Backup", command=self.import_json).pack(side="left", padx=5)
            ttk.Button(restore, text="เปิดโฟลเดอร์ฉบับร่าง", command=self.open_cache).pack(side="left", padx=5)
            ttk.Label(restore, text="ระบบบันทึกฉบับร่างลงเครื่องอัตโนมัติทุกครั้งที่แก้ข้อมูล",
                      style="Hint.TLabel").pack(side="left", padx=16)
            note = ttk.LabelFrame(self.sync_tab, text="ข้อแนะนำ", padding=14)
            note.pack(fill="x", pady=7)
            ttk.Label(note, justify="left", text=(
                "• กด 'บันทึกเป็น GitHub Commit' เมื่อต้องการแชร์ข้อมูลกับคอมเครื่องอื่น\n"
                "• กด 'โหลดล่าสุด' เมื่อมีผู้อื่นแก้ BOM ผ่านเว็บหรือ GitHub\n"
                "• หากแก้ข้อมูลค้างไว้ โปรแกรมเก็บฉบับร่างในเครื่อง และเตือนก่อนเขียนทับ\n"
                "• ข้อมูล Wiring/Purchasing อยู่ในไฟล์ BOM JSON เดียวกัน; หน้าเว็บรุ่นเก่าอาจยังไม่มีหน้าแก้ไขสองหมวดนี้\n"
                "• Backup JSON เก็บข้อมูลทั้งหมด; Export CSV มีเฉพาะรายการอุปกรณ์\n"
                "• การจัดเก็บ Token อยู่ใน Windows Credential Manager ไม่ฝังในรายงาน"), style="Hint.TLabel").pack(anchor="w")

        def refresh_table(self):
            # Base method maintains the original GitHub BOM Treeview without rewriting item data.
            super().refresh_table()
            if hasattr(self, "category_var"):
                categories = sorted({str(x.get("category") or "ไม่ระบุ")
                                     for x in self.payload.get("items", [])})
                selected = self.category_var.get()
                self.cat_combo.configure(values=["ทุกหมวด"] + categories)
                if selected not in categories and selected != "ทุกหมวด":
                    self.category_var.set("ทุกหมวด")
                selected = self.category_var.get()
                if selected != "ทุกหมวด":
                    for iid in self.tree.get_children():
                        if str(self.payload["items"][int(iid)].get("category") or "ไม่ระบุ") != selected:
                            self.tree.delete(iid)
            if not hasattr(self, "kpi_vars"):
                return
            summary = bom_core.metrics(self.payload)
            for key in ("items", "priced", "missing", "wires", "purchase_count"):
                self.kpi_vars[key].set(str(summary[key]))
            self.kpi_vars["known_cost"].set(f"{summary['known_cost']:,.2f}")
            for iid in self.category_tree.get_children():
                self.category_tree.delete(iid)
            for category, count in sorted(summary["categories"].items()):
                self.category_tree.insert("", "end", values=(category, count))
            self.warning_var.set(
                f"ยอดรวมเฉพาะรายการที่มีราคา — ยังไม่มีราคา {summary['missing']} รายการ; "
                f"สายไฟ {summary['wires']} จุดต่อ; การจัดซื้อ {summary['purchase_count']} รายการ")
            if hasattr(self, "wiring_tree"):
                self._refresh_wires()
            if hasattr(self, "purchase_tree"):
                self._refresh_purchases()

        def _refresh_wires(self):
            for iid in self.wiring_tree.get_children():
                self.wiring_tree.delete(iid)
            for idx, item in enumerate(self.payload.get("wiring", [])):
                self.wiring_tree.insert("", "end", iid=str(idx),
                                        values=tuple(item.get(k, "") for k in
                                                     ("id", "from", "to", "signal", "voltage",
                                                      "cable", "protection", "status")))

        def _refresh_purchases(self):
            for iid in self.purchase_tree.get_children():
                self.purchase_tree.delete(iid)
            for idx, item in enumerate(self.payload.get("purchases", [])):
                qty = bom_core.decimal_or_none(item.get("qty")) or 0
                price = bom_core.decimal_or_none(item.get("unitPrice"))
                value = f"{qty*price:,.2f}" if price is not None else "—"
                self.purchase_tree.insert("", "end", iid=str(idx),
                                          values=(item.get("itemId", ""), item.get("description", ""),
                                                  item.get("supplier", ""), item.get("qty", ""),
                                                  item.get("unitPrice", ""), value,
                                                  item.get("status", ""), item.get("po", ""),
                                                  item.get("dueDate", "")))
            summary = bom_core.metrics(self.payload)
            self.purchase_label.set(f"ยอดรวมจัดซื้อที่มีราคา: {summary['purchase_total']:,.2f} บาท")

        def _modified(self):
            self.dirty = True
            self._persist_cache()
            self.refresh_table()
            self.status_var.set("มีการแก้ไข — เก็บฉบับร่างในเครื่องแล้ว; ยังไม่ได้บันทึก GitHub")

        def add_item(self):
            dialog = DetailDialog(self, "เพิ่มอุปกรณ์ใน BOM", item_fields,
                                  values={"qty": 1, "unit": "ชิ้น", "status": "ยังไม่เลือก"})
            self.wait_window(dialog)
            if dialog.result is None:
                return
            try:
                result = bom_core.normalize_dialog_values(dialog.result)
            except bom_core.DataError as exc:
                messagebox.showerror("ข้อมูลไม่ถูกต้อง", str(exc), parent=self)
                return
            self.payload["items"].append({
                "id": bom_core.next_id(self.payload["items"]), **result
            })
            self._modified()

        def edit_item(self):
            selection = self.tree.selection()
            if not selection:
                messagebox.showinfo("เลือกรายการ", "กรุณาเลือกรายการก่อน", parent=self)
                return
            idx = int(selection[0])
            original = dict(self.payload["items"][idx])
            dialog = DetailDialog(self, "แก้ไขอุปกรณ์ BOM", item_fields, values=original)
            self.wait_window(dialog)
            if dialog.result is None:
                return
            try:
                incoming = bom_core.normalize_dialog_values(dialog.result)
            except bom_core.DataError as exc:
                messagebox.showerror("ข้อมูลไม่ถูกต้อง", str(exc), parent=self)
                return
            self.payload["items"][idx] = {**original, **incoming}
            self._modified()
            if self.tree.exists(str(idx)):
                self.tree.selection_set(str(idx))

        def delete_item(self):
            before = len(self.payload.get("items", []))
            super().delete_item()
            if len(self.payload["items"]) != before:
                self._modified()

        def _edit_rows(self, list_name, fields, title, index=None, defaults=None, options=None):
            rows = self.payload.setdefault(list_name, [])
            existing = rows[index] if index is not None else {}
            seed = {**(defaults or {}), **existing}
            dialog = DetailDialog(self, title, fields, values=seed, options=options)
            self.wait_window(dialog)
            if dialog.result is None:
                return
            result = dict(dialog.result)
            try:
                if list_name == "wiring":
                    if not result["from"] or not result["to"]:
                        raise bom_core.DataError("ต้องระบุทั้งต้นทางและปลายทาง")
                else:
                    if not result.get("description"):
                        raise bom_core.DataError("กรุณากรอกชื่อรายการจัดซื้อ")
                    result["qty"] = bom_core.valid_qty(result.get("qty"))
                    result["unitPrice"] = bom_core.valid_price(result.get("unitPrice"))
                    date = result.get("dueDate", "")
                    if date:
                        datetime.strptime(date, "%Y-%m-%d")
            except (bom_core.DataError, ValueError) as exc:
                messagebox.showerror("ข้อมูลไม่ถูกต้อง", str(exc), parent=self)
                return
            if index is None:
                rows.append({"id": bom_core.next_id(rows), **result})
            else:
                rows[index] = {**existing, **result}
            self._modified()

        @staticmethod
        def _selected_index(tree):
            picked = tree.selection()
            return int(picked[0]) if picked else None

        def add_wire(self):
            self._edit_rows("wiring", WIRE_FIELDS, "เพิ่มจุดต่อสาย (Wiring)",
                            options={"status": WIRE_STATUS})

        def edit_wire(self):
            idx = self._selected_index(self.wiring_tree)
            if idx is None:
                messagebox.showinfo("เลือกรายการ", "กรุณาเลือกจุดต่อสายก่อน", parent=self)
                return
            self._edit_rows("wiring", WIRE_FIELDS, "แก้ไขจุดต่อสาย",
                            index=idx, options={"status": WIRE_STATUS})

        def delete_wire(self):
            self._delete_row("wiring", self.wiring_tree, "จุดต่อสาย")

        def check_wiring(self):
            errors = bom_core.connection_warnings(self.payload)
            message = ("\n".join(errors[:20]) + (f"\n... อีก {len(errors)-20} รายการ" if len(errors)>20 else "")
                       if errors else "ไม่พบข้อมูลอ้างอิงที่หายหรือจุดต่อที่ไม่ครบจากการตรวจอัตโนมัติ")
            messagebox.showinfo("ตรวจข้อมูล Wiring", message +
                                "\n\nผลนี้ไม่ใช่การตรวจรับรองทางไฟฟ้า/ความปลอดภัย", parent=self)

        def add_purchase(self):
            self._edit_rows("purchases", PURCHASE_FIELDS, "เพิ่มรายการจัดซื้อ",
                            defaults={"qty": 1, "status": PURCHASE_STATUS[0]},
                            options={"status": PURCHASE_STATUS})

        def buy_selected_bom(self):
            idx = self._selected_index(self.tree)
            if idx is None:
                messagebox.showinfo("เลือกรายการ", "กรุณาเลือกอุปกรณ์ใน BOM ก่อน", parent=self)
                return
            entry = self.payload["items"][idx]
            self.tabs.select(self.buy_tab)
            self._edit_rows("purchases", PURCHASE_FIELDS, "เพิ่มการจัดซื้อจาก BOM",
                            defaults={"itemId": str(entry.get("id", "")),
                                      "description": str(entry.get("name", "")),
                                      "supplier": str(entry.get("supplier") or ""),
                                      "qty": entry.get("qty", 1),
                                      "unitPrice": entry.get("unitPrice"),
                                      "link": str(entry.get("link") or ""),
                                      "status": PURCHASE_STATUS[0]},
                            options={"status": PURCHASE_STATUS})

        def edit_purchase(self):
            idx = self._selected_index(self.purchase_tree)
            if idx is None:
                messagebox.showinfo("เลือกรายการ", "กรุณาเลือกรายการจัดซื้อก่อน", parent=self)
                return
            self._edit_rows("purchases", PURCHASE_FIELDS, "แก้ไขการจัดซื้อ",
                            index=idx, options={"status": PURCHASE_STATUS})

        def delete_purchase(self):
            self._delete_row("purchases", self.purchase_tree, "รายการจัดซื้อ")

        def _delete_row(self, list_name, tree, label):
            idx = self._selected_index(tree)
            if idx is None:
                messagebox.showinfo("เลือกรายการ", f"กรุณาเลือก{label}ก่อน", parent=self)
                return
            if messagebox.askyesno("ยืนยันลบ", f"ลบ{label}ที่เลือกใช่หรือไม่?", parent=self):
                del self.payload[list_name][idx]
                self._modified()

        def load_remote(self):
            if self._first_load:
                self._first_load = False
                cached = self._cached_state
                if cached and cached.get("dirty"):
                    self.payload = cached["payload"]
                    self.file_sha = cached.get("sha")
                    self.dirty = True
                    self.refresh_table()
                    self.status_var.set("กู้คืนฉบับร่างที่ยังไม่บันทึกขึ้น GitHub — ตรวจข้อมูลก่อนบันทึก")
                    return
            if self._remote_busy:
                return
            if self.dirty and not messagebox.askyesno(
                    "โหลดข้อมูลทับฉบับร่าง?",
                    "มีข้อมูลที่แก้ไขแต่ยังไม่ได้บันทึก GitHub\n"
                    "ต้องการโหลดข้อมูลใหม่ทับฉบับร่างหรือไม่? แนะนำให้ส่งออก JSON ก่อน",
                    parent=self):
                return
            def work():
                try:
                    result = api_request("GET", token=self.token)
                    content = base64.b64decode(result["content"]).decode("utf-8-sig")
                    data = json.loads(content)
                    bom_core.ensure_doc(data)
                    return data, result["sha"], "github"
                except Exception:
                    if self._cached_state:
                        return self._cached_state["payload"], self._cached_state.get("sha"), "cache"
                    raise
            def success(result):
                self.payload, self.file_sha, source = result
                self.dirty = source == "cache" and bool(self._cached_state.get("dirty", False))
                self._persist_cache()
                self.refresh_table()
                if source == "github":
                    self.status_var.set(f"โหลด GitHub สำเร็จ • {len(self.payload['items'])} รายการ")
                else:
                    self.status_var.set("ใช้ข้อมูลแคชในเครื่อง (GitHub ติดต่อไม่ได้) • อย่าลืมตรวจเวอร์ชันข้อมูล")
            self._run_async(work, success, "กำลังโหลดข้อมูลจาก GitHub…")

        def save_remote(self):
            if self._remote_busy:
                return
            try:
                bom_core.ensure_doc(self.payload)
            except bom_core.DataError as exc:
                messagebox.showerror("BOM ไม่ถูกต้อง", str(exc), parent=self)
                return
            if not self._require_token():
                return
            if not self.file_sha:
                messagebox.showwarning("ยังไม่มี SHA ล่าสุด", "กรุณาโหลดข้อมูลจาก GitHub ก่อนบันทึก", parent=self)
                return
            if not messagebox.askyesno(
                    "ยืนยันสร้าง GitHub Commit",
                    f"บันทึกอุปกรณ์ {len(self.payload['items'])} รายการ, "
                    f"Wiring {len(self.payload.get('wiring',[]))}, "
                    f"จัดซื้อ {len(self.payload.get('purchases',[]))} รายการขึ้น GitHub ใช่หรือไม่?",
                    parent=self):
                return
            snapshot = {**self.payload, "updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            payload_bytes = json.dumps(snapshot, ensure_ascii=False, indent=2).encode("utf-8")
            sha = self.file_sha
            def work():
                return api_request("PUT", {"message": f"Update BOM: {len(snapshot['items'])} items + wiring/purchases",
                                           "content": base64.b64encode(payload_bytes).decode("ascii"),
                                           "sha": sha, "branch": "main"}, token=self.token)
            def success(data):
                self.payload = snapshot
                self.file_sha = data["content"]["sha"]
                self.dirty = False
                self._cached_state = None
                self._persist_cache()
                self.refresh_table()
                self.status_var.set("บันทึกสำเร็จ • สร้าง GitHub Commit แล้ว")
                messagebox.showinfo("บันทึกสำเร็จ",
                                    "บันทึก BOM/Wiring/Purchasing ขึ้น GitHub แล้ว\n" +
                                    str(data.get("commit",{}).get("html_url", "")), parent=self)
            self._run_async(work, success, "กำลังบันทึก GitHub…")

        def _choose_export(self, extension, name, filetypes, exporter):
            dest = filedialog.asksaveasfilename(parent=self, defaultextension=extension,
                                                 initialfile=name, filetypes=filetypes)
            if not dest:
                return
            try:
                exporter(self.payload, dest)
                self.status_var.set(f"ส่งออกเรียบร้อย: {dest}")
                messagebox.showinfo("ส่งออกสำเร็จ", f"บันทึกไฟล์แล้ว:\n{dest}", parent=self)
            except Exception as exc:
                messagebox.showerror("ส่งออกไม่สำเร็จ", str(exc), parent=self)

        def export_excel(self):
            self._choose_export(".xlsx", "CraneVehicle_BOM.xlsx",
                                [("Excel Workbook", "*.xlsx")], bom_reports.export_excel)

        def export_pdf(self):
            self._choose_export(".pdf", "CraneVehicle_BOM_Report.pdf",
                                [("PDF Document", "*.pdf")], bom_reports.export_pdf)

        def export_csv(self):
            self._choose_export(".csv", "CraneVehicle_BOM.csv",
                                [("CSV UTF-8", "*.csv")], bom_reports.export_csv)

        def export_json(self):
            self._choose_export(".json", "CraneVehicle_BOM_Backup.json",
                                [("JSON Backup", "*.json")], bom_reports.export_json)

        def import_json(self):
            path = filedialog.askopenfilename(parent=self, filetypes=[("JSON Backup", "*.json")])
            if not path:
                return
            try:
                with open(path, encoding="utf-8-sig") as f:
                    doc = json.load(f)
                bom_core.ensure_doc(doc)
                if not messagebox.askyesno(
                        "ยืนยันนำเข้าข้อมูล",
                        f"นำเข้ารายการ {len(doc['items'])} รายการจากไฟล์นี้ใช่หรือไม่?\n"
                        "ระบบจะเก็บเป็นฉบับร่างก่อน (ยังไม่บันทึก GitHub)", parent=self):
                    return
                self.payload = doc
                self._modified()
                self.tabs.select(self.bom_tab)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                messagebox.showerror("นำเข้าไม่สำเร็จ", str(exc), parent=self)

        def open_cache(self):
            path = self._cache_folder()
            os.startfile(str(path)) if os.name == "nt" else webbrowser.open(path.as_uri())

        def show_history(self):
            self.status_var.set("กำลังโหลดประวัติ GitHub…")
            def work():
                url = ("https://api.github.com/repos/tronza449-dot/"
                       "crane-vehicle-engineering-tool-updates/commits?"
                       "path=bom-manager%2Fbom.json&per_page=30")
                headers = {"Accept": "application/vnd.github+json",
                           "User-Agent": "CraneVehicleBOMManager"}
                if self.token:
                    headers["Authorization"] = "Bearer " + self.token
                with urlopen(Request(url, headers=headers), timeout=25) as r:
                    return json.load(r)
            def success(data):
                win = tk.Toplevel(self)
                win.title("GitHub Commit History — BOM")
                win.geometry("980x520")
                frame = ttk.Frame(win, padding=12)
                frame.pack(fill="both", expand=True)
                tree = self._table(frame, ("sha", "date", "message"),
                                   {"sha": "Commit", "date": "วันที่", "message": "รายละเอียด"},
                                   {"sha": 125, "date": 185, "message": 660})
                tree_data = {}
                for i, item in enumerate(data):
                    sha = item.get("sha", "")
                    message = item.get("commit", {}).get("message", "").splitlines()[0]
                    date = item.get("commit", {}).get("author", {}).get("date", "")
                    tree.insert("", "end", iid=str(i), values=(sha[:12], date, message))
                    tree_data[str(i)] = item.get("html_url", "")
                def open_selected(*_):
                    selected = tree.selection()
                    if selected and tree_data.get(selected[0]):
                        webbrowser.open(tree_data[selected[0]])
                tree.bind("<Double-1>", open_selected)
                ttk.Button(win, text="เปิด Commit ที่เลือกใน GitHub", command=open_selected).pack(pady=10)
                self.status_var.set(f"แสดง GitHub Commit {len(data)} รายการ")
            self._run_async(work, success, "กำลังโหลด GitHub history…")

    return BOMManagerPlus
