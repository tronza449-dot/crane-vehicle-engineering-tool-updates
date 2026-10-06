# Crane Vehicle Engineering Tool V53.8.25

## Web Stability — Units + Variable Dictionary

เพิ่มหน่วยวิศวกรรมและตารางตัวแปรให้หน้า Stability อ่านง่ายและใช้เป็นเอกสารประกอบการนำเสนอได้ชัดเจนขึ้น

### Variable + Unit table
เพิ่มตารางก่อนผล Stability:
- ตัวแปร
- ความหมาย
- ค่า
- หน่วย
- แหล่งที่มา (Input / Derived / Constant / Calculated)

ครอบคลุมตัวแปรหลัก:
- m_total, m_V, m_L, m_B → kg
- W, WB, L, x_CG,V, y_CG,V, d_R, h_CG → m
- θ, α → deg
- a, g → m/s²
- M_O, M_R → N·m
- Kdyn, SF_req, SF → ไม่มีหน่วย

### Unit Convention
เพิ่มกล่องสรุปมาตรฐานหน่วย:
Mass = kg
Distance = m
Force = N
Moment = N·m
Angle = deg
Acceleration = m/s²
Safety Factor = ไม่มีหน่วย

### Guided calculation
- ตาราง Step 1 ระบุหัวคอลัมน์ Force (N), Position (m), Arm (m) ชัดเจน
- Step 2/3 แสดง M_O และ M_R เป็น N·m
- Step 4 แสดงการตัดหน่วย N·m / N·m และระบุว่า SF ไม่มีหน่วย
- Metric cards ระบุ SF เป็น dimensionless

### Component Mass
- ปรับหัวตารางเป็น Mass (kg), x (m), y (m), z (m)

### Regression
- ตรวจว่าหน้า Web มี Stability variable dictionary
- ตรวจ Unit Convention
- ตรวจ N·m และ m/s²
- ตรวจหัวตาราง Component units
- Regression เดิมของ Stability, Component Mode, FBD, PDF และ Desktop/Web parity ยังคงทำงาน

### Calculation scope
เป็น Preliminary engineering calculation
ควรยืนยันมวลจริง, CG จริง, geometry จุดรองรับ และโหลดไดนามิกก่อนผลิตใช้งาน
