# CVET Web Server

Crane Vehicle Engineering Tool สามารถรันเป็น Web App โดยใช้เครื่อง Windows ของผู้ใช้เป็น Server

## โหมดการใช้งาน

### 1. PUBLIC INTERNET
เปิด CraneVehicleWebServer.exe แล้วเลือก 1

โปรแกรมจะ:
1. เปิด FastAPI Web Server ที่เครื่องนี้
2. ดาวน์โหลด cloudflared.exe จาก GitHub ทางการของ Cloudflare ถ้ายังไม่มี
3. เปิด Cloudflare Quick Tunnel
4. แสดงลิงก์ HTTPS แบบ https://xxxxx.trycloudflare.com
5. คนอื่นสามารถเปิดลิงก์จากมือถือหรือคอมผ่านอินเทอร์เน็ตภายนอกได้

ไม่ต้อง Port Forward Router

ถ้าต้องการ PIN ให้กรอกตอนเปิด Public mode

### 2. LAN / Wi-Fi
เลือก 2

เครื่องอื่นใน Wi-Fi/LAN เดียวกันเข้าได้จาก:
http://<IP-เครื่อง-server>:8000

### 3. LOCAL
เลือก 3

ใช้เฉพาะเครื่อง Server:
http://127.0.0.1:8000

## Web Calculators

- Drive Torque
- Main Battery 72 V
- Winch Datasheet interpolation
- Operating Cycles / 3 h
- Winch Battery Auto / Manual lift events
- Crane Stability / Tipping

## Winch Manual Mode

หน้า Winch มี:
- Auto — ใช้จำนวนงานยกจาก Operating Cycles
- Manual — กำหนดจำนวนงานยกเอง

นิยาม:
1 งานยก = Winch UP 1 ครั้ง + Winch DOWN 1 ครั้ง

## Security

ตั้ง Web PIN ได้:
CraneVehicleWebServer.exe --public --pin 123456

หรือจำกัดอีเมลด้วย Cloudflare Quick Tunnel:
CraneVehicleWebServer.exe --public --allowed-mail user@example.com

## Source mode

ติดตั้ง dependency:
pip install -r requirements-web.txt

เปิด Public:
python web_launcher.py --public

เปิด LAN:
python web_launcher.py --lan

## Important

- เครื่อง Server ต้องเปิดอยู่ตลอดเวลาที่ต้องการให้เว็บเข้าได้
- Quick Tunnel URL จะเปลี่ยนเมื่อปิดแล้วเปิดใหม่
- Quick Tunnel เหมาะกับการทดสอบ/แชร์ชั่วคราว
- ถ้าต้องการ URL คงที่ เช่น https://crane.example.com ให้สร้าง Named Cloudflare Tunnel + Domain ในขั้นถัดไป
