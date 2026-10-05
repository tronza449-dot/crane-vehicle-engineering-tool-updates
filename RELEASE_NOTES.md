# Crane Vehicle Engineering Tool V53.8.22

## Web Calculation Audit & Parity Fix

ตรวจสอบสูตรฝั่ง Web เทียบกับ Desktop และแก้จุดที่ทำให้ผลดูไม่ตรงกัน

### Ramp Geometry
- สูตรหลักเดิมถูกต้อง: θ = atan(h/x), Slope(%) = h/x × 100, L = √(x²+h²)
- แยกให้ชัดว่า “มุมหลักสำหรับมอเตอร์” มาจาก h/x
- “มุมจาก L ที่วัด” เป็นค่าตรวจสอบอีกชุดหนึ่ง ไม่ใช่มุมหลัก
- เพิ่มข้อความเตือนเมื่อข้อมูล h, x และ L_measured ให้มุมต่างกัน

ตัวอย่าง h=55 cm, x=280 cm, L_measured=290 cm:
- L_theory ≈ 285.35 cm
- θ_from_hx ≈ 11.11°
- Slope ≈ 19.64%
- θ_from_measured_L ≈ 10.93°
- F_slope @ 300 kg ≈ 567.25 N

### Web parameter sync
- Mass จาก Drive/Battery/Ramp sync เข้า Stability total mass ด้วย
- Track width ใน Battery Pivot Turn sync จาก Stability
- Slope angle ไม่ auto-sync ทุกครั้งที่แก้แล้ว
- Slope จะ sync ข้าม Drive + Battery + Stability เมื่อผู้ใช้กดปุ่ม “ใช้มุม...” เท่านั้น
- ป้องกัน Battery default เก่า 12° ไปทับ Drive/Stability 19° แบบเงียบ ๆ

### Stability
- Default Boom mass ปรับจาก 80 kg → 20 kg ให้ตรงกับโมเดล Desktop ปัจจุบัน
- Default crane position from rear axle ปรับ 0.20 m → 0.15 m
- Current/Critical governing case ใช้เฉพาะ Side Left / Side Right / Front / Rear
- Slope stability แสดงแยก ไม่เอาไปแทน Crane Worst Case
- เพิ่ม Input echo เพื่อให้เห็นว่าค่าไหนถูกใช้คำนวณจริง

### Main Battery / BMS
- Battery energy sizing ยังใช้ Simple Cycle เหมือนเดิม
- BMS/C-rate check เพิ่ม Drive Torque design-current reference
- ใช้ค่ากระแสที่มากกว่าระหว่าง Battery uphill model, Pivot turn และ Drive Torque reference
- ป้องกัน Web ประเมิน BMS current ต่ำกว่าค่า Drive Torque

### Regression
เพิ่ม Desktop ↔ Web parity regression:
- Side Left
- Side Right
- Front
- Rear
- MO / MR / SF ต้องตรงกันเมื่อใช้ Input เดียวกัน
- ตรวจ sample Side Left ที่ θ=-66°, Track=1.1 m, Boom=20 kg ได้ SF ประมาณ 1.511
- ตรวจว่า Slope ไม่ถูกนับเป็น Crane governing case
- ตรวจ Drive current reference ใน Battery/BMS

### Calculation scope
ยังเป็น Preliminary engineering calculation
ไม่มีการเปลี่ยนหลักสมการพื้นฐานของ Desktop
