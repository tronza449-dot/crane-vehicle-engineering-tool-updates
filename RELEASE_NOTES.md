# Crane Vehicle Engineering Tool V53.5.1

## Free Permanent Web Link — Tailscale Funnel

อัปเดตรอบนี้เพิ่มโหมดลิงก์เว็บถาวรฟรี โดยไม่ต้องซื้อ Domain และไม่ต้องใช้ลิงก์สุ่มของ Cloudflare ทุกครั้ง

### โหมดใหม่
เพิ่มตัวเลือกในโปรแกรมหลัก:
1. FREE PERMANENT LINK — Tailscale Funnel (*.ts.net) [แนะนำ]
2. QUICK PUBLIC LINK — Cloudflare (ลิงก์สุ่ม)
3. LAN / Wi-Fi
4. LOCAL

### FREE PERMANENT LINK
- ใช้ Tailscale Funnel
- ได้ HTTPS อัตโนมัติ
- ไม่ต้อง Port Forward Router
- ไม่ต้องซื้อ Domain
- ตั้งชื่อเครื่อง Tailscale เป็น `cvet`
- ลิงก์จะมีรูปแบบประมาณ `https://cvet.<tailnet>.ts.net`
- ลิงก์เดิมสามารถใช้ซ้ำได้ตราบใดที่ยังใช้ Tailnet และชื่อเครื่องเดิม

### First-time Setup
ครั้งแรกเท่านั้น:
- โปรแกรมตรวจหา Tailscale
- ถ้ายังไม่มี จะลองติดตั้งผ่าน winget
- ถ้าติดตั้งอัตโนมัติไม่ได้ จะเปิดหน้าดาวน์โหลด Tailscale ทางการ
- Login Tailscale ฟรี
- อนุญาต Funnel หนึ่งครั้ง
- หลังจากนั้นเปิด Permanent Link ได้จากโปรแกรมโดยตรง

### Security
- Web PIN ยังใช้ได้เหมือนเดิม
- แนะนำให้ตั้ง PIN เมื่อนำลิงก์ออกอินเทอร์เน็ต

### Compatibility
- Cloudflare Quick Tunnel เดิมยังใช้งานได้
- LAN และ Local mode ยังใช้งานได้
- Web Calculators แบบละเอียดจาก V53.5.0 ยังอยู่ครบ
