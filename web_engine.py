"""Pure calculation engine for the CVET web application.

The formulas mirror the current desktop project calculations but avoid any Qt/UI
dependency so they can run safely inside FastAPI on the user's Windows PC.
"""
from __future__ import annotations

import math
from typing import Any, Dict

G = 9.81

WINCH_PERF = (
    (0.0, 3.3, 12.0),
    (454.0, 2.5, 60.0),
    (907.0, 1.1, 100.0),
    (2041.0, 0.8, 140.0),
)
WINCH_LAYERS = (
    (1, 2041.0, 1.5),
    (2, 1597.0, 4.4),
    (3, 1197.0, 5.8),
    (4, 930.0, 8.1),
    (5, 739.0, 10.0),
)
STANDARD_AH = (10, 12, 15, 20, 30, 40, 50, 60, 80, 100, 120, 150, 200, 250, 300)


def _f(data: Dict[str, Any], key: str, default: float) -> float:
    try:
        return float(data.get(key, default))
    except (TypeError, ValueError):
        return float(default)


def _i(data: Dict[str, Any], key: str, default: int) -> int:
    try:
        return int(float(data.get(key, default)))
    except (TypeError, ValueError):
        return int(default)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def next_standard_capacity(required_ah: float, step_up: bool = False) -> float:
    for idx, size in enumerate(STANDARD_AH):
        if size + 1e-9 >= required_ah:
            if step_up and idx + 1 < len(STANDARD_AH):
                return float(STANDARD_AH[idx + 1])
            return float(size)
    return float(math.ceil(required_ah / 50.0) * 50.0)


def winch_interpolate(load_kg: float) -> Dict[str, float]:
    m = _clamp(float(load_kg), WINCH_PERF[0][0], WINCH_PERF[-1][0])
    for a, b in zip(WINCH_PERF[:-1], WINCH_PERF[1:]):
        if m <= b[0]:
            x0, v0, i0 = a
            x1, v1, i1 = b
            alpha = (m - x0) / (x1 - x0) if x1 > x0 else 0.0
            return {
                "load_kg": m,
                "speed_m_min": v0 + alpha * (v1 - v0),
                "current_a": i0 + alpha * (i1 - i0),
                "alpha": alpha,
                "lower_load_kg": x0,
                "upper_load_kg": x1,
                "lower_speed_m_min": v0,
                "upper_speed_m_min": v1,
                "lower_current_a": i0,
                "upper_current_a": i1,
            }
    x, v, current = WINCH_PERF[-1]
    return {"load_kg": m, "speed_m_min": v, "current_a": current, "alpha": 1.0,
            "lower_load_kg": x, "upper_load_kg": x,
            "lower_speed_m_min": v, "upper_speed_m_min": v,
            "lower_current_a": current, "upper_current_a": current}


def winch_layer_for_distance(distance_m: float) -> Dict[str, float]:
    h = max(0.0, float(distance_m))
    for layer, pull_kg, cumulative_m in WINCH_LAYERS:
        if h <= cumulative_m + 1e-12:
            return {"layer": layer, "line_pull_kg": pull_kg, "cumulative_rope_m": cumulative_m}
    layer, pull_kg, cumulative_m = WINCH_LAYERS[-1]
    return {"layer": layer, "line_pull_kg": pull_kg, "cumulative_rope_m": cumulative_m}


def winch_core(data: Dict[str, Any]) -> Dict[str, Any]:
    load = _clamp(_f(data, "load_kg", 100.0), 1.0, 2041.0)
    lift = _clamp(_f(data, "lift_m", 1.5), 0.01, 10.0)
    perf = winch_interpolate(load)
    layer = winch_layer_for_distance(lift)
    speed = perf["speed_m_min"]
    t_up = lift / speed * 60.0 if speed > 0 else 0.0
    return {
        "load_kg": load,
        "lift_m": lift,
        "up_speed_m_min": speed,
        "up_current_a": perf["current_a"],
        "up_time_s": t_up,
        "interp_alpha": perf["alpha"],
        "interp_lower_load_kg": perf["lower_load_kg"],
        "interp_upper_load_kg": perf["upper_load_kg"],
        "interp_lower_speed_m_min": perf["lower_speed_m_min"],
        "interp_upper_speed_m_min": perf["upper_speed_m_min"],
        "interp_lower_current_a": perf["lower_current_a"],
        "interp_upper_current_a": perf["upper_current_a"],
        "layer": int(layer["layer"]),
        "layer_line_pull_kg": layer["line_pull_kg"],
        "layer_rope_m": layer["cumulative_rope_m"],
        "layer_pull_ok": load <= layer["line_pull_kg"],
        "max_spec_current_a": 140.0,
    }


def winch_down_profile(data: Dict[str, Any], core: Dict[str, Any]) -> Dict[str, Any]:
    mode = str(data.get("down_mode", "conservative")).strip().lower()
    if mode not in {"custom", "measured", "manual"}:
        return {
            "mode": "Conservative",
            "basis": "Down = Up",
            "current_a": core["up_current_a"],
            "speed_m_min": core["up_speed_m_min"],
            "time_s": core["up_time_s"],
        }

    current = max(0.0, _f(data, "down_current_a", 10.0))
    basis = str(data.get("down_basis", "speed")).strip().lower()
    if basis == "time":
        t = max(0.01, _f(data, "down_time_s", 30.0))
        speed = core["lift_m"] / (t / 60.0) if t > 0 else 0.0
        label = "Measured / Custom Time"
    else:
        speed = max(0.001, _f(data, "down_speed_m_min", 3.0))
        t = core["lift_m"] / speed * 60.0
        label = "Measured / Custom Speed"
    return {"mode": "Measured / Custom", "basis": label, "current_a": current,
            "speed_m_min": speed, "time_s": t}


