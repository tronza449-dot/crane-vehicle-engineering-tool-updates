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
            }
    x, v, current = WINCH_PERF[-1]
    return {"load_kg": m, "speed_m_min": v, "current_a": current, "alpha": 1.0,
            "lower_load_kg": x, "upper_load_kg": x}


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


def calculate_drive_torque(data: Dict[str, Any]) -> Dict[str, Any]:
    m = max(0.0, _f(data, "mass_kg", 300.0))
    wheel_in = max(0.1, _f(data, "wheel_diameter_in", 16.0))
    r = wheel_in * 0.0254 / 2.0
    deg = _f(data, "slope_deg", 19.0)
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
    m = max(0.0, _f(data, "mass_kg", 300.0))
    voltage = max(0.1, _f(data, "voltage_v", 72.0))
    speed_kmh = max(0.001, _f(data, "speed_kmh", 1.0))
    v = speed_kmh / 3.6
    one = max(0.01, _f(data, "one_way_m", 30.0))
    slope_len = _clamp(_f(data, "slope_length_m", 30.0), 0.0, one)
    slope_deg = _f(data, "slope_deg", 19.0)
    theta = math.radians(slope_deg)
    runtime_h = max(0.001, _f(data, "runtime_h", 3.0))

    # Operating-time model for the MAIN 72 V battery:
    # driving time + lifting time + other stops determine how many complete
    # vehicle rounds fit in the requested runtime. Winch ENERGY is excluded
    # because this project uses a separate 12 V winch battery.
    lift_event_s = max(0.0, _f(data, "lift_time_per_event_s", 0.0))
    lift_events_per_round = max(0, _i(data, "lift_events_per_round", 0))
    lift_round_s = lift_event_s * lift_events_per_round
    other_stop_s = max(
        0.0,
        _f(
            data,
            "other_stop_time_per_round_s",
            _f(data, "stop_time_per_round_s", 0.0),
        ),
    )

    crr = max(0.0, _f(data, "rolling_coeff", 0.02))
    eff = _clamp(_f(data, "drive_eff_pct", 85.0) / 100.0, 0.01, 1.0)
    up_eff = _clamp(_f(data, "uphill_eff_pct", 85.0) / 100.0, 0.01, 1.0)
    starts = max(0, _i(data, "starts_per_round", 2))
    accel_time = max(0.01, _f(data, "accel_time_s", 5.0))
    motor_rated_w = max(0.0, _f(data, "motor_rated_w", 1500.0))
    motors = max(1, _i(data, "motors", 2))
    aux_w = max(0.0, _f(data, "aux_power_w", 100.0))
    dod = _clamp(_f(data, "dod_pct", 80.0) / 100.0, 0.01, 1.0)
    reserve = max(0.0, _f(data, "reserve_pct", 20.0) / 100.0)
    model = str(data.get("energy_model", "calculated")).strip().lower()

    runtime_s = runtime_h * 3600.0
    cycle_distance = 2.0 * one
    drive_cycle_s = cycle_distance / v
    cycle_total_s = drive_cycle_s + lift_round_s + other_stop_s
    cycles_theoretical = runtime_s / cycle_total_s if cycle_total_s > 0 else 0.0
    completed_rounds = int(math.floor(cycles_theoretical + 1e-12))

    drive_time_total_s = completed_rounds * drive_cycle_s
    lift_time_total_s = completed_rounds * lift_round_s
    other_stop_total_s = completed_rounds * other_stop_s
    operation_time_used_s = completed_rounds * cycle_total_s
    remaining_time_s = max(0.0, runtime_s - operation_time_used_s)

    flat_cycle = max(0.0, cycle_distance - 2.0 * slope_len)
    flat_time_h = (flat_cycle / v) / 3600.0
    up_time_h = (slope_len / v) / 3600.0
    down_time_h = up_time_h

    fflat = crr * m * G
    pflat_mech = fflat * v
    fgrade = m * G * math.sin(theta)
    frrs = crr * m * G * math.cos(theta)
    fup = fgrade + frrs
    pup_mech = fup * v
    fdown = max(0.0, frrs - fgrade)
    pdown_mech = fdown * v

    eflat_mech_cycle = pflat_mech * flat_time_h
    eup_mech_cycle = pup_mech * up_time_h
    edown_mech_cycle = pdown_mech * down_time_h

    accel_a = v / accel_time
    facc_peak = m * accel_a
    pacc_peak_mech = (fup + facc_peak) * v
    eacc_mech_cycle = (0.5 * m * v * v / 3600.0) * starts

    emech_cycle = eflat_mech_cycle + eup_mech_cycle + edown_mech_cycle + eacc_mech_cycle
    emech_total = emech_cycle * completed_rounds
    ecalc_drive_cycle = emech_cycle / eff
    ecalc_drive = ecalc_drive_cycle * completed_rounds

    rated_total = motor_rated_w * motors
    pworst_batt = rated_total / up_eff
    eworst_up_cycle = pworst_batt * up_time_h
    eflat_batt_cycle = eflat_mech_cycle / eff
    edown_batt_cycle = edown_mech_cycle / eff
    eacc_batt_cycle = eacc_mech_cycle / eff
    eworst_drive_cycle = eflat_batt_cycle + edown_batt_cycle + eacc_batt_cycle + eworst_up_cycle
    eworst_drive = eworst_drive_cycle * completed_rounds

    use_worst = model == "worst"
    edrive_cycle = eworst_drive_cycle if use_worst else ecalc_drive_cycle
    edrive = edrive_cycle * completed_rounds

    # Aux power remains active across the whole requested runtime.
    eaux = aux_w * runtime_h
    eload = edrive + eaux
    enom = eload / dod
    edesign = enom * (1.0 + reserve)
    ah = edesign / voltage

    icalc_up = (pup_mech / eff) / voltage
    icalc_accel = (pacc_peak_mech / eff) / voltage
    iworst = pworst_batt / voltage
    return {
        "energy_model": "worst" if use_worst else "calculated",
        "mass_kg": m, "voltage_v": voltage, "speed_kmh": speed_kmh, "speed_m_s": v,
        "one_way_m": one, "slope_length_m": slope_len, "slope_deg": slope_deg,
        "runtime_h": runtime_h,
        "cycles_theoretical": cycles_theoretical,
        "completed_round_trips": completed_rounds,
        "cycle_distance_m": cycle_distance,
        "drive_time_per_round_s": drive_cycle_s,
        "lift_time_per_event_s": lift_event_s,
        "lift_events_per_round": lift_events_per_round,
        "lift_time_per_round_s": lift_round_s,
        "other_stop_time_per_round_s": other_stop_s,
        "round_time_s": cycle_total_s,
        "drive_time_total_s": drive_time_total_s,
        "lift_time_total_s": lift_time_total_s,
        "other_stop_total_s": other_stop_total_s,
        "operation_time_used_s": operation_time_used_s,
        "remaining_time_s": remaining_time_s,
        "drive_energy_wh": edrive, "aux_energy_wh": eaux, "load_energy_wh": eload,
        "nominal_energy_wh": enom, "design_energy_wh": edesign, "design_ah": ah,
        "standard_ah": next_standard_capacity(ah),
        "uphill_current_calc_a": icalc_up, "accel_current_calc_a": icalc_accel,
        "calculated_peak_current_a": max(icalc_up, icalc_accel),
        "worst_current_reference_a": iworst,
        "trip_drive_energy_wh": edrive_cycle,
        "no_regen": True,
        "winch_energy_included": False,
    }


