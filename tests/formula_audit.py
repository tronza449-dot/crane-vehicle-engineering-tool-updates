"""CVET engineering formula invariant audit (desktop-independent, run before release).

This deliberately checks mathematical identities independently of UI golden numbers.
Assumptions: rigid-body quasi-static tipping; positive uphill motor demand;
no regenerative drive-energy credit; first-layer winch performance estimates.
"""
import math
import web_engine as calc

G = 9.81

def near(value, expected, label, rtol=1e-9, atol=1e-8):
    assert math.isfinite(float(value)), (label, "nonfinite", value)
    assert abs(value - expected) <= atol + rtol * abs(expected), (
        label, value, expected
    )

# 1. Measured ramp geometry: length and grade are different quantities.
ramp=calc.calculate_ramp_geometry(dict(rise_cm=55,run_cm=280,measured_slant_cm=290,mass_kg=300))
near(ramp["theoretical_slant_cm"], math.hypot(55,280), "ramp length")
near(ramp["angle_deg"], math.degrees(math.atan2(55,280)), "ramp angle")
near(ramp["slope_percent"], 100*55/280, "ramp percent")
near(ramp["f_slope_n"], 300*G*55/math.hypot(55,280), "ramp force")
assert abs(ramp["angle_deg"]-19.0)>5.0, "19deg must not be confused with ~19.64 percent grade"

# 2. Motor sizing: force components, power identities, and mass/radius monotonicity.
drive=dict(mass_kg=300,wheel_diameter_in=16,slope_deg=19,speed_kmh=5,
           motors=2,accel_time_s=5,rolling_coeff=.02,
           safety_factor=1.5,drive_eff_pct=85,voltage_v=72)
d=calc.calculate_drive_torque(drive)
r=16*.0254/2;v=5/3.6;th=math.radians(19)
force=300*(G*math.sin(th)+.02*G*math.cos(th)+v/5)
near(d["design_force_n"],force*1.5,"motor design force")
near(d["torque_per_motor_nm"],force*1.5*r/2,"motor torque")
near(d["design_wheel_power_total_w"],d["torque_per_motor_nm"]*2*(v/r),"T omega")
near(d["electrical_power_total_w"],d["design_wheel_power_total_w"]/.85,"electrical power")
near(d["battery_current_a"],d["electrical_power_total_w"]/72,"electrical current")
for m in (100,200,300,400,500):
    test=calc.calculate_drive_torque({**drive,"mass_kg":m})
    near(test["torque_per_motor_nm"]/d["torque_per_motor_nm"],m/300,"torque mass ratio")
    near(test["design_wheel_power_total_w"]/d["design_wheel_power_total_w"],m/300,"power mass ratio")
assert calc.calculate_drive_torque({**drive,"slope_deg":20})["torque_per_motor_nm"]>d["torque_per_motor_nm"]
assert calc.calculate_drive_torque({**drive,"wheel_diameter_in":20})["torque_per_motor_nm"]>d["torque_per_motor_nm"]
assert calc.calculate_drive_torque({**drive,"motors":4})["torque_per_motor_nm"]<d["torque_per_motor_nm"]
near(d["driven_normal_load_n"],300*G*math.cos(th)*.5,"driven normal force")

# 3. Traction-energy cycle, 72V vs separate 12V winch.
bdata=dict(mass_kg=300,voltage_v=72,speed_kmh=1,one_way_m=30,
    slope_length_m=2.9,slope_deg=ramp["angle_deg"],runtime_h=3,
    rolling_coeff=.02,drive_eff_pct=60,aux_power_w=50,
    dod_pct=80,reserve_pct=20,battery_design_factor=3,
    lift_time_per_event_s=0,lift_events_per_round=0)
b=calc.calculate_drive_battery(bdata)
# Purchase current envelope must never replace the simple 3h energy calculation.
rated_expected=(2*1500/.85+50)/60
near(b["rated_current_reference_a"],rated_expected,"rated power / low-voltage current")
near(b["continuous_current_required_a"],rated_expected*1.25,"design BMS continuous reference")
assert b["continuous_current_required_a"]>b["operating_current_a"]
assert b["peak_verified"] is False and b["vesc_limit_known"] is False
reduced_v=calc.calculate_drive_battery({**bdata,"min_pack_voltage_v":50})
assert reduced_v["rated_current_reference_a"]>b["rated_current_reference_a"]
assert reduced_v["continuous_current_required_a"]>b["continuous_current_required_a"]
near(reduced_v["design_ah"],b["design_ah"],"Ah invariant against Vmin")
near(reduced_v["load_energy_wh"],b["load_energy_wh"],"Wh invariant against Vmin")
assert reduced_v["completed_round_trips"]==b["completed_round_trips"]
with_vesc=calc.calculate_drive_battery({**bdata,"vesc_pack_battery_limit_a":110})
assert with_vesc["peak_current_required_a"]>=110+50/60
assert with_vesc["peak_verified"] is False
Ls=2.9;flat=30-Ls;angle=math.radians(ramp["angle_deg"])
expected_up=(300*G*(math.sin(angle)+.02*math.cos(angle))*Ls)/3600/.60
expected_flat=(300*G*.02*(2*flat))/3600/.60
expected_down=max(0,300*G*(.02*math.cos(angle)-math.sin(angle)))*Ls/3600/.60
near(b["uphill_slope_energy_wh"],expected_up,"uphill Wh")
near(b["downhill_slope_energy_wh"],expected_down,"downhill battery Wh")
near(b["trip_drive_energy_wh"],expected_up+expected_down+expected_flat,"drive cycle Wh")
near(b["aux_energy_wh"],50*3,"aux 3 hour energy")
near(b["load_energy_wh"],b["trip_drive_energy_wh"]*b["completed_round_trips"]+150,"total energy")
near(b["design_ah"],b["load_energy_wh"]*1.2/.8/72,"battery Ah")
assert b["winch_energy_included"] is False and b["energy_recovery_included"] is False
for mass in (200,300,400):
    p=calc.calculate_drive_battery({**bdata,"mass_kg":mass})
    near(p["trip_drive_energy_wh"]/b["trip_drive_energy_wh"],mass/300,"drive Wh/mass")
    assert p["completed_round_trips"]==b["completed_round_trips"]
