# Crane Vehicle Engineering Tool V53.3.2

## Winch Formula + Calculation Pages

เพิ่มหน้าสูตรและวิธีคำนวณในเมนู Winch ให้รูปแบบใกล้เคียงกับโมดูลคำนวณอื่นของโปรแกรม

### Winch tabs
1. Spec + Battery
   - ใบสเปก 4500LB
   - Load / Lift Distance / Cycles
   - ตาราง First Layer
   - ตาราง Rope Layer
   - ผล Battery Wh / Ah

2. สูตร + วิธีคำนวณ
   - เลือกช่วงข้อมูล First Layer ที่คร่อม Load
   - Linear interpolation factor
   - Interpolated line speed
   - Interpolated motor current
   - Lift time
   - Electrical power P = VI
   - Energy up/down
   - Energy per cycle
   - Total energy
   - Ah before reserve
   - Design Ah with DoD + Reserve
   - Standard battery size
   - Rope layer / line-pull check

3. ตัวแปร / Variables
   - ความหมาย
   - หน่วย
   - ค่าปัจจุบัน
   - ใช้ในสูตรใด

### Live recalculation
หน้า Formula และ Variables อัปเดตอัตโนมัติเมื่อเปลี่ยน:
- Load
- Lift Distance
- Cycles

ทุกขั้นแสดงรูปแบบ:
สูตรตัวแปร → แทนค่าปัจจุบัน → คำตอบ

### Source / assumption separation
- Speed และ Current มาจาก First-layer performance table ในใบสเปกที่ผู้ใช้ส่งมา
- ค่าระหว่างจุดในตารางใช้ linear interpolation
- ใบสเปกไม่ให้ข้อมูล lowering current/speed จึงใช้ค่าเท่าขาขึ้นแบบ conservative
- First-layer speed/current อาจไม่แทนพฤติกรรมบน rope layer สูงกว่าได้ทั้งหมด
- Starting / stall surge ยังไม่ระบุและต้องตรวจจริงก่อนเลือก BMS/fuse/cable ขั้นสุดท้าย

### Export PDF
Winch PDF ตอนนี้รวม:
- สูตร + วิธีคำนวณ
- Specification / Battery summary
- Variable table
