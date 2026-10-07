# Crane Vehicle Engineering Tool V53.8.31

## Confirmed Vehicle Width + Centered 250×250 mm Crane Base

### Confirmed project geometry
- Vehicle width = 1.00 m
- Crane base = 0.25 × 0.25 m
- Crane base is centered left-right
- Crane lateral center y_C = 0.00 m
- Side clearance = (1.00 - 0.25)/2 = 0.375 m = 375 mm per side

### Important distinction
- Vehicle width = actual frame/body width
- Wheel track W = center-to-center distance of left/right wheels
- These are separate values and are no longer presented as the same dimension

### Desktop Stability
- Added a green geometry summary card
- Wheel track label explicitly says it is not vehicle width
- Crane x from rear axle now states sign convention:
  - + = toward vehicle front
  - - = toward vehicle tail
- x_C remains user/measured input because rear-axle-to-tail distance is not yet confirmed
- Stability variable table and formal summary now include:
  - VehicleWidth
  - CraneBaseW / CraneBaseL
  - y_C
  - side clearance

### 3D Crane View
- Vehicle body is now drawn using the confirmed 1.00 m body width
- Wheels remain positioned by Wheel track W
- Crane base is drawn as 0.25 × 0.25 m instead of the previous generic 0.38 × 0.38 m block
- Crane pivot remains centered laterally at y_C = 0
- Live Data panel shows Vehicle width, Wheel track and Crane base separately

### Web
- Stability Geometry section shows the confirmed 1.00 m / 0.25 × 0.25 m dimensions
- Shows 375 mm clearance each side
- Wheel track label is explicitly center-to-center
- x_C label shows +front / -tail convention
- Vehicle Parameters now includes Crane Base = 250 × 250 mm

### Note
The longitudinal crane location x_C is intentionally not auto-calculated yet because the actual rear-axle-to-tail distance has not been confirmed.
