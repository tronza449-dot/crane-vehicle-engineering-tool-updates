"""Privacy-first diagnostics for Crane Vehicle BOM Manager.

Stores only operational events and aggregated counts, never BOM rows, tokens or
other environment variables. JSON reports are deliberately safe-by-default.
"""
import json
import os
import platform
import re
import sys
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path


MAX_LOG_BYTES = 1_000_000
MAX_EVENTS_IN_REPORT = 150
MAX_FIELD_CHARS = 1100
REDACTED = "[REDACTED]"
_SECRET_RE = re.compile(
    r"(?i)(?:github_pat_[A-Za-z0-9_]{8,}|gh[pousr]_[A-Za-z0-9_]{8,}|"
    r"(?:bearer\s+)[^\s,;]+|"
    r"(?:authorization|access[_-]?token|api[_-]?key|password|secret|token)"
    r"\s*(?:=|:)\s*[\"']?[^\s,;\"']+)"
)
_EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
_USER_PATH_RE = re.compile(r"(?i)(?:[A-Z]:\\Users\\|/Users/|/home/)[^\\/\s\"']+")
_URL_CREDENTIAL_RE = re.compile(r"(?i)https?://[^\s/@]+:[^\s/@]+@")
_URL_AUTH_QUERY_RE = re.compile(r"(?i)([?&](?:token|access_token|api_key|key|password|secret)=)[^&#\s]+")
_ABSOLUTE_WIN_PATH_RE = re.compile(r"(?i)\b[A-Z]:\\(?:[^\\\s\"'\r\n]+\\)*[^\\\s\"'\r\n]+")
_ABSOLUTE_POSIX_PATH_RE = re.compile(r"(?<![:/])/(?:[^/\s\"'\r\n]+/)*[^/\s\"'\r\n]+")

_SAFE_AREA = re.compile(r"^[A-Za-z0-9_.-]{1,45}$")
_SAFE_CODE = re.compile(r"^[A-Z0-9_]{1,50}$")


