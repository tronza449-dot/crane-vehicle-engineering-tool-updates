# Crane Vehicle Engineering Tool V53.8.30

## Simpler Stability Inputs + Green Desktop Completion Feedback

### Stability Mode A — Total Mass
ปรับให้ใช้งานง่ายขึ้นสำหรับผู้ใช้ที่ไม่ทราบตำแหน่ง CG:
- กรอกเฉพาะ Total mass, Payload, Boom และ Geometry
- ไม่ต้องกรอก Base vehicle CG x / y
- ไม่ต้องกรอก Driving combined CG x ในหน้า Stability
- โปรแกรมใช้ preliminary assumption อัตโนมัติ:
  - x_CG,V = 0 m
  - y_CG,V = 0 m
  - x_CG,drive = 0 m
- แสดงคำอธิบายว่ากำลังใช้ centered-CG assumption

### Stability Mode B — Component Mass
- ซ่อน Total mass / Payload / Boom manual inputs ที่ไม่ได้ใช้
- ซ่อน CG manual inputs
- ใช้มวลและ CG จาก Mass_CG table อัตโนมัติ
- หน้า Mass_CG จะแสดง Component table เฉพาะเมื่อ Mode B ทำงาน

### Unused-mode cleanup
- Mode A: Component table ถูกซ่อน เพราะไม่ได้เป็นแหล่งข้อมูล
- Mode B: manual mass fields ถูกซ่อน เพราะไม่ได้เป็นแหล่งข้อมูล
- เหลือเฉพาะ Input ที่เกี่ยวข้องกับโหมดปัจจุบัน

### Desktop button feedback
ปรับให้เห็นผลชัดเหมือน Web:
- Press: opacity animation
- Completed action: ปุ่มเปลี่ยนเป็นสีเขียว
- เพิ่มเครื่องหมาย ✓ ชั่วคราวบนข้อความปุ่ม
- Status bar แสดง “เสร็จแล้ว ✓”
- หลังประมาณ 0.9 s ปุ่มกลับเป็นหน้าตาเดิม
- ปุ่ม Mode / Navigation ไม่โดน completion flash เพื่อคง selected-state styling

### Regression
เพิ่มการตรวจว่า:
- Mode B ซ่อน manual fields และแสดง Component table
- Mode A แสดงเฉพาะ manual mass fields
- CG manual rows ถูกซ่อนทั้งสองโหมด
- Mode A บังคับ centered CG = 0 อัตโนมัติ
- Generic desktop action ต้องเข้าสถานะ success สีเขียวและมี ✓
