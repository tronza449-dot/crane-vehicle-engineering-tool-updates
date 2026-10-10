# Crane Vehicle BOM Manager (Windows Desktop)

แอปเดสก์ท็อปสำหรับดูและแก้ BOM โดยใช้ข้อมูลชุดเดียวกับหน้าเว็บ `bom-manager/` ใน GitHub repository นี้

## ติดตั้ง

ดาวน์โหลด `CraneVehicleBOMManager_Setup.exe` จาก **GitHub Releases → Crane Vehicle BOM Manager** (`bom-v*`) หรือแท็บ **Actions → Build BOM Manager Desktop → Artifacts** แล้วดับเบิลคลิกติดตั้ง ตัวติดตั้งสร้างไอคอนบน Desktop และ Start Menu

## วิธีใช้

1. เปิดโปรแกรม แล้วกด **ตั้งค่า GitHub Token** ครั้งแรก
2. สร้าง Fine-grained personal access token โดยเลือกเฉพาะ repository `crane-vehicle-engineering-tool-updates` และให้สิทธิ์ **Contents: Read and write**
3. วาง token โปรแกรมจะทดสอบการอ่าน BOM และเก็บ token ใน Windows Credential Manager
4. เปิดโปรแกรมแล้วระบบจะโหลด BOM ล่าสุดจาก GitHub ให้อัตโนมัติ (ต้องมีอินเทอร์เน็ต และสิทธิ์อ่าน Repo) ไม่ต้องกดปุ่มโหลดเอง
5. เพิ่ม/แก้/ลบ/เรียงอุปกรณ์ได้ตามต้องการ โปรแกรมบันทึกฉบับร่างทันที และ Auto Save ขึ้น GitHub เมื่อมี Token แล้ว (ค่าเริ่มต้นเปิดอยู่)

ข้อมูล BOM จะไม่ถูกฝังในตัวติดตั้ง ตัวแอปอ่านและเขียนไฟล์เดียวกับเว็บผ่าน GitHub API จึงต้องมีอินเทอร์เน็ตและสิทธิ์เขียน repository เมื่อบันทึก

## ความปลอดภัยและข้อจำกัด

- Token เก็บใน Windows Credential Manager ของบัญชีผู้ใช้เครื่องนั้น ไม่เก็บในไฟล์ BOM และไม่ commit ลง repository
- ใช้ Fine-grained token เฉพาะ repository นี้ พร้อม Contents: Read and write เท่านั้น
- ถ้าไฟล์ถูกแก้บน GitHub หลังจากโหลด แอปจะปฏิเสธการเขียนทับ (conflict) ให้โหลดล่าสุดก่อน
- ราคาว่างจะไม่นำมาคิดในยอดรวม
- ไฟล์ติดตั้งถูกสร้างบน GitHub Actions สำหรับ Windows; ไฟล์ workflow artifact มีอายุจำกัดตามการตั้งค่า GitHub

## พัฒนา/สร้างติดตั้งเองบน Windows

ติดตั้ง Python 3.12, PyInstaller, keyring และ Inno Setup จากนั้นสั่ง:

```powershell
python -m pip install pyinstaller keyring xlsxwriter reportlab
pyinstaller --noconfirm --clean --windowed --name CraneVehicleBOMManager --collect-all keyring --collect-all reportlab --collect-all xlsxwriter --add-data "VERSION;." app.py
& "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" "/DAppVersion=$((Get-Content VERSION -Raw).Trim())" installer.iss
```

ตัวติดตั้งจะอยู่ใน `output/CraneVehicleBOMManager_Setup.exe`


## ตรวจสอบเวอร์ชัน / อัปเดตโปรแกรม (v1.1.0+)

- ใต้แถบหัวโปรแกรมมี **เวอร์ชันปัจจุบัน**, **ตรวจสอบเวอร์ชัน** และ **อัปเดตตอนนี้**
- โปรแกรมตรวจสอบเวอร์ชันอัตโนมัติหลังเปิด และสามารถกดตรวจสอบด้วยตนเองได้
- ถ้าไม่พบเวอร์ชันใหม่ จะแสดงว่าใช้เวอร์ชันล่าสุด ถ้ามี จะเปิดปุ่ม **อัปเดตตอนนี้**
- เมื่อกดอัปเดต โปรแกรมดาวน์โหลด installer จาก GitHub Release ที่มี tag รูปแบบ `bom-vMAJOR.MINOR.PATCH` เท่านั้น
- ตรวจสอบทั้งชื่อไฟล์ ขนาด และ SHA256 จากไฟล์ `.sha256` ที่เผยแพร่คู่กัน ถ้าไม่ผ่านจะไม่เปิดไฟล์
- ดาวน์โหลดเป็นไฟล์ `.part` ก่อน จึงไม่เปิดไฟล์ที่ดาวน์โหลดไม่ครบ
- ปุ่มยกเลิกหยุดการดาวน์โหลดและลบไฟล์ชั่วคราว
- ถ้ามีรายการ BOM ที่แก้แต่ยังไม่บันทึกขึ้น GitHub โปรแกรม **จะไม่ยอมอัปเดต** จนกว่าจะบันทึก
- หลังตรวจสอบเสร็จ โปรแกรมจะเปิด Windows Installer แล้วปิดแอปเวอร์ชันเก่า ให้ดำเนินการติดตั้งตามหน้าจอ
- GitHub Token ใน Windows Credential Manager และข้อมูล BOM บน GitHub ไม่ถูกลบเมื่ออัปเดต
- การอัปเดตอัตโนมัติรองรับเฉพาะรุ่น `.exe` ที่ติดตั้งแล้วบน Windows; การเปิดด้วย `python app.py` เหมาะสำหรับพัฒนาและทดสอบการตรวจสอบเวอร์ชันเท่านั้น

### การปล่อยเวอร์ชันถัดไป

1. เปลี่ยน `bom-manager-desktop/VERSION` เป็นรุ่นใหม่ เช่น `1.2.0`
2. Push ไปที่ `main` พร้อมโค้ดเวอร์ชันใหม่
3. GitHub Actions จะตรวจ syntax, ทดสอบตัวอัปเดต, สร้าง `.exe` ด้วย PyInstaller และทำ Installer ด้วย Inno Setup
4. Pipeline จะสร้าง `bom-v1.2.0` Release พร้อม `CraneVehicleBOMManager_Setup.exe` และ `CraneVehicleBOMManager_Setup.exe.sha256` ถ้า tag ยังไม่มี
5. โปรแกรมที่ติดตั้งรุ่นก่อนหน้า (ตั้งแต่ v1.1.0) จะพบเวอร์ชันใหม่เมื่อเปิดหรือกดตรวจสอบ

