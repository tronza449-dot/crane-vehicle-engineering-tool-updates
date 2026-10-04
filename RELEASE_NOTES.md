# Crane Vehicle Engineering Tool V53.8.1

## Stability PDF - All-Direction Free Body Diagrams (FBD)

อัปเดตนี้ปรับหน้า Stability และ PDF Export ให้มี Free Body Diagram แบบวิศวกรรมครบทุกทิศทางตามที่ต้องการ

### FBD ในโปรแกรม
หน้า FBD เปลี่ยนจาก 3 โหมดเป็น 5 โหมด:
1. Side Left / คว่ำด้านซ้าย
2. Side Right / คว่ำด้านขวา
3. Front / คว่ำด้านหน้า
4. Rear / คว่ำด้านหลัง
5. Slope / ทางลาด

Auto FBD ยังเลือกกรณีวิกฤตจาก Side / Front / Rear ตามมุมเครนปัจจุบัน

### แรงที่แสดงบนรูป
FBD แสดงและระบุ:
- W_vehicle = น้ำหนักตัวรถส่วนหลัก
- W_boom = น้ำหนักแขนเครน
- W_payload = น้ำหนักโหลด
- R_L / R_R = Ground Reaction ด้านซ้าย/ขวา
- R_front / R_rear = Ground Reaction หน้า/หลัง
- N = Normal Reaction บนทางลาด
- mg sin(alpha) = แรงตามทางลาด
- mg cos(alpha) = แรงตั้งฉากกับทางลาด
- F_a = m a = ผลของความเร่งบนทางลาด
- Pivot / Tipping axis
- Track width / Wheelbase
- CG / ตำแหน่งโหลด
- Overturning Moment M_O
- Restoring Moment M_R
- Safety Factor

### Stability PDF Export
เมื่อกด Export PDF ในหน้า Stability รายงานจะสร้าง FBD แยกเป็นหน้า:
- FBD 1: Side Tipping - Left
- FBD 2: Side Tipping - Right
- FBD 3: Front Tipping
- FBD 4: Rear Tipping
- FBD 5: Slope Stability

แต่ละหน้ามี:
- รูป FBD
- จุด Pivot
- ชื่อและทิศทางแรง
- Moment arm / ระยะที่เกี่ยวข้อง
- สมการ Moment balance
- ค่า M_O
- ค่า M_R
- ค่า SF
- Target SF
- PASS / FAIL
- คำอธิบายภาษาไทยว่าแรงแต่ละแรงกระทำที่ใดและมีผลอย่างไร

### Governing Case
Front และ Rear FBD ใช้มุมเครนที่ทำให้ Safety Factor ของทิศนั้นต่ำที่สุดในช่วง -90 ถึง +90 องศา
Side Left ใช้ -90 องศา และ Side Right ใช้ +90 องศา

### Final Engineering Report
Final Engineering PDF จะรวม FBD ทั้ง 5 กรณีเหมือน Stability PDF ด้วย ไม่ใช่เพียง screenshot FBD เดียวอีกต่อไป

### Engineering note
เกณฑ์พื้นฐาน:
SF = M_R / M_O

โปรแกรมเปรียบเทียบกับ Target SF ที่ผู้ใช้ตั้งไว้

ผลยังเป็น Preliminary rigid-body stability calculation ต้องยืนยันมวลจริง ตำแหน่ง CG จริง โครงสร้าง จุดยึด ยาง/พื้น Dynamic Shock และการทดสอบจริงก่อนผลิตหรือใช้งาน


### Build fix
- แก้การ render FBD แบบ offscreen สำหรับ PDF Export ให้ทำงานถูกต้องบน PySide6/Windows build.
