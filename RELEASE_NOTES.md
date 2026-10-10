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
