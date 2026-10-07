# Crane Vehicle Engineering Tool V53.8.36

## Web Step-by-Step Every Calculation Mode + Desktop/Web Parity Audit

### 1. Step-by-step calculation on every Web calculation mode
The Web UI now adds a consistent engineering sequence:
- STEP title
- Formula
- Substitution using the current inputs
- Result with unit
- Meaning / design check

Covered calculation modes:
- Drive Torque
- Ramp Geometry
- Main Battery 72 V
- Winch / Operating Cycle
- Winch Battery 12 V
- Stability: Side Left, Side Right, Front, Rear, and Slope in Current/Critical views

### 2. Desktop is the calculation reference
Regression now directly compares Desktop calculations against the Web Engine using the same input values.

Parity checks include:
- Drive force, torque, battery current and traction limit
- Ramp length, angle, slope percentage and slope force
- Winch interpolation, UP time, operating rounds, lift count and 12 V battery energy
- Main Battery cycle time, Wh/Cycle, total energy, Ah, Continuous/Peak current and suggested battery size
- Stability Left / Right / Front / Rear moment balance

The release build fails if Desktop and Web calculations drift apart.

### 3. Transparent substitutions
Web Engine responses now expose the values needed for readable substitutions:
- Rolling coefficient
- Safety factor
- Voltage
- Drive efficiency
- Traction coefficient / driven-load fraction
- DoD / Reserve
- Auxiliary power

### 4. Stability Step-by-Step
The existing Web Engineering FBD remains Step-by-Step by selected case.
The interface now explicitly identifies that all five Stability modes have their own calculation steps.

### 5. Browser cache
Static asset cache tags were bumped so an updated Web Server does not keep the previous calculation interface in the browser.