assert calc.calculate_drive_battery({**bdata,"mass_kg":400})["design_ah"]>b["design_ah"]
turn=calc.calculate_drive_battery({**bdata,"turn_enabled":True,
                "turns_per_cycle":2,"turn_angle_deg":180,"track_width_m":.7})
assert turn["turn_energy_per_cycle_wh"]>0
near(turn["turn_energy_per_cycle_wh"],turn["turn_energy_per_event_wh"]*2,"turn count")

# 4. First-layer winch interpolation and lift counts.
for load in (0,100,454,907,1800,2041):
    perf=calc.winch_interpolate(load)
    low=perf["lower_load_kg"];high=perf["upper_load_kg"]
    frac=(perf["load_kg"]-low)/(high-low) if high>low else 0.0
    near(perf["speed_m_min"],perf["lower_speed_m_min"]+
         frac*(perf["upper_speed_m_min"]-perf["lower_speed_m_min"]),"interpolated speed")
    near(perf["current_a"],perf["lower_current_a"]+
         frac*(perf["upper_current_a"]-perf["lower_current_a"]),"interpolated current")
w=calc.calculate_winch(dict(load_kg=100,lift_m=1.5,vehicle_speed_kmh=1,
    one_way_m=30,operating_hours=3,events_per_round=2,down_mode="conservative",
    winch_voltage_v=12,dod_pct=80,reserve_pct=20))
wc=w["core"];op=w["operation"];wb=w["battery"]
near(wc["up_time_s"],1.5/wc["up_speed_m_min"]*60,"winch time")
near(wb["e_up_wh"],12*wc["up_current_a"]*wc["up_time_s"]/3600,"winch Wh")
near(wb["ah_design"],wb["e_total_wh"]*1.2/(12*.8),"winch Ah")
assert op["completed_round_trips"]==32 and op["lift_events"]==64
assert wb["events"]==64 and wb["winch_moves"]==128
manual=calc.calculate_winch(dict(load_kg=100,lift_m=1.5,
         event_mode="manual",manual_events=50))
assert manual["battery"]["events"]==50 and manual["battery"]["winch_moves"]==100
assert calc.winch_core(dict(load_kg=100,lift_m=5))["layer_correction_available"] is False
assert calc.winch_core(dict(load_kg=100,lift_m=5))["first_layer_performance_warning"]

# 5. Four overturning axes and uphill quasi-static force balance.
stab=dict(total_mass_kg=300,payload_mass_kg=100,boom_mass_kg=20,
          track_width_m=1.1,wheelbase_m=1.1,boom_length_m=1.2,
          dynamic_factor=1.2,required_sf=1.5,crane_from_rear_m=.15,
          vehicle_cg_x_from_center_m=0,vehicle_cg_y_m=0,
          slope_deg=ramp["angle_deg"],slope_accel_mps2=.28,
          combined_cg_from_rear_m=.55,combined_cg_height_m=.57)
left=calc.calculate_stability({**stab,"crane_angle_deg":-90})
right=calc.calculate_stability({**stab,"crane_angle_deg":90})
near(left["side_left"]["overturning_moment_nm"],774.99,"left overturn")
near(left["side_left"]["resisting_moment_nm"],971.19,"left resist")
near(left["side_left"]["sf"],971.19/774.99,"left SF")
near(left["side_right"]["overturning_moment_nm"],0,"left load cannot overturn right")
near(right["side_right"]["sf"],left["side_left"]["sf"],"left/right symmetry")
front=calc.calculate_stability({**stab,"crane_angle_deg":0})
near(front["front"]["overturning_moment_nm"],294.3,"front overturn")
near(front["front"]["resisting_moment_nm"],1039.86,"front resist")
near(front["rear"]["overturning_moment_nm"],0,"rear no overturn in -90..+90")
s=front["slope"];alpha=math.radians(stab["slope_deg"])
near(s["overturning_moment_nm"],300*(G*math.sin(alpha)+.28)*.57,"slope overturn")
near(s["resisting_moment_nm"],300*G*math.cos(alpha)*.55,"slope resist")
assert s["sf"]>0
assert left["critical_cases"]["side_left"]["angle_deg"]==-90
assert right["critical_cases"]["side_right"]["angle_deg"]==90
assert front["critical_cases"]["front"]["angle_deg"]==0

# 6. A changed operating cycle is NOT a valid mass-only comparison.
# With longer lift times fewer completed rounds may lower 3h total drive Ah.
slow=calc.calculate_drive_battery({**bdata,"mass_kg":400,
                                  "lift_time_per_event_s":180,
                                  "lift_events_per_round":2})
assert slow["completed_round_trips"]<b["completed_round_trips"]
assert slow["trip_drive_energy_wh"]>b["trip_drive_energy_wh"]
print("CVET_FORMULA_AUDIT_OK: torque, ramp, 72V energy, winch 12V, tipping and slope",flush=True)
