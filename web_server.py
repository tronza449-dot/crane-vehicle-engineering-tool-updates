from __future__ import annotations

import hmac
import json
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


def _desktop_state_candidates():
    """Known Desktop Save Values locations on the same Windows user account."""
    paths = []
    override = os.environ.get("CVET_DESKTOP_STATE", "").strip()
    if override:
        paths.append(("Environment override", Path(override)))

    app_roots = []
    for key in ("APPDATA", "LOCALAPPDATA"):
        raw = os.environ.get(key, "").strip()
        if raw:
            app_roots.append(Path(raw))
    for base in app_roots:
        paths.extend([
            ("Desktop AppData", base / "Mechatronics Engineering Project" / "Crane Vehicle Engineering Tool" / "last_values.json"),
            ("Desktop AppData", base / "Crane Vehicle Engineering Tool" / "last_values.json"),
            ("Desktop AppData", base / "CraneVehicleEngineeringTool" / "last_values.json"),
        ])

    home = Path.home()
    docs = [home / "Documents"]
    for key in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer"):
        raw = os.environ.get(key, "").strip()
        if raw:
            docs.append(Path(raw) / "Documents")
    for folder in docs:
        paths.append(("Documents backup", folder / "CVET_Data" / "saved_values_backup.json"))

    unique = []
    seen = set()
    for label, path in paths:
        try:
            key = str(path.resolve())
        except Exception:
            key = str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append((label, path))
    return unique


def _load_latest_desktop_state():
    valid = []
    for label, path in _desktop_state_candidates():
        try:
            if not path.exists():
                continue
            state = json.loads(path.read_text(encoding="utf-8-sig"))
            if state.get("format") != "CraneVehicleEngineeringToolProject":
                continue
            saved_at = str(state.get("saved_at", ""))
            valid.append((saved_at, path.stat().st_mtime, label, path, state))
        except Exception:
            continue
    if not valid:
        return None
    return sorted(valid, key=lambda x: (x[0], x[1]), reverse=True)[0]


