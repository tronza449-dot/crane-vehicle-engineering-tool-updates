# Crane Vehicle Engineering Tool V53.8.19

## Live Web FBD

เพิ่ม Engineering FBD เข้าเวอร์ชันเว็บ โดยใช้ผลคำนวณสดจาก Web API ไม่ใช่รูปภาพสำเร็จ

### Web Stability FBD
หน้า Stability บนเว็บเพิ่ม 5 Case:
- Side Left / คว่ำซ้าย
- Side Right / คว่ำขวา
- Front / คว่ำหน้า
- Rear / คว่ำหลัง
- Slope / ทางลาด

เลือก View ได้:
- Current Angle / มุมปัจจุบัน
- Critical Case / มุมวิกฤตของ Case ที่เลือก

### Diagram
Web FBD แสดง:
- Vehicle / Boom / Payload
- Tipping axis P
- R_P
- R_opposite = 0
- W_V / W_B / W_L
- d_V / d_B / d_L
- M_O
- M_R
- Safety Factor
- PASS / FAIL

Slope FBD แสดง:
- Combined CG
- W_parallel
- W_normal
- F_I = ma
- N_R
- N_F = 0
- d_R
- h_CG

### สูตรภาษาไทย
ใต้ Web FBD แสดงสูตรและการแทนค่าแบบเดียวกับ Desktop:
- M_O = Σ(F_i d_i)
- อ่านสูตรแบบภาษาคน
- อธิบายตัวแปร
- แสดงว่าแรงแต่ละส่วน × แขนโมเมนต์ = โมเมนต์เท่าไร
- M_R
- SF
- สูตรทางลาด

### Web stability engine
Web API เพิ่ม:
- current_cases
- critical_cases
- current_governing
- critical_governing
- detailed Front/Rear components
- slope case

Critical Case scan มุมเครนตั้งแต่ -90° ถึง +90° ด้วย step 1° สำหรับ Side Left / Side Right / Front / Rear

### Web input
เพิ่ม Input สำหรับ Slope FBD:
- slope angle
- uphill acceleration
- combined CG from rear axle
- combined CG height

Slope angle sync กับ Drive Torque และ Main Battery ผ่าน Shared Project Parameters

### Regression
GitHub Actions เพิ่ม:
- node --check web/app.js
- ตรวจ Web FBD HTML/JS
- ตรวจ current_cases / critical_cases ครบ 5 case
- ตรวจ slope output
- ตรวจ Front/Rear component data

### Calculation scope
เป็น Preliminary rigid-body model เช่นเดียวกับ Desktop
ต้องยืนยันน้ำหนักจริง ตำแหน่ง CG จริง และผลทดสอบจริงก่อน fabrication/use
