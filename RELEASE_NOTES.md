# Crane Vehicle Engineering Tool V53.7.1

## Formal Engineering FBD + Stability Report Audit

ต่อจาก V53.7.0 โดยคงระบบ Ramp Geometry และฟังก์ชันหลักเดิมไว้ แล้วปรับ Stability/FBD สำหรับใช้ในรายงานวิศวกรรม

### Formal FBD
- แยก Geometry Top View ออกจาก Free-Body Diagram
- Side Left / Side Right ใช้ Front Elevation
- Front / Rear ใช้ Side Elevation
- Slope FBD ใช้ resolved weight components โดยไม่วาด W=mg ซ้ำกับ mg sin(alpha), mg cos(alpha)
- แสดง coordinate axes, tipping axis, support reactions, weights และ moment arms
- ที่ impending tipping ระบุ reaction ฝั่งตรงข้าม tipping axis -> 0

### Calculation convention
- +x = ด้านหน้ารถ
- +y = ด้านขวารถ
- +z = ด้านบน
- crane theta: -90 deg = left, 0 deg = forward, +90 deg = right
- Left/Right/Front/Rear moment balance แยกกัน
- Payload dynamic factor ใช้เฉพาะ adverse overturning payload moment
- Worst-case search = 181 angles x 4 directions = 724 cases

### PDF Export
Stability PDF และ Final Engineering PDF มี:
- Geometry & Tipping-Axis Definition
- FBD Left
- FBD Right
- FBD Front
- FBD Rear
- FBD Uphill Slope
- Variable table
- Formula
- Numeric substitution
- M_O / M_R / SF
- PASS / FAIL

### Slope
- W_parallel = m g sin(alpha)
- W_normal = m g cos(alpha)
- F_I = m a opposite acceleration for quasi-static check
- M_O = (W_parallel + F_I) h_CG
- M_R = W_normal d_rear
- SF_slope = M_R / M_O

### Scope
Preliminary rigid-body engineering calculation. Actual mass/CG, structure, wheel/ground behavior, brakes, bearing, shock/dynamic loads and manufacturer limits still require validation.
