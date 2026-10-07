# Crane Vehicle Engineering Tool V53.8.37

## Desktop Save Values ↔ Web Project Sync

### 1. Desktop is the Web source of truth
The Web interface can now load the latest saved Desktop project values from the same Windows user account.

The Web Server checks the newest valid Desktop Save Values from:
- Desktop AppData last_values.json
- Documents/CVET_Data/saved_values_backup.json
- OneDrive Documents/CVET_Data backup when applicable

The Web never exposes the full local path; it only reports the source type, saved time, and Desktop version.

### 2. New sticky “Sync Desktop” button
A visible **↻ Sync Desktop** control is added to the Web navigation.

It imports current Desktop values into:
- Drive Torque
- Ramp Geometry
- Main Battery 72 V
- Winch / Operating Cycle
- Winch Battery 12 V
- Stability

The Web also attempts one silent Desktop sync when the page first opens. If no Desktop save exists, the existing browser values remain untouched.

### 3. Stability geometry and CG sync
The Stability Web page now receives the same saved Desktop inputs:
- Total mass
- Payload mass
- Boom mass
- Mass mode A / B
- Track width W
- Wheelbase WB
- Boom length L
- Crane angle θ
- Dynamic factor
- Required SF
- Crane base position x_C from rear axle
- Base vehicle CG x / y
- Combined driving CG height
- Combined driving CG distance from rear axle
- Slope angle
- Slope acceleration
- Component Mass & CG table

For slope stability, Web combined_cg_from_rear_m is derived from the Desktop driveXCG and wheelbase using:
combined_cg_from_rear = driveXCG + WB/2

### 4. Other module values also sync
Drive Torque:
- effective mass source
- wheel diameter
- slope
- speed
- acceleration time
- Crr
- motor count
- rated motor power
- Safety Factor
- efficiency
- voltage
- driven-wheel load fraction
- traction coefficient

Main Battery:
- effective mass source
- voltage, speed, route, slope
- runtime
- Crr, efficiency, auxiliary power
- DoD, reserve, Kb
- Differential/Pivot settings
- Battery selection and BMS candidate inputs

Winch:
- load and lift height
- operating speed/distance/time
- lift events per round
- DOWN mode and measured/custom values
- 12 V battery design inputs and BMS candidate

### 5. Automatic recalculation after sync
After importing Desktop values, the Web automatically recalculates in a safe sequence:
Ramp → Drive → Winch → Winch Battery → Main Battery → Stability.

This ensures Winch UP/DOWN time is refreshed before Main Battery uses it for cycle-time calculation.

### 6. Regression coverage
The release test now creates a real Desktop-style project JSON and verifies that the Web API maps:
- W, WB, x_C, L
- mass / payload / boom
- CG values
- slope
- Winch values
- Main Battery / BMS values
- Component Mass rows

The existing Desktop ↔ Web numerical parity tests remain enabled.