def _longitudinal_sf(total_mass: float, payload_mass: float, boom_mass: float,
                     wheelbase: float, boom_length: float, angle_deg: float,
                     crane_from_rear: float, vehicle_cg_x: float, dynamic_factor: float) -> Dict[str, float]:
    rear = -wheelbase / 2.0
    front = wheelbase / 2.0
    xc = rear + crane_from_rear
    xload = xc + boom_length * math.cos(math.radians(angle_deg))
    xboom = xc + (boom_length / 2.0) * math.cos(math.radians(angle_deg))
    mveh = max(0.0, total_mass - payload_mass - boom_mass)

    def chk(pivot: float, direction: float) -> float:
        mo = 0.0
        mr = 0.0
        for mass, x, is_payload in (
            (mveh, vehicle_cg_x, False),
            (payload_mass, xload, True),
            (boom_mass, xboom, False),
        ):
            signed = direction * (x - pivot)
            if signed > 0:
                factor = dynamic_factor if is_payload else 1.0
                mo += factor * mass * G * signed
            elif signed < 0:
                mr += mass * G * (-signed)
        return mr / mo if mo > 1e-12 else 999.0

    return {
        "front_sf": chk(front, 1.0),
        "rear_sf": chk(rear, -1.0),
        "rear_x_m": rear, "front_x_m": front, "crane_x_m": xc,
        "load_x_m": xload, "boom_x_m": xboom,
    }


