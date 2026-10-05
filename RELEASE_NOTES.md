# Crane Vehicle Engineering Tool V53.8.8

## Formal Engineering FBD + Stability Report Upgrade

อัปเดตต่อจาก V53.8.7 โดยนำระบบ Formal FBD ที่ตรวจสอบใหม่มาใช้กับสายเวอร์ชันล่าสุด เพื่อให้ Auto Update อัปเดตขึ้นตามลำดับเวอร์ชันได้ตามปกติ

### Formal FBD
- Geometry Top View ใช้สำหรับนิยาม Support Polygon และ Tipping Axis
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
- Worst-case scan รายงาน Side critical + Front + Rear ต่อมุม และภายในเปรียบเทียบ Left/Right ครบ

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

### Compatibility
- รุ่นนี้ต่อเลขจาก V53.8.7 โดยตรง
- Auto Updater จะมอง V53.8.8 เป็นเวอร์ชันใหม่กว่าและอัปเดตได้ตามปกติ

### Scope
Preliminary rigid-body engineering calculation. Actual mass/CG, structure, wheel/ground behavior, brakes, bearing, shock/dynamic loads and manufacturer limits still require validation.