**หมายเหตุ:** แอปที่ติดตั้งรุ่น 1.0.0 ไม่มีปุ่มอัปเดต จึงต้องติดตั้งรุ่น 1.1.0 ด้วยตนเองเพียงครั้งแรก เมื่อเปลี่ยนโค้ดแต่ไม่เปลี่ยน `VERSION` ระบบจะไม่ทับ Release เดิม ระบบ Release ของ BOM Manager แยก tag `bom-v...` จาก Crane Vehicle Engineering Tool และไม่กำหนดให้เป็น Latest Release หลักของ repository

**ข้อจำกัด:** SHA256 ตรวจความครบถ้วนของไฟล์ แต่ไม่ทดแทนการเซ็นโค้ด Windows; บางเครื่องอาจแสดงคำเตือน SmartScreen


## v1.2.0 — Dashboard / Wiring / Purchasing / Export

แอป Windows จัดเป็น 5 แท็บ:

| แท็บ | ฟังก์ชัน |
| --- | --- |
| ภาพรวม | จำนวนรายการ, จำนวนที่มีราคา/ขาดราคา, ยอดรวมที่ทราบ, หมวดหมู่ |
| BOM อุปกรณ์ | ค้นหา, กรองหมวด, เพิ่ม/แก้/ลบ, Part Number, ผู้ขาย, ลิงก์สินค้า |
| Wiring Manager | เพิ่ม/แก้/ลบจุดต่อ (ต้นทาง/ปลายทาง/อ้างอิง BOM ID/สัญญาณ/แรงดัน/สาย/ฟิวส์/สถานะ), ตรวจข้อมูล, ดูแผนภาพ, ส่งออก Draw.io |
| จัดซื้อ | สร้างรายการจาก BOM, บันทึกร้านค้า/ราคา/จำนวน/สถานะ/PO/กำหนดรับ/ลิงก์, สรุปยอด |
| GitHub / ส่งออก | โหลด/บันทึก Commit, ดู Commit History, Export Excel/PDF/CSV/JSON, Import JSON Backup, เปิดโฟลเดอร์ฉบับร่าง |

**ข้อมูลที่แชร์บน GitHub:** ยังคงใช้ `bom-manager/bom.json` (`schemaVersion: 1`) เพื่อรักษาการทำงานร่วมกับเว็บเดิม เพิ่มอาร์เรย์ `wiring` และ `purchases` เฉพาะเมื่อเริ่มใช้งาน ไม่เปลี่ยนรายการอุปกรณ์เดิมหรือสร้างจุดต่อสายที่ไม่เคยยืนยัน

**ป้องกันข้อมูลหาย:** ทุกครั้งที่แก้โปรแกรมจะบันทึกฉบับร่างลงโฟลเดอร์ `%LOCALAPPDATA%\CraneVehicleBOMManager\draft.json` ด้วยการเขียนไฟล์ชั่วคราวก่อนแทนที่ไฟล์จริง ถ้าปิดโดยยังไม่ GitHub Commit ครั้งต่อไปจะคืนฉบับร่างอัตโนมัติและไม่โหลด GitHub ทับทันที การบันทึก GitHub ใช้ blob SHA เพื่อปฏิเสธการเขียนทับข้อมูลที่คนอื่นแก้ไปแล้ว

**Excel (.xlsx):** มีชีต `Summary`, `BOM`, `Wiring`, `Purchasing` รวมสูตรคูณราคากับจำนวนและยอดรวม ไม่มีการนับราคาที่เว้นว่างเป็นศูนย์เพื่อหลอกให้ยอดดูครบ

**PDF:** รายงาน A4 แนวนอนภาษาไทย (ใช้ฟอนต์ Tahoma ที่ติดตั้งใน Windows) พร้อม BOM / Wiring / Purchasing และคำเตือนว่าข้อมูลต้องตรวจสอบก่อนนำไปประกอบจริง

**CSV:** ส่งเฉพาะรายการอุปกรณ์พร้อม BOM ID และยอดรวม ป้องกันสูตร CSV ที่มาจากชื่อรายการ/ข้อความที่ผู้ใช้กรอก

**Draw.io:** เป็นผังแสดงการเชื่อมต่อทีละแถวเพื่อไม่ให้เส้นไขว้หรือทับกัน เปิดแก้ใน diagrams.net ได้ ไม่ใช่ผังไฟฟ้าที่รับรองการออกแบบ

### สร้างตัวติดตั้งเวอร์ชันใหม่

แก้ `bom-manager-desktop/VERSION` เป็นเวอร์ชันที่สูงขึ้น เช่น `1.3.0` แล้ว Push ไปยัง `main` ระบบ GitHub Actions จะตรวจสอบไวยากรณ์, รัน Unit Tests, ทดสอบการสร้างรายงานกับ BOM จริง, สร้างไฟล์ EXE/Inno Setup และตรวจ SHA256 ก่อนปล่อย GitHub Release ที่ใช้ tag `bom-v1.3.0` จากนั้นโปรแกรมเดิมจะพบเวอร์ชันใหม่ผ่านปุ่ม **ตรวจสอบเวอร์ชัน** และกด **อัปเดตตอนนี้** ได้

การติดตั้งรุ่นใหม่ไม่ลบ GitHub Token ใน Windows Credential Manager และไม่ลบฉบับร่างใน Local AppData


## v1.3.0 — UI/UX refresh + ฟอนต์ไทยอ่านง่าย

