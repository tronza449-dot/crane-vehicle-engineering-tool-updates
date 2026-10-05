# FBD Rebuild Specification — Crane Vehicle Engineering Tool

## Purpose

This document is the drawing contract for Stability Free-Body Diagrams (FBDs).
The FBD must explain the exact moment-balance calculation visually. It is not a decorative vehicle drawing.

## A. Engineering drawing requirements

### 1. Geometry page and FBD pages are different
- Top View is only for track width, wheelbase, crane slew angle and tipping-axis geometry.
- Gravity-force FBDs use Front Elevation or Side Elevation.
- Never use the Top View as the gravity-force FBD.

### 2. Force line of action
Every force must originate from, or be visually tied to, its physical application point:
- W_V through CG_V.
- W_B through CG_B.
- W_L through CG_L / payload point.
- R_P at the selected tipping support.
- Opposite support reaction is labelled R_opposite = 0 at impending tipping.

Do not clamp a physical load coordinate back inside the chassis for drawing convenience.
If a payload lies outside the support polygon, the diagram must show it outside the support polygon.

### 3. Tipping axis / pivot
- P is the selected wheel-contact tipping axis.
- P and R_P labels must not overlap each other or the wheel graphic.
- Tipping direction must be labelled as Overturning Side and Resisting Side.

### 4. Moment arms
For every Vehicle / Boom / Payload load:
- Draw the vertical line of action.
- Project that line to a dedicated dimension lane.
- Draw the perpendicular arm from P to that line.
- Label d_V, d_B, d_L with the numeric value used by the calculation.
- Red arm = overturning contribution.
- Green arm = resisting contribution.

The picture must allow the reader to verify M = F d without using the result table.

### 5. Side tipping
Use Front Elevation.
The crane front-elevation projection must visually connect:
vehicle / column -> boom -> payload.
LEFT and RIGHT cases are mirrored by the actual physical coordinates, not by moving labels only.

### 6. Front / Rear tipping
Use Side Elevation.
Show:
- rear and front wheel contacts,
- crane column and projected boom,
- CG_V, CG_B, CG_L,
- pivot P,
- R_P,
- R_opposite = 0,
- d_V, d_B, d_L.

If M_O = 0, state clearly:
"NO OVERTURNING GRAVITY MOMENT in this case: all shown vertical loads remain on the resisting side of P."

### 7. Uphill rear-tipping FBD
Use slope-fixed axes:
- +x_s = uphill.
- +z_s = outward normal from road surface.

At the Combined CG:
- W_parallel = mg sin(alpha), downhill.
- W_normal = mg cos(alpha), into the road surface.
- F_I = ma, opposite uphill acceleration. It is a D'Alembert pseudo-force and must be identified as such.

At the rear pivot:
- N_R points outward normal from the road.
At the front support:
- N_F = 0 at impending rear tip.

Show:
- d_R along the slope from rear pivot to CG projection.
- h_CG normal to the slope.

W_parallel and W_normal are components of W = mg. Do not add W = mg as an additional force.

## B. Generator / report logic

### Critical-case report
Each exported FBD page uses the searched critical angle for that case:
- Side Left critical angle.
- Side Right critical angle.
- Front critical angle.
- Rear critical angle.
- Slope uses the current slope-driving case.

The page heading must state "CRITICAL CASE".

### Current-angle appendix
The Variables / Equations / Substitution appendix uses the current input crane angle.
It must be labelled "CURRENT-ANGLE SNAPSHOT".
The report must explicitly warn that current-angle values and critical-case values must not be mixed unless the angles coincide.

### Calculation source of truth
The FBD renderer must consume the same balance objects used by the numerical calculation:
- side_moment_balance(...)
- longitudinal_moment_balance(...)
- slope_stability_results(...)

No separate drawing-only geometry formula may replace the calculation positions.

## Visual conventions
- Weight forces: black.
- Ground reactions: green.
- Tipping axis / zero opposite reaction: red.
- Overturning moment arms: red.
- Resisting moment arms: green.
- Geometry dimensions: gray.
- Crane structure: orange.
- Vehicle structure: light gray / dark outline.

## Acceptance checklist
A release is acceptable only when:
- No force label overlaps the pivot label.
- No load arrow floats without a CG/load point.
- No load line is artificially clamped into the chassis.
- d_V, d_B, d_L are visible on Side/Front/Rear FBDs.
- N_R on slope points outward from the road.
- W_normal points into the road.
- F_I is identified as D'Alembert / pseudo-force.
- Current-angle appendix is clearly separated from critical-case FBD pages.
- Numerical M_O, M_R and SF remain generated from the same engineering calculation functions.
