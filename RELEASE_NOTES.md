# Crane Vehicle Engineering Tool V53.8.14

## FBD / UI Polish and Report Consistency

อัปเดตต่อจาก V53.8.13 โดยเน้นแก้ความสับสนระหว่าง Current Angle กับ Critical Case และแก้ Interactive FBD ที่ layout ถูกบีบในหน้าจอจน result cards / moment arms ทับกับรูป

### Engineering FBD UI
เพิ่ม View mode ชัดเจน 3 แบบ:
1. Current Angle Snapshot / มุมปัจจุบัน
2. Critical Case / มุมวิกฤตของด้านที่เลือก
3. Auto Current Worst / ด้านที่มี SF ต่ำสุด ณ มุมปัจจุบัน

แต่ละโหมดมี context banner บอกชัดว่ากำลังใช้มุมใดและเป็น Current หรือ Critical

### Interactive FBD compact layout
- แยก compact screen layout ออกจาก PDF layout
- ปรับ ground/deck/boom/dimension lanes ตามความสูง widget
- Result cards M_O / M_R / SF ไม่ทับรูป
- d_V / d_B / d_L อยู่คนละ lane และไม่ถูกผลลัพธ์บัง
- Slope FBD ย่อ geometry และ force arrows ตามพื้นที่หน้าจอ
- เพิ่ม color legend บน FBD:
  - Black = Weight
  - Green = Reaction / Resisting
  - Red = Overturning / tipping information
  - Orange = Crane
  - Purple = inertia force in slope case

### Report consistency
หน้า Summary เพิ่ม:
- Current crane input angle
- Worst critical-case stability
- Uphill rear-tipping stability
- Overall preliminary status

Slope FBD note แก้ให้ถูกบริบท:
- ใช้ combined driving mass/CG
- payload assumed stowed on vehicle
- Kdyn ไม่ถูกใช้ใน slope equation

### 3D report figure
เปลี่ยน label ขอบเขตการหมุนจาก -90° / +90° ที่อาจถูกเข้าใจผิดว่าเป็น current angle เป็น:
- LEFT LIMIT
- CENTER
- RIGHT LIMIT

เพิ่ม marker:
- CURRENT θ = actual displayed crane angle

### Stability Map
ถ้าค่า SF ถูกตัดที่เพดานกราฟเพื่อให้อ่านค่าต่ำบริเวณ target ได้ชัด จะมีข้อความ:
DISPLAY NOTE: SF > limit is clipped for readability

### Calculation scope
สูตรหลักของ stability ไม่เปลี่ยนจาก V53.8.13
- side_moment_balance(...)
- longitudinal_moment_balance(...)
- slope_stability_results(...)
ยังเป็น source of truth เดียวกันของตัวเลขและ FBD