- ปรับ UI ของโปรแกรม Desktop จริง (ไม่ใช่แค่ภาพตัวอย่าง) โดยคง BOM, Wiring, Purchasing, GitHub และตัวอัปเดตเดิม
- ใช้ชุดสี Navy/Blue/White พื้นหลังอ่อน พร้อมแท็บและปุ่มที่มีความต่างสีชัดเจน
- ใช้ฟอนต์ Leelawadee UI บน Windows และเพิ่มขนาดพื้นฐานเป็น 12pt / หัวข้อ 17–21pt / ตัวเลข Dashboard 26pt
- เปิด Windows DPI-awareness ก่อนสร้าง Tk window เพื่อไม่ให้ตัวอักษรแตกหรือเบลอเมื่อ Windows ตั้งการขยายหน้าจอ
- สร้าง Dashboard ใหม่เป็น 6 การ์ดกดได้ (รายการทั้งหมด/มีราคา/ยังไม่มีราคา/ยอดรวม/จุดต่อสาย/จัดซื้อ)
- คลิกการ์ดจะไปยังแท็บที่เกี่ยวข้องพร้อมกรองรายการตามราคาจริงได้
- เพิ่มความคืบหน้าการกรอกราคา (%) และแถบ Progress พร้อมตารางหมวดที่แยกแถวชัดเจน
- เพิ่มช่องกรองราคาบนแท็บ BOM ได้แก่ ทุกราคา / มีราคา / ไม่มีราคา
- เพิ่มหัวข้อและคำอธิบายทุกแท็บ จัดช่องว่างใหม่ ขยายแถวตาราง และใช้สีสลับแถวเพื่อช่วยอ่าน
- ไม่เปลี่ยนสูตรต้นทุน, รายการ BOM ที่มีอยู่, ฟอร์แมต JSON, GitHub Token หรือข้อมูลฉบับร่าง

### การตรวจสอบ

GitHub Actions สร้าง installer ของเวอร์ชันนี้จาก `bom-manager-desktop/VERSION`
พร้อม smoke test: เปิด 5 แท็บ, ตรวจฟอนต์ >= 12pt, ตรวจตัวกรองราคา และตัวเลข KPI


## v1.4.0 — Industrial Dark (Windows PySide6)

เวอร์ชันนี้เปลี่ยน **UI ของไฟล์ติดตั้ง Windows เป็น PySide6 (Qt)** ใช้ธีม Industrial Dark แทน Tkinter พร้อมปุ่มและตารางที่ใช้งานได้จริง:

- แถบเมนูด้านซ้าย 5 หน้า: ภาพรวม, BOM, Wiring, จัดซื้อ, GitHub/ส่งออก
- โทนสี Navy/Dark Steel ตัดด้วย Cyan, Emerald, Amber, Violet และข้อความภาษาไทยสีสว่าง
- Dashboard การ์ด 6 ช่องกดเพื่อเปิดหน้าข้อมูลและกรองรายการได้
- ตาราง BOM ค้นหา/กรองหมวด/กรองรายการที่มีหรือไม่มีราคา
- เพิ่ม/แก้ไข/ลบรายการ BOM, Wiring และ Purchasing ผ่านหน้าต่างฟอร์ม
- Wiring Preview + Draw.io, Import JSON, Export Excel/PDF/CSV/JSON, GitHub Commit History
- บันทึกฉบับร่างใน `%LOCALAPPDATA%\CraneVehicleBOMManager\draft.json` โดยไม่เปลี่ยนโครงสร้างข้อมูลเดิม
- ใช้ Token เดิมจาก Windows Credential Manager; ยังคงอัปเดตเวอร์ชันผ่าน BOM GitHub Release และตรวจ SHA256
- PySide6 รองรับหน้าจอ High DPI ของ Windows โดยอัตโนมัติ พร้อมตัวอักษร Leelawadee UI

### เปิดจากซอร์ส (Windows)

```powershell
python -m pip install PySide6 keyring xlsxwriter reportlab
cd bom-manager-desktop
python qt_launcher.py
```

### สร้างไฟล์ติดตั้ง

GitHub Actions จะทดสอบ UI ด้วย Qt `offscreen` ก่อนสร้าง `CraneVehicleBOMManager_Setup.exe` ด้วย PyInstaller
และ Inno Setup แล้วจึงเผยแพร่ GitHub Release แยก `bom-v1.4.0`

หมายเหตุ: `app.py` เป็นส่วน Tkinter รุ่นเก่าเพื่ออ้างอิง/ทดสอบย้อนหลัง แต่ไฟล์ติดตั้ง Windows รุ่น v1.4.0 เรียก `qt_launcher.py`


## v1.5.0 — Debug Report / System Diagnostics

Industrial Dark UI มีเมนู **Debug Report** ด้านซ้ายเป็นหน้าที่ 6 สำหรับตรวจสอบปัญหาและสร้างรายงานช่วยวิเคราะห์:

- **ตรวจสอบระบบตอนนี้:** ตรวจโครงสร้าง BOM, จำนวนรายการที่มี/ไม่มีราคา, Wiring reference, พื้นที่บันทึก Log, สถานะ GitHub Token และสถานะการโหลดข้อมูล
- **ทดสอบเชื่อมต่อ GitHub:** ทดสอบ GitHub REST API ตามคำสั่งผู้ใช้ ไม่ส่งข้อมูล BOM ขึ้นเซิร์ฟเวอร์
- **ประวัติ Error:** บันทึกเหตุการณ์ GitHub load/save, export, update และ exception จาก background jobs ลงไฟล์ในเครื่อง
- **ส่งออก Debug Report (.json):** มีเวอร์ชันแอป, ข้อมูล OS/Python, จำนวนอุปกรณ์รวม, ผลตรวจและเหตุการณ์ล่าสุด 150 รายการ
- **เปิดโฟลเดอร์ Log** และ **ล้าง Log** มีปุ่มแยก พร้อมยืนยันก่อนลบ
- Log จำกัดขนาดประมาณ 1 MB ต่อไฟล์ มี 1 ไฟล์ย้อนหลัง (`events.previous.jsonl`); การเขียน Log ล้มเหลวไม่ทำให้แอปหยุด
- Debug Report ไม่บันทึก BOM รายแถว, ชื่ออุปกรณ์, ลิงก์ผู้ขาย, GitHub Token หรือ credential ของผู้ใช้
- สตริงเหตุการณ์และ traceback ถูกลบ token/password/email/user paths ก่อนเก็บในเครื่องและก่อน export
- การส่ง Debug Report เป็นไฟล์ในเครื่องตามที่ผู้ใช้เลือก **ไม่อัปโหลดอัตโนมัติ**

**ตำแหน่ง Log (Windows):** `%LOCALAPPDATA%\CraneVehicleBOMManager\debug`

**วิธีส่งข้อผิดพลาดให้ตรวจ:** เข้าเมนู Debug Report → กดตรวจสอบระบบ → หากเกี่ยวกับ GitHub กดทดสอบเชื่อมต่อ → กดส่งออก JSON → เปิดไฟล์ตรวจเนื้อหา → แนบรายงานในแชทนี้

