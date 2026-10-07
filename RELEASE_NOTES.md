# Crane Vehicle Engineering Tool V53.8.33

## Easier Stability Report + Durable Save Values

### 1. Stability PDF redesigned for easier reading
The main Stability report is now presentation-first instead of table-first.

Each critical case now follows the same reading flow:
1. What is being checked
2. Where the tipping axis P is
3. Force calculation
4. Moment-arm calculation showing where each d⊥ value comes from
5. Overturning moment M_O
6. Resisting moment M_R
7. Safety Factor and a large PASS / FAIL result

Moment-arm values are no longer shown as unexplained numbers. Example format:
- d_V = |y_V - y_P| = |0.000 - (-0.550)| = 0.550 m
- The report explicitly states whether that force contributes to M_O or M_R
- It explicitly explains that d⊥ is the distance from the force line to the tipping axis, not the crane boom length

The detailed engineering tables and full substitution pages are moved to:
- Appendix A — Detailed Engineering Calculation
- Appendix B — Other Figures

### 2. Save Values button
Added a visible Save Values control:
- On the Stability input page
- In the global bottom status bar so it is available from every module

Button behavior:
- "กำลังบันทึก..." while saving
- Green "บันทึกแล้ว ✓" / "เซฟแล้ว ✓" when complete

### 3. More durable persistence
Current project values are now written to two locations:
- Primary AppData autosave: last_values.json
- Backup copy: Documents/CVET_Data/saved_values_backup.json

On startup the program restores the newest valid copy and repairs the other copy automatically.

### 4. Autosave bug fixes
Previously, some state could change without triggering autosave.

Fixed autosave coverage for:
- Mode A / Mode B selection
- Mass_CG component-table edits
- Device/BOM/validation table edits
- Existing SpinBox / ComboBox / CheckBox / LineEdit inputs remain covered

Save state includes:
- All normal input widgets
- Hidden mass-mode state
- Component Mass & CG table
- Hardware I/O rows
- Integration tables and revisions

### 5. Mode A wording
Updated the Stability card text to match the current workflow:
- Mode A now says Total Mass + Payload + Boom + Geometry
- It no longer says the user must enter CG manually

### Regression coverage
The release test now verifies:
- Save to both primary and backup files
- Change values after save
- Restore saved values correctly
- Component table values restore correctly
- Mode A/B changes schedule autosave
- Easy Stability report contains the moment-arm derivation and simplified case flow
- All five FBD images are still generated
- Full PDF export still succeeds
