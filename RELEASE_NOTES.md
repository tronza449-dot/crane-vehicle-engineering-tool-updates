# Crane Vehicle Engineering Tool V53.3.3

## Winch Formula Explanation + Calculation Summary

ปรับหน้า Winch ให้สูตรอ่านง่ายขึ้นสำหรับใช้ตรวจแบบและอธิบายอาจารย์

### สูตร + วิธีคำนวณ
ทุกขั้นแสดง 3 ส่วน:
- สูตรตัวแปร
- ความหมายภาษาไทยว่ากำลังเอาอะไรคูณ/หารกับอะไร
- แทนค่าปัจจุบันและคำตอบ

ตัวอย่าง:
- t_up = (h / v) × 60
- ความหมาย: เวลายกขึ้น = ระยะยก ÷ ความเร็วสลิง × 60
- h/v ได้หน่วยเป็นนาที และ ×60 เพื่อแปลงเป็นวินาที

เพิ่มคำอธิบายแบบเดียวกันให้:
- Interpolation factor
- Line speed interpolation
- Motor current interpolation
- Lift time
- Electrical power P = V × I
- Energy up/down
- Energy per cycle
- Total energy
- Ah used
- Design Ah with DoD + Reserve

### Calculation Summary
เพิ่มแท็บ “สรุปการคำนวณ” ในหน้า Winch โดยรวม:
- Input: Load / Lift Distance / Cycles
- ค่าที่ได้จาก Datasheet / interpolation
- เวลาขึ้น / เวลาลง / เวลาต่อรอบ
- E_up / E_down / E_cycle / E_total
- Ah ก่อนเผื่อ
- DoD / Reserve
- Ah_design
- Standard battery size
- Extra-margin battery size
- Rope Layer / Line Pull / Status
- ข้อสรุปขนาดแบตเชิงพลังงานและข้อควรตรวจเรื่องกระแส/BMS

### Winch tabs
1. Spec + Battery
2. สูตร + วิธีคำนวณ
3. ตัวแปร / Variables
4. สรุปการคำนวณ

### Live update
ทั้ง Formula, Variables และ Calculation Summary จะอัปเดตอัตโนมัติเมื่อเปลี่ยน:
- Load
- Lift Distance
- Cycles

### Export PDF
Winch PDF รวม Calculation Summary, Formula, Specification และ Variable Table
