# Crane Vehicle Engineering Tool V53.8.21

## Button Feedback / Animation Upgrade

แก้ปัญหากดปุ่มแล้วไม่รู้ว่าคำสั่งถูกกดหรือทำงานเสร็จหรือยัง ทั้ง Desktop และ Web

### Desktop
ปุ่มทุกปุ่มมี visual feedback ทันทีเมื่อกด:
- Pressed state ชัดขึ้น
- ขอบ/พื้นหลังเปลี่ยนทันที
- Status bar แสดง “รับคำสั่งแล้ว ✓” สำหรับปุ่มทั่วไป

ปุ่ม Ramp Geometry มีสถานะแบบเต็ม:
- กำลังคำนวณ...
- คำนวณเสร็จ ✓
- กำลังใช้ค่า...
- ใช้มุมแล้ว ✓
- ใช้ระยะแล้ว ✓
- Error state สีแดงเมื่อเกิดข้อผิดพลาด

ปุ่ม Apply ที่ปรับ:
- ใช้มุมกับ Torque + Main Battery + Stability
- ใช้ L ทฤษฎีกับ Slope Length ใน Main Battery

### Web
เพิ่ม feedback animation สำหรับปุ่มทั่วทั้งเว็บ:
- กดยุบ/scale ลงเล็กน้อย
- pulse เมื่อรับ click
- Busy state สีเหลืองพร้อม spinner
- Success state สีเขียว
- Error state สีแดง
- Toast ยืนยันผลด้านล่างหน้าจอ

ปุ่มคำนวณหลักแสดง Busy → Success/Error:
- Drive Torque
- Ramp Geometry
- Main Battery
- Winch
- Stability + FBD

ปุ่ม Ramp Apply แสดงผลชัดเจน:
- “กำลังใช้ค่า...”
- “ใช้มุมแล้ว ✓”
- “ใช้ระยะแล้ว ✓”
- Toast บอกค่าที่ถูกนำไปใช้จริง

### Regression
- Python/UI/PDF regression เดิมยังทำงาน
- Node syntax check สำหรับ web/app.js
- ตรวจ helper feedback ของ Desktop
- ตรวจ helper/CSS animation ของ Web

### Calculation scope
ไม่มีการเปลี่ยนสูตรคำนวณหลัก
เป็น UX/feedback upgrade เท่านั้น
