## V53.8.80 — 72V battery purchasing current envelope (keep the original 3h Wh/Ah calculations)

- Preserve the original 30 m out-and-back, two lifting jobs per round, completed-round energy Wh/Ah, DoD, reserve and Kb unchanged.
- New **Battery Selection / Current Design Envelope** controls: battery minimum loaded voltage (default 60 V), rated-power efficiency (default 85%), continuous-current design margin (default 25%) and optional combined VESC Battery Current Max (0 = not configured).
- Show current separately: existing Operating Current, rated-power reference from `motor rated W × motor count / (efficiency × min voltage)`, and higher **Design Continuous** with user-defined margin. Include simultaneous 72 V auxiliary load in rated reference.
- Use Design Continuous for BMS continuous sizing and capacity/C-rate checks; rounded to the next 10 A for a comparison reference. Do not recommend 5 A / 10 A from low-speed operating alone.
- **Never mark Peak validated** from the simple drive model or unconfigured VESC alone. Peak current is a modeled floor only; mark CHECK until VESC Battery Current Max and pack/cell starting/transient ratings are confirmed.
- Align Windows Battery Selection, integrated BMS checks, exported Thai Battery PDF STEP 6 and web calculator purchase inputs/results; do not alter motor controller's actual settings.
- Add release smoke regression for design current increasing as minimum battery voltage decreases while Wh/Ah remain unchanged, plus desktop ↔ web parity regression.
- Rated motor wattage might be an electrical-input nameplate rating rather than delivered mechanical output; the configurable efficiency adjustment should be treated as a conservative assumption until supplier documents are verified.

## V53.8.79 — Rewrite Battery Report STEP 6 for clear Thai engineering explanations

- Redesign **STEP 6** with five short sections: (6.1) A versus Ah, (6.2) meanings and source values of I_up/I_turn/I_drive,design/I_aux, (6.3) Continuous current, (6.4) modeled Peak current, and (6.5) why the reported BMS current is rounded to 5 A / 10 A in the example.
- Fully spell out formulas and their Thai readings, substituted numeric values, and the auxiliary load equation I_aux = P_aux/V. Clarify that max(Drive uphill, Turn) is not the sum of two exclusive scenarios, while auxiliary is simultaneous.
- Emphasize that the modeled **5 A continuous / 10 A peak are not final purchase recommendations** for actual high-power motors, controllers and startup surges.
- Explain STEP 5 DoD 80% and Reserve 20% in simple Thai, retaining its original energy formula and complete-cycle accounting.
- Start STEP 6 on a fresh report page and avoid ambiguous compressed formulas.
- Add release smoke assertions for the five Thai sections, numeric 5 A rounding, **physical PDF export**, and A4 page render artifacts under the GitHub Actions smoke log.
- **No change** to energy, 3h cycle, peak/continuous arithmetic, battery capacity or design safety assumptions.

## V53.8.78 — Battery PDF report: Thai Step 5 reading and corrected Step 6 BMS substitutions

- STEP 5: Replace a vague description with the literal Thai reading of `E_total = E_drive,cycle × N_cycle + P_aux × t_runtime` and explain the meaning of complete round trips versus auxiliary power for all runtime hours.
- Use HTML subscript notation for Step 5–6 formulas so exported PDF symbols are easier to read.
- STEP 6: Correct the displayed BMS Continuous and Peak formulas to explicitly include `I_aux`. Previous report could incorrectly show `max(4.02,0) = 4.71 A` and `max(4.71,4.37) = 5.06 A` despite calculations having added auxiliary current.
- Add a short warning that modeled peak is not a measured starting/stall transient.
- **No calculation policy or battery-cycle counting changes**; this is a PDF presentation/formula traceability fix.
- Add a release smoke regression for Thai Step 5 and exact Step 6 numeric substitutions.

## V53.8.77 — Fix inconsistent BMS current checks found during formula audit