def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class DebugReporter:
    def __init__(self, base_dir=None, version="unknown"):
        folder = (Path(base_dir) if base_dir is not None else
                  Path(os.environ.get("LOCALAPPDATA") or Path.home() / ".local" / "share")
                  / "CraneVehicleBOMManager" / "debug")
        self.folder = folder
        self.file = folder / "events.jsonl"
        self.version = str(version)
        self._lock = threading.RLock()
        self._secrets = set()
        self.write_error = None

    def register_secret(self, secret):
        if isinstance(secret, str) and len(secret) >= 6:
            with self._lock:
                self._secrets.add(secret)

    def scrub(self, value):
        text = str(value)
        with self._lock:
            for secret in sorted(self._secrets, key=len, reverse=True):
                text = text.replace(secret, REDACTED)
        text = _SECRET_RE.sub(REDACTED, text)
        text = _EMAIL_RE.sub("[EMAIL]", text)
        text = _URL_CREDENTIAL_RE.sub("https://[CREDENTIALS]@", text)
        text = _URL_AUTH_QUERY_RE.sub(r"\1[REDACTED]", text)
        text = _USER_PATH_RE.sub("[USER_HOME]", text)
        text = _ABSOLUTE_WIN_PATH_RE.sub("[LOCAL_PATH]", text)
        text = _ABSOLUTE_POSIX_PATH_RE.sub("[LOCAL_PATH]", text)
        try:
            home = str(Path.home())
            if len(home) > 4:
                text = text.replace(home, "[USER_HOME]")
        except (OSError, RuntimeError):
            pass
        return text[:MAX_FIELD_CHARS]

    def _rotate(self):
        try:
            if self.file.exists() and self.file.stat().st_size >= MAX_LOG_BYTES:
                old = self.folder / "events.previous.jsonl"
                os.replace(self.file, old)
        except OSError:
            pass

    def event(self, level, area, code, message, detail=None):
        level = level if level in {"INFO", "WARN", "ERROR"} else "WARN"
        area = area if isinstance(area, str) and _SAFE_AREA.fullmatch(area) else "application"
        code = code if isinstance(code, str) and _SAFE_CODE.fullmatch(code) else "UNSPECIFIED"
        record = {
            "timestamp": now_utc(), "level": level, "area": area, "code": code,
            "message": self.scrub(message),
        }
        if detail:
            record["detail"] = self.scrub(detail)
        with self._lock:
            try:
                self.folder.mkdir(parents=True, exist_ok=True)
                self._rotate()
                with self.file.open("a", encoding="utf-8") as output:
                    output.write(json.dumps(record, ensure_ascii=False) + "\n")
                self.write_error = None
            except OSError as exc:
                # Diagnostics may fail on read-only disks. Never crash the main app.
                self.write_error = type(exc).__name__
        return record

    def exception(self, area, code, exc):
        detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        return self.event("ERROR", area, code, f"{type(exc).__name__}: {exc}", detail)

    def read_events(self, limit=MAX_EVENTS_IN_REPORT):
        result = []
        with self._lock:
            for name in ("events.previous.jsonl", "events.jsonl"):
                path = self.folder / name
                try:
                    with path.open(encoding="utf-8") as stream:
                        for line in stream:
                            try:
                                item = json.loads(line)
                            except (ValueError, TypeError):
                                continue
                            if not isinstance(item, dict):
                                continue
                            # Re-scrub legacy logs and previously unknown secrets.
                            event = {key: self.scrub(value) for key, value in item.items()
                                     if key in ("timestamp", "level", "area", "code",
                                                "message", "detail")}
                            result.append(event)
                except OSError:
                    continue
        return result[-max(1, min(int(limit), MAX_EVENTS_IN_REPORT)):]

    @staticmethod
    def inspect_document(document):
        """Validate the live in-memory document without including its contents."""
        import bom_core
        checks = []
        try:
            bom_core.ensure_doc(document)
            checks.append({"name": "BOM structure", "status": "PASS",
                           "detail": "จำนวนและราคาอยู่ในรูปแบบที่ตรวจสอบได้"})
            metrics = bom_core.metrics(document)
            counts = {
                "bom_items": metrics["items"],
                "with_price": metrics["priced"],
                "without_price": metrics["missing"],
                "wiring_connections": metrics["wires"],
                "purchases": metrics["purchase_count"],
            }
            if metrics["missing"]:
                checks.append({"name": "Price completeness", "status": "WARN",
                               "detail": f"ยังไม่มีราคา {metrics['missing']} รายการ"})
            else:
                checks.append({"name": "Price completeness", "status": "PASS",
                               "detail": "ทุกรายการมีราคาที่ระบุ"})
            issues = bom_core.connection_warnings(document)
            checks.append({"name": "Wiring references",
                           "status": "WARN" if issues else "PASS",
                           "detail": f"พบข้อควรตรวจสอบ {len(issues)} จุด (ไม่ใช่การรับรองทางไฟฟ้า)"})
        except (ValueError, TypeError, KeyError) as exc:
            counts = None
            checks.append({"name": "BOM structure", "status": "FAIL",
                           "detail": f"เอกสาร BOM ไม่ถูกต้อง ({type(exc).__name__})"})
        return checks, counts

    def snapshot(self, document, *, dirty=False, remote_loaded=False, github_token_present=False,
                 github_connected=None):
        checks, counts = self.inspect_document(document)
        try:
            self.folder.mkdir(parents=True, exist_ok=True)
            probe = self.folder / ".diagnostic-probe"
            probe.write_text("OK", encoding="utf-8")
            probe.unlink()
            storage_ok = True
        except OSError:
            storage_ok = False
        checks.extend([
            {"name": "Local storage", "status": "PASS" if storage_ok else "FAIL",
             "detail": "บันทึกไฟล์ได้" if storage_ok else "ไม่สามารถเขียนไฟล์ในโฟลเดอร์ Debug"},
            {"name": "Credential setup", "status": "PASS" if github_token_present else "WARN",
             "detail": "มี Token ใน Credential Manager" if github_token_present
                       else "ยังไม่ได้ตั้งค่า Token สำหรับบันทึก GitHub"},
            {"name": "GitHub connectivity", "status": "PASS" if github_connected is True else "WARN",
             "detail": "GitHub API ติดต่อได้" if github_connected is True else
                       "GitHub API ติดต่อไม่ได้" if github_connected is False else
                       "ยังไม่ได้ทดสอบ GitHub ในรอบนี้"}, 
            {"name": "Local diagnostics", "status": "WARN" if self.write_error else "PASS",
             "detail": "เขียน log ไม่สำเร็จ" if self.write_error else "พร้อมบันทึกเหตุการณ์"},
            {"name": "GitHub state", "status": "WARN" if not remote_loaded else "PASS",
             "detail": "ยังไม่โหลดข้อมูล GitHub ในรอบนี้" if not remote_loaded else "มีข้อมูลอ้างอิง GitHub"},
        ])
        return {
            "report_type": "CraneVehicleBOMManager-Debug",
            "report_version": 1,
            "generated_at_utc": now_utc(),
            "app_version": self.version,
            "runtime": {
                "os": platform.system(), "os_release": platform.release(),
                "architecture": platform.machine(),
                "python": ".".join(map(str, sys.version_info[:3])),
                "packaged_exe": bool(getattr(sys, "frozen", False)),
            },
            "state": {
                "unsaved_changes": bool(dirty),
                "github_reference_loaded": bool(remote_loaded),
                "github_credential_configured": bool(github_token_present),
                "github_connectivity_checked": github_connected is not None,
                "github_api_reachable": github_connected if github_connected is not None else None,
                "counts": counts,
            },
            "checks": checks,
            "events": self.read_events(),
            "privacy": "No GitHub token, BOM row content, buyer names or raw file paths included.",
        }

    def export_json(self, destination, document, **state):
        report = self.snapshot(document, **state)
        file_path = Path(destination)
        # Caller chooses destination. Never write to GitHub implicitly.
        with file_path.open("w", encoding="utf-8") as output:
            json.dump(report, output, indent=2, ensure_ascii=False)
            output.write("\n")
        self.event("INFO", "diagnostics", "REPORT_EXPORTED", "ส่งออก Debug Report JSON")
        return report

    def clear_logs(self):
        with self._lock:
            for name in ("events.jsonl", "events.previous.jsonl"):
                try:
                    (self.folder / name).unlink(missing_ok=True)
                except OSError:
                    pass
            self.write_error = None


_reporter = None


def install_hooks(reporter):
    """Capture Python main-thread and worker-thread uncaught exceptions."""
    global _reporter
    _reporter = reporter
    old_hook = sys.excepthook
    old_thread_hook = threading.excepthook

    def top_hook(exc_type, exc, tb):
        reporter.exception("application", "UNHANDLED_EXCEPTION", exc)
        old_hook(exc_type, exc, tb)

    def worker_hook(args):
        reporter.exception("threading", "UNHANDLED_THREAD", args.exc_value)
        old_thread_hook(args)

    sys.excepthook = top_hook
    threading.excepthook = worker_hook