def _desktop_web_values(state: Dict[str, Any]) -> Dict[str, Any]:
    widgets = state.get("widgets", {}) if isinstance(state, dict) else {}

    def wv(name: str, default=None):
        item = widgets.get(name)
        if isinstance(item, dict) and "value" in item:
            return item.get("value")
        return default

    def n(name: str, default: float = 0.0) -> float:
        try:
            return float(wv(name, default))
        except Exception:
            return float(default)

    def i(name: str, default: int = 0) -> int:
        try:
            return int(wv(name, default))
        except Exception:
            return int(default)

    def b(name: str, default: bool = False) -> bool:
        value = wv(name, default)
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)

    mt = n("mt", 300.0)
    ml = n("ml", 100.0)
    mb = n("mb", 20.0)
    wb = n("WB", 1.10)
    drive_mass = mt if b("tUseMain", True) else n("tm", mt)
    battery_mass = mt if b("euseTorqueMass", False) else n("emass", mt)
    ramp_mass = n("emass", battery_mass) if b("rampUseMainMass", True) else n("rampMass", battery_mass)
    mass_mode = "components" if i("massCalcMode", 0) == 1 else "total"
    drive_xcg = n("driveXCG", n("xCG", 0.0))

    components = []
    for row in state.get("components", []) or []:
        if not isinstance(row, (list, tuple)) or len(row) < 5:
            continue
        try:
            components.append({
                "name": str(row[0]),
                "mass_kg": float(row[1]),
                "x_m": float(row[2]),
                "y_m": float(row[3]),
                "z_m": float(row[4]),
            })
        except Exception:
            continue

    return {
        "forms": {
            "driveForm": {
                "mass_kg": drive_mass,
                "wheel_diameter_in": n("twheelInch", 10.0),
                "slope_deg": n("tgrade", 19.0),
                "speed_kmh": n("tspeed", 5.0),
                "accel_time_s": n("taccel", 5.0),
                "rolling_coeff": n("tmu", 0.02),
                "motors": i("tmotors", 2),
                "motor_rated_w": n("motorRatedPower", 1500.0),
                "safety_factor": n("tsf", 1.30),
                "drive_eff_pct": n("teff", 85.0),
                "voltage_v": n("tvoltage", 72.0),
                "driven_load_pct": n("tDriveLoadFrac", 50.0),
                "traction_coeff": n("ttraction", 0.70),
            },
            "rampForm": {
                "rise_cm": n("rampRiseCm", 55.0),
                "run_cm": n("rampRunCm", 280.0),
                "measured_slant_cm": n("rampMeasuredCm", 290.0),
                "mass_kg": ramp_mass,
            },
            "batteryForm": {
                "mass_kg": battery_mass,
                "voltage_v": n("evolt", 72.0),
                "speed_kmh": n("espeed", 1.0),
                "one_way_m": n("eoneway", 30.0),
                "slope_length_m": n("eslopeLen", 2.9),
                "slope_deg": n("eslopeDeg", 12.0),
                "runtime_h": n("eruntime", 3.0),
                "other_stop_time_per_round_s": n("estopTime", 0.0),
                "rolling_coeff": n("err", 0.02),
                "drive_eff_pct": n("edriveEff", 60.0),
                "aux_power_w": n("eaux", 50.0),
                "dod_pct": n("edod", 80.0),
                "reserve_pct": n("ereserve", 20.0),
                "battery_design_factor": n("ebatteryFactor", 3.0),
                "turn_enabled": b("eTurnEnable", False),
                "turns_per_cycle": i("eTurnEvents", 2),
                "turn_angle_deg": n("eTurnAngle", 180.0),
                "turn_time_s": n("eTurnTime", 5.0),
                "track_width_m": n("W", 1.0),
                "turn_coeff": n("eTurnCoeff", 0.20),
                "target_cont_c": n("bselTargetContC", 3.0),
                "target_peak_c": n("bselTargetPeakC", 5.0),
                "candidate_ah": n("eCandidateAh", 0.0),
                "candidate_bms_cont_a": n("eCandidateContA", 0.0),
                "candidate_bms_peak_a": n("eCandidatePeakA", 0.0),
            },
            "winchForm": {
                "load_kg": n("wmass", 100.0),
                "lift_m": n("wheight", 1.0),
                "vehicle_speed_kmh": n("wopSpeed", 1.0),
                "one_way_m": n("wopDistance", 30.0),
                "operating_hours": n("wopHours", 3.0),
                "events_per_round": i("wopEvents", 2),
                "other_stop_s": n("wopOther", 0.0),
                "down_mode": "custom" if i("wbDownMode", 0) == 1 else "conservative",
                "down_basis": "time" if i("wbDownBasis", 0) == 1 else "speed",
                "down_current_a": n("wbDownCurrent", 10.0),
                "down_speed_m_min": n("wbDownSpeed", 3.0),
                "down_time_s": n("wbDownTime", 30.0),
            },
            "winchBatteryForm": {
                "event_mode": "manual" if i("wbEventMode", 0) == 1 else "auto",
                "manual_events": i("wbEvents", 64),
                "winch_voltage_v": n("wbVoltage", 12.0),
                "dod_pct": n("wbDoD", 80.0),
                "reserve_pct": n("wbReserve", 20.0),
                "candidate_ah": n("wbCandidateAh", 40.0),
                "bms_cont_a": n("wbBmsCont", 0.0),
                "bms_peak_a": n("wbBmsPeak", 0.0),
            },
            "stabilityForm": {
                "mass_mode": mass_mode,
                "total_mass_kg": mt,
                "payload_mass_kg": ml,
                "boom_mass_kg": mb,
                "vehicle_cg_x_from_center_m": n("xCG", 0.0),
                "vehicle_cg_y_m": n("yCG", 0.0),
                "combined_cg_from_rear_m": max(0.0, drive_xcg + wb / 2.0),
                "combined_cg_height_m": n("hcg", 0.55),
                "track_width_m": n("W", 1.0),
                "wheelbase_m": wb,
                "boom_length_m": n("L", 1.20),
                "crane_angle_deg": n("th", 0.0),
                "dynamic_factor": n("kd", 1.0),
                "required_sf": n("req", 1.5),
                "crane_from_rear_m": n("xC", 0.15),
                "slope_deg": n("slope", 19.0),
                "slope_accel_mps2": n("acc", 0.278),
            },
        },
        "components": components,
    }


@app.get("/api/project-values")
def api_project_values():
    latest = _load_latest_desktop_state()
    if latest is None:
        return JSONResponse(
            status_code=404,
            content={
                "ok": False,
                "error": "DESKTOP_SAVE_NOT_FOUND",
                "message": "ยังไม่พบ Desktop Save Values — เปิดโปรแกรม Desktop แล้วกด 💾 Save Values ก่อน",
            },
        )
    _saved_at, _mtime, label, _path, state = latest
    mapped = _desktop_web_values(state)
    return {
        "ok": True,
        "version": APP_VERSION,
        "desktop_version": state.get("version", "-"),
        "saved_at": state.get("saved_at", "-"),
        "source": label,
        "forms": mapped["forms"],
        "components": mapped["components"],
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