- Main 72 V BMS Continuous and modeled Peak checks now use the **same reference** as Battery Selection, including simultaneously active auxiliary current.
- Remove the incorrect equation that treated the VESC controller phase/motor current-limit indicator as measured DC battery peak current.
- The winch 12 V BMS startup/stall Peak status now stays **CHECK**, never PASS based only on the manufacturer's 140 A loaded first-layer table entry.
- The Integrated Design Check shows the unresolved winch starting/stall peak requirement and uses exactly the same battery current references as Battery Selection.
- Add a release-blocking desktop test to compare BMS required amps across panels and check the unverified stall Peak status.
- The independent overall formula audit remains at `docs/ENGINEERING_FORMULA_AUDIT_2026-10-11.md`.

## V53.8.76 — Independent formula audit and release-blocking engineering invariants

- Independently review formulas across ramp, traction torque/power, 72 V battery, winch and 12 V battery, front/rear/side/slope stability, and What-if input propagation.
- Add `tests/formula_audit.py`: independent reference calculations, dimensional invariants, torque monotonicity vs mass, speed/current interpolation, completed cycle accounting and tipping moments.
- GitHub Actions now runs the formula audit **before** creating the Windows installer, and blocks release on an assertion failure.
- Full audit and engineering caveats: `docs/ENGINEERING_FORMULA_AUDIT_2026-10-11.md`.
- No silent rewrites of project assumptions or calculation results. Outstanding cases are documented: incomplete final cycle in 3h energy, invalid total-mass decomposition, first-layer winch interpolation and unvalidated dynamics/CGs.

## V53.8.75 — Fix What-if increasing payload incorrectly reducing drive torque

- Fix stale scenario reference: `What-if` was constructed before restored/synced project inputs, so the Baseline could retain the startup slope (e.g. 19°) while the Scenario used the updated real slope. This compared different driving conditions and could incorrectly show lower torque with higher mass.
- Simple What-if now reads the current authoritative project inputs for both columns and changes **only the one selected control**, plus linked Winch load when appropriate. Hidden advanced controls no longer silently alter simple comparisons.
- Enforce mass-link consistency across Torque, Battery and Stability; regression-check 300 → 400 kg with the same slope and settings (torque per motor must increase in the simple model).
- Show Total Mass and Driving Slope in the compact comparison, plus route cycles and driving Wh per cycle so decreases in total Ah caused by fewer completed jobs are understandable.
- Warn when a trial scenario exceeds the project's 300 kg target (comparison is exploratory; not a safety approval).
- Refresh the displayed current What-if value after restoring project data without wiping the user's trial input.

## V53.8.74 — Show fixed 90° mast-to-boom geometry in FBD

- Correct the out-of-plane boom cue in Front/Rear FBD at θ=±90°: the dashed illustrative boom is now perpendicular to the vertical column, instead of incorrectly slanting upward.
- Add a small 90° corner mark in both the main diagram and boom-profile inset.
- The θ angle is horizontal slew rotation, **not boom pitch**. The structural mast-to-boom angle remains fixed at 90°.
- Dashed stub is explicitly marked SCHEMATIC ONLY: x_B, x_L and all force/moment arms remain true orthographic projections and no SF calculation changes.
- Update regression checks for the corrected on-diagram 90° caption and projected boom at θ=0°.

## V53.8.73 — Visible out-of-plane boom on main longitudinal FBD

- Front/Rear FBDs now show a short **dashed orange boom stub** attached to the crane mast when the arm is perpendicular to the side-elevation plane (at ±90°).
- The stub is explicitly labeled `BOOM OUT OF PLANE - SKETCH ONLY`. Its x-offset is purely visual, NOT a force position, geometry dimension or moment arm.
- Keep both `CG_B` and `CG_L` on the real same x-projection at ±90°; their combined gravity arrow and tipping moment calculations remain unchanged.
- At θ=0° the real longitudinal projection is drawn as a solid horizontal boom with separate boom/payload arrows.
- Added release smoke checks for the cue at ±90° and its absence when the boom points forward.

## V53.8.72 — Separate boom mass and payload in front/rear FBD

