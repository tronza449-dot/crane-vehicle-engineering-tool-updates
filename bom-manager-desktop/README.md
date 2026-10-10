# Crane Vehicle BOM Manager (Windows Desktop)

แอปเดสก์ท็อปสำหรับดูและแก้ BOM โดยใช้ข้อมูลชุดเดียวกับหน้าเว็บ `bom-manager/` ใน GitHub repository นี้

## ติดตั้ง

ดาวน์โหลด `CraneVehicleBOMManager_Setup.exe` จากแท็บ **Actions → Build BOM Manager Desktop → Artifacts** ใน GitHub แล้วดับเบิลคลิกติดตั้ง ตัวติดตั้งสร้างไอคอนบน Desktop และ Start Menu

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
python -m pip install pyinstaller keyring
pyinstaller --noconfirm --clean --windowed --name CraneVehicleBOMManager --collect-all keyring app.py
& "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" installer.iss
```

ตัวติดตั้งจะอยู่ใน `output/CraneVehicleBOMManager_Setup.exe`
