# Crane Vehicle Engineering Tool V53.5.4

## Permanent Link Name Fix

แก้ปัญหา Tailscale Funnel เปิดได้แล้ว แต่ชื่อด้านหน้าของ URL ยังไม่เปลี่ยนตามที่ต้องการ

### สิ่งที่เพิ่ม
- ก่อนเปิด FREE PERMANENT LINK โปรแกรมจะถามชื่อ Web Link
- ค่าเริ่มต้นคือ `cvet`
- ตัวอย่าง:
  `https://cvet.<tailnet>.ts.net`
- โปรแกรมเรียก `tailscale set --hostname=<name>`
- ตรวจสอบผลจริงจาก MagicDNS หลังเปลี่ยนชื่อ
- ถ้าเปลี่ยนอัตโนมัติไม่สำเร็จ โปรแกรมจะเปิดหน้า Tailscale Machines ให้อัตโนมัติ เพื่อให้แก้ชื่อเครื่องเองครั้งเดียว
- หน้า CVET แสดงสถานะว่าการเปลี่ยนชื่อสำเร็จหรือมีคำเตือน

### ข้อจำกัดของ Tailscale Free Link
แก้ได้เฉพาะชื่อเครื่องด้านหน้า เช่น `cvet`
ส่วน `<tailnet>.ts.net` เป็นโดเมนของ Tailscale และจะยังคงอยู่
