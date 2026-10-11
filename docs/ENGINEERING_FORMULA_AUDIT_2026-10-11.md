# CVET Engineering Formula Audit — 11 October 2026
Source baseline: V53.8.75, checked against desktop \`CraneVehicleEngineeringTool.py\` and pure web \`web_engine.py\`.
Scope: engineering calculation paths, dimensional consistency, linked state assumptions, existing deep regression and new invariant tests. This is a software/engineering-model audit, **not physical certification**.

## How to reproduce
- \`python tests/formula_audit.py\` — independent Python reference equations, dimensional checks and metamorphic invariants (no Qt needed).
- \`QT_QPA_PLATFORM=offscreen python tests/release_smoke.py\` — desktop UI, saved-state What-if baseline, calculation and FBD render checks.
- \`QT_QPA_PLATFORM=offscreen python tests/full_regression.py\` — extensive desktop/web parity and integrated functions (not currently a blocking release job).
- The Windows release workflow now runs \`tests/formula_audit.py\` BEFORE the UI smoke and installer build; a failure blocks a new version. CI success must be confirmed in GitHub Actions, not inferred from a successful commit.

## Verification matrix

| Module | Equation(s) audited | Assessment | Boundaries / cautions |
|---|---|---|---|
| Ramp geometry | \`L=hypot(run,rise)\`, \`θ=atan2(rise,run)\`, \`grade%=100 rise/run\`, \`F=mg sinθ\` | Formula/units consistent | 55 cm rise / 280 cm run = approx **11.11°**, **19.64% grade**, NOT 19°; 290 cm tape slant disagrees with theoretical ~285.35 cm by ~4.65 cm |
| Drive torque | \`Fg=mg sinθ\`, \`Frr=Crr mg cosθ\`, \`Fa=mv/t\`, \`Fdesign=(Fg+Frr+Fa) SF\`, \`T=Fdesign r/n\` | Formula/units consistent for straight uphill positive-demand case | Assumes equal sharing between two hub motors, constant Crr/η, preset driven-wheel load fraction. Rated power alone does not prove low-speed torque or grip |
| Drive power/current | \`Pwheel=Fdesign v=Tω n\`, \`Pelec=Pwheel/η\`, \`I=Pelec/V\` | Identity consistent | Controller/battery peak currents and true motor torque-speed curve still require datasheets/measurements |
| Traction 72 V energy | Per-cycle flat/up/down travel, \`Wh=F·distance/(3600η)\`, \`Etotal=Ncycles Edrive,cycle + Paux runtime\`, \`Ah=E(1+reserve)/(V DoD)\` | Dimensional identity consistent | Does not include start/acceleration energy, regenerative credit, unmodeled crane-slew demand or measured downhill braking current |
| Pivot/differential | \`s=(W/2)φ\`, \`E= Cturn mg s/(3600η)\` | Dimensions consistent | \`Cturn\` is empirical; calibration on actual tires/concrete required |
| Main battery sizing/BMS | Usable DoD, reserve, Kb, continuous/peak current checks; Wh and Ah separate | Arithmetic consistent | C-rate and current margins are design assumptions, not BMS or thermal validation |
| Winch speed | Piecewise linear first-layer interpolation of supplier speed and current against load | Interpolation correct against table knots | Results are **first-layer estimates**, not certified for higher rope layers or altered voltage |
| Winch time/energy | \`tup=h/vup·60\`, \`Eup=VIup tup/3600\`; same separately for DOWN | Unit conversions correct | DOWN=UP is a conservative modeling option, not a measurement; stall/startup surge unknown |
| Winch work cycles | 1 job = 1 UP + 1 DOWN, 2 jobs/round where configured; \`rounds=floor(3h / tcycle)\` | Consistent with project definition | Manual jobs need to be physically feasible within the requested operation window |
| Side/rear/front tipping | Per mass, actual projected CG line and lever to chosen wheel-contact pivot; \`MO=sum(F d)_overturn\`, \`MR=sum(F d)_resist\`, \`SF=MR/MO\` | Independent reference numbers confirm side 774.99/971.19, front 294.30/1039.86, rear zero MO at ±90° with the reference dimensions | Rigid-body static model, assumes boom CG at arm midpoint and crane column/base represented in base mass; side case SF~1.253 **fails** target 1.5 |
| Uphill rear tipping | \`MO=(mg sinθ + ma) hCG\`, \`MR=mg cosθ dR\` | Dimensionally correct for rigid vehicle and uphill acceleration | This slope driving case does not simultaneously include a suspended load swinging on the crane; use actual driving configuration and combined CG |
| Worst-case scan | 181 angles [-90..+90] × four directions = 724 directional evaluations | Complete at 1° angular resolution | Not a continuum guarantee between angles; shock, side slopes and obstacle crossings not modeled |
| What-if | \`m_total=m_base+m_boom+m_payload\` propagated into torque/battery/stability; winch payload link optional | V53.8.75 fixes stale initial baseline vs post-restore scenario | The 3h battery capacity can drop if operation slows and **fewer complete cycles** are performed. Compare Wh/round and job count separately |

## Outstanding findings, with severity

1. **HIGH — invalid manual mass decomposition not rejected.** Desktop/Web stability use \`m_vehicle=max(0,m_total-m_payload-m_boom)\`. If an input has \`m_total < m_payload+m_boom\`, the modeled force sum no longer equals the claimed total, and results must not be treated as valid. Prevent saving/reporting a PASS until corrected. This is not yet fully guarded.
2. **HIGH — boundary of 3-hour energy model.** Drive energy is counted only for **completed** integer cycles while auxiliary energy covers all 3h. If vehicle continues moving for the final partial cycle, the drive energy in that interval is omitted. In particular, a planned full route that exceeds the whole runtime results in zero completed rounds and zero estimated traction energy. For guaranteed 3h driving sizing, count an explicit partial last cycle or use a conservative extra cycle; current approximation must be labeled clearly.
3. **HIGH — statics-only SF must not certify lifting without outriggers.** \`SF=∞\` means no gravity overturning moment **in that specific case**, not infinite real safety. The 1.5 threshold is preliminary. Shock, basket motion, tire/suspension flexibility, frame deflection and the side-slope/diagonal directions need independent assessment.
4. **MEDIUM — boom CG and mass model.** \`m_B\` is represented at \`L/2\`, correct only if the boom's CG is near its midpoint. Separate actual column, slew unit, winch and boom component CGs before final design; in basic Mode A the base vehicle CG defaults to chassis center.
5. **MEDIUM — rope layers and performance.** Speed/current interpolation is made using first-layer table data regardless of rope layer. The app warns but does not calculate corrected multi-layer speed/current. Check line-pull capacity for the ending layer and validate with vendor.
6. **MEDIUM — changing dimensions without redesign.** Track/length changes do not automatically determine mass, structural stiffness or new CG; users must provide resulting data.
7. **MEDIUM — 19° design vs measured slope.** 55/280 cm implies ~11.11°, while 19° is a separate steeper design case. Do not substitute one for the other; conservatively assess both if relevant.
8. **MEDIUM — downhill braking and electronic loads.** No regen is credited; zero downhill **traction** energy is possible on a steep descent, but real control/braking electronics and crane rotation require power-budget inclusion or measurement.
9. **MEDIUM — battery surge and thermal sizing.** Manufacturer winch first-layer 140 A table value is NOT a confirmed starting/stall surge; do not interpret continuous/peak BMS checks as certification.

## Engineering priority before fabrication
- Confirm **300 kg mass budget** with individual component masses and actual CGs. A 100→200 kg what-if increases total from 300→400 kg when other parts are held fixed, violating the target even if the software can explore it.
- Compare 19° and measured ~11.11° driving/slip/tip conditions separately and use actual center-to-center wheel track, wheelbase, tire diameter.
- Check all four lift directions with the crane and payload actually positioned at the measured loading points. Side static SF below 1.5 is a design failure.
- Measure winch current/speed including real layer, voltage sag, and startup; record actual BMS peak/current capability.
- Validate critical results using both desktop and web and export the line-by-line substituted-value reports.

## Status definitions
- **Equation reviewed** = static independent mathematical inspection completed.
- **Invariant test written** = assertions added to \`tests/formula_audit.py\`.
- **Test passed** = only after the GitHub Actions run is green. This report does not claim CI passed before results are inspected.
- **Certified design** = NOT achieved; requires physical measurements, structural checks, suitable safety standards and faculty/supervisor review.
