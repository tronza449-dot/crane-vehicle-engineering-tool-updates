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