- Treat `m_B` as the boom/arm mass (20 kg in the reference input), applied at the boom midpoint; `m_L` is the carried load, applied at the hook position.
- Add a clearly labeled boom-profile schematic in the FBD inset with distinct downward weight arrows for arm and payload.
- Keep the true longitudinal x-projection in the main force diagram: when the boom points sideways at ±90°, both weights project onto the same x line and must NOT be drawn at invented longitudinal lever arms.
- Label the mast/base mass as part of the remaining vehicle mass `W_V` under the current lumped-mass model; a separate actual mast/base mass and CG input is not yet introduced.
- Fix rear overturning/resisting captions and preserve numerical tipping moments/SF.
- Expand release smoke tests to check both the front separated arrows and rear coincident projection.

## V53.8.69 — Engineering FBD readability and Slope number fields

- **Engineering FBD:** prevent force diagram being squeezed under convention/help panels at laptop resolutions; move the whole page inside a vertical scrolling workspace and reserve 525px minimum height for the diagram.
- Change the FBD case/view/action toolbar to a compact two-column layout rather than an over-wide six-column row.
- **Slope:** restore visible up/down arrows to every numeric spinbox and explicitly set numeric text color for better Windows scaling/theme compatibility.
- Keep linked-mass checkbox, clearly visible Final Design Lock notification and one-click unlock from V53.8.68.
- Extend release GUI checks: actual click-and-type, no horizontal overflow, FBD height/vertical scrolling, and top/bottom FBD screenshots at 1024x650 and 1366x768.

## V53.8.68 — Fix mass-link checkbox mouse hit target

- Main Battery mass checkbox no longer stretches into a huge invisible click target; clicking the center of the visible control reliably toggles it.
- Keeps the quick Final Design unlock, explicit mass source, editable geometry, and compact FBD coordinate/legend adjustments from V53.8.67.
- Verify using actual Qt simulated clicks on lock/unlock, checkbox, and keyboard input before shipping.

## V53.8.67 — Restore editable Slope inputs and clean FBD labels

- **Fix locked input confusion.** Final Design Input Lock (stored in saved projects) disables Ramp/Slope spinboxes. Stability now shows a prominent lock notice and a one-click "ปลดล็อกเพื่อแก้ค่า" control rather than leaving disabled boxes unexplained.
- **Make the battery mass link obvious.** When Main Battery mass is selected, only the manual Ramp mass field is disabled and an explanation shows the effective linked mass. Unchecking the option enables manual mass entry again.
- **Keep all other Ramp dimensions and Slope inputs interactive** when Final Design Input Lock is off.
- **Fix overlapping axes and legend labels** in compact Engineering FBD widgets so axes no longer cut through the header.
- Add release-blocking GUI checks that simulate an actual user mouse click to unlock, mouse click to toggle mass linking, typing a geometry value, and creating both Slope and FBD screenshots.

## V53.8.65 — Prevent Slope panel width overflow

- Fix the true remaining cause of the 1024px Slope failure: long QGroupBox headings generated an unbreakable 758px minimum width.
- Shorten section headings while keeping the engineering meanings and explanatory content inside each section.
- Retain one-column buttons, responsive form, scrolling result text and formula wrapping.
- Keep the GitHub Actions responsive regression at 1024x650 and 1366x768.

## V53.8.63 — Fix horizontal overflow on small screens

- Fixed the Stability > Slope actions grid that could force content wider than the available 1024px laptop viewport.
- Place actions vertically so long Thai/English button captions wrap/fit instead of hiding controls off-screen.
- Keep the slope summary, geometry, and driving stability sections scrollable with compact inputs.
- Improved GitHub Actions Slope layout diagnostics so error logs do not fail on Windows console encoding.
- Release-blocking screenshot/layout checks remain enabled at 1366x768 and 1024x650.

## V53.8.61 — Slope layout validated at 1024px

- After inspecting automated screenshots, fix a real horizontal cut-off in Stability > Slope on compact laptop displays.
- Put Ramp Geometry input grid above the complete formula explanation; do not hide results beyond the right edge.
- Convert the headline ramp results to a 2-column / 2-row grid.
- Add a release-blocking test to detect horizontal overflow, plus capture full-window screenshots at 1024x650 and 1366x768.
- Retain the same calculations and linked project inputs.