**สำคัญ:** GitHub Token ยังคงอยู่ใน Windows Credential Manager (ไม่ฝังใน Debug Report) ข้อมูล BOM ที่ทำค้างอยู่ยังบันทึกใน `draft.json` เหมือนเดิม และ Debug Report ไม่เปลี่ยนสูตรคำนวณต้นทุน


## v1.5.1 — ปรับตัวอักษรไทยให้อ่านง่ายขึ้น

- เพิ่มขนาดตัวอักษรตั้งต้นพร้อมเพิ่มความต่างสีของข้อความบน Industrial Dark
- แถบเมนูซ้ายมี **ขนาดตัวอักษร** ให้เลือกระดับ 100%, 115% (ค่าเริ่มต้น), 130% และ 145%
- เลือกฟอนต์ภาษาไทยได้: **Leelawadee UI** (ค่าเริ่มต้น) หรือ **Tahoma**
- โปรแกรมจำค่าแสดงผลที่เลือกด้วย Windows Application Settings แม้อัปเดตโปรแกรม
- ทางลัด `Ctrl++` และ `Ctrl+-` เพิ่มหรือลดขนาด, `Ctrl+0` กลับค่าเริ่มต้น
- เพิ่มระยะสูงของแถวตารางและหัวตารางตามตัวอักษร ปรับความกว้าง Sidebar อัตโนมัติ
- ปรับส่วนหัวโปรแกรมให้แยกชื่อและปุ่มเป็น 2 แถว และให้ Dashboard เลื่อนลงได้ในหน้าจอเล็ก
- การปรับตัวอักษรไม่แตะไฟล์ BOM, Wiring, การจัดซื้อ, GitHub Token หรือ Debug Report
- เพิ่มภาพ `ReadableBOMPreview.png` จากการเปิด EXE บน Windows และเลือกขนาด 130% จริง

หากยังอ่านยากหลังอัปเดต ให้ลองเลือก **130% + Tahoma** ในเมนูซ้าย หรือใช้การขยายหน้าจอที่ Settings → Display ของ Windows ซึ่งเป็นคนละการตั้งค่ากับขนาดตัวอักษรในแอป


## v1.5.2 — จัดหมวด BOM ใหม่ตามระบบวิศวกรรม

ปรับจาก 5 หมวดเดิมเป็น **7 หมวดมาตรฐาน** สำหรับรถขนซากสัตว์พร้อมเครน:

| หมวดใหม่ | จำนวนอุปกรณ์ (BOM ต้นฉบับ 33 รายการ) | รหัสเดิม |
| --- | ---: | --- |
| โครงสร้างและเครื่องกล | 3 | 26–28 |
| ระบบขับเคลื่อน | 2 | 2–3 |
| แบตเตอรี่และไฟฟ้ากำลัง | 6 | 4–7, 9–10 |
| ระบบควบคุมและสื่อสาร | 7 | 1, 11, 14–15, 18–20 |
| เซนเซอร์และความปลอดภัย | 6 | 8, 12–13, 16–17, 21 |
| ระบบเครนและวินช์ | 4 | 22–25 |
| สายไฟและอุปกรณ์ติดตั้ง | 5 | 29–33 |

**ข้อมูลเดิมถูกจัดหมวดจริงใน GitHub** ที่ `bom-manager/bom.json` และยังใช้ได้กับเว็บ BOM
พร้อมกัน โดยเปลี่ยนแค่ช่อง `category` ของอุปกรณ์ทั้ง 33 รายการ
ไม่เปลี่ยน `id`, `name`, `spec`, `qty`, `unitPrice`, `link` หรือข้อมูลอื่น

**Desktop Industrial Dark**
- รายการ BOM แยกหัวหมวดสีกรมท่าพร้อมจำนวนชิ้นในหมวด และเรียงตามลำดับระบบวิศวกรรม
- ตัวเลือกรูปแบบแสดงผล: **จัดกลุ่มตามระบบ** (ค่าเริ่มต้น) / **แสดงรายการต่อเนื่อง**
- กรองหมวดด้วยรายการ 7 หมวดใหม่; ดับเบิลคลิกหมวดใน Dashboard เพื่อเปิดเฉพาะหมวดนั้น
- เมื่อเพิ่มหรือแก้ไขอุปกรณ์ เลือกหมวดจากเมนูแนะนำหรือพิมพ์ชื่อหมวดเฉพาะใหม่ได้
- การกรอง ค้นหา แก้ไข ส่งออก CSV/Excel/PDF และ GitHub Sync ยังใช้ข้อมูล BOM ชุดเดิม
- ไม่มีการจัดหมวดอัตโนมัติทุกครั้งที่โหลด เพื่อไม่ให้เปลี่ยนหมวดที่ผู้ใช้แก้เองในภายหลัง

การแก้ข้อมูลบน GitHub ยังคงตรวจ blob SHA หากข้อมูลถูกเปลี่ยนจากคอมอีกเครื่อง โปรแกรมจะต้องแจ้ง conflict ก่อนบันทึกทับ


## v1.5.3 — เลือกหมวดจากรายการสำเร็จรูป ไม่ต้องพิมพ์

- **Desktop Industrial Dark:** เปิดเพิ่ม/แก้ไขอุปกรณ์ → เลือก **หมวดอุปกรณ์** ด้วย Dropdown แบบอ่านอย่างเดียว ไม่มีช่องพิมพ์ชื่อหมวดเองอีกแล้ว
- มีตัวเลือกสำเร็จรูปทั้ง 7 หมวดตามระบบวิศวกรรม และ **อื่น ๆ / รอจัดหมวด**
- หมวดจากไฟล์ BOM เก่าที่ยังไม่ตรงกับ 7 หมวดใหม่ยังคงมีให้เลือก ไม่แก้หรือทำข้อมูลเก่าสูญหาย
- **Web BOM:** เปลี่ยนคอลัมน์หมวดจากช่องพิมพ์เป็น Dropdown เช่นกัน และจัดเรียงข้อมูลตามหมวดหลังเลือก
- รายการใหม่บนเว็บเริ่มต้นด้วยหมวด **อื่น ๆ / รอจัดหมวด** เพื่อให้ผู้ใช้เลือกหมวดจริงภายหลัง
- ไม่มีการเปลี่ยนข้อมูล BOM รายการเดิมในอัปเดตนี้ และ GitHub Sync / Backup / ราคายังคงใช้เหมือนเดิม


