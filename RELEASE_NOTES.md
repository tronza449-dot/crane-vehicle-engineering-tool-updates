# Crane Vehicle Engineering Tool V53.8.34

## Save Every Module + FBD Figure Variable Legend

### 1. Save Values now covers more UI state
The desktop Save Values / Auto Save system has been expanded so project state is captured more completely across modules.

New generic persistence coverage:
- QSlider values
- Checkable QPushButton mode cards
- Existing SpinBox / DoubleSpinBox
- ComboBox
- CheckBox / RadioButton
- LineEdit
- Mass & CG component table
- Hardware I/O rows
- Device Library / Validation / BOM integration tables
- Design Revision data

The explicit Save Values verification now checks all saved sections:
- widgets
- components
- hardware
- integration

Both persistent copies are still written:
- AppData/last_values.json
- Documents/CVET_Data/saved_values_backup.json

### 2. Autosave consistency fixes
Fixed stale autosave-timer references used by Design Revision and custom Hardware I/O row changes.

This prevents those edits from being missed by the current autosave system.

### 3. FBD variable table beside every report figure
Stability reports now show a bilingual table next to the FBD image titled:

**ตัวแปรในรูป / Figure Variable Legend**

Side / Front / Rear FBD pages explain:
- P — tipping axis
- CG_V / CG_B / CG_L
- W_V / W_B / W_L
- R_P and R_opposite = 0
- d_V / d_B / d_L
- M_O
- M_R
- SF

Slope FBD pages explain:
- P
- N_R
- N_F = 0
- W_parallel
- W_normal
- F_I = ma
- d_R
- h_CG
- M_O / M_R / SF

Geometry pages explain:
- W
- WB
- L
- θ
- x_C
- CG_V
- CG_B
- CG_L

The legend is used in:
- Full Stability Engineering PDF
- Easy Stability report pages
- Formal FBD report pages
- Export Selected Stability Mode PDF

### 4. Regression coverage
Release tests now verify:
- Slider state is saved and restored
- Checkable mode buttons are serialized
- Primary and backup Save Values copies match for widgets/components/hardware/integration
- FBD HTML contains the new figure-variable legend
- Side/Front/Rear symbols are present
- Slope symbols are present
- All FBD PNG images are still generated