## V53.8.60 — Slope UI rebuilt for Windows

- Rebuild Stability > Slope as a scrolling workspace. Inputs, results and actions no longer shrink into clipped boxes on laptops.
- Add four immediately visible, automatically updating ramp metrics: slope angle, percentage, theoretical length, measurement difference.
- Fix full-width number spinboxes: comfortable field widths, readable labels, no cramped up/down spinner buttons.
- Arrange calculation results to the right of geometry inputs, with its own document scrolling rather than cutting off the bottom.
- Separate action buttons and uphill stability parameters into clean sections with readable source-of-input guidance.
- Prevent lower slope stability report from being cut off; page scrolls vertically at 1024x650 and 1366x768.
- Add automated Qt UI layout checks and PNG screenshots at two display resolutions.
- Keep the original equations and linked inputs unchanged.

## V53.8.59 — Reliable Windows build and visible update progress

- Fix repeated GitHub Actions cancellations: remove the long-running full regression from the release-blocking pipeline.
- Add fast syntax, desktop startup, engineering and update-UI smoke checks before packaging.
- Preserve the complete regression in tests/full_regression.py and a separate Deep Engineering Regression workflow, run after successful release or manually.
- Add a timeout and step-by-step logs so a stuck test is reported clearly.
- Update screen shows a prominent progress bar, live percent, stage name, and downloaded MB.
- Hide Hardware I/O from the visible Home, side navigation, telemetry shortcuts and main routing, retaining internal compatibility for project saves.
- Carry forward compact UI fixes for Stability, Slope and Engineering FBD.

## V53.8.53 — Stability UI cleanup + Hardware I/O removed

- ใช้ V53.8.52 ล่าสุดจาก main เป็นฐานแก้ไข
- เอา Hardware I/O ออกจากการสร้างหน้า, เมนูซ้าย, page routing และ shortcut ใน Telemetry
- ปรับ Stability hub ให้กระชับ ลด margin/spacing ที่ทำให้หน้าดูยืด
- ปรับ Page Header และ Save bar ให้เตี้ยลงและอ่านง่ายขึ้น
- หน้า Engineering FBD เปลี่ยน control bar เป็น 2 แถวแบบ responsive ลดอาการปุ่มเบียด/ล้น
- ลด minimum height ของ FBD เพื่อให้ใช้งานได้ดีขึ้นบนจอ 1366×768 และจอ scaling สูง
- หน้า Slope เปลี่ยนชุดปุ่มเป็น grid 2×2 และลดพื้นที่ว่าง
- ลด base font เล็กน้อยเพื่อป้องกัน clipping จาก Windows display scaling

## V53.8.52 — Clean UI + GitHub Smart Cloud Sync

- ปรับ Desktop UI/UX ให้ clean ขึ้น: card/button/navigation radius และ spacing สม่ำเสมอ อ่านง่ายขึ้น
- เพิ่มสถานะ Cloud Sync แบบ dynamic ที่แถบซ้าย เห็น OFF / READY / SYNCING / SYNCED / CONFLICT / ERROR / OFFLINE ได้ทันที
- GitHub Smart Sync รองรับ Read-only PC: ไม่มี Token ก็ Auto Pull ข้อมูลล่าสุดได้
- เครื่องที่มี Fine-grained Token จะ Auto Push หลัง Local Auto Save และตรวจ Remote อัตโนมัติ
- เปิด Cloud Sync เป็นค่าเริ่มต้นสำหรับการติดตั้งใหม่ และตรวจ Remote ทุก 90 วินาที
- ยังคง conflict backup และไม่เขียนทับข้อมูลสองฝั่งแบบเงียบ ๆ
- Token ไม่ถูกฝังในโปรแกรม: เก็บด้วย Windows DPAPI หรือ environment variable เท่านั้น

# Crane Vehicle Engineering Tool V53.8.51

## Clean UI/UX + GitHub Cloud Sync

