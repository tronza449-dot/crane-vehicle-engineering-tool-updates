# Crane Vehicle Engineering Tool V53.3.6

## Winch Calculation Cleanup — Single Source of Truth

ปรับโครงสร้างหน้า Winch เพื่อตัดการคำนวณซ้ำซ้อนระหว่าง Spec, Formula, Summary และ Battery

### New data flow
Datasheet → Operating Cycles → Battery → Summary

### Visible Winch tabs
1. Spec / Datasheet
2. สูตร + วิธีคำนวณ
3. รอบการทำงาน / 3h
4. Battery / แบตวินช์
5. สรุป / Summary

### Spec / Datasheet
- แก้ได้เฉพาะ Load และ Lift Distance
- แสดง First Layer interpolation
- แสดง Up speed / Up current / Up time
- แสดง Rope Layer / Line Pull check
- ยกเลิกการคำนวณ Wh / Ah / Battery Cycles ในหน้านี้

### Operating Cycles
เป็นแหล่งข้อมูลหลักสำหรับจำนวนงานยก:
- Vehicle speed
- One-way distance
- Operating time
- Lift events per round
- Other stop time
- Completed round trips
- One-way trips
- Lift events
- Winch UP / DOWN counts
- Total distance / remaining time

จำนวนงานยกถูกส่งไปหน้า Battery อัตโนมัติเมื่อเปิด Use Operating Cycles

### Battery
เป็นตัวคำนวณพลังงานและ Ah หลักเพียงชุดเดียว:
- E_up
- E_down
- E_event
- E_total
- Ah_used
- Ah_design
- Standard Ah
- Candidate Battery / BMS check

รองรับ Conservative และ Measured / Custom DOWN เหมือน V53.3.5

### Formula
หน้า Formula ไม่สร้าง Battery calculation แยกอีกชุด
แต่แสดงสูตรและแทนค่าจากผล Datasheet + Operating Cycles + Battery ชุดเดียวกัน

### Summary
หน้า Summary ไม่คำนวณใหม่
แสดงผลรวมจากแหล่งข้อมูลเดียว:
- Load / Lift
- First-layer speed/current
- Rope layer
- UP/DOWN time
- Completed round trips
- Lift events
- Winch movements
- Total Wh
- Ah used / Ah design
- Standard battery size
- Candidate battery status

### Compatibility
ตัวแปรและ compatibility widgets เก่ายังคงอยู่ภายในเพื่อไม่ทำให้โมดูลอื่นเสีย
แต่ไม่แสดงเป็นหน้าคำนวณซ้ำใน Winch UI

### PDF
จัดรายงานเป็น:
Summary → Datasheet → Operating Cycles → Battery → Formula → Variables
โดย Battery totals มาจาก calculator หลักชุดเดียว
