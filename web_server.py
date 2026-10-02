from __future__ import annotations

import hmac
import os
import sys
from pathlib import Path
from typing import Any, Dict

from fastapi import Body, FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from web_engine import (
    calculate_drive_battery,
    calculate_drive_torque,
    calculate_ramp_geometry,
    calculate_stability,
    calculate_winch,
)


def resource_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


ROOT = resource_root()
WEB_DIR = ROOT / "web"


def read_version() -> str:
    for candidate in (ROOT / "VERSION", Path(__file__).resolve().parent / "VERSION"):
        try:
            return candidate.read_text(encoding="utf-8-sig").strip()
        except Exception:
            pass
    return "web-dev"


APP_VERSION = read_version()
ACCESS_PIN = os.environ.get("CVET_WEB_PIN", "").strip()

app = FastAPI(
    title="Crane Vehicle Engineering Tool — Web",
    version=APP_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


@app.middleware("http")
async def optional_pin_guard(request: Request, call_next):
    if (
        ACCESS_PIN
        and request.url.path.startswith("/api/")
        and request.url.path not in {"/api/health", "/api/openapi.json"}
    ):
        supplied = request.headers.get("X-CVET-PIN", "")
        if not hmac.compare_digest(supplied, ACCESS_PIN):
            return JSONResponse(
                status_code=401,
                content={"ok": False, "error": "PIN_REQUIRED", "message": "รหัสเข้าใช้งานไม่ถูกต้อง"},
            )
    return await call_next(request)


@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "name": "Crane Vehicle Engineering Tool — Web",
        "version": APP_VERSION,
        "pin_required": bool(ACCESS_PIN),
        "server": "user-pc",
    }


def safe_calc(fn, payload: Dict[str, Any]):
    try:
        return {"ok": True, "version": APP_VERSION, "result": fn(payload)}
    except Exception as exc:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": type(exc).__name__, "message": str(exc)},
        )


@app.post("/api/calc/ramp-geometry")
def api_ramp_geometry(payload: Dict[str, Any] = Body(default_factory=dict)):
    return safe_calc(calculate_ramp_geometry, payload)


@app.post("/api/calc/drive-torque")
def api_drive_torque(payload: Dict[str, Any] = Body(default_factory=dict)):
    return safe_calc(calculate_drive_torque, payload)


@app.post("/api/calc/drive-battery")
def api_drive_battery(payload: Dict[str, Any] = Body(default_factory=dict)):
    return safe_calc(calculate_drive_battery, payload)


@app.post("/api/calc/winch")
def api_winch(payload: Dict[str, Any] = Body(default_factory=dict)):
    return safe_calc(calculate_winch, payload)


@app.post("/api/calc/stability")
def api_stability(payload: Dict[str, Any] = Body(default_factory=dict)):
    return safe_calc(calculate_stability, payload)
