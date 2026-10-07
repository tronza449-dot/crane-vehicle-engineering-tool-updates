# Crane Vehicle Engineering Tool V53.8.44

## Engineering Decision Tools

**V53.8.44 final package:** includes all V53.8.42 decision tools plus hardened Desktop Final Design Lock mutation guards.

This release implements the requested items 2, 3, 5, 6 and 7:
Sensitivity Analysis, Worst-Case Summary, Calculation Trace, Final Design Input Lock,
and Compare Design Revision.

### 1. Sensitivity / What-if Analysis
Desktop Project Tools now includes a **Sensitivity / What-if** tab.

It evaluates these design variables around the current design:
- Track width W
- Boom length L
- Payload mass
- Crane base position x_C from rear axle
- Vehicle CG x

Default range is ±20% and can be changed from 5% to 50%.

For every sample point the tool reuses the same Stability moment equations and performs
the same -90°…+90° critical-angle scan used by the main Stability module.

The result table reports:
- tested value
- governing tipping direction
- worst SF
- PASS / FAIL

The Web Project Summary now has the same Sensitivity / What-if tool.

### 2. Engineering Worst-Case Summary
A new Desktop **Engineering Summary** tab and Web **Engineering Worst-Case Summary**
combine the main design checks into one view:

Drive:
- required torque per motor
- rated motor power check
- traction margin

Main Battery 72 V:
- calculated minimum Ah
- practical Ah
- total modeled load energy
- completed route cycles

Winch 12 V:
- battery Ah
- lift time
- number of jobs

Stability:
- Side Left critical SF
- Side Right critical SF
- Front critical SF
- Rear critical SF / no-overturning indication
- Slope SF
- governing lifting case
- overall governing stability including Slope

### 3. Calculation Trace
Desktop Project Tools now includes a **Calculation Trace** tab.
Web Project Summary includes the same feature.

Trace format:
Input → Formula → Substitute → Result → PASS/FAIL

Modules:
- ALL
- Drive Torque
- Ramp Geometry
- Main Battery
- Winch
- Stability

The Web reuses the existing audited Step-by-Step renderers instead of creating a second
formula implementation.

### 4. Final Design Input Lock
Desktop Project Tools now has a persistent:
**🔒 Design Inputs Locked / 🔓 Design Inputs Unlocked**

The lock protects core design values from accidental editing:
- total / payload / boom mass
- manual Torque / Battery / Ramp mass inputs
- Winch load
- Effective wheel OD
- W
- WB
- L
- x_C
- vehicle CG
- slope and slope geometry inputs
- mass-source selector controls

The lock state is included in Save Values / Project state.

Web has the same Final Design Input Lock.
Locked Web inputs remain part of FormData calculations but are not editable by pointer/keyboard.
Desktop Sync is blocked while the Web design lock is active so a locked final design cannot
be silently overwritten.

Desktop lock hardening:
- Open Project File is blocked while Final Lock is active
- Apply Scenario Preset is blocked while Final Lock is active
- Apply saved Design Revision is blocked while Final Lock is active
- Apply Project Tools Design A/B is blocked while Final Lock is active
- Comparison calculations may still read revisions internally, but the current locked design is restored afterward

### 5. Compare Design Revision upgraded
The existing Design Revision Manager is retained and upgraded.

Comparing two saved revisions now shows both:
1. Input Revision Diff
2. Engineering Output Diff

Engineering outputs include:
- required torque
- motor power
- Main Battery Ah
- Winch Battery Ah
- Side / Front / Rear SF
- Worst SF and angle

The older Project Tools Design A / Design B comparison remains available.

Web Project Summary now supports:
- Capture Design A
- Capture Design B
- Compare A ↔ B

Each captured Web revision stores both input values and calculated engineering metrics.
The comparison now contains both **Input Revision Diff** and **Engineering Output Diff**,
including Ramp inputs as part of the captured design snapshot.

### 6. No duplicate calculation engine
These tools intentionally reuse the existing audited calculation functions.
They do not introduce separate Stability, Torque, Battery or Winch equations.

### 7. Regression coverage
The release regression now verifies:
- Desktop Engineering Summary tab exists and renders
- Sensitivity tables exist for all requested parameters
- Calculation Trace contains Drive, Ramp, Main Battery, Winch and Stability modules
- Design Lock disables and restores the core Desktop inputs
- Design Revision comparison contains Engineering Output Diff
- all new Web controls and functions exist
- all previous calculation, PDF, Save/Restore, Desktop↔Web parity and updater regressions remain enabled
