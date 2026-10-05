# Crane Vehicle Engineering Tool V53.8.24

## Web Stability — Mass Modes + Guided Calculation Steps

ปรับหน้า Stability บน Web ให้ใช้งานและอ่านผลเหมือน Desktop มากขึ้น โดยแยกแหล่งข้อมูลมวลออกเป็น 2 โหมด และจัดสูตรเป็นขั้นตอน 1 → 4

### Stability Mass Mode
- Mode A — Total Mass: กรอก m_total, Payload, Boom และ CG เอง
- Mode B — Component Mass: กรอกน้ำหนักและพิกัด x/y/z ของแต่ละชิ้น แล้วรวมมวลและ CG อัตโนมัติ
- ตาราง Component เริ่มต้น 12 รายการตรงกับ Desktop
- ใช้กฎจัดกลุ่มเดียวกับ Desktop:
  - Boom / แขนเครน → m_B
  - Basket + Payload / ตะกร้า + ซากสัตว์ → m_L
  - รายการอื่น → Base vehicle
- คำนวณ Base CG และ Combined CG แบบ weighted average
- ใน Component Mode ค่า m_total, m_L, m_B, Base CG และ Slope CG ถูก derive จากตารางจริง
- มวลรวมที่ derive แล้ว sync กลับไปยัง Project mass ที่เกี่ยวข้อง

### Guided Calculation UI
ใต้ FBD ของแต่ละ Case แสดงการคำนวณเป็น 4 ขั้น:
1. หาแรงและระยะแขนโมเมนต์จากแกนคว่ำ P
2. หาโมเมนต์คว่ำ M_O = Σ(F_i d_i)
3. หาโมเมนต์ต้าน M_R = Σ(F_i d_i)
4. หา Safety Factor SF = M_R / M_O และ PASS/FAIL

สำหรับ Slope:
1. หา W_parallel, W_normal และ F_I
2. หา d_R และ h_CG
3. หา M_O และ M_R
4. หา SF_slope และ PASS/FAIL

### Web UX
- เพิ่ม Mode cards A/B ที่เห็นชัดว่าเลือกโหมดไหนอยู่
- Component table แสดง Σm และ CG preview ทันที
- แสดง Base / Boom / Basket+Payload breakdown
- ผลลัพธ์บอก Mass Source ว่ามาจาก Total Mass หรือ Component Mass
- Step cards รองรับจอมือถือด้วย

### Regression
- เพิ่ม Web Component Mass regression
- ตรวจ Σm = 300 kg, Base = 180 kg, Boom = 20 kg, Basket+Payload = 100 kg จาก default table
- ตรวจผล Component Mode เท่ากับ Total Mode เมื่อใช้ derived mass/CG เดียวกัน
- ตรวจ Static UI สำหรับ mass mode และ 4-step calculation
- Regression ชุด Desktop/Web เดิมยังคงทำงานทั้งหมด

### Calculation scope
ยังเป็น Preliminary engineering calculation
ควรยืนยันมวลจริง, CG จริง, ตำแหน่งอุปกรณ์จริง และ geometry จุดรองรับก่อนผลิตใช้งาน
