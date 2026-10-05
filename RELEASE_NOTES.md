# Crane Vehicle Engineering Tool V53.8.17

## Thai Formula + Substitution Upgrade

อัปเดตต่อจาก V53.8.16 ตามรูปแบบรายงานที่ต้องการให้อ่านง่ายสำหรับนำเสนออาจารย์:
กำลังหาอะไร → สูตร → ความหมาย → แทนค่า → ผลลัพธ์ → ใช้ตัดสินอะไร

### Stability / FBD
- Current-angle Snapshot เปลี่ยนหัวข้อเป็นภาษาไทยร่วมกับอังกฤษ
- ตารางตัวแปรเพิ่มคำอธิบายภาษาไทย
- Left / Right / Front / Rear แสดงทีละขั้น:
  1. หาโมเมนต์คว่ำ M_O
  2. หาโมเมนต์ต้าน M_R
  3. หา Safety Factor
- แสดงตัวเลขแทนค่าจริงของ F_i × d_i ก่อนรวมผล
- ระบุ PASS/FAIL พร้อมคำว่า ผ่าน/ไม่ผ่าน
- Slope อธิบายไทยแบบทีละขั้น:
  W_parallel, W_normal, F_I, d_R, M_O, M_R และ SF
- Critical-case FBD PDF เปลี่ยนหัวข้อเป็น
  สูตรและการแทนค่า / Equation and Substitution
- ตาราง Force / Moment arm / Moment / Role เป็นอังกฤษ + ไทย

### Main Battery 72 V
แท็บ "สูตร + แทนค่า / Calculation Steps" เขียนใหม่เป็นภาษาไทยแบบทีละขั้น:
1. แบ่งระยะ 1 Cycle
2. หาแรงและพลังงานทางราบ
3. หาแรงและพลังงานขึ้นทางลาด
4. หาแรงและพลังงานลงทางลาด
5. Differential / Pivot Turning Energy
6. รวมเที่ยวไป + เที่ยวกลับ + Turning + Auxiliary
7. หาเวลาต่อ Cycle และจำนวน Cycle
8. หาพลังงานรวม E_total
9. เผื่อ DoD + Reserve
10. แปลง Wh → Ah และใช้ Battery Design Factor Kb

ทุกขั้นมี:
- กำลังหาอะไร
- สูตร
- แทนค่าจริง
- ผลลัพธ์
- คำอธิบายว่าค่านั้นหมายถึงอะไร

### Battery PDF
- หัวรายงานเป็นภาษาไทย
- ใช้ Calculation Steps ชุดเดียวกับหน้าโปรแกรม
- แสดงคำตอบสุดท้ายสำหรับเลือกแบต:
  Ah_min → Ah_practical → Standard Ah
- ย้ำว่า Ah เป็นการเลือกความจุพลังงาน
  ส่วน BMS / Continuous current / Peak current / Fuse / Cable / VESC limit ต้องตรวจแยก

### Calculation scope
ไม่มีการเปลี่ยนสูตรหลักของ Stability หรือ Battery
การอัปเดตนี้เน้น presentation / explanation / substitution เท่านั้น