This release redesigns the Desktop and Web visual system and adds secure automatic GitHub synchronization so multiple PCs can use one shared CVET project state.

### 1. Clean / Modern UI
Desktop:
- lighter neutral background and white cards,
- flatter borders and reduced visual noise,
- unified blue primary action color,
- compact module cards,
- cleaner light page headers,
- Home dashboard reorganized into a 2×2 status layout,
- GitHub Cloud Sync status visible directly on Home,
- simplified Local Save / App Update / Web Server cards.

Web:
- matching light visual system,
- cleaner navigation and inputs,
- flatter dashboard cards,
- reduced heavy gradients and shadows,
- GitHub shared-project explanation added to the dashboard.

### 2. GitHub Cloud Sync
The Desktop app can now keep one project state in GitHub and share it across PCs.

Default cloud path:
`cloud_data/project_state.json`

Cloud settings support:
- repository `owner/repo`,
- branch,
- cloud file path,
- GitHub fine-grained token,
- automatic pull/check at startup,
- automatic push after Local Auto Save,
- remote polling interval.

Recommended token permission:
- Fine-grained Personal Access Token
- Repository access limited to the CVET data repository
- Contents: Read and write

### 3. Automatic synchronization flow
After Cloud Sync is configured:
1. CVET checks GitHub when the app starts.
2. If GitHub already contains a project and this PC has no common baseline, GitHub is pulled first.
3. If no remote project exists, CVET creates it from this PC.
4. Local edits continue to use the existing Auto Save.
5. A debounced GitHub Push runs after Local Auto Save only when project content actually changed.
6. CVET polls GitHub for newer remote data.
7. When another PC has newer data and this PC has no unsynced edits, the remote state is applied automatically.

### 4. Conflict protection
CVET uses optimistic synchronization rather than blind overwrite.

If both this PC and GitHub changed after the last common sync:
- automatic overwrite is blocked,
- status becomes **CONFLICT**,
- a full local + remote conflict backup is written to `Documents/CVET_Cloud_Conflicts`,
- manual resolution can choose GitHub or This PC.

### 5. No meaningless GitHub commits
The project `saved_at` timestamp is excluded from the cloud content hash.

This means the existing 60-second safety Auto Save does not create a GitHub commit unless actual engineering/project data changed.

### 6. Token security
The GitHub token is never included in:
- project JSON,
- cloud project JSON,
- Debug Report,
- GitHub commits.

On Windows the token is encrypted locally with **Windows DPAPI**, tied to that Windows user.
Each PC should enter its own token once.

For non-Windows source/development mode, CVET does not persist the token in plaintext.

### 7. Public/private repository safety
CVET supports both public and private repositories.

The Cloud Settings screen clearly warns:
- if the repository is public, the synced project JSON is publicly readable,
- a private repository is recommended for non-public engineering data.

### 8. Debug Report integration
Debug Report now includes privacy-safe cloud information:
- enabled/disabled,
- repository/branch/path,
- token present: true/false only,
- last sync time,
- last remote device.

The token value is never shown.

### 9. Web consistency
The Web dashboard remains linked to Desktop Save Values through **Sync Desktop**.
When the Desktop app receives the latest GitHub cloud state, the Web interface can load that same synchronized project state from the local CVET server.

### Regression / Safety Audit
The Windows release audit now verifies:
- `cloud_sync.py` syntax,
- state hashing ignores only the volatile `saved_at` timestamp,
- real engineering changes do change the cloud hash,
- cloud payload validation,
- repository/path normalization,
- GitHub Push cannot run without a token,
- plaintext tokens cannot be written into cloud config,
- Windows DPAPI encrypt/decrypt round-trip,
- Cloud UI/status controls exist,
- cloud-prefixed widgets are excluded from Project JSON,
- token value is absent from Debug Report,
- mocked GitHub Push updates remote SHA and synced hash,
- clean Desktop visual-system markers,
- clean Web visual-system markers,
- all previous engineering calculations, What-if, Scenario Presets, Input Source, Debug Report, PDF, Save/Restore, updater and Desktop↔Web regression.
