# Crane Vehicle Engineering Tool V53.8.41

## Full Web Calculation Audit Fixes

This release follows a complete formula and UI audit of:
Drive Torque, Ramp Geometry, Main Battery 72 V, Winch, Winch Battery 12 V,
Side Left/Right, Front/Rear, Slope Stability, Component Mass mode, and Desktop↔Web parity.

### 1. Drive Torque — Motor rated power is now actually checked
Previously the Web form accepted “Motor rated power / motor” but the calculation engine did not use it.

Now the engine calculates:
- Required mechanical design power / motor
- Entered rated power / motor
- Power margin = Rated / Required
- PASS / FAIL

This is added to both the result card and STEP-BY-STEP calculation.

### 2. Wheel diameter input clarified
The Drive Torque wheel input now explicitly means:

**Effective wheel outside / rolling diameter**

It is not the rim number printed in a tire size.
Example: for 3.0-10, “10” refers to the rim size; it must not automatically be used as a 10-inch rolling diameter.

New-project Desktop default is changed from 10 in to 16 in, and the field includes a warning tooltip.
Existing saved user values are not silently overwritten.

### 3. Main Battery — Auxiliary energy now covers the full requested runtime
Previously Auxiliary energy in forward sizing was multiplied only by completed integer Cycles.
That omitted the final fractional time after the last full Cycle.

Now:
- Drive energy = E_drive,cycle × completed Cycles
- Auxiliary energy = P_aux × requested runtime
- E_total = E_drive,total + E_aux,total

Therefore a 50 W Auxiliary load over 3 h contributes exactly 150 Wh,
even when the route finishes with unused time after the last full Cycle.

Per-Cycle Auxiliary energy is still shown for teaching/explanation purposes.

### 4. Main Battery / BMS current now includes Auxiliary current
Auxiliary is supplied by the 72 V vehicle battery, so simultaneous current must be included.

Now:
- I_aux = P_aux / V
- Continuous = max(I_uphill, I_pivot) + I_aux
- Peak = max(Continuous, Drive Torque design reference + I_aux)

Desktop and Web use the same rule.

### 5. Winch — Rope-layer limitation is now explicit
The supplied datasheet provides speed/current performance for First Layer.

When lift distance reaches Layer > 1:
- Line-pull limit is still checked using the layer table
- Speed/current remain based on First-Layer interpolation because no layer-specific speed/current table was supplied
- Web and Desktop now show a visible warning instead of silently implying layer-corrected performance

No unsupported correction factor is invented.

### 6. Stability — M_O = 0 is no longer presented as “infinite real safety”
The internal mathematical sentinel remains available for comparison logic,
but the user-facing FBD now shows:

**N/A (M_O = 0)**

when no overturning moment exists in that direction.

For a Critical Case with no overturning anywhere in the allowed crane range -90°…+90°:
- angle = N/A
- no_overturning_in_range = true
- the UI states that no overturning was found in the permitted range

This is especially relevant to Rear tipping when the boom cannot rotate behind the rear tipping axis.

### 7. Component Mass mode wording clarified
For Side/Front/Rear lifting stability:
- Boom/Payload position is derived from crane geometry x_C, L, and θ

The x/y values entered in the Component Mass table are primarily used for the combined CG / travel-slope configuration.
The Web now states this explicitly to avoid double interpretation of Boom/Payload location.

### 8. Battery report formulas corrected everywhere
Desktop report/STEP text now matches the corrected full-runtime Auxiliary model.

Old displayed wording:
E_total = E_cycle × N_cycle

New displayed wording:
E_total = E_drive,cycle × N_cycle + P_aux × t_runtime

The numerical result, variable table, STEP-BY-STEP report, and simple explanation now use the same definition.

### 9. Regression coverage expanded
The release build now verifies:
- Motor rated-power PASS/FAIL fields exist and are numerically valid
- 50 W Auxiliary × 3 h = 150 Wh
- I_aux = 50/72 A
- Continuous current includes I_aux
- Winch Layer > 1 generates a First-Layer-performance warning
- Rear no-overturning Critical Case returns angle=None and no_overturning_in_range=True
- Stability directional case remains:
  Side Right Critical M_O ≈ 774.99 N·m
  M_R ≈ 971.19 N·m
  SF ≈ 1.253
- Desktop↔Web numerical parity remains enabled

### Unchanged because already correct
The audit confirmed these calculations did not need formula changes:
- Ramp geometry: Pythagoras, atan(h/x), Slope %
- Winch 64 jobs vs 128 winch movements
- Winch Battery: one job = UP + DOWN
- Side Left/Right moment balance
- Front/Rear tipping-axis logic
- Uphill Slope Stability quasi-static model
- Differential/Pivot preliminary energy model (still explicitly empirical)
- No regenerative-energy credit in the simple Main Battery model
