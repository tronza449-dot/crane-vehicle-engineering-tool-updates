# Crane Vehicle Engineering Tool V53.3.4

## Operating Cycles — Vehicle + Winch

เพิ่มฟังก์ชันคำนวณจำนวนรอบการทำงานจริงในหน้า Winch โดยรวมเวลาวิ่งรถและเวลาวินช์ขึ้น/ลงเข้าด้วยกัน

### Operating logic
1 รอบไป-กลับ =
- วิ่งขาไป
- งานยกสัตว์ขาไป 1 งาน = Winch UP + Winch DOWN
- วิ่งขากลับ
- งานยกสัตว์ขากลับ 1 งาน = Winch UP + Winch DOWN

ค่าเริ่มต้น:
- Vehicle speed = 1 km/h
- One-way distance = 30 m
- Operating time = 3 h
- Lift events per round = 2
- Other stop time = 0 s

Load และ Lift Distance ใช้ค่าปัจจุบันจากหน้า Spec + Battery

### Calculated results
โปรแกรมคำนวณ:
- เวลาวิ่งเที่ยวเดียว
- เวลาวินช์ขึ้น
- เวลาวินช์ลง
- เวลา 1 งานยกสัตว์
- เวลาวิ่งไป-กลับ
- เวลางานยกรวมต่อรอบ
- เวลารวมต่อรอบ
- จำนวนรอบเชิงทฤษฎี
- จำนวนรอบไป-กลับที่ทำครบ
- จำนวนเที่ยวทางเดียว
- จำนวนงานยกสัตว์
- จำนวนครั้ง Winch UP
- จำนวนครั้ง Winch DOWN
- จำนวนการเคลื่อนที่วินช์รวม
- ระยะทางรวม
- เวลาที่ใช้จริง
- เวลาเหลือ

### Formula + substitution
หน้า Operating Cycles แสดงทุกขั้นในรูปแบบ:
สูตร → ความหมาย → แทนค่าตัวเลข → ผลลัพธ์

ตัวอย่าง:
t_up = (h / v_winch) × 60
= (1.5 / 3.1238) × 60
= 28.81 s

### Battery integration
เพิ่มปุ่ม:
“ใช้จำนวนงานยกนี้เป็น Battery Cycles”

เพราะ Battery Cycle ใน Winch calculator หมายถึง 1 รอบ Winch UP + DOWN ซึ่งตรงกับ 1 งานยกสัตว์ในฟังก์ชันนี้

### Conservative assumption
ใบสเปกไม่ได้ระบุ lowering speed/current แยก จึงใช้:
t_down = t_up

### Export PDF
Winch PDF รวม Operating Cycles report พร้อมสูตรและค่าที่แทนแล้ว
