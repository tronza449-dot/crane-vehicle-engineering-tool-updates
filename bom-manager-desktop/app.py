import base64
import json
import subprocess
import threading
import tkinter as tk
from datetime import datetime, timezone
from tkinter import messagebox, simpledialog, ttk
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import keyring
import updater
import bom_core


APP_VERSION = updater.current_version()
OWNER = "tronza449-dot"
REPO = "crane-vehicle-engineering-tool-updates"
BRANCH = "main"
PATH = "bom-manager/bom.json"
API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}"
SERVICE = "CraneVehicleBOMManager"
FIELDS = [
    ("category", "กลุ่ม"), ("name", "รายการ / รุ่น"), ("spec", "รายละเอียด / สเปก"),
    ("qty", "จำนวน"), ("unit", "หน่วย"), ("connection", "การต่อ / GPIO / สื่อสาร"),
    ("unitPrice", "ราคาต่อหน่วย (บาท)"), ("link", "ลิงก์สินค้า"),
    ("status", "สถานะ"), ("supplier", "ร้านค้า/ผู้ขาย"),
    ("partNumber", "รหัส Part Number"), ("notes", "หมายเหตุ"),
]


def api_request(method="GET", payload=None, token=None):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = Request(API_URL, data=data, headers=headers, method=method)
    with urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


class ItemDialog(tk.Toplevel):
    def __init__(self, parent, item=None):
        super().__init__(parent)
        self.title("แก้ไขรายการ BOM" if item else "เพิ่มรายการ BOM")
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.vars = {}
        item = item or {}
        self.columnconfigure(1, weight=1)
        for row, (key, label) in enumerate(FIELDS):
            ttk.Label(self, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="nw")
            value = item.get(key, "")
            if key in ("spec", "connection", "notes"):
                widget = tk.Text(self, width=58, height=3, wrap="word")
                widget.insert("1.0", "" if value is None else str(value))
                widget.grid(row=row, column=1, padx=10, pady=4, sticky="ew")
                self.vars[key] = widget
            else:
                var = tk.StringVar(value="" if value is None else str(value))
                widget = ttk.Entry(self, textvariable=var)
                widget.grid(row=row, column=1, padx=10, pady=4, sticky="ew")
                self.vars[key] = var
        buttons = ttk.Frame(self)
        buttons.grid(row=len(FIELDS), column=0, columnspan=2, pady=10)
        ttk.Button(buttons, text="บันทึกรายการ", command=self.accept).pack(side="left", padx=5)
        ttk.Button(buttons, text="ยกเลิก", command=self.destroy).pack(side="left", padx=5)
        self.bind("<Escape>", lambda _e: self.destroy())
        self.wait_visibility()
        self.focus_set()

    def accept(self):
        values = {}
        for key, _label in FIELDS:
            widget = self.vars[key]
            values[key] = widget.get("1.0", "end-1c").strip() if isinstance(widget, tk.Text) else widget.get().strip()
        try:
            values["qty"] = float(values["qty"] or 0)
            if values["qty"].is_integer():
                values["qty"] = int(values["qty"])
            price = values["unitPrice"].replace(",", "").strip()
            values["unitPrice"] = float(price) if price else None
        except ValueError:
            messagebox.showerror("ข้อมูลไม่ถูกต้อง", "จำนวนและราคาต้องเป็นตัวเลข", parent=self)
            return
        try:
            values = bom_core.normalize_dialog_values(values)
        except bom_core.DataError as exc:
            messagebox.showerror("ข้อมูลไม่ถูกต้อง", str(exc), parent=self)
            return
        self.result = values
        self.destroy()


class BOMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BOM Manager — รถไฟฟ้าพร้อมเครน")
        self.geometry("1420x760")
        self.minsize(950, 560)
        self.payload = {"schemaVersion": 1, "project": "รถไฟฟ้าพร้อมเครน", "currency": "THB", "items": []}
        self.file_sha = None
        self.token = keyring.get_password(SERVICE, "github-token")
        self.search_var = tk.StringVar()
        self.dirty = False
        self._remote_busy = False
        self._checking_update = False
        self._update_busy = False
        self.available_update = None
        self.update_status_var = tk.StringVar(value="ยังไม่ได้ตรวจสอบเวอร์ชัน")
        self.status_var = tk.StringVar(value="ยังไม่ได้โหลดข้อมูลจาก GitHub")
        self._build_ui()
        self.refresh_table()
        self.after(350, self.load_remote)
        self.after(2000, lambda: self.check_updates(silent=True))

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="BOM รถไฟฟ้าพร้อมเครน", font=("Segoe UI", 16, "bold")).pack(side="left")
        ttk.Button(top, text="ตั้งค่า GitHub Token", command=self.configure_token).pack(side="right", padx=4)
        ttk.Button(top, text="โหลดจาก GitHub", command=self.load_remote).pack(side="right", padx=4)
        ttk.Button(top, text="บันทึกขึ้น GitHub", command=self.save_remote).pack(side="right", padx=4)


        update_bar = ttk.Frame(self, padding=(10, 0, 10, 8))
        update_bar.pack(fill="x")
        ttk.Label(update_bar, text=f"เวอร์ชันปัจจุบัน: v{APP_VERSION}",
                  font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 12))
        ttk.Label(update_bar, textvariable=self.update_status_var).pack(side="left")
        self.check_update_button = ttk.Button(update_bar, text="ตรวจสอบเวอร์ชัน",
                                               command=self.check_updates)
        self.check_update_button.pack(side="right", padx=4)
        self.install_update_button = ttk.Button(update_bar, text="อัปเดตตอนนี้",
                                                 command=self.install_update, state="disabled")
        self.install_update_button.pack(side="right", padx=4)

        actions = ttk.Frame(self, padding=(10, 0, 10, 8))
        actions.pack(fill="x")
        ttk.Label(actions, text="ค้นหา:").pack(side="left")
        search = ttk.Entry(actions, textvariable=self.search_var, width=32)
        search.pack(side="left", padx=6)
        search.bind("<KeyRelease>", lambda _e: self.refresh_table())
        ttk.Button(actions, text="เพิ่มรายการ", command=self.add_item).pack(side="left", padx=3)
        ttk.Button(actions, text="แก้ไขที่เลือก", command=self.edit_item).pack(side="left", padx=3)
        ttk.Button(actions, text="ลบที่เลือก", command=self.delete_item).pack(side="left", padx=3)
        ttk.Button(actions, text="ส่งออก CSV", command=self.export_csv).pack(side="left", padx=3)

        cols = ("category", "name", "qty", "unit", "unitPrice", "lineTotal", "status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        heads = {"category": "กลุ่ม", "name": "รายการ / รุ่น", "qty": "จำนวน", "unit": "หน่วย", "unitPrice": "ราคา/หน่วย", "lineTotal": "รวม (บาท)", "status": "สถานะ"}
        widths = {"category": 150, "name": 390, "qty": 70, "unit": 70, "unitPrice": 110, "lineTotal": 110, "status": 160}
        for col in cols:
            self.tree.heading(col, text=heads[col])
            self.tree.column(col, width=widths[col], anchor="w" if col in ("category", "name", "status") else "center")
        self.tree.pack(fill="both", expand=True, padx=10)
        self.tree.bind("<Double-1>", lambda _e: self.edit_item())
        footer = ttk.Frame(self, padding=10)
        footer.pack(fill="x")
        self.total_label = ttk.Label(footer, text="ยอดรวมที่ทราบ: 0.00 บาท", font=("Segoe UI", 11, "bold"))
        self.total_label.pack(side="left")
        ttk.Label(footer, textvariable=self.status_var).pack(side="right")

    def configure_token(self):
        token = simpledialog.askstring("GitHub Token", "วาง Fine-grained token ที่ให้สิทธิ์ Contents: Read and write\nสำหรับ repository นี้เท่านั้น:", show="•", parent=self)
        if token is None:
            return
        token = token.strip()
        if not token:
            messagebox.showerror("Token ว่าง", "กรุณาวาง token ก่อนบันทึก", parent=self)
            return
        try:
            api_request("GET", token=token)
            keyring.set_password(SERVICE, "github-token", token)
            self.token = token
            self.status_var.set("Token ใช้งานได้และบันทึกใน Windows Credential Manager แล้ว")
            self.load_remote()
        except Exception as exc:
            messagebox.showerror("เชื่อม GitHub ไม่สำเร็จ", self._error_text(exc), parent=self)

    def _require_token(self):
        if not self.token:
            self.configure_token()
        return bool(self.token)

    @staticmethod
    def _error_text(exc):
        if isinstance(exc, HTTPError):
            try:
                detail = exc.read().decode("utf-8", errors="replace")
            except Exception:
                detail = str(exc)
            if exc.code == 401:
                return "Token ไม่ถูกต้องหรือหมดอายุ (401)"
            if exc.code == 403:
                return "GitHub ปฏิเสธคำขอ กรุณาตรวจสิทธิ์ Contents: Read and write (403)"
            if exc.code == 409:
                return "ไฟล์บน GitHub ถูกแก้หลังจากโหลดครั้งล่าสุด ให้โหลดข้อมูลใหม่ก่อน แล้วค่อยนำการแก้ของคุณกลับมาใส่"
            return f"GitHub ตอบกลับ HTTP {exc.code}\n{detail[:500]}"
        if isinstance(exc, URLError):
            return f"เชื่อมต่ออินเทอร์เน็ตไม่ได้: {exc}"
        return str(exc)

    def _run_async(self, work, success, title):
        self.status_var.set(title)
        self._remote_busy = True
        def runner():
            try:
                result = work()
                def complete():
                    self._remote_busy = False
                    success(result)
                self.after(0, complete)
            except Exception as exc:
                text = self._error_text(exc)
                def failed(msg=text):
                    self._remote_busy = False
                    self._show_error(msg)
                self.after(0, failed)
        threading.Thread(target=runner, daemon=True).start()

    def _show_error(self, message):
        self.status_var.set("ดำเนินการไม่สำเร็จ")
        messagebox.showerror("เกิดข้อผิดพลาด", message, parent=self)

    def load_remote(self):
        if not self._require_token():
            return
        def work():
            result = api_request("GET", token=self.token)
            content = base64.b64decode(result["content"]).decode("utf-8-sig")
            return json.loads(content), result["sha"]
        def success(data):
            self.payload, self.file_sha = data[0], data[1]
            self.dirty = False
            self.refresh_table()
            self.status_var.set(f"โหลดแล้ว • {len(self.payload.get('items', []))} รายการ • branch {BRANCH}")
        self._run_async(work, success, "กำลังโหลด BOM จาก GitHub…")

    def save_remote(self):
        if not self._require_token():
            return
        if not self.file_sha:
            messagebox.showinfo("ยังไม่มีข้อมูล", "โหลด BOM จาก GitHub ก่อนบันทึก", parent=self)
            return
        if not messagebox.askyesno("ยืนยันบันทึก", "บันทึก BOM ชุดนี้ไปทับไฟล์บน GitHub และสร้าง commit ใหม่หรือไม่?", parent=self):
            return
        self.payload["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        content = json.dumps(self.payload, ensure_ascii=False, indent=2) + "\n"
        expected_sha = self.file_sha
        def work():
            return api_request("PUT", {"message": "Update BOM from desktop manager", "content": base64.b64encode(content.encode("utf-8")).decode("ascii"), "sha": expected_sha, "branch": BRANCH}, self.token)
        def success(result):
            self.file_sha = result["content"]["sha"]
            self.dirty = False
            commit = result.get("commit", {}).get("html_url", "")
            self.status_var.set("บันทึกสำเร็จ • GitHub commit ถูกสร้างแล้ว")
            messagebox.showinfo("บันทึกแล้ว", f"BOM ถูกบันทึกขึ้น GitHub แล้ว.\n\n{commit}", parent=self)
        self._run_async(work, success, "กำลังบันทึก BOM เป็น GitHub commit…")

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        query = self.search_var.get().strip().casefold()
        total = 0.0
        known = 0
        for idx, item in enumerate(self.payload.get("items", [])):
            searchable = " ".join(str(item.get(k, "")) for k, _ in FIELDS).casefold()
            price = item.get("unitPrice")
            amount = float(item.get("qty") or 0) * float(price or 0)
            if price is not None:
                total += amount
                known += 1
            if query and query not in searchable:
                continue
            self.tree.insert("", "end", iid=str(idx), values=(item.get("category", ""), item.get("name", ""), item.get("qty", ""), item.get("unit", ""), self._money(price), self._money(amount) if price is not None else "—", item.get("status", "")))
        self.total_label.config(text=f"ยอดรวมที่มีราคา ({known} รายการ): {total:,.2f} บาท")

    @staticmethod
    def _money(value):
        return "—" if value is None else f"{float(value):,.2f}"

    def add_item(self):
        dialog = ItemDialog(self)
        self.wait_window(dialog)
        if dialog.result is not None:
            new_id = str(max([int(x.get("id", 0)) for x in self.payload["items"] if str(x.get("id", "")).isdigit()] + [0]) + 1)
            self.payload["items"].append({"id": new_id, **dialog.result})
            self.dirty = True
            self.refresh_table()

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("เลือกรายการ", "เลือกรายการในตารางก่อน", parent=self)
            return
        idx = int(selected[0])
        item = self.payload["items"][idx]
        dialog = ItemDialog(self, item)
        self.wait_window(dialog)
        if dialog.result is not None:
            self.payload["items"][idx] = {**item, **dialog.result}
            self.dirty = True
            self.refresh_table()
            self.tree.selection_set(str(idx))

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("เลือกรายการ", "เลือกรายการในตารางก่อน", parent=self)
            return
        idx = int(selected[0])
        item = self.payload["items"][idx]
        if messagebox.askyesno("ลบรายการ", f"ลบ “{item.get('name', '')}” ใช่หรือไม่?", parent=self):
            del self.payload["items"][idx]
            self.dirty = True
            self.refresh_table()


    def check_updates(self, silent=False):
        if self._checking_update or self._update_busy:
            return
        self._checking_update = True
        self.check_update_button.config(state="disabled")
        self.update_status_var.set("กำลังตรวจสอบ GitHub Releases…")

        def complete(info):
            self._checking_update = False
            self.check_update_button.config(state="normal")
            self.available_update = info
            if info:
                self.install_update_button.config(state="normal")
                self.update_status_var.set(f"พบเวอร์ชันใหม่ v{info['version']} — พร้อมอัปเดต")
                if not silent:
                    messagebox.showinfo("มีเวอร์ชันใหม่", f"ปัจจุบัน v{APP_VERSION}\n"
                                        f"เวอร์ชันใหม่ v{info['version']}\n"
                                        "กด 'อัปเดตตอนนี้' เพื่อดาวน์โหลดและติดตั้ง", parent=self)
            else:
                self.install_update_button.config(state="disabled")
                self.update_status_var.set(f"เป็นเวอร์ชันล่าสุดแล้ว (v{APP_VERSION})")
                if not silent:
                    messagebox.showinfo("ตรวจสอบแล้ว", "คุณใช้ BOM Manager เวอร์ชันล่าสุดอยู่แล้ว",
                                        parent=self)

        def failed(message):
            self._checking_update = False
            self.check_update_button.config(state="normal")
            self.update_status_var.set("ตรวจสอบเวอร์ชันไม่ได้ — ลองใหม่อีกครั้ง")
            if not silent:
                messagebox.showerror("ตรวจสอบเวอร์ชันไม่ได้", message, parent=self)

        def worker():
            try:
                info = updater.find_update(APP_VERSION)
                self.after(0, lambda data=info: complete(data))
            except Exception as exc:
                self.after(0, lambda message=str(exc): failed(message))
        threading.Thread(target=worker, daemon=True).start()

    def install_update(self):
        info = self.available_update
        if not info or self._checking_update or self._update_busy:
            return
        if self._remote_busy:
            messagebox.showwarning("กำลังทำงาน", "รอให้การโหลด/บันทึก GitHub เสร็จก่อน",
                                   parent=self)
            return
        if self.dirty:
            messagebox.showwarning("มีข้อมูลยังไม่บันทึก",
                                   "คุณแก้ไข BOM แต่ยังไม่ได้กด 'บันทึกขึ้น GitHub'\n"
                                   "กรุณาบันทึกข้อมูลก่อนอัปเดต เพื่อป้องกันข้อมูลสูญหาย",
                                   parent=self)
            return
        if not messagebox.askyesno("ยืนยันอัปเดต",
                                   f"อัปเดตจาก v{APP_VERSION} เป็น v{info['version']} หรือไม่?\n"
                                   "โปรแกรมจะดาวน์โหลด ตรวจ SHA256 และเปิดตัวติดตั้ง Windows\n"
                                   "จากนั้นปิด BOM Manager ตัวปัจจุบัน",
                                   parent=self):
            return

        self._update_busy = True
        self.install_update_button.config(state="disabled")
        self.check_update_button.config(state="disabled")
        dialog = tk.Toplevel(self)
        dialog.title("กำลังดาวน์โหลด BOM Manager")
        dialog.transient(self)
        dialog.resizable(False, False)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=18)
        frame.pack(fill="both", expand=True)
        info_text = tk.StringVar(value=f"กำลังดาวน์โหลด v{info['version']}…")
        ttk.Label(frame, textvariable=info_text).pack(anchor="w", pady=(0, 8))
        progress = ttk.Progressbar(frame, length=390, maximum=100, mode="determinate")
        progress.pack(fill="x")
        cancel = threading.Event()

        def cancel_download():
            cancel.set()
            info_text.set("กำลังยกเลิกการดาวน์โหลด…")
            cancel_button.config(state="disabled")

        cancel_button = ttk.Button(frame, text="ยกเลิก", command=cancel_download)
        cancel_button.pack(anchor="e", pady=(10, 0))
        dialog.protocol("WM_DELETE_WINDOW", cancel_download)

        def clean_dialog():
            self._update_busy = False
            self.check_update_button.config(state="normal")
            self.install_update_button.config(state="normal")
            dialog.grab_release()
            dialog.destroy()

        def set_progress(received, total):
            def redraw():
                if not cancel.is_set() and dialog.winfo_exists():
                    progress["value"] = min(100, received * 100 / total)
                    info_text.set(f"ดาวน์โหลดแล้ว {received / 1048576:.1f} / "
                                  f"{total / 1048576:.1f} MB")
            self.after(0, redraw)

        def failed(message, was_cancelled=False):
            clean_dialog()
            if was_cancelled:
                self.update_status_var.set("ยกเลิกการอัปเดตแล้ว")
            else:
                self.update_status_var.set("อัปเดตไม่สำเร็จ — ตรวจสอบแล้วลองใหม่")
                messagebox.showerror("อัปเดตไม่สำเร็จ", message, parent=self)

        def downloaded(installer):
            if cancel.is_set():
                from shutil import rmtree
                rmtree(installer.parent, ignore_errors=True)
                failed("ยกเลิกการดาวน์โหลด", True)
                return
            info_text.set("ตรวจ SHA256 ผ่านแล้ว — กำลังเปิดตัวติดตั้ง…")
            try:
                import os
                if os.name != "nt" or not getattr(__import__("sys"), "frozen", False):
                    raise updater.UpdateError("ติดตั้งอัตโนมัติได้เฉพาะโปรแกรม .exe บน Windows")
                subprocess.Popen([str(installer), "/NORESTART"], cwd=str(installer.parent),
                                 close_fds=True)
            except Exception as exc:
                from shutil import rmtree
                rmtree(installer.parent, ignore_errors=True)
                failed(str(exc))
                return
            self.update_status_var.set("เปิดตัวติดตั้งแล้ว — ปิดโปรแกรมเวอร์ชันเก่า")
            dialog.grab_release()
            dialog.destroy()
            self.destroy()

        def worker():
            try:
                installer = updater.download_update(info, progress=set_progress, cancelled=cancel)
                self.after(0, lambda path=installer: downloaded(path))
            except updater.DownloadCanceled as exc:
                self.after(0, lambda message=str(exc): failed(message, True))
            except Exception as exc:
                self.after(0, lambda message=str(exc): failed(message))
        threading.Thread(target=worker, daemon=True).start()

    def export_csv(self):
        from csv import DictWriter
        from tkinter.filedialog import asksaveasfilename
        path = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile="BOM.csv")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = DictWriter(file, fieldnames=[key for key, _label in FIELDS] + ["lineTotal"])
            writer.writeheader()
            for item in self.payload.get("items", []):
                row = dict(item)
                price = row.get("unitPrice")
                row["lineTotal"] = float(row.get("qty") or 0) * float(price or 0) if price is not None else ""
                writer.writerow(row)
        self.status_var.set(f"ส่งออก CSV แล้ว: {path}")


if __name__ == "__main__":
    from bom_ui import make_app
    EnhancedApp = make_app(BOMApp, ItemDialog, api_request, APP_VERSION, API_URL, SERVICE, FIELDS)
    EnhancedApp().mainloop()
