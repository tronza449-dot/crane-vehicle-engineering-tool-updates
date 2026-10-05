# Crane Vehicle Engineering Tool V53.8.16

## Final FBD Geometry + Design Guidance Update

อัปเดตต่อจาก V53.8.15 หลังตรวจภาพ FBD แยกและ PDF จริงครบทุกหน้า

### Geometry top view
- แก้ screen-coordinate mapping ให้ +y physical ถูกวาดขึ้นบนจอ
- θ<0 จึงไปฝั่ง -y ตาม convention จริง
- แก้กรณี Current θ=-66° ที่ภาพเดิมดูเหมือนชี้ไป +y

### FBD layout
- ย้าย legend ลงคนละระดับกับ Overturning / Resisting labels
- ขยับ Tipping axis label ออกจาก wheel/pivot
- Front / Rear note เปลี่ยน x_C ที่เป็นพิกัด global เป็น x_crane(global)
  เพื่อไม่ให้สับสนกับ input x_C ที่วัดจาก rear axle
- Slope: แยก label W_parallel กับ F_I ออกจากกัน
- Slope pivot label จัดตำแหน่งเฉพาะ

### PDF pagination
หน้า 2 เดิมมีเพียง row ที่ 5 ของ Critical Case Summary เพราะตารางล้นหน้า
รุ่นนี้เปลี่ยนหน้า 2 เป็น:
DESIGN GUIDANCE & CRITICAL-CASE SUMMARY

ทำให้ page break มีความหมายและไม่มี orphan row

### Automatic preliminary design guidance
เพิ่ม stability_design_guidance() ใช้ calculation model เดียวกับ FBD เพื่อหา:
- Minimum track width ที่ทำให้ full -90°...+90° slew ผ่าน Required SF
- Contiguous safe slew range รอบ 0° สำหรับ track ปัจจุบัน
- Margin ของ current angle ถึง safe range boundary

สำหรับค่าตัวอย่างปัจจุบัน W=1.10 m, m_total=300 kg, payload=100 kg,
boom=20 kg, L=1.20 m, Kdyn=1.20 และ Required SF=1.50:
- Full ±90° ยังไม่ผ่าน
- Current -66° ผ่านแบบมี margin เล็กมาก
- โปรแกรมจะคำนวณค่าคำแนะนำจริงจาก input ทุกครั้ง ไม่ hard-code ตัวเลข

### 3D figure in report
- เพิ่ม reportMode
- ตัด interactive mouse instructions, in-scene current label และ bottom badge ออกจาก PDF
- คง CRANE LIVE DATA เป็นแหล่งแสดง current angle หลัก

### Worst Case wording
แก้ UI และ report เป็น:
181 angles × 4 directions = 724 directional moment-balance evaluations

### Calculation scope
สูตรหลัก stability ไม่เปลี่ยน
ค่าทั้งหมดอ้างอิง:
- side_moment_balance(...)
- longitudinal_moment_balance(...)
- slope_stability_results(...)

Design guidance เป็น preliminary sizing เท่านั้น ต้องตรวจ measured CG, ground/tire compliance,
dynamic shock, structural strength, bearing/brake limits และ manufacturer limits ก่อน fabrication/use.
