# Crane Vehicle Engineering Tool — Update Channel

Repository นี้ใช้เป็นช่องทางตรวจสอบและแจกจ่ายเวอร์ชันใหม่ของ **Crane Vehicle Engineering Tool**

## Current version
- **V53.8.26**

## Main additions
- ESP32 DevKit V1 / ESP-WROOM-32 as current project controller target
- ESP32 / VESC Hardware I/O Manager
- Animated GPIO board / Custom I/O Builder
- Real-Time ESP32 Telemetry over USB Serial
- Live Current / Speed / Tilt graphs
- CSV Data Logger
- ESP32 telemetry sender template


## Free Permanent Web Link

V53.5.1 เพิ่ม Tailscale Funnel สำหรับลิงก์ HTTPS แบบใช้ซ้ำได้ฟรี เช่น `https://cvet.<tailnet>.ts.net`

- ไม่ต้องซื้อ Domain
- ไม่ต้อง Port Forward
- Web PIN ยังใช้ได้
- Cloudflare Quick Tunnel เดิมยังอยู่เป็นตัวเลือกสำรอง

## Web Server
V53.4.0 เพิ่ม **CraneVehicleWebServer.exe** สำหรับเปิดโปรแกรมเป็น Web App โดยใช้เครื่อง Windows ของผู้ใช้เป็น Server

โหมดหลัก:
- Local: ใช้เฉพาะเครื่อง Server
- LAN: เครื่องอื่นใน Wi-Fi/LAN เดียวกันเข้าได้
- Public Internet: สร้างลิงก์ HTTPS ผ่าน Cloudflare Quick Tunnel โดยไม่ต้อง Port Forward Router

Web Calculator รองรับ Drive Torque, Main Battery 72 V, Winch + Auto/Manual Lift Events และ Stability / Tipping พร้อมตารางสูตร-แทนค่า-ผลลัพธ์แบบละเอียด

ดูวิธีใช้งานเพิ่มเติมที่ `README_WEB.md`

## Manifest URL ที่โปรแกรมใช้
`https://raw.githubusercontent.com/tronza449-dot/crane-vehicle-engineering-tool-updates/main/latest.json`

## Stable Setup URL
`https://github.com/tronza449-dot/crane-vehicle-engineering-tool-updates/releases/latest/download/CraneVehicleEngineeringTool_Setup.exe`

โปรแกรมจะอ่าน `latest.json` แล้วเปรียบเทียบ `latest_version` กับเวอร์ชันที่ติดตั้งอยู่ในเครื่อง

ถ้าเวอร์ชันบน GitHub ใหม่กว่า โปรแกรมจะ:
1. แจ้งว่ามี Update
2. ดาวน์โหลด Setup.exe จาก GitHub Release
3. ตรวจ SHA256 เมื่อมีค่า
4. ปิดโปรแกรมและเรียก Installer เพื่ออัปเดตทับเวอร์ชันเดิม

## สำหรับเวอร์ชันใหม่
ทุกครั้งที่มี Release ใหม่ต้อง:
- เปลี่ยน `latest_version`
- อัปโหลดไฟล์ Release asset ชื่อ **CraneVehicleEngineeringTool_Setup.exe**
- ใส่ SHA256 ของ Setup.exe
- ใส่ Release notes

> ตอนนี้ตัว Update Channel ถูกผูกกับ GitHub แล้ว แต่ Stable Setup URL จะใช้งานได้หลังจากมี GitHub Release ที่แนบไฟล์ `CraneVehicleEngineeringTool_Setup.exe` อย่างน้อย 1 ครั้ง