def winch_operation(data: Dict[str, Any], core: Dict[str, Any] | None = None,
                    down: Dict[str, Any] | None = None) -> Dict[str, Any]:
    core = core or winch_core(data)
    down = down or winch_down_profile(data, core)
    speed_kmh = max(0.001, _f(data, "vehicle_speed_kmh", 1.0))
    one_way = max(0.01, _f(data, "one_way_m", 30.0))
    hours = max(0.001, _f(data, "operating_hours", 3.0))
    events_per_round = max(1, _i(data, "events_per_round", 2))
    other = max(0.0, _f(data, "other_stop_s", 0.0))

    car_mps = speed_kmh * 1000.0 / 3600.0
    t_one = one_way / car_mps
    t_event = core["up_time_s"] + down["time_s"]
    t_drive_round = 2.0 * t_one
    t_lift_round = t_event * events_per_round
    t_round = t_drive_round + t_lift_round + other
    total_s = hours * 3600.0
    n_theory = total_s / t_round if t_round > 0 else 0.0
    rounds = int(math.floor(n_theory + 1e-12))
    trips = rounds * 2
    events = rounds * events_per_round
    time_used = rounds * t_round
    return {
        "vehicle_speed_kmh": speed_kmh,
        "car_mps": car_mps,
        "one_way_m": one_way,
        "operating_hours": hours,
        "events_per_round": events_per_round,
        "other_stop_s": other,
        "one_way_time_s": t_one,
        "up_time_s": core["up_time_s"],
        "down_time_s": down["time_s"],
        "event_time_s": t_event,
        "drive_round_time_s": t_drive_round,
        "lift_round_time_s": t_lift_round,
        "round_time_s": t_round,
        "theoretical_rounds": n_theory,
        "completed_round_trips": rounds,
        "one_way_trips": trips,
        "lift_events": events,
        "up_count": events,
        "down_count": events,
        "winch_moves": events * 2,
        "distance_total_m": rounds * 2.0 * one_way,
        "time_used_s": time_used,
        "remaining_s": max(0.0, total_s - time_used),
    }


def winch_battery(data: Dict[str, Any], core: Dict[str, Any] | None = None,
                  operation: Dict[str, Any] | None = None,
                  down: Dict[str, Any] | None = None) -> Dict[str, Any]:
    core = core or winch_core(data)
    down = down or winch_down_profile(data, core)
    operation = operation or winch_operation(data, core, down)

    voltage = max(0.1, _f(data, "winch_voltage_v", 12.0))
    dod = _clamp(_f(data, "dod_pct", 80.0) / 100.0, 0.01, 1.0)
    reserve = max(0.0, _f(data, "reserve_pct", 20.0) / 100.0)
    event_mode = str(data.get("event_mode", "auto")).strip().lower()
    use_operation = event_mode != "manual"
    events = operation["lift_events"] if use_operation else max(1, _i(data, "manual_events", 50))

    e_up = voltage * core["up_current_a"] * core["up_time_s"] / 3600.0
    e_down = voltage * down["current_a"] * down["time_s"] / 3600.0
    e_event = e_up + e_down
    total = events * e_event
    ah_used = total / voltage
    ah_design = total * (1.0 + reserve) / (voltage * dod)

    candidate = max(0.0, _f(data, "candidate_ah", 40.0))
    bms_cont = max(0.0, _f(data, "bms_cont_a", 0.0))
    bms_peak = max(0.0, _f(data, "bms_peak_a", 0.0))
    operating_current = max(core["up_current_a"], down["current_a"])
    return {
        "event_mode": "Auto" if use_operation else "Manual",
        "events": int(events),
        "up_count": int(events),
        "down_count": int(events),
        "winch_moves": int(events) * 2,
        "voltage_v": voltage,
        "dod": dod,
        "reserve": reserve,
        "up_current_a": core["up_current_a"],
        "up_speed_m_min": core["up_speed_m_min"],
        "up_time_s": core["up_time_s"],
        "down_mode": down["mode"],
        "down_basis": down["basis"],
        "down_current_a": down["current_a"],
        "down_speed_m_min": down["speed_m_min"],
        "down_time_s": down["time_s"],
        "e_up_wh": e_up,
        "e_down_wh": e_down,
        "e_event_wh": e_event,
        "e_total_wh": total,
        "ah_used": ah_used,
        "ah_design": ah_design,
        "standard_ah": next_standard_capacity(ah_design),
        "extra_margin_ah": next_standard_capacity(ah_design, step_up=True),
        "candidate_ah": candidate,
        "candidate_energy_ok": candidate > 0 and candidate + 1e-9 >= ah_design,
        "operating_current_a": operating_current,
        "bms_cont_a": bms_cont,
        "bms_cont_ok": bms_cont > 0 and bms_cont + 1e-9 >= operating_current,
        "bms_140a_reference_ok": bms_cont > 0 and bms_cont + 1e-9 >= 140.0,
        "bms_peak_a": bms_peak,
        "peak_status": "CHECK — Starting/Stall surge ไม่ระบุในใบสเปก",
    }


