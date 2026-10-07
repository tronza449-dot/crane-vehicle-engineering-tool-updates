# Crane Vehicle Engineering Tool V53.8.48

## Simpler What-if redesign

This release keeps the coupled engineering calculation model from V53.8.47 but redesigns the user experience so What-if is much easier to understand and use.

### New default workflow
The main What-if page now asks only:
1. What do you want to change?
2. What new value do you want to try?
3. View the system impact.

Available quick choices:
- Payload
- Track width W
- Boom length L
- Crane base position x_C
- Slope
- Operation speed
- Winch lift distance

### Result-first layout
The first result table now shows only the most useful before/after outputs:
- Torque per motor
- Main Battery
- Winch Battery
- Worst Stability SF
- Governing / critical case

The full engineering input/output comparison is still available under a details section.

### Advanced mode
All coupled scenario inputs are still available for users who want to change several values at once, but they are hidden by default under:
**ค่าขั้นสูง / ปรับหลายค่าพร้อมกัน**

### Coupled calculation model retained
The simpler UI does not remove system relationships.
Derived mass, Torque, Main Battery, Winch cycle and Stability continue to recalculate from the same coupled scenario engine.

The program still intentionally does not invent structural relationships that require real design data, such as:
- additional frame mass caused by a wider W/WB,
- Boom mass caused by a longer L,
- CG movement without actual component positions.

### Desktop and Web
The simplified guided What-if workflow is implemented in both Desktop and Web.

### Regression
Regression now checks:
- the simplified What-if tab and controls exist,
- quick Payload editing updates the coupled Payload field,
- reducing Payload reduces derived Total mass,
- the result-first summary includes Torque, Main Battery, Winch Battery, Stability SF and the governing case.
