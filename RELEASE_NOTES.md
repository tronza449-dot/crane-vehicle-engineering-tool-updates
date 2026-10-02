# Crane Vehicle Engineering Tool V53.6.0

## Main 72 V Battery — Operating Time Correction

แก้การคำนวณ **แบตรถ 72 V** ให้ใช้เวลาการทำงานจริงของรถ ไม่ใช่สมมติว่ารถวิ่งตลอด 3 ชั่วโมง

### หลักการใหม่
1 รอบการทำงาน =
- เวลารถวิ่งไป-กลับ
- เวลางานยกทั้งหมดในรอบ
- เวลาหยุดอื่น

จำนวนรอบที่ใช้คำนวณพลังงานขับ:
`N = floor(T_operating / T_round)`

### แยก Main Battery กับ Winch Battery ชัดเจน
- เวลายกมีผลต่อ **จำนวนรอบที่รถสามารถวิ่งได้**
- แต่พลังงานของวินช์ **ไม่ถูกนำมารวมใน Main Battery 72 V**
- เพราะโปรเจกต์ใช้แบตวินช์ 12 V แยก

ดังนั้น:
`E_main = E_drive_per_round × N_completed + E_aux`

แล้ว:
`E_design = (E_main / DoD) × (1 + Reserve)`

`Ah_required = E_design / V_battery`

### Desktop CVET
- เพิ่มตัวเลือก **รวมเวลายกจาก Winch Operating Cycles อัตโนมัติ**
- ค่าเริ่มต้นเปิดใช้งาน
- Main Battery จะอ่านเวลา 1 งานยกและจำนวนงานยก/รอบจากหน้า Winch
- เมื่อค่า Winch Operating Cycles เปลี่ยน Main Battery จะคำนวณตามใหม่
- แสดง Drive time / Lift time / Other stop / Total round time
- แสดงทั้งจำนวนรอบเชิงทฤษฎีและจำนวนรอบเต็มที่ทำได้จริง

### Web
- Main Battery เพิ่ม:
  - เวลา 1 งานยก
  - งานยกต่อรอบ
  - เวลาหยุดอื่นต่อรอบ
- หลังคำนวณหน้า Winch ค่าเวลางานยกจะ Sync ไปหน้า Main Battery อัตโนมัติ
- แสดงจำนวนรอบเต็มและ Time Breakdown
- ระบุชัดว่า Winch energy ไม่รวมใน Main Battery

### Regression
กรณีทดสอบ:
- Vehicle speed 1 km/h
- One-way 30 m
- Operating time 3 h
- 2 lift events / round
- Lift event ≈ 57.62 s

ได้เวลาต่อรอบ ≈ 331.24 s และทำได้ **32 รอบเต็ม**
