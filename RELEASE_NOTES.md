# Crane Vehicle Engineering Tool V53.8.35

## Readable FBD Legend + Visible Save Buttons on T / B / W / S

### 1. Stability PDF legend redesigned
The V53.8.34 side-by-side FBD legend was too narrow on A4 and caused words and values to wrap vertically across multiple pages.

V53.8.35 changes the report layout to:
- Large FBD figure first
- Full-width variable legend directly below the figure
- Wider fixed table columns
- Shorter Thai-first bilingual descriptions
- Current value and unit kept in a dedicated wide column

The old 62% figure / 38% legend side-by-side layout has been removed.

The compact legend now uses readable symbols such as:
- P
- CG_V/B/L
- W_V/B/L
- R_P
- R_opp
- d_V/B/L
- M_O / M_R
- SF

Slope legend uses:
- P
- N_R
- N_F
- W∥
- W⊥
- F_I
- d_R
- h_CG
- M_O / M_R / SF

### 2. Visible Save Values on T / B / W / S
Added a large visible Save Values bar directly at the top of:
- T — Drive Torque
- B — Main Battery 72 V
- W — Winch
- S — Stability

Each button saves the complete current project state, including the values on the current page, to both:
- AppData/last_values.json
- Documents/CVET_Data/saved_values_backup.json

The save-status label on each T/B/W/S module updates after a successful save.

### 3. Winch save button stays visible
The Winch Save Values bar is outside the Winch sub-tabs, so it stays visible when switching between:
- Spec / Datasheet
- Operating Cycles
- Battery
- Summary

### 4. Regression checks
Release tests now verify:
- All four T/B/W/S Save Values buttons exist
- Winch save remains visible across every W sub-tab
- All module save-status labels update after saving
- The old narrow side-by-side FBD layout is absent
- FBD image width and full-width legend structure are present
- All existing Stability FBD PNG/PDF generation still passes