def calculate_stability(data: Dict[str, Any]) -> Dict[str, Any]:
    mt = max(0.0, _f(data, "total_mass_kg", 300.0))
    ml = max(0.0, _f(data, "payload_mass_kg", 100.0))
    mb = max(0.0, _f(data, "boom_mass_kg", 80.0))
    track = max(0.01, _f(data, "track_width_m", 0.7))
    wb = max(0.01, _f(data, "wheelbase_m", 1.1))
    boom = max(0.0, _f(data, "boom_length_m", 1.2))
    angle = _f(data, "crane_angle_deg", 90.0)
    kd = max(0.0, _f(data, "dynamic_factor", 1.0))
    req = max(0.0, _f(data, "required_sf", 1.5))
    crane_from_rear = _f(data, "crane_from_rear_m", 0.2)
    vehicle_cg_x = _f(data, "vehicle_cg_x_from_center_m", 0.0)

    pivot = track / 2.0
    y_load = abs(boom * math.sin(math.radians(angle)))
    y_boom = abs((boom / 2.0) * math.sin(math.radians(angle)))
    m_vehicle = max(0.0, mt - ml - mb)
    vehicle_mr = m_vehicle * G * pivot
    payload_over = kd * ml * G * max(0.0, y_load - pivot)
    payload_res = ml * G * max(0.0, pivot - y_load)
    boom_over = mb * G * max(0.0, y_boom - pivot)
    boom_res = mb * G * max(0.0, pivot - y_boom)
    mo = payload_over + boom_over
    mr = vehicle_mr + payload_res + boom_res
    side_sf = mr / mo if mo > 1e-12 else 999.0

    longi = _longitudinal_sf(mt, ml, mb, wb, boom, angle, crane_from_rear, vehicle_cg_x, kd)
    return {
        "total_mass_kg": mt, "payload_mass_kg": ml, "boom_mass_kg": mb,
        "track_width_m": track, "wheelbase_m": wb, "boom_length_m": boom,
        "crane_angle_deg": angle, "dynamic_factor": kd, "required_sf": req,
        "side": {
            "pivot_m": pivot, "load_lateral_m": y_load, "boom_lateral_m": y_boom,
            "overturning_moment_nm": mo, "resisting_moment_nm": mr,
            "sf": side_sf, "pass": side_sf >= req,
        },
        "front": {"sf": longi["front_sf"], "pass": longi["front_sf"] >= req},
        "rear": {"sf": longi["rear_sf"], "pass": longi["rear_sf"] >= req},
        "geometry": {k: v for k, v in longi.items() if k not in {"front_sf", "rear_sf"}},
        "note": "Preliminary static model; confirm real CG/masses before fabrication.",
    }
