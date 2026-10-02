# Crane Vehicle Engineering Tool V53.4.0

## Web Server — ใช้เครื่องของคุณเป็น Server ได้แล้ว

เพิ่ม Web App สำหรับคนที่ไม่มีโปรแกรม Desktop ให้เปิดผ่าน Browser แล้วคำนวณได้ โดยเครื่อง Windows ของคุณเป็น Server

### ไฟล์ใหม่
- CraneVehicleWebServer.exe
- ติดตั้งรวมมากับ CraneVehicleEngineeringTool_Setup.exe
- มี Shortcut ใน Start Menu ชื่อ Crane Vehicle Web Server

### โหมด Web Server
1. PUBLIC INTERNET
- เปิด CraneVehicleWebServer.exe แล้วเลือก 1
- โปรแกรมเปิด FastAPI Server ที่เครื่องคุณ
- ถ้ายังไม่มี cloudflared โปรแกรมจะดาวน์โหลดจาก GitHub ทางการของ Cloudflare
- สร้าง HTTPS Quick Tunnel
- ได้ลิงก์รูปแบบ https://xxxxx.trycloudflare.com
- ส่งลิงก์ให้คนอื่นเปิดจากมือถือหรือคอมผ่านอินเทอร์เน็ตภายนอกได้
- ไม่ต้อง Port Forward Router

2. LAN / Wi-Fi
- เลือก 2
- เครื่องในเครือข่ายเดียวกันเปิดผ่าน IP ของเครื่อง Server

3. LOCAL
- เลือก 3
- ใช้เฉพาะเครื่อง Server

### Web PIN
Public mode สามารถตั้ง PIN ได้
ผู้ที่มีลิงก์ต้องกรอก PIN ก่อนใช้ API คำนวณ

### Web Calculators
- Drive Torque
- Main Battery 72 V
- Winch Datasheet interpolation
- Operating Cycles / 3 h
- Winch Battery
- Auto / Manual Lift Events
- Crane Stability / Tipping

### Winch Manual Events
- Auto = ใช้จำนวนงานยกจากรอบการทำงาน
- Manual = ผู้ใช้กำหนดจำนวนงานยกเอง
- 1 งานยก = Winch UP 1 ครั้ง + Winch DOWN 1 ครั้ง

### สูตรภาษาไทย
หน้า Web แสดง:
- สูตรตัวแปร
- สูตรภาษาไทย
- แทนค่า
- ผลลัพธ์

### Web Calculation Engine
เพิ่ม web_engine.py เป็น Pure Python calculation layer สำหรับ Web โดยไม่มี Qt dependency
Regression Test ตรวจค่าหลักกับ Project baseline เช่น:
- 100 kg
- Lift 1.5 m
- 1 km/h
- 30 m one-way
- 3 h
- Conservative Down
- 32 รอบไป-กลับ
- 64 งานยก

### Public access
Public mode ใช้ Cloudflare Quick Tunnel ดังนั้น URL จะเปลี่ยนเมื่อปิดแล้วเปิด Server ใหม่
ถ้าต้องการ URL คงที่แบบโดเมนจริง สามารถต่อยอดเป็น Named Cloudflare Tunnel ได้ภายหลัง

### Installer / Release
Release มี 2 ไฟล์:
- CraneVehicleEngineeringTool_Setup.exe
- CraneVehicleWebServer.exe

Setup.exe ติดตั้งทั้ง Desktop App และ Web Server
