# Crane Vehicle Engineering Tool V53.6.2

## Web Dashboard Click Fix

แก้ปัญหาหน้าเว็บเปิดได้ แต่ปุ่ม/แท็บ/การ์ด Dashboard กดไม่ได้ทั้งหมด

### สาเหตุ
JavaScript ของหน้า Dashboard ใช้ single-element selector กับ `.forEach()`
ทำให้ script หยุดทำงานตั้งแต่ตอน bind ปุ่ม:
- Server status ค้างที่ "กำลังเชื่อมต่อ Server..."
- Version ค้างเป็น "-"
- Dashboard tabs กดไม่ได้
- Dashboard cards กดไม่ได้
- ปุ่มคำนวณทั้งหมดไม่ทำงาน

### แก้ไข
- เปลี่ยนการ bind tabs/pages/cards ให้ใช้ querySelectorAll helper (`$$`) ถูกต้อง
- เพิ่ม regression check ใน workflow เพื่อกัน bug แบบนี้กลับมาอีก

### ผลที่ควรเห็นหลังอัปเดต
- CVET WEB STATUS เปลี่ยนเป็น Server Online
- Version แสดงเลขเวอร์ชัน
- Dashboard tabs กดเปลี่ยนหน้าได้
- การ์ด Drive Torque / Main Battery / Winch / Stability / Vehicle Parameters / Live Telemetry / Project Summary กดได้
- ปุ่มคำนวณกลับมาทำงานตามปกติ
