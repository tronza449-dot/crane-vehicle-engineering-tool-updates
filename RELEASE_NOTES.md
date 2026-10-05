# Crane Vehicle Engineering Tool V53.8.15

## Final Stability Report Polish

อัปเดตต่อจาก V53.8.14 หลังตรวจ PDF จริงครบ 11 หน้า

### Summary
- เพิ่ม Current-angle governing case
- แสดง SF และ PASS/FAIL ของมุมปัจจุบันแยกจาก Worst critical-case
- ทำให้เห็นทันทีว่ามุมที่กำลังใช้งานอยู่ปลอดภัยตาม Required SF หรือไม่

### Current-angle appendix
- แต่ละ Left / Right / Front / Rear case แสดง Current-angle status: PASS / FAIL
- ไม่ต้องเทียบค่า SF กับ Required SF เอง

### FBD readability
- เพิ่มขนาดตัวอักษรเฉพาะ exported FBD ประมาณ 16% เพื่ออ่านบน A4 ได้ง่ายขึ้น
- Interactive compact view ไม่ถูกขยายตาม
- Slope legend เพิ่ม Purple = Inertia F_I

### 3D report figure
- ตัดข้อความ LEFT LIMIT / CENTER / RIGHT LIMIT ออกจาก scene เพื่อลดข้อความทับตัวรถ
- คง endpoint markers และ CURRENT θ ที่ active boom
- Render รูป Vehicle สำหรับ PDF ที่ขนาดคงที่ ไม่ขึ้นกับขนาดหน้าต่างโปรแกรมขณะ Export

### Stability Map
- Render สำหรับ PDF ที่ 1100×650
- เพิ่มเส้น dashed ที่ Current crane angle
- เพิ่มจุดและข้อความ Current governing case / SF
- Worst critical point และ Target SF ยังอยู่เหมือนเดิม
- ถ้าค่า SF ถูก clip จะมี display note

### Worst-case appendix
เปลี่ยนคำอธิบายจำนวนการคำนวณเป็น:
181 angles × 4 tipping directions = 724 directional moment-balance evaluations

### Calculation scope
ไม่มีการเปลี่ยนสูตร stability หลัก
ตัวเลขยังมาจาก side_moment_balance, longitudinal_moment_balance และ slope_stability_results เดิม
