# CVET Web Server

Crane Vehicle Engineering Tool สามารถรันเป็น Web App โดยใช้เครื่อง Windows ของผู้ใช้เป็น Server

## โหมดแนะนำ — FREE PERMANENT LINK

ใช้ Tailscale Funnel เพื่อให้ได้ลิงก์ HTTPS ที่ใช้ซ้ำได้โดยไม่ต้องซื้อ Domain

ลิงก์จะมีรูปแบบประมาณ:

`https://cvet.<tailnet>.ts.net`

ครั้งแรก:
1. เปิดโปรแกรม CVET
2. กด `เปิด Web Server`
3. เลือก `FREE PERMANENT LINK — Tailscale Funnel`
4. ถ้ายังไม่มี Tailscale โปรแกรมจะช่วยเปิดขั้นตอนติดตั้ง
5. Login Tailscale ฟรี
6. อนุญาต Funnel หนึ่งครั้ง
7. Browser จะเปิดลิงก์ HTTPS ให้

ครั้งถัดไปใช้ลิงก์เดิมได้ ตราบใดที่ยังใช้ Tailnet และชื่อเครื่องเดิม

หมายเหตุ:
- เครื่อง Server ต้องเปิด CVET Web Server อยู่ขณะใช้งาน
- Tailscale ต้องทำงานอยู่
- แนะนำตั้ง Web PIN

## QUICK PUBLIC LINK — Cloudflare

ใช้สำหรับแชร์ชั่วคราวผ่าน `trycloudflare.com`

ข้อดี:
- เปิดง่าย
- ไม่ต้อง Login Tailscale

ข้อจำกัด:
- URL เปลี่ยนเมื่อปิดแล้วเปิดใหม่

## LAN / Wi-Fi

เครื่องอื่นใน Wi-Fi/LAN เดียวกันเข้าได้จาก:

`http://<IP-เครื่อง-server>:8000`

## LOCAL

ใช้เฉพาะเครื่อง Server:

`http://127.0.0.1:8000`

## Web Calculators

- Drive Torque
- Main Battery 72 V — แบตรถ: Drive + Auxiliary เท่านั้น
- Winch / Lift — Datasheet interpolation + UP/DOWN + Operating Cycles
- Winch Battery 12 V — แบตแยกสำหรับวินช์, Auto / Manual lift events
- Crane Stability / Tipping
- ตารางสูตร / แทนค่า / ผลลัพธ์ / หน่วย / คำอธิบายแบบละเอียด

### Battery systems are separate

- **Main Battery 72 V:** ใช้กับระบบขับเคลื่อนรถและ Auxiliary
- **Winch Battery 12 V:** ใช้กับวินช์ขึ้น/ลง
- พลังงาน Wh/Ah ของวินช์ **ไม่ถูกบวก** เข้า Main Battery 72 V
- ข้อมูลที่แชร์กันมีเฉพาะ **เวลา UP/DOWN / เวลา 1 งานยก** เพื่อใช้หา Operating Cycle ของรถให้สมจริง

## Security

ตั้ง Web PIN ได้ทั้ง Permanent Link และ Quick Public Link

ตัวอย่าง Source mode:

`python web_launcher.py --tailscale --tailscale-hostname cvet --pin 123456`

## Source mode

ติดตั้ง dependency:

`pip install -r requirements-web.txt`

เปิด Permanent Link:

`python web_launcher.py --tailscale --tailscale-hostname cvet`

เปิด Quick Public:

`python web_launcher.py --public`

เปิด LAN:

`python web_launcher.py --lan`
