# Crane Vehicle BOM Manager (Windows Desktop)

แอปเดสก์ท็อปสำหรับดูและแก้ BOM โดยใช้ข้อมูลชุดเดียวกับหน้าเว็บ `bom-manager/` ใน GitHub repository นี้

## ติดตั้ง

ดาวน์โหลด `CraneVehicleBOMManager_Setup.exe` จาก **GitHub Releases → Crane Vehicle BOM Manager** (`bom-v*`) หรือแท็บ **Actions → Build BOM Manager Desktop → Artifacts** แล้วดับเบิลคลิกติดตั้ง ตัวติดตั้งสร้างไอคอนบน Desktop และ Start Menu

## วิธีใช้

1. เปิดโปรแกรม แล้วกด **ตั้งค่า GitHub Token** ครั้งแรก
2. สร้าง Fine-grained personal access token โดยเลือกเฉพาะ repository `crane-vehicle-engineering-tool-updates` และให้สิทธิ์ **Contents: Read and write**
3. วาง token โปรแกรมจะทดสอบการอ่าน BOM และเก็บ token ใน Windows Credential Manager
4. เพิ่ม/แก้/ลบรายการ แล้วกด **บันทึกขึ้น GitHub** เพื่อสร้าง commit ไปยัง `bom-manager/bom.json`
5. กด **โหลดจาก GitHub** เพื่อดึงข้อมูลล่าสุดที่มีคนแก้จากหน้าเว็บหรือ GitHub

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
