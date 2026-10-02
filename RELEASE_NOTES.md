# Crane Vehicle Engineering Tool V53.4.1

## Web Server Launcher — เห็นและเปิดจากโปรแกรมหลักได้โดยตรง

แก้ปัญหาที่ V53.4.0 มี Web Server แต่ผู้ใช้หาเมนูเปิดเว็บไม่เจอ

### หน้า Home
เพิ่มแผงใหม่:
WEB SERVER • PUBLIC INTERNET

มีปุ่ม:
- เปิด Web Server
- วิธีใช้

### เมื่อกด “เปิด Web Server”
โปรแกรมให้เลือก 3 โหมด:
1. PUBLIC INTERNET — คนนอก Wi-Fi เข้าได้
2. LAN / Wi-Fi — เครือข่ายเดียวกัน
3. LOCAL — ใช้เฉพาะเครื่องนี้

### PUBLIC INTERNET
- ถาม Web PIN ก่อนเปิด (เว้นว่างได้)
- เปิด CraneVehicleWebServer.exe ในหน้าต่างใหม่
- เปิด FastAPI Server บนเครื่องผู้ใช้
- สร้าง Cloudflare Quick Tunnel
- เมื่อได้ลิงก์ https://xxxxx.trycloudflare.com โปรแกรม Web Server จะเปิด Browser อัตโนมัติ
- ส่งลิงก์ให้คนอื่นเข้าได้จากอินเทอร์เน็ตภายนอก

### Installer
เพิ่ม Shortcut “Crane Vehicle Web Server” ทั้ง:
- Start Menu
- Desktop

### Safety / Usability
- ถ้าไฟล์ Web Server ไม่พบ โปรแกรมแจ้งให้อัปเดต/ติดตั้งใหม่
- หน้าต่าง Web Server ต้องเปิดค้างไว้ขณะให้คนอื่นใช้งาน
- Public URL แบบ Quick Tunnel จะเปลี่ยนเมื่อปิดแล้วเปิด Server ใหม่

### Regression
เพิ่มการตรวจว่าหน้า Home มีปุ่ม “เปิด Web Server” จริง และ Source mode หา web_launcher.py ได้