## v1.6.0 — UI ใช้งานง่ายขึ้น + รายงาน PDF/Excel แบบทางการ

**หน้าจอ**
- ปรับชื่อ Sidebar เป็นภาษาไทยอ่านง่าย: ภาพรวม, รายการอุปกรณ์, การเดินสาย,
  รายการจัดซื้อ, รายงาน / GitHub, ตรวจสอบระบบ
- เพิ่มปุ่ม **ส่งออกรายงาน PDF / Excel** บนแถบด้านบนให้เข้าถึงง่าย
- ย้ายปุ่มอัปเดตแอปไปไว้ในหน้ารายงาน / GitHub ลดปุ่มที่ไม่ใช้บ่อยบนหน้าแรก
- หน้า BOM แสดงข้อความวิธีใช้แถวและการเลือกหมวด และยังใช้ค้นหา/กรอง/จัดหมวดตามระบบได้
- หน้ารายงานใหม่แยกเป็น 3 กลุ่ม: ส่งออกรายงาน, GitHub Sync, สำรอง/เครื่องมืออื่น
- ปุ่ม PDF และ Excel สามารถสั่งพร้อมกันโดยเลือกโฟลเดอร์ครั้งเดียว
- แบบฟอร์มก่อน Export เก็บ **ชื่อผู้จัดทำ, สถาบัน, เลขที่เอกสาร และ Revision** ใน Settings ของเครื่อง
  โดยไม่เขียนทับข้อมูล BOM หรือแชร์ชื่อผู้จัดทำขึ้น GitHub

**PDF แบบทางการ**
- A4 แนวนอน มีส่วนหัว ENGINEERING BOM, ชื่อโครงการ, ผู้จัดทำ, สถาบัน, เลขที่เอกสาร,
  Revision, วันที่, เลขหน้าทุกหน้า และข้อมูลการใช้งานเอกสาร
- หน้าแรกเป็นหน้ารายงานและสรุปงบประมาณ ต่อด้วยหน้าสรุปหมวด
- ภาคผนวก ก: BOM แยกตาม 7 ระบบวิศวกรรม พร้อมจำนวน ราคา และสถานะ
- ภาคผนวก ข: ตารางการต่อสายและแรงดัน (เป็นแบบร่าง ไม่ใช่แบบรับรอง)
- ภาคผนวก ค: ตารางจัดซื้อและสถานะ
- ไม่ใส่ลายเซ็นอนุมัติ/ตราองค์กร/ข้อความรับรองที่ไม่มีข้อมูล

**Excel แบบทางการ**
- 6 ชีต: Summary, BOM, Specification, Wiring, Purchasing, Notes
- หัวกระดาษและท้ายกระดาษมีชื่อเอกสาร Revision และเลขหน้า พร้อมตั้งค่าพิมพ์แนวนอน
- มีหัวตารางชัดเจน สลับสีแถว Freeze และกรองข้อมูลบน BOM/Specification
- ใช้สูตรจริงใน Excel สำหรับมูลค่าต่อชิ้น ยอดรวมตามหมวด และ Summary
- เก็บข้อมูลจาก BOM จริง รวมแหล่งอ้างอิง/ลิงก์สินค้าในชีต Specification
- ราคาที่ยังไม่รู้ **ปล่อยช่องว่างและแสดงคำเตือน** ไม่ปัดเป็น 0 บาท

**ไฟล์ตัวอย่างจาก BOM จริง**
- `EngineeringBOM_Example.pdf`
- `EngineeringBOM_Example.xlsx`
ตัวอย่างดังกล่าวแสดงข้อมูล BOM ปัจจุบันแต่ **ผู้จัดทำและสถาบันเป็นค่าตัวอย่าง**
หากจะนำไปส่งอาจารย์ ให้สร้างใหม่ผ่านโปรแกรมและกรอกข้อมูลของผู้จัดทำให้เรียบร้อย

การส่งออกไฟล์ยังไม่ส่ง GitHub Token หรือข้อมูล credential ไปกับเอกสาร


## v1.7.0 — Engineering BOM ตามตัวอย่างวิชาชีพ (ISO 7573 / CAD BOM-inspired)