def calculate_winch(data: Dict[str, Any]) -> Dict[str, Any]:
    core = winch_core(data)
    down = winch_down_profile(data, core)
    op = winch_operation(data, core, down)
    battery = winch_battery(data, core, op, down)
    return {"core": core, "operation": op, "battery": battery}


def calculate_ramp_geometry(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate ramp geometry from measured rise/run and compare with measured slant."""
    rise_cm = max(0.0, _f(data, "rise_cm", 55.0))
    run_cm = max(0.001, _f(data, "run_cm", 280.0))
    measured_slant_cm = max(0.0, _f(data, "measured_slant_cm", 290.0))
    mass_kg = max(0.0, _f(data, "mass_kg", 300.0))

    theoretical_slant_cm = math.hypot(run_cm, rise_cm)
    angle_deg = math.degrees(math.atan2(rise_cm, run_cm))
    slope_percent = (rise_cm / run_cm) * 100.0
    ratio_h_over_l = rise_cm / theoretical_slant_cm if theoretical_slant_cm > 0 else 0.0

    measured_difference_cm = (
        measured_slant_cm - theoretical_slant_cm if measured_slant_cm > 0 else 0.0
    )
    measured_difference_abs_cm = abs(measured_difference_cm)
    measured_difference_pct = (
        measured_difference_abs_cm / theoretical_slant_cm * 100.0
        if theoretical_slant_cm > 0 and measured_slant_cm > 0
        else 0.0
    )

    measured_angle_deg = None
    if measured_slant_cm >= rise_cm and measured_slant_cm > 0:
        measured_angle_deg = math.degrees(
            math.asin(_clamp(rise_cm / measured_slant_cm, -1.0, 1.0))
        )

    f_slope_n = mass_kg * G * math.sin(math.radians(angle_deg))
    f_slope_ratio_n = mass_kg * G * ratio_h_over_l

    return {
        "rise_cm": rise_cm,
        "run_cm": run_cm,
        "measured_slant_cm": measured_slant_cm,
        "theoretical_slant_cm": theoretical_slant_cm,
        "theoretical_slant_m": theoretical_slant_cm / 100.0,
        "angle_deg": angle_deg,
        "slope_percent": slope_percent,
        "ratio_h_over_l": ratio_h_over_l,
        "measured_difference_cm": measured_difference_cm,
        "measured_difference_abs_cm": measured_difference_abs_cm,
        "measured_difference_pct": measured_difference_pct,
        "measured_angle_deg": measured_angle_deg,
        "mass_kg": mass_kg,
        "f_slope_n": f_slope_n,
        "f_slope_ratio_n": f_slope_ratio_n,
        "grade_ratio_run_per_rise": (run_cm / rise_cm if rise_cm > 0 else 999.0),
        "motor_angle_deg": angle_deg,
        "warning": "Slope (%) is not degrees. Use angle_deg in sin/cos motor-force equations.",
    }


def calculate_drive_torque(data: Dict[str, Any]) -> Dict[str, Any]:
    m = max(0.0, _f(data, "mass_kg", 300.0))
    wheel_in = max(0.1, _f(data, "wheel_diameter_in", 16.0))
    r = wheel_in * 0.0254 / 2.0
    deg = _f(data, "slope_deg", 11.11)
    speed_kmh = max(0.0, _f(data, "speed_kmh", 1.0))
    v = speed_kmh / 3.6
    accel_time = max(0.01, _f(data, "accel_time_s", 5.0))
    a = v / accel_time
    rolling = max(0.0, _f(data, "rolling_coeff", 0.02))
    motors = max(1, _i(data, "motors", 2))
    sf = max(0.01, _f(data, "safety_factor", 1.5))
    eff = _clamp(_f(data, "drive_eff_pct", 85.0) / 100.0, 0.01, 1.0)
    voltage = max(0.1, _f(data, "voltage_v", 72.0))
    drive_load_fraction = _clamp(_f(data, "driven_load_pct", 50.0) / 100.0, 0.0, 1.0)
    traction_coeff = max(0.0, _f(data, "traction_coeff", 0.7))

    th = math.radians(deg)
    fg = m * G * math.sin(th)
    fr = rolling * m * G * math.cos(th)
    fa = m * a
    fsum = fg + fr + fa
    fdesign = fsum * sf
    fmotor = fdesign / motors
    torque = fmotor * r
    rpm = v / (2 * math.pi * r) * 60.0 if r > 0 else 0.0
    pcalc_total = fsum * v
    pwheel = fdesign * v
    pmech_per = pwheel / motors
    ptotal = pwheel / eff
    pelec_per = ptotal / motors
    ibatt = ptotal / voltage
    ntotal = m * G * math.cos(th)
    ndrive = ntotal * drive_load_fraction
    ftraction = traction_coeff * ndrive
    return {
        "mass_kg": m, "wheel_radius_m": r, "slope_deg": deg, "speed_kmh": speed_kmh,
        "speed_m_s": v, "accel_m_s2": a, "fg_n": fg, "fr_n": fr, "fa_n": fa,
        "force_sum_n": fsum, "design_force_n": fdesign, "force_per_motor_n": fmotor,
        "torque_per_motor_nm": torque, "wheel_rpm": rpm, "calc_mech_power_total_w": pcalc_total,
        "design_wheel_power_total_w": pwheel, "design_mech_power_per_motor_w": pmech_per,
        "electrical_power_total_w": ptotal, "electrical_power_per_motor_w": pelec_per,
        "battery_current_a": ibatt, "driven_normal_load_n": ndrive,
        "traction_limit_n": ftraction, "traction_margin": (ftraction / fdesign if fdesign > 0 else 999.0),
        "motors": motors, "efficiency": eff,
    }


def calculate_drive_battery(data: Dict[str, Any]) -> Dict[str, Any]:
    """Simple per-cycle sizing model for the 72 V traction battery.

    A complete cycle is one outbound trip plus one return trip. Each one-way
    trip is split into flat distance and slope distance. Acceleration/start
    energy and recovered downhill energy are intentionally excluded from the
    sizing energy model to keep the preliminary calculation easy to audit.
    """
    m = max(0.0, _f(data, "mass_kg", 300.0))
    voltage = max(0.1, _f(data, "voltage_v", 72.0))
    speed_kmh = max(0.001, _f(data, "speed_kmh", 1.0))
    v = speed_kmh / 3.6
    one = max(0.01, _f(data, "one_way_m", 30.0))
    slope_len = _clamp(_f(data, "slope_length_m", 2.9), 0.0, one)
    flat_oneway = max(0.0, one - slope_len)
    slope_deg = _f(data, "slope_deg", 11.11)
    theta = math.radians(slope_deg)
    runtime_h = max(0.001, _f(data, "runtime_h", 3.0))

    lift_event_s = max(0.0, _f(data, "lift_time_per_event_s", 0.0))
    lift_events_per_round = max(0, _i(data, "lift_events_per_round", 0))
    lift_round_s = lift_event_s * lift_events_per_round
    other_stop_s = max(
        0.0,
        _f(data, "other_stop_time_per_round_s", _f(data, "stop_time_per_round_s", 0.0)),
    )

    crr = max(0.0, _f(data, "rolling_coeff", 0.02))
    eff = _clamp(_f(data, "drive_eff_pct", 60.0) / 100.0, 0.01, 1.0)
    aux_w = max(0.0, _f(data, "aux_power_w", 50.0))
    dod = _clamp(_f(data, "dod_pct", 80.0) / 100.0, 0.01, 1.0)
    reserve = max(0.0, _f(data, "reserve_pct", 20.0) / 100.0)
    battery_factor = max(1.0, _f(data, "battery_design_factor", 3.0))

    turn_enabled = str(data.get("turn_enabled", "false")).strip().lower() in ("1","true","on","yes")
    turn_events = max(0, _i(data, "turns_per_cycle", 2)) if turn_enabled else 0
    turn_angle_deg = max(0.0, _f(data, "turn_angle_deg", 180.0))
    turn_time_event_s = max(0.1, _f(data, "turn_time_s", 5.0))
    turn_coeff = max(0.0, _f(data, "turn_coeff", 0.20))
    track_width = max(0.01, _f(data, "track_width_m", 0.70))

    target_cont_c = max(0.1, _f(data, "target_cont_c", 3.0))
    target_peak_c = max(0.1, _f(data, "target_peak_c", 5.0))
    candidate_ah = max(0.0, _f(data, "candidate_ah", 40.0))
    candidate_bms_cont_a = max(0.0, _f(data, "candidate_bms_cont_a", 0.0))
    candidate_bms_peak_a = max(0.0, _f(data, "candidate_bms_peak_a", 0.0))

    runtime_s = runtime_h * 3600.0
    cycle_distance = 2.0 * one
    drive_cycle_s = cycle_distance / v
    turn_time_cycle_s = turn_events * turn_time_event_s
    cycle_total_s = drive_cycle_s + lift_round_s + other_stop_s + turn_time_cycle_s
    cycles_theoretical = runtime_s / cycle_total_s if cycle_total_s > 0 else 0.0
    completed_rounds = int(math.floor(cycles_theoretical + 1e-12))

    drive_time_total_s = completed_rounds * drive_cycle_s
    lift_time_total_s = completed_rounds * lift_round_s
    other_stop_total_s = completed_rounds * other_stop_s
    operation_time_used_s = completed_rounds * cycle_total_s
    remaining_time_s = max(0.0, runtime_s - operation_time_used_s)

    flat_cycle = 2.0 * flat_oneway

    fflat = crr * m * G
    fgrade = m * G * math.sin(theta)
    frrs = crr * m * G * math.cos(theta)
    fup = fgrade + frrs
    fdown = max(0.0, frrs - fgrade)

    pflat_mech = fflat * v
    pup_mech = fup * v
    pdown_mech = fdown * v

    eflat_mech_oneway = fflat * flat_oneway / 3600.0
    eup_mech = fup * slope_len / 3600.0
    edown_mech = fdown * slope_len / 3600.0
    emech_cycle = 2.0 * eflat_mech_oneway + eup_mech + edown_mech

    eflat_batt_oneway = eflat_mech_oneway / eff
    eup_batt = eup_mech / eff
    edown_batt = edown_mech / eff

    eout_drive = eflat_batt_oneway + eup_batt
    ereturn_drive = edown_batt + eflat_batt_oneway

    turn_phi = abs(math.radians(turn_angle_deg))
    turn_wheel_path = (track_width / 2.0) * turn_phi
    fturn_effective = turn_coeff * m * G
    eturn_event = (fturn_effective * turn_wheel_path) / (eff * 3600.0) if turn_events > 0 else 0.0
    eturn_cycle = eturn_event * turn_events
    pturn_avg = eturn_event * 3600.0 / turn_time_event_s if turn_events > 0 else 0.0
    iturn_avg = pturn_avg / voltage if voltage > 0 else 0.0

    edrive_cycle = eout_drive + ereturn_drive + eturn_cycle

    eaux_cycle = aux_w * (cycle_total_s / 3600.0)
    ecycle = edrive_cycle + eaux_cycle

    emech_total = emech_cycle * completed_rounds
    edrive = edrive_cycle * completed_rounds
    eaux = eaux_cycle * completed_rounds
    eload = ecycle * completed_rounds
    enom = eload / dod
    edesign = enom * (1.0 + reserve)
    ah = edesign / voltage
    erecommended = edesign * battery_factor
    ah_recommended = ah * battery_factor

    icalc_up = (pup_mech / eff) / voltage
    # Battery energy sizing remains the simple-cycle model, but BMS/current checks
    # must also respect the Drive Torque design-current reference when the web UI
    # supplies it. This prevents the web purchase checker from understating current.
    drive_reference_current = max(0.0, _f(data, "drive_reference_current_a", 0.0))
    # Continuous current represents steady operating demand only.
    # The Drive Torque reference includes acceleration/design allowance, so it
    # belongs in the peak/design check instead of inflating continuous current.
    cont_req = max(0.0, icalc_up, iturn_avg)
    peak_req = max(cont_req, drive_reference_current)

    ah_by_cont = cont_req / target_cont_c
    ah_by_peak = peak_req / target_peak_c
    design_ah_with_current = max(ah_recommended, ah_by_cont, ah_by_peak)
    suggested_ah = next_standard_capacity(design_ah_with_current)

    cycle_h = cycle_total_s / 3600.0 if cycle_total_s > 0 else 0.0
    load_per_cycle_wh = ecycle

    def reverse_for(capacity_ah: float) -> Dict[str, Any]:
        cap = max(0.0, float(capacity_ah))
        rated_wh = voltage * cap
        load_budget_wh = rated_wh * dod / (1.0 + reserve) if (1.0 + reserve) > 0 else 0.0
        avg_load_w = load_per_cycle_wh / cycle_h if cycle_h > 0 else 0.0
        runtime_est_h = load_budget_wh / avg_load_w if avg_load_w > 0 else 0.0
        full_rounds = int(math.floor(runtime_est_h / cycle_h + 1e-12)) if cycle_h > 0 else 0
        margin_wh = rated_wh - erecommended
        margin_pct = (100.0 * margin_wh / rated_wh) if rated_wh > 0 else -100.0
        return {
            "capacity_ah": cap,
            "rated_wh": rated_wh,
            "runtime_h": runtime_est_h,
            "full_rounds": full_rounds,
            "target_margin_wh": margin_wh,
            "target_margin_pct": margin_pct,
            "required_cont_c": cont_req / cap if cap > 0 else 999.0,
            "required_peak_c": peak_req / cap if cap > 0 else 999.0,
            "energy_ok": cap + 1e-9 >= ah_recommended,
            "c_rate_ok": (
                cap > 0
                and cont_req / cap <= target_cont_c + 1e-9
                and peak_req / cap <= target_peak_c + 1e-9
            ),
            "load_budget_wh": load_budget_wh,
            "load_per_cycle_wh": load_per_cycle_wh,
        }

    comparison = []
    for cap in STANDARD_AH:
        rv = reverse_for(cap)
        rv["check"] = (
            "PASS"
            if rv["energy_ok"] and rv["c_rate_ok"]
            else ("ENERGY LOW" if not rv["energy_ok"] else "C-RATE CHECK")
        )
        comparison.append(rv)

    candidate = reverse_for(candidate_ah)
    candidate.update({
        "bms_cont_a": candidate_bms_cont_a,
        "bms_peak_a": candidate_bms_peak_a,
        "bms_cont_ok": candidate_bms_cont_a > 0 and candidate_bms_cont_a + 1e-9 >= cont_req,
        "bms_peak_ok": candidate_bms_peak_a > 0 and candidate_bms_peak_a + 1e-9 >= peak_req,
    })

    return {
        "calculation_method": "simple_cycle",
        "energy_model": "calculated",
        "mass_kg": m, "voltage_v": voltage, "speed_kmh": speed_kmh, "speed_m_s": v,
        "one_way_m": one, "slope_length_m": slope_len, "flat_one_way_m": flat_oneway,
        "flat_cycle_m": flat_cycle, "slope_deg": slope_deg, "runtime_h": runtime_h,
        "cycles_theoretical": cycles_theoretical,
        "completed_round_trips": completed_rounds,
        "cycle_distance_m": cycle_distance,
        "drive_time_per_round_s": drive_cycle_s,
        "lift_time_per_event_s": lift_event_s,
        "lift_events_per_round": lift_events_per_round,
        "lift_time_per_round_s": lift_round_s,
        "other_stop_time_per_round_s": other_stop_s,
        "turn_time_per_event_s": turn_time_event_s,
        "turn_time_per_round_s": turn_time_cycle_s,
        "round_time_s": cycle_total_s,
        "drive_time_total_s": drive_time_total_s,
        "lift_time_total_s": lift_time_total_s,
        "other_stop_total_s": other_stop_total_s,
        "operation_time_used_s": operation_time_used_s,
        "remaining_time_s": remaining_time_s,

        "flat_force_n": fflat,
        "grade_force_n": fgrade,
        "slope_rolling_force_n": frrs,
        "uphill_force_n": fup,
        "downhill_drive_force_n": fdown,
        "flat_power_mech_w": pflat_mech,
        "uphill_power_mech_w": pup_mech,
        "downhill_power_mech_w": pdown_mech,

        "flat_energy_one_way_wh": eflat_batt_oneway,
        "uphill_slope_energy_wh": eup_batt,
        "downhill_slope_energy_wh": edown_batt,
        "outbound_drive_energy_wh": eout_drive,
        "return_drive_energy_wh": ereturn_drive,
        "turn_enabled": turn_enabled,
        "turns_per_cycle": turn_events,
        "turn_angle_deg": turn_angle_deg,
        "turn_coeff": turn_coeff,
        "track_width_m": track_width,
        "turn_wheel_path_m": turn_wheel_path,
        "turn_force_n": fturn_effective,
        "turn_energy_per_event_wh": eturn_event,
        "turn_energy_per_cycle_wh": eturn_cycle,
        "turn_average_power_w": pturn_avg,
        "turn_average_current_a": iturn_avg,
        "trip_drive_energy_wh": edrive_cycle,
        "aux_energy_per_cycle_wh": eaux_cycle,
        "total_energy_per_cycle_wh": ecycle,

        "drive_energy_wh": edrive,
        "aux_energy_wh": eaux,
        "load_energy_wh": eload,
        "nominal_energy_wh": enom,
        "design_energy_wh": edesign,
        "design_ah": ah,
        "battery_design_factor": battery_factor,
        "recommended_energy_wh": erecommended,
        "recommended_ah": ah_recommended,
        "standard_ah": next_standard_capacity(ah_recommended),

        "uphill_current_calc_a": icalc_up,
        # Compatibility fields retained; the simplified energy model does not use acceleration.
        "accel_current_calc_a": icalc_up,
        "calculated_peak_current_a": icalc_up,
        "worst_current_reference_a": icalc_up,
        "drive_reference_current_a": drive_reference_current,
        "continuous_current_required_a": cont_req,
        "peak_current_required_a": peak_req,

        "target_cont_c": target_cont_c,
        "target_peak_c": target_peak_c,
        "ah_by_continuous_c": ah_by_cont,
        "ah_by_peak_c": ah_by_peak,
        "design_ah_with_current": design_ah_with_current,
        "suggested_ah": suggested_ah,
        "suggested_reverse": reverse_for(suggested_ah),
        "candidate": candidate,
        "comparison": comparison,
        "energy_recovery_included": False,
        "winch_energy_included": False,
    }


def _longitudinal_balance(total_mass: float, payload_mass: float, boom_mass: float,
                          wheelbase: float, boom_length: float, angle_deg: float,
                          crane_from_rear: float, vehicle_cg_x: float,
                          dynamic_factor: float, case: str, required_sf: float) -> Dict[str, Any]:
    rear = -wheelbase / 2.0
    front = wheelbase / 2.0
    xc = rear + crane_from_rear
    xload = xc + boom_length * math.cos(math.radians(angle_deg))
    xboom = xc + (boom_length / 2.0) * math.cos(math.radians(angle_deg))
    mveh = max(0.0, total_mass - payload_mass - boom_mass)

    if case == "front":
        pivot, direction = front, 1.0
    else:
        pivot, direction = rear, -1.0

    mo = 0.0
    mr = 0.0
    components = []
    for name, mass, x, is_payload in (
        ("Vehicle", mveh, vehicle_cg_x, False),
        ("Boom", boom_mass, xboom, False),
        ("Payload", payload_mass, xload, True),
    ):
        signed = direction * (x - pivot)
        role = "overturning" if signed > 1e-12 else "resisting" if signed < -1e-12 else "on_pivot"
        factor = dynamic_factor if (is_payload and role == "overturning") else 1.0
        force = mass * G * factor
        arm = abs(signed)
        moment = force * arm
        if role == "overturning":
            mo += moment
        elif role == "resisting":
            mr += moment
        components.append({
            "name": name, "mass_kg": mass, "x_m": x, "factor": factor,
            "force_n": force, "arm_m": arm, "moment_nm": moment, "role": role,
        })

    sf = mr / mo if mo > 1e-12 else 999.0
    return {
        "case": case,
        "angle_deg": angle_deg,
        "pivot_m": pivot,
        "rear_x_m": rear,
        "front_x_m": front,
        "crane_x_m": xc,
        "load_x_m": xload,
        "boom_x_m": xboom,
        "vehicle_x_m": vehicle_cg_x,
        "overturning_moment_nm": mo,
        "resisting_moment_nm": mr,
        "sf": sf,
        "pass": sf >= required_sf,
        "components": components,
    }


def _longitudinal_sf(total_mass: float, payload_mass: float, boom_mass: float,
                     wheelbase: float, boom_length: float, angle_deg: float,
                     crane_from_rear: float, vehicle_cg_x: float, dynamic_factor: float) -> Dict[str, float]:
    """Compatibility wrapper retained for existing callers/tests."""
    front = _longitudinal_balance(
        total_mass, payload_mass, boom_mass, wheelbase, boom_length, angle_deg,
        crane_from_rear, vehicle_cg_x, dynamic_factor, "front", 0.0
    )
    rear = _longitudinal_balance(
        total_mass, payload_mass, boom_mass, wheelbase, boom_length, angle_deg,
        crane_from_rear, vehicle_cg_x, dynamic_factor, "rear", 0.0
    )
    return {
        "front_sf": front["sf"],
        "rear_sf": rear["sf"],
        "rear_x_m": rear["rear_x_m"],
        "front_x_m": front["front_x_m"],
        "crane_x_m": front["crane_x_m"],
        "load_x_m": front["load_x_m"],
        "boom_x_m": front["boom_x_m"],
    }


def _component_mass_summary(raw: Any) -> Dict[str, Any]:
    """Mirror the Desktop Component Mass grouping and weighted-CG rules."""
    rows = []
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            try:
                name = str(item.get("name", "")).strip()
                mass = max(0.0, float(item.get("mass_kg", 0.0)))
                x = float(item.get("x_m", 0.0))
                y = float(item.get("y_m", 0.0))
                z = float(item.get("z_m", 0.0))
            except (TypeError, ValueError):
                continue
            rows.append({"name": name, "mass_kg": mass, "x_m": x, "y_m": y, "z_m": z})

    def group_stats(items):
        mass = sum(r["mass_kg"] for r in items)
        if mass <= 0:
            return {"mass_kg": 0.0, "x_m": 0.0, "y_m": 0.0, "z_m": 0.0}
        return {
            "mass_kg": mass,
            "x_m": sum(r["mass_kg"] * r["x_m"] for r in items) / mass,
            "y_m": sum(r["mass_kg"] * r["y_m"] for r in items) / mass,
            "z_m": sum(r["mass_kg"] * r["z_m"] for r in items) / mass,
        }

    base, boom, payload = [], [], []
    for row in rows:
        name = row["name"].lower()
        if ("boom" in name) or ("แขนเครน" in name):
            boom.append(row)
        elif (
            ("basket" in name) or ("ตะกร้า" in name)
            or ("payload" in name) or ("ซากสัตว์" in name)
        ):
            payload.append(row)
        else:
            base.append(row)

    total = group_stats(rows)
    return {
        "rows": rows,
        "total_mass_kg": total["mass_kg"],
        "total_x_m": total["x_m"],
        "total_y_m": total["y_m"],
        "total_z_m": total["z_m"],
        "base": group_stats(base),
        "boom": group_stats(boom),
        "payload": group_stats(payload),
    }


def calculate_stability(data: Dict[str, Any]) -> Dict[str, Any]:
    mass_mode = str(data.get("mass_mode", "total")).strip().lower()
    if mass_mode not in {"total", "components"}:
        mass_mode = "total"

    track = max(0.01, _f(data, "track_width_m", 0.7))
    wb = max(0.01, _f(data, "wheelbase_m", 1.1))
    boom = max(0.0, _f(data, "boom_length_m", 1.2))
    angle = _clamp(_f(data, "crane_angle_deg", 90.0), -90.0, 90.0)
    kd = max(0.0, _f(data, "dynamic_factor", 1.0))
    req = max(0.0, _f(data, "required_sf", 1.5))
    crane_from_rear = _f(data, "crane_from_rear_m", 0.15)

    component_summary = _component_mass_summary(data.get("components", []))

    mt = max(0.0, _f(data, "total_mass_kg", 300.0))
    ml = max(0.0, _f(data, "payload_mass_kg", 100.0))
    mb = max(0.0, _f(data, "boom_mass_kg", 20.0))
    vehicle_cg_x = _f(data, "vehicle_cg_x_from_center_m", 0.0)
    vehicle_cg_y = _f(data, "vehicle_cg_y_m", 0.0)

    slope_deg = _f(data, "slope_deg", 11.11)
    slope_accel = max(0.0, _f(data, "slope_accel_mps2", 0.28))
    combined_cg_from_rear = max(0.0, _f(data, "combined_cg_from_rear_m", wb / 2.0))
    combined_cg_height = max(0.001, _f(data, "combined_cg_height_m", 0.55))

    if mass_mode == "components" and component_summary["total_mass_kg"] > 0:
        mt = component_summary["total_mass_kg"]
        ml = component_summary["payload"]["mass_kg"]
        mb = component_summary["boom"]["mass_kg"]
        vehicle_cg_x = component_summary["base"]["x_m"]
        vehicle_cg_y = component_summary["base"]["y_m"]
        combined_cg_from_rear = max(0.0, component_summary["total_x_m"] + wb / 2.0)
        combined_cg_height = max(0.001, component_summary["total_z_m"])

    m_vehicle = max(0.0, mt - ml - mb)

    def side_balance(side: str, angle_deg: float) -> Dict[str, Any]:
        y_load = boom * math.sin(math.radians(angle_deg))
        y_boom = (boom / 2.0) * math.sin(math.radians(angle_deg))
        direction = 1.0 if side == "right" else -1.0
        pivot = direction * track / 2.0
        mo = 0.0
        mr = 0.0
        components = []
        for name, mass, y, is_payload in (
            ("Vehicle", m_vehicle, vehicle_cg_y, False),
            ("Boom", mb, y_boom, False),
            ("Payload", ml, y_load, True),
        ):
            signed = direction * (y - pivot)
            role = "overturning" if signed > 1e-12 else "resisting" if signed < -1e-12 else "on_pivot"
            factor = kd if (is_payload and role == "overturning") else 1.0
            force = mass * G * factor
            arm = abs(signed)
            moment = force * arm
            if role == "overturning":
                mo += moment
            elif role == "resisting":
                mr += moment
            components.append({
                "name": name, "mass_kg": mass, "y_m": y, "factor": factor,
                "force_n": force, "arm_m": arm, "moment_nm": moment, "role": role,
            })
        sf = mr / mo if mo > 1e-12 else 999.0
        return {
            "case": f"side_{side}", "side": side, "angle_deg": angle_deg,
            "pivot_m": pivot, "load_lateral_m": y_load, "boom_lateral_m": y_boom,
            "overturning_moment_nm": mo, "resisting_moment_nm": mr,
            "sf": sf, "pass": sf >= req, "components": components,
        }

    current_left = side_balance("left", angle)
    current_right = side_balance("right", angle)
    current_front = _longitudinal_balance(
        mt, ml, mb, wb, boom, angle, crane_from_rear, vehicle_cg_x, kd, "front", req
    )
    current_rear = _longitudinal_balance(
        mt, ml, mb, wb, boom, angle, crane_from_rear, vehicle_cg_x, kd, "rear", req
    )

    alpha = math.radians(slope_deg)
    w_parallel = mt * G * math.sin(alpha)
    w_normal = mt * G * math.cos(alpha)
    inertia = mt * slope_accel
    slope_mo = (w_parallel + inertia) * combined_cg_height
    slope_mr = w_normal * combined_cg_from_rear
    slope_sf = slope_mr / slope_mo if slope_mo > 1e-12 else 999.0
    slope_case = {
        "case": "slope",
        "angle_deg": None,
        "slope_deg": slope_deg,
        "accel_mps2": slope_accel,
        "combined_cg_from_rear_m": combined_cg_from_rear,
        "combined_cg_height_m": combined_cg_height,
        "w_parallel_n": w_parallel,
        "w_normal_n": w_normal,
        "inertia_n": inertia,
        "overturning_moment_nm": slope_mo,
        "resisting_moment_nm": slope_mr,
        "sf": slope_sf,
        "pass": slope_sf >= req,
    }

    def critical_for(key: str) -> Dict[str, Any]:
        best = None
        for deg in range(-90, 91):
            if key == "side_left":
                bal = side_balance("left", float(deg))
            elif key == "side_right":
                bal = side_balance("right", float(deg))
            elif key == "front":
                bal = _longitudinal_balance(
                    mt, ml, mb, wb, boom, float(deg), crane_from_rear, vehicle_cg_x, kd, "front", req
                )
            else:
                bal = _longitudinal_balance(
                    mt, ml, mb, wb, boom, float(deg), crane_from_rear, vehicle_cg_x, kd, "rear", req
                )
            if best is None or bal["sf"] < best["sf"]:
                best = bal
        return best or {}

    critical_cases = {
        "side_left": critical_for("side_left"),
        "side_right": critical_for("side_right"),
        "front": critical_for("front"),
        "rear": critical_for("rear"),
        "slope": dict(slope_case),
    }

    current_cases = {
        "side_left": current_left,
        "side_right": current_right,
        "front": current_front,
        "rear": current_rear,
        "slope": slope_case,
    }

    # Match Desktop: crane tipping governing case is Left/Right/Front/Rear.
    # Uphill slope stability is a separate driving case and must not silently
    # replace the crane critical case shown in the main Stability summary.
    crane_keys = ("side_left", "side_right", "front", "rear")
    current_candidates = [(k, current_cases[k]["sf"]) for k in crane_keys]
    current_governing_key, current_governing_sf = min(current_candidates, key=lambda item: item[1])
    critical_candidates = [(k, critical_cases[k]["sf"]) for k in crane_keys]
    critical_governing_key, critical_governing_sf = min(critical_candidates, key=lambda item: item[1])

    # Compatibility fields used by the existing web result card.
    critical_direction = "left" if current_left["sf"] <= current_right["sf"] else "right"
    critical_side = current_left if critical_direction == "left" else current_right

    return {
        "mass_mode": mass_mode,
        "mass_mode_label": "Component Mass / Sum Components" if mass_mode == "components" else "Total Mass / Manual Total",
        "component_summary": component_summary,
        "base_vehicle_mass_kg": m_vehicle,
        "vehicle_cg_x_m": vehicle_cg_x,
        "vehicle_cg_y_m": vehicle_cg_y,
        "total_mass_kg": mt, "payload_mass_kg": ml, "boom_mass_kg": mb,
        "track_width_m": track, "wheelbase_m": wb, "boom_length_m": boom,
        "crane_angle_deg": angle, "dynamic_factor": kd, "required_sf": req,
        "coordinate_convention": {
            "x": "+x forward", "y": "+y right", "z": "+z up",
            "crane_angle": "-90 left, 0 forward, +90 right",
        },
        "side": {**critical_side, "critical_direction": critical_direction},
        "side_left": current_left,
        "side_right": current_right,
        "front": current_front,
        "rear": current_rear,
        "slope": slope_case,
        "current_cases": current_cases,
        "critical_cases": critical_cases,
        "current_governing": {
            "key": current_governing_key, "sf": current_governing_sf,
            "pass": current_governing_sf >= req,
        },
        "critical_governing": {
            "key": critical_governing_key, "sf": critical_governing_sf,
            "pass": critical_governing_sf >= req,
            "angle_deg": critical_cases[critical_governing_key].get("angle_deg"),
        },
        "geometry": {
            "rear_x_m": current_front["rear_x_m"],
            "front_x_m": current_front["front_x_m"],
            "crane_x_m": current_front["crane_x_m"],
            "load_x_m": current_front["load_x_m"],
            "boom_x_m": current_front["boom_x_m"],
        },
        "note": "Formal preliminary rigid-body model; web FBD uses the same returned force/moment data. Confirm real CG/masses before fabrication.",
    }

