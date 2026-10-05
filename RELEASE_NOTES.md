# Crane Vehicle Engineering Tool V53.8.13

## FBD Engineering Rebuild

อัปเดตต่อจาก V53.8.12 โดยรื้อระบบวาด Stability Free-Body Diagram (FBD) ใหม่ทั้งชุด เพื่อแก้ปัญหาเส้นทับกัน แรงลอย ตำแหน่งแรงถูกบีบกลับเข้าโครงรถ และ slope reaction แสดงทิศไม่ถูกหลัก

### Root cause fixed
FBD เดิมใช้ตำแหน่งวาดแบบคงที่และ clamp พิกัดแรงให้อยู่ในกรอบภาพ ทำให้ load ที่จริงอยู่นอก support polygon ถูกย้ายตำแหน่งเชิงภาพ และทำให้ line of action ไม่ตรงกับ moment arm ที่ใช้คำนวณ

Slope FBD เดิมนิยาม outward normal ไว้แต่ใช้เครื่องหมายกลับทิศตอนวาด N_R ทำให้ reaction ชี้เข้า road surface

### Side tipping — rebuilt
- ใช้ Front Elevation
- วาด Crane / Boom / Payload เชื่อมกันจริงใน projection
- W_V ออกจาก CG_V
- W_B ออกจาก CG_B
- W_L ออกจาก CG_L
- ไม่ clamp load position เข้า chassis
- แสดง Tipping axis P และ R_P แยกตำแหน่ง label
- R_opposite = 0 แสดงที่ support ฝั่งตรงข้าม
- แสดง Overturning Side / Resisting Side
- วาด moment arm จริง d_V, d_B, d_L จาก line of action ถึง P
- สีแดง = overturning arm
- สีเขียว = resisting arm

### Front / Rear tipping — rebuilt
- ใช้ Side Elevation
- ตำแหน่ง x ของ Vehicle / Boom / Payload ใช้ค่าจาก longitudinal_moment_balance เดียวกับสูตร
- วาด d_V, d_B, d_L ทุก component
- Pivot / Reaction / wheel label ไม่ซ้อนกัน
- ถ้า M_O = 0 จะแสดงข้อความชัดว่าไม่มี overturning gravity moment ใน case นั้น

### Uphill rear-tipping — corrected
ใช้ slope-fixed coordinate:
- +x_s = uphill
- +z_s = outward normal from road

แรง:
- W_parallel = mg sin(alpha) ชี้ downhill
- W_normal = mg cos(alpha) ชี้เข้า road surface
- F_I = ma เป็น D'Alembert inertia / pseudo-force ตรงข้าม uphill acceleration
- N_R ชี้ออกจาก road surface
- N_F = 0 ที่ impending rear tip

แสดง d_R และ h_CG สอดคล้องกับ:
- M_O = (W_parallel + F_I) h_CG
- M_R = W_normal d_R

ตัด traction arrow ที่ไม่ได้ใช้ใน moment equation ออกจาก FBD เพื่อไม่ให้คนอ่านสับสน

### Report structure
แยกชัดเจนระหว่าง:
1. CRITICAL-CASE FBD SECTION — แต่ละ FBD ใช้มุมวิกฤตที่ค้นหาของ case นั้น
2. CURRENT-ANGLE SNAPSHOT — Appendix สูตร/ตัวแปรใช้ crane angle ปัจจุบันจาก Input

โปรแกรมเตือนว่าไม่ควรนำค่าจาก Current angle ไปปนกับ Critical case เว้นแต่มุมตรงกัน

### Permanent engineering specification
เพิ่ม:
- docs/FBD_REBUILD_SPEC.md

เอกสารนี้กำหนด drawing contract ของ FBD สำหรับการพัฒนารุ่นต่อไป

### Regression guard
GitHub Actions ตรวจเพิ่มว่า source ต้องมี:
- Critical/Current angle separation
- d_V / d_B / d_L
- outward-normal N_R slope convention
- W_parallel / W_normal component warning
- D'Alembert force note
- zero-overturning-moment explanation

### Calculation scope
สูตร stability หลักไม่ได้เปลี่ยนในรุ่นนี้
FBD renderer ใช้ผลจาก:
- side_moment_balance(...)
- longitudinal_moment_balance(...)
- slope_stability_results(...)

ดังนั้นรูปและตารางคำนวณอ้าง source of truth เดียวกัน
