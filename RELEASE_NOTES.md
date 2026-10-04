# Crane Vehicle Engineering Tool V53.8.4

## FBD Simple Mode — อ่านรูปการคว่ำให้ง่ายขึ้น

ปรับหน้า Engineering FBD ใหม่จาก feedback ว่าแบบเดิมมีข้อมูลเยอะและดูยาก

### โหมดเข้าใจง่าย (ค่าเริ่มต้น)
เพิ่ม checkbox:
**โหมดเข้าใจง่าย (แนะนำ)**

เมื่อเปิด โครงสร้างรูปจะเหลือเฉพาะสิ่งที่จำเป็น:
1. Pivot จุดแดง — จุดที่รถจะเริ่มหมุนรอบ
2. น้ำหนัก/แรงที่ทำให้คว่ำ
3. น้ำหนัก/แรงที่ช่วยต้าน
4. Ground Reaction ที่ Pivot
5. กล่องสรุป M_O, M_R และ Safety Factor

ข้อมูลรายละเอียดทางวิศวกรรมเดิมยังดูได้โดยปิดโหมดเข้าใจง่าย

### สีที่ใช้
- แดง = ฝั่ง/แรงที่สร้างโมเมนต์ทำให้คว่ำ
- น้ำเงิน = น้ำหนักที่ช่วยต้านหรืออยู่ด้านใน Pivot
- เขียว = Ground Reaction
- จุดแดง = Pivot / Tipping Axis
- ส้ม = โครงเครน

### Side Left / Side Right
แสดงให้อ่านง่ายว่า:
- Pivot อยู่ล้อด้านที่จะคว่ำ
- Reaction ฝั่งตรงข้ามจะเข้าใกล้ 0 N เมื่อเริ่มคว่ำ
- W_payload / W_boom ที่ยื่นนอก Pivot ทำให้เกิด M_O
- น้ำหนักรถด้านในฐานล้อช่วยสร้าง M_R

### Front / Rear
แสดง:
- Pivot หน้า/หลัง
- แรงที่อยู่นอก Pivot = Overturning
- แรงที่อยู่ในฐาน = Restoring
- Wheelbase
- M_O / M_R / SF ในกล่องแยก

### Slope
ลดความรกของรูปและแสดงเฉพาะแรงหลัก:
- mg
- mg sin(alpha)
- N ≈ mg cos(alpha)
- F_a = ma เมื่อมีความเร่ง
- Rear Pivot
- M_O / M_R / SF_slope

### คำอธิบายใต้รูป
เพิ่ม Step-by-step ภาษาไทยตามกรณีที่เลือก:
- Pivot คืออะไร
- แรงไหนทำให้คว่ำ
- แรงไหนช่วยต้าน
- Safety Factor คิดอย่างไร
- ผ่าน / ไม่ผ่าน ตาม Target SF

### Auto FBD
เปลี่ยนค่าเริ่มต้นเป็น Manual เพื่อไม่ให้รูปเปลี่ยนเองจนผู้ใช้สับสน
ถ้าต้องการให้โปรแกรมเลือกทิศวิกฤตอัตโนมัติ สามารถเปิด Auto ได้

### PDF Export
Stability PDF และ Final Engineering PDF ใช้รูป FBD แบบเข้าใจง่ายเป็นค่าเริ่มต้น
แต่ยังคงตาราง Moment Balance, M_O, M_R, Moment Arm และสูตรรายละเอียดไว้ใต้รูป

เพิ่มกล่อง "วิธีอ่าน FBD แบบง่าย" ใน PDF ก่อนเริ่ม FBD ทั้ง 5 กรณี

### Regression
เพิ่ม automated regression ตรวจ:
- Simple FBD เป็นค่าเริ่มต้น
- สลับ Simple / Engineering Detail ได้
- คำอธิบายภาษาไทยแสดงจริง
- FBD ทั้ง 5 รูป render ได้
- Stability PDF และ Final PDF ยัง export ผ่าน
