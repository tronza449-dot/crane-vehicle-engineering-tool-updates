# Crane Vehicle Engineering Tool V53.8.32

## Winch Linear Interpolation — Show Full Calculation

### Why this update
The Winch calculator previously showed the interpolated result only, for example:
- Speed ≈ 3.124 m/min
- Current ≈ 22.57 A

This release now shows exactly how those values are obtained from the supplied 4500LB First Layer datasheet.

### Desktop
Added a visible LINEAR INTERPOLATION calculation section on the Winch Spec / Datasheet page.

For the current Load, the program now shows:
1. The two datasheet rows used
2. Interpolation fraction
3. Speed interpolation
4. Current interpolation
5. The resulting Speed and Current that are passed to later calculations

Example for 100 kg:
- Datasheet interval: 0 kg → 454 kg
- v1 = 3.3 m/min, v2 = 2.5 m/min
- I1 = 12 A, I2 = 60 A
- r = (100 - 0) / (454 - 0) = 0.220264
- v = 3.3 + r(2.5 - 3.3) = 3.124 m/min
- I = 12 + r(60 - 12) = 22.57 A

The section also explains:
- interpolated speed is used to calculate UP time
- interpolated current is used in Winch Battery Wh calculations

### PDF / Report
The exported Winch PDF now includes the full interpolation derivation before the operating-cycle and battery calculations.

### Web
The Winch result now shows:
- First Layer interval used
- STEP 1 interpolation ratio
- STEP 2 line-speed interpolation
- STEP 3 motor-current interpolation
- substituted values and final units

### Calculation source
The interpolation remains based only on the supplied First Layer table:
- 0 kg: 3.3 m/min, 12 A
- 454 kg: 2.5 m/min, 60 A
- 907 kg: 1.1 m/min, 100 A
- 2041 kg: 0.8 m/min, 140 A

No new performance values were invented.

### Regression
Added tests for the 100 kg case:
- r = 100/454
- Speed = 3.3 + r(2.5 - 3.3)
- Current = 12 + r(60 - 12)
- Desktop visible interpolation section
- PDF interpolation section
- Web interpolation fields and formula rendering