ปรับ **เฉพาะรูปแบบรายงานที่โปรแกรมสร้าง** โดยอ้างอิงหลักการจาก
[ISO 7573:2008](https://www.iso.org/standard/43883.html),
[SOLIDWORKS BOM](https://help.solidworks.com/2021/English/SolidWorks/sldworks/c_Bill_of_Materials_-_Custom_Properties.htm)
และ [OpenBOM](https://www.openbom.com/blog/bill-of-materials-types-formats-and-examples)
โดยไม่ได้อ้างว่าเอกสารผ่านการรับรอง ISO หรือเป็นเอกสารอนุมัติผลิต

### PDF: คั่นหน้าอ่านง่ายและตรวจสอบย้อนกลับได้

- หน้าข้อมูลเอกสาร: โครงการ, ผู้จัดทำ, สถาบัน, เลขเอกสาร, Revision, วันที่และสถานะ **DRAFT**
- สรุปรายการและราคาที่ทราบ พร้อม **จำนวนข้อมูลที่ต้องตรวจสอบ** (Part No., ผู้ขาย, แหล่งอ้างอิง, ราคา)
- หมวดระบบ 7 หมวด; BOM หลักมี **BOM ID แยกจาก Part Number ผู้ผลิต**, ชื่อรุ่น, จำนวน, หน่วย, ราคา, สถานะ
- ภาคผนวกสเปกทางวิศวกรรม: รายละเอียดและลิงก์ผู้ผลิต/ร้านค้าจากข้อมูลจริง (ถ้าไม่ทราบแสดง "ยังไม่ระบุ")
- ภาคผนวก Wiring และ Purchasing; ตารางขึ้นหัวใหม่เมื่อต่อหน้าและมีเลขหน้า/Revision
- Part Number ที่ยังไม่มี **ไม่แต่งรหัสสมมติ**

### Excel: ตารางหลัก/ภาคผนวก/ตรวจคุณภาพข้อมูล

- เพิ่มคอลัมน์ **Part Number** ที่ BOM พร้อมแก้สูตร Excel อ้างอิงคอลัมน์จำนวนและราคาใหม่อย่างถูกต้อง
- Summary, BOM, Specification, Wiring, Purchasing, Notes ยังคงอยู่
- เพิ่มชีต **References** มีแหล่งอ้างอิง/สถานะ/ผู้ขาย/Part Number แยกตาม BOM ID พร้อมลิงก์กดเปิดได้
- เพิ่มชีต **Completeness** ระบุสิ่งที่ยังไม่ครบและแหล่งแนวทางมาตรฐาน
- Summary แสดงจำนวนรายการที่ยังขาด Part Number, ผู้ขาย, ลิงก์และราคา
- Excel มีสูตรบวกราคาและจัดหมวด; ราคาไม่ทราบเว้นว่าง **ไม่ใช่ 0 บาท**
- แผ่นรายงานกำหนดหน้ากระดาษ A4/A3 แนวนอน, freeze headers และ print area

### ข้อมูลจริง ณ รุ่นนี้

ชุดข้อมูลโครงการมี 33 รายการ; มี Part Number ผู้ผลิตในช่อง `partNumber` = 0,
มีผู้ขายในช่อง `supplier` = 0, มีแหล่งอ้างอิง `link` 20 รายการ และราคาที่ระบุ 1 รายการ
ข้อมูลรุ่นที่อยู่ในชื่อสินค้าไม่ได้ถูกเดามาเป็น Part Number ผู้ผลิต
ผู้ใช้ควรตรวจสอบเติมข้อมูลจาก Datasheet และใบเสนอราคาก่อนใช้เพื่อจัดซื้อ

ไฟล์ตัวอย่าง `EngineeringBOM_Example.pdf` และ `EngineeringBOM_Example.xlsx`
แนบ GitHub Release v1.7.0; ผู้จัดทำ/สถาบันเป็นค่าตัวอย่าง ให้ใส่ข้อมูลจริงผ่านปุ่ม Export ในโปรแกรม


## v1.8.0 — Minimal Engineering UI (ดีไซน์ที่ผู้ใช้เลือก: แบบ 3)

หน้าตา **โปรแกรม Windows PySide6** เปลี่ยนจาก Industrial Dark เป็นธีมสว่างที่อ่านง่าย:
- Sidebar สีกรมท่า / พื้นที่ทำงานสีขาวเทา / ปุ่มหลักสีน้ำเงินและข้อความไทยคอนทราสต์สูง
- Dashboard: แถบโครงการที่อ่านจากข้อมูลจริง, การ์ด KPI กดเพื่อกรองข้อมูล, การ์ดหมวดวิศวกรรม 7 หมวดกดเพื่อเปิด BOM, ความครบถ้วนของราคา
- ตาราง BOM: ค้นหา, กรองหมวด, กรองราคา, โหมดจัดกลุ่ม/รายการต่อเนื่อง; แสดงรหัส BOM และ Part Number แยกกัน พร้อมจำนวน ราคา และสถานะ
- ฟอร์มเพิ่ม/แก้ไข BOM แบ่งแท็บ **ข้อมูลหลัก / สเปกและการเชื่อมต่อ / ราคาและร้านค้า / หมายเหตุ** โดยบันทึกครบทุกช่องเดิม
- หน้ารายงาน: การ์ด 3 ทางเลือก PDF แบบทางการ, Excel พร้อมสูตร, สร้างสองไฟล์พร้อมกัน โดยใช้ฟังก์ชันเดิมจริง
- ระบบ GitHub Sync, Wiring, Purchasing, Debug Report, Font Zoom 100–145%, GitHub update และบันทึกฉบับร่างยังทำงานตามเดิม
- **ไม่สร้างข้อมูลจำลองใน Dashboard**: จำนวน/ราคา/หมวด/ชื่อโครงการอ้างอิง BOM ปัจจุบัน และยังไม่ถือว่าราคาที่ขาดเป็นศูนย์
- **ไม่แก้โครงสร้างหรือรายการใน bom-manager/bom.json** การเปลี่ยน UI ไม่ควรทำให้ข้อมูลเปลี่ยนโดยไม่กดบันทึก

### รูปภาพจากโปรแกรม EXE จริง (GitHub Release v1.8.0)
- `MinimalDashboardPreview.png` — หน้าหลัก
- `MinimalBOMPreview.png` — ตารางอุปกรณ์
- `MinimalFormPreview.png` — แก้ไขข้อมูลแบบสี่แท็บ
- `MinimalReportsPreview.png` — เลือกสร้าง PDF/Excel
- `ReadableBOMPreview.png` — ตัวอย่างปรับตัวอักษรใหญ่ 130%

ในเวอร์ชันนี้ยังเป็น desktop UI ไม่ได้เปลี่ยนหน้าเว็บ BOM ให้มีหน้าตาเดียวกัน
จึงไม่มีการอ้างว่าเว็บไซต์เปลี่ยนแล้วด้วย

## v1.8.1 — แก้ปุ่มอัปเดตหาไม่เจอ

- ปุ่ม **ตรวจสอบอัปเดต** ถูกย้ายกลับมาวางที่ **มุมขวาบนของแถบหัวโปรแกรม** และแสดงในทุกหน้า ไม่ซ่อนในเมนูรายงานอีกต่อไป
- แสดงเวอร์ชันปัจจุบันอยู่ข้างปุ่มเสมอ และแสดงคำว่า **ล่าสุด** หลังตรวจสอบว่าไม่มีเวอร์ชันใหม่
- หาก GitHub พบรุ่นใหม่ จะแสดงปุ่ม **ดาวน์โหลดและอัปเดต** ทันที และแสดงหมายเลขรุ่นใหม่ในหัวโปรแกรม
- ระบบอัปเดตเดิมใช้การตรวจ SHA256 และยังป้องกันการปิดโปรแกรมขณะมีข้อมูล BOM ค้างบันทึก
- ทดสอบการเข้าถึงปุ่มจากทุกหน้า และการซ่อน/แสดงปุ่มติดตั้งตามสถานะเวอร์ชัน
- การแก้ไขนี้ไม่เปลี่ยนข้อมูล BOM และไม่แตะการตั้งค่า GitHub Token


## v1.8.2 — Thai Text Clarity / อ่านตัวอักษรได้ชัดขึ้น

ปรับการแสดงผลใน Windows PySide6 จากข้อเสนอแนะเรื่องตัวหนังสือดูไม่ชัด:
- ใช้ **Tahoma** เป็นฟอนต์ไทยเริ่มต้นสำหรับการติดตั้งหรือผู้ใช้ที่ยังไม่เคยเลือกฟอนต์เอง
- ตั้ง font-family ให้เป็นฟอนต์ตัวเดียวใน Qt StyleSheet (ไม่ใช่ CSS fallback list แบบเว็บ)
- กำหนด font hinting แบบ Full และเปิด antialiasing ใน QFont
- ใช้ DPI rounding policy เป็น PassThrough เพื่อเคารพ Windows display scaling แบบเศษส่วน (เช่น 125% / 150%)
- เน้นน้ำหนักข้อความในตาราง ช่องกรอก และข้อความอธิบายที่เดิมบางหรือสีจาง
- เพิ่มความต่างสีของข้อความรองกับพื้นหลังขาว/กรมท่า และความชัดของหัวตาราง
- คงตัวเลือกฟอนต์ Leelawadee UI และระดับ 100%, 115%, 130%, 145% ไว้เช่นเดิม
- หากผู้ใช้เคยเลือกฟอนต์เอง โปรแกรมยังจำค่าที่เลือกไว้ ไม่บังคับเปลี่ยนทับ
- ไม่เปลี่ยน BOM JSON, ข้อมูล GitHub, สูตรคำนวณ หรือไฟล์ส่งออกรายงาน

**ถ้ายังรู้สึกว่าตัวอักษรเบลอ:** ตรวจสอบ Windows Settings → System → Display →
Scale / Display resolution (ใช้ค่าที่ Windows แนะนำ) และเปิดตัวช่วย
Adjust ClearType text บน Windows หากหน้าจอใช้งาน ClearType
หลังอัปเดตลองเลือก Tahoma + 115% หรือ 130% จากเมนูซ้าย ถ้าปัญหายังคงอยู่
ส่งภาพหน้าจอจากเครื่องจริง พร้อมค่า Scale 100/125/150% เพื่อวิเคราะห์เฉพาะจุด


## v1.9.0 — GitHub Shared Data / Cloud Auto Save + BOM-linked Purchasing

**หลักการ: ทุกเครื่องใช้ BOM JSON ไฟล์เดียวกันบน GitHub**
- แหล่งข้อมูลหลักคือ `bom-manager/bom.json` บน GitHub (สาขา `main`)
- เมื่อเปิดโปรแกรมพร้อมอินเทอร์เน็ต โหลด BOM ล่าสุดจาก GitHub
- เมื่อเปลี่ยนข้อมูล บันทึกฉบับร่างลง `%LOCALAPPDATA%\CraneVehicleBOMManager\draft.json`
  แบบ atomic write + fsync แล้วเริ่มจับเวลารอแก้ไขหยุดประมาณ **90 วินาที**
- ถ้ามี Token และรู้ GitHub SHA จะ Auto Save เป็น Commit ไปยัง GitHub;
  เปิด/ปิดได้ในหน้า **รายงาน / GitHub** (ค่าเริ่มต้นเปิด)
- เมื่อคอมดับ/เน็ตหลุด เก็บข้อมูลฉบับร่างไว้ในเครื่องและโหลดคืนตอนเปิดโปรแกรม;
  ทุก **3 นาที** จะลองส่งที่ยังค้างซ้ำ (ตราบใดที่เปิดโปรแกรม/มีอินเทอร์เน็ต)
- เครื่องอื่นที่ไม่มีการแก้ไขค้างจะตรวจสอบ GitHub ทุก **2 นาที**
  และโหลดเวอร์ชันใหม่เมื่อ SHA เปลี่ยน หรือกด **รับข้อมูล GitHub ล่าสุด** เพื่อโหลดทันที
- มี GitHub connection/status บนหัวโปรแกรม **ทุกหน้า** ไม่บอกว่าซิงก์แล้วหากยังไม่ได้ตรวจสอบ
- ก่อนอัปโหลดทุกครั้ง ตรวจ SHA จาก GitHub แบบสด และ GitHub Contents API ยังป้องกัน
  SHA mismatch ระหว่าง PUT หากมีเครื่องอื่นแก้ก่อน จะ **หยุด Auto Save พร้อมเก็บ
  local draft** ไว้ ไม่เขียนทับข้อมูลจากอีกเครื่องแบบเงียบ ๆ
- หากมีข้อมูลที่แก้ระหว่างการดาวน์โหลด GitHub ก็ไม่ยอมโหลดมาทับ local draft
- ใช้ GitHub fine-grained PAT ต่อเครื่องเฉพาะ repository นี้ (Contents: Read/write);
  เก็บ Token ใน Windows Credential Manager ของแต่ละเครื่อง ไม่ใส่ใน BOM JSON หรือ PDF

**ข้อจำกัดจริง:** GitHub ไม่ใช่ฐานข้อมูล realtime; ซิงก์มีหน่วงตามรอบ Auto Save (90 วินาที
หลังแก้ไขครั้งสุดท้าย) และรอบตรวจของอีกเครื่อง (ไม่เกินประมาณ 2 นาทีขณะที่ออนไลน์และไม่มี
งานค้าง; อาจนานกว่านี้เมื่ออินเทอร์เน็ตหรือ GitHub ขัดข้อง) ไม่รับประกันการเห็นข้อมูลทันที
หลายเครื่องที่แก้พร้อมกันจำเป็นต้องแก้ conflict ด้วยตนเอง — โปรแกรมหยุดส่งเพื่อไม่ให้ข้อมูลหาย

**รายการสั่งซื้อ**
- กด **+ เลือกอุปกรณ์จาก BOM** แล้วเลือกชื่ออุปกรณ์พร้อมรหัส BOM จาก Dropdown
- ดึงชื่อ จำนวน ราคาอ้างอิง ผู้ขาย และลิงก์อุปกรณ์เข้า Purchase draft อัตโนมัติ
- ปรับจำนวนที่จะซื้อ, ราคาเสนอขายจริง, ผู้ขาย, PO และสถานะการจัดซื้อได้เอง
- เก็บ `itemId` เชื่อมกลับไปยังรหัส BOM เดิม ไม่เปลี่ยนรายการ BOM เมื่อแก้ Purchase
- หากแก้รายการเก่า เลือกอุปกรณ์อ้างอิงเดิมที่เคยบันทึกไว้ได้ แม้ถูกลบจาก BOM ปัจจุบัน
- สถานะการสั่งซื้อที่ยังไม่คอนเฟิร์มไม่ถือเป็นยอดจ่ายจริง

## v1.9.0 — GitHub เป็นฐานข้อมูล BOM กลางสำหรับทุกคอมพิวเตอร์

โปรแกรมทุกเครื่องอ่าน/บันทึก BOM, Wiring และ Purchasing จากไฟล์ bom-manager/bom.json ใน Repository เดียวกัน

วิธีใช้งาน:
1. ติดตั้งโปรแกรมในแต่ละคอมพิวเตอร์
2. ตั้ง GitHub Token (Repository Contents: Read and write) ในแต่ละเครื่องผ่านหน้า รายงาน / GitHub หากต้องการแก้ไขข้อมูล
3. เมื่อเปิดโปรแกรมจะดึงข้อมูลล่าสุด หากไม่มีฉบับร่างแก้ไขที่ยังไม่ส่ง
4. เมื่อเพิ่ม/แก้ไขข้อมูล จะบันทึกฉบับร่างในเครื่องทันที
5. ถ้าเปิด Auto Save (ค่าเริ่มต้น) จะส่ง GitHub Commit หลังหยุดแก้ไข ~90 วินาที
6. เครื่องอื่นที่ไม่มีข้อมูลค้างจะตรวจข้อมูลใหม่ทุก ~2 นาที หรือกด ซิงก์ข้อมูลตอนนี้ เพื่อรับทันที
7. หากพบการแก้ไขพร้อมกัน GitHub SHA จะป้องกันการบันทึกทับ และ Auto Save จะหยุดพร้อมเก็บฉบับร่างในเครื่อง
8. ก่อนยืนยันโหลด GitHub ทับฉบับร่าง โปรแกรมสำรองไฟล์ไว้ใน LOCALAPPDATA/CraneVehicleBOMManager/recovery

ข้อควรทราบ: ไม่ใช่ real-time collaborative editing แบบ Google Docs และไม่รวมการแก้ไขชนกันอัตโนมัติ
หากเครื่องยังไม่เคยโหลด BOM จาก GitHub เลย ต้องเชื่อมต่อก่อนจึงจะเปิดใช้ Auto Save ได้
GitHub Token อยู่ใน Windows Credential Manager แต่ละเครื่อง (ไม่เก็บบน GitHub หรือส่งผ่านแชท)
ทดสอบการซิงก์สองเครื่อง เน็ตหลุดและ Retry, SHA conflict และการกู้คืนใน tests/test_multi_pc_sync.py


## v1.9.2 — โหลดอัตโนมัติ / จัดซื้อไม่ซ้ำ / จัดลำดับเอง

- เปิดแอป Desktop: ดึงข้อมูลล่าสุดจาก GitHub อัตโนมัติ; ไม่มีอินเทอร์เน็ตจะยังใช้ฉบับร่างในเครื่องได้
- ถ้ามีฉบับร่างที่ยังไม่ส่ง GitHub แอปจะตรวจ SHA ของ GitHub ก่อนเสมอ ถ้าเปลี่ยนแล้วจะหยุด Auto Save และเก็บฉบับร่างไว้ ไม่เขียนทับจากหลายเครื่อง
- ในหน้า **จัดซื้อ** รายการอุปกรณ์ที่ถูกเลือกเข้าตารางจัดซื้อแล้วจะหายจากตัวเลือกเพิ่มรายการทันที; แก้ไขรายการจัดซื้อเดิมยังเลือกอุปกรณ์ของตัวเองได้ เมื่อรายการจัดซื้อถูกลบ อุปกรณ์จะกลับมาให้เลือกใหม่
- ในหน้า **BOM อุปกรณ์** เลือกแถวแล้วกด **↑ เลื่อนขึ้น / ↓ เลื่อนลง**; โหมดจัดกลุ่มเลื่อนภายในหมวดเดียวกัน ถ้าจะเรียงข้ามหมวดให้เลือก **แสดงรายการต่อเนื่อง**
- การเรียงเป็นการเปลี่ยนลำดับอาร์เรย์ items ใน `bom.json` ไม่แก้ BOM ID ทำให้ references ของ Wiring/Purchasing คงเดิม; ลำดับใหม่ซิงก์ไปเครื่องอื่นเมื่อ GitHub Auto Save สำเร็จ
- หน้าเว็บยังคงโหลด GitHub เมื่อเปิด และตรวจข้อมูลใหม่ทุก 2 นาทีเมื่อไม่มีการแก้ค้าง พร้อมปุ่ม ↑ ↓ สำหรับเรียงรายการภายในหมวด

## v1.10.0 — Procurement & Collaboration Tools

- Three-way GitHub merge compares the cached remote ancestor, local draft, and latest GitHub JSON. Independent field edits and newly added rows can merge automatically. True conflicts pause Auto Save and can be resolved through **เปรียบเทียบข้อมูล** with a backup before applying. Never force-push conflicting drafts.
- Purchase quantities: status **ได้รับบางส่วน**, editable **จำนวนรับจริง**, dashboard shows ordered/received counts and outstanding quantities. The default item selector hides already selected BOM IDs; an explicit **+ สั่งเพิ่มส่วนที่ขาด** flow allows further orders for missing quantities.
- BOM: manual ↑/↓ and drag/drop ordering persist as BOM JSON item order, without renumbering referenced IDs.
- Github history panel offers a restore action that imports a previous BOM file as a new local draft and preserves the current draft in a recovery backup.
- Dashboard shows known budget, recorded purchasing total and unpriced remaining components. Unknown prices are not assumed zero.
- **ตรวจสอบ BOM** audits item names, duplicate Part Numbers and names, unknown prices, suppliers, product links, wiring references, PO references and overordering.
- **นำเข้า Excel (.xlsx)** imports the BOM worksheet of standard .xlsx without executing macros or formulas, skips matching name+part-number pairs, and allocates fresh stable IDs when an imported ID would clash. Existing wiring and purchases are retained.
- **สร้างใบสั่งซื้อ PDF** exports a single selected PO/supplier as a clearly marked DRAFT with editable VAT, no invented vendor approval or signatures.
- Windows app and the existing browser page use the same GitHub JSON file. The browser-only BOM page remains a simpler editor; it does not yet have every Windows tool. Publishing GitHub Pages is separate from storing index.html in the repository.

**Manual verification before rollout:** build the Windows installer via GitHub Actions, review unit test results and run cross-PC acceptance tests with real credentials. A GitHub source commit alone is not proof that the installer is published.
