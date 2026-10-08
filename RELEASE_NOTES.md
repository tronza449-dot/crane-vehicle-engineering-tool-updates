# Crane Vehicle Engineering Tool V53.8.49

## Input Source indicators + Engineering Scenario Presets

This release implements two usability improvements across Desktop and Web.

### 1. Input Source / ที่มาของค่า
The program now shows where important engineering inputs come from instead of leaving the user to infer the relationship.

Source states include:
- **MANUAL** — value entered directly by the user.
- **AUTO** — value derived automatically, such as wheel radius from Effective wheel OD.
- **LINKED** — value linked from another module or shared project parameter.
- **FROM COMPONENT** — mass or CG derived from the Component Mass / Mass_CG table.
- **FROM WINCH** — timing or event data supplied by the Winch operating-cycle model.
- **FROM DATASHEET** — value derived from the supplied winch datasheet, including interpolation.

Desktop source panels are shown on the Torque, Main Battery, Stability, Ramp/Slope, Winch and Winch Battery inputs.
Web source badges are attached directly to important input fields and update with Stability mass mode.

### 2. Engineering Scenario Presets
The old demonstration presets are replaced with design-oriented presets:
- Payload 0 kg
- Payload 50 kg
- Payload 100 kg
- Track W = 0.70 m
- Track W = 1.00 m
- Boom L = 1.20 m
- Boom L = 1.50 m
- Slope = 19°
- Project Target: Payload 100 kg + L 1.20 m + Slope 19°

### Preset propagation rules
Payload presets preserve the existing non-payload vehicle mass:
**new total mass = current total mass − current payload + new payload**

The resulting Total mass is synchronized to Stability, Drive Torque, Main Battery and Ramp mass inputs.
Payload presets also synchronize the Winch load.

Slope 19° is synchronized to Torque, Main Battery and Stability.

Track presets change Track W only. They do not invent an increase in frame mass.

Boom-length presets change L only. They intentionally keep Boom mass unchanged because a new Boom mass requires real section/material information.

In Component Mass Mode, payload presets are blocked rather than silently rewriting the Component table or inventing CG distribution.

### Before / After comparison
Desktop and Web presets can automatically capture:
- Design A = Before preset
- Design B = After preset

This reuses the existing engineering comparison tools so the effect on Torque, Battery, Winch and Stability can be reviewed numerically.

### Regression
The release audit verifies:
- all Desktop source indicators exist,
- Linked/Manual/Component/Datasheet/Winch source states,
- all nine presets,
- Payload 100→50 kg causes Total mass 300→250 kg in the controlled regression case,
- Drive/Battery/Ramp masses follow the new total,
- Winch load follows the payload preset,
- Boom L = 1.50 m does not change Boom mass,
- Slope 19° reaches Torque + Main Battery + Stability,
- Track W = 0.70 m applies correctly,
- the Web preset and source-badge controls/functions are present,
- existing calculation, PDF, Save/Restore, updater and Desktop↔Web regression remain enabled.
