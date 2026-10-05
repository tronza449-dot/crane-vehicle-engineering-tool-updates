# Crane Vehicle Engineering Tool V53.8.9

## Stability Mass Modes + Complete Variables + Per-Mode PDF Export

อัปเดตต่อจาก V53.8.8 เพื่อแก้การป้อนมวลและการ Export Stability ให้ชัดเจนขึ้น

### 1) Mass Calculation Mode แยกเป็น 2 โหมด
- Mode A — Total Mass
  - ผู้ใช้กรอก m_total, m_L, m_B, Base CG และ Driving CG เอง
- Mode B — Component Mass
  - ผู้ใช้กรอกน้ำหนักแต่ละส่วนในตาราง
  - โปรแกรมรวม m_total อัตโนมัติ
  - Boom ถูกส่งไป m_B
  - Basket + Payload ถูกส่งไป m_L
  - ชิ้นส่วนที่เหลือรวมเป็น Base vehicle
  - คำนวณ x_CG,V, y_CG,V, x_CG,drive และ h_CG จากตาราง
  - ช่องค่าที่เป็นผลลัพธ์จะถูกล็อกเพื่อป้องกันการกรอกซ้ำ/ค่าขัดกัน

### 2) Component Mass table
เพิ่มรายการแยก:
- Frame
- Battery
- Drive motors
- Support wheels
- Crane column
- Slewing drive + bearing
- Winch
- Boom
- Basket
- Payload
- Counterweight
- Other

### 3) Stability variables
Variable Dictionary เพิ่มตัวแปรที่ใช้จริงให้ครบมากขึ้น:
- Mass source / mass mode
- m_total, m_V, m_B, m_L
- W_V, W_B, W_L, F_L,d
- x/y tipping axes
- x/y CG
- Boom/Payload positions
- Moment arms ของ Left / Right / Front / Rear
- M_O, M_R และ SF ของทุกทิศ
- Slope variables: alpha, a, d_rear, W_parallel, W_normal, F_I, traction,
  CG shift, stability margin, M_O,slope, M_R,slope, SF_slope
- Component source table แสดงในรายงานเมื่อใช้ Component Mass Mode

### 4) PDF Export
เพิ่มการส่งออกแยก:
- Geometry + Tipping Axes
- Side Left
- Side Right
- Front
- Rear
- Slope

เพิ่มปุ่ม:
- Export Current Mode PDF ที่หน้า FBD
- Export Slope PDF ที่หน้า Slope
- Export Selected Mode PDF ที่หน้า Report
- Export ALL Stability Modes PDF
- Export All Stability Modes ที่หน้า Mass & CG

### 5) Side CG
เพิ่ม y_CG,V และใช้จริงใน Left/Right moment balance
Component Mass Mode จะคำนวณ y_CG,V จากตารางอัตโนมัติ

### Validation
ทดสอบ syntax, Total/Component mode, automatic Boom/Payload sync,
base lateral CG, complete variables และการ render Export ครบทุกโหมดแล้ว

### Scope
ยังเป็น Preliminary rigid-body engineering calculation.
ควรยืนยันมวล/CG จริง, โครงสร้าง, wheel-ground interaction, braking,
slewing bearing และ dynamic/shock load ก่อนใช้งานจริง.
