# Crane Vehicle Engineering Tool V52.2.0

## Battery Selection / เลือกแบตที่จะซื้อ

เพิ่มระบบแยก “ค่าขั้นต่ำจากการคำนวณ” ออกจาก “แบตที่ควรนำไปตรวจสเปกก่อนซื้อ” เพื่อไม่ให้ผู้ใช้เอาค่า Ah ขั้นต่ำไปซื้อแบตตรง ๆ โดยไม่ตรวจกระแสและ BMS

### Battery Selection ใหม่
อยู่ที่ Electrical / Battery → “เลือกแบต / Battery Selection”

แสดง:
- Minimum capacity จาก Energy model (Ah / Wh)
- Continuous current requirement
- Calculated Peak current
- Suggested standard battery size ที่ควรนำไปตรวจสเปกต่อ
- Required continuous C-rate / peak C-rate
- Design-equivalent runtime ของแต่ละขนาดมาตรฐาน

### Standard Battery Comparison
เปรียบเทียบขนาด:
5 / 10 / 15 / 20 / 25 / 30 / 40 / 50 / 60 / 80 / 100 / 120 / 150 / 200 Ah

แต่ละขนาดแสดง:
- Rated Wh
- Required continuous C-rate
- Required peak C-rate
- Design runtime
- PASS / ENERGY LOW / C-RATE CHECK

### Candidate Battery Check
ผู้ใช้กรอกสเปกแบตจากร้าน:
- Capacity (Ah)
- Continuous current rating (A)
- Peak current rating (A)

โปรแกรมตรวจ:
- Energy capacity
- Continuous current
- Peak current
- READY TO VERIFY DATASHEET / NOT READY

### Suggested size logic
Suggested standard size = ขนาดมาตรฐานถัดไปที่ผ่านทั้ง:
- Energy requirement จาก Electrical model
- Target continuous C-rate
- Target peak C-rate

ค่า Target C-rate แก้ไขได้ และเป็นเพียง design target ไม่ใช่สเปกเซลล์จริงจากผู้ผลิต

### Project integration
- Candidate Battery sync กับ Project Tools → Battery+BMS
- Save/Load / Auto Save รองรับค่าของ Battery Selection
- Project เก่าที่มี Battery+BMS แต่ยังไม่มี Battery Selection จะ sync ค่าเดิมเข้าหน้าใหม่
- Integrated Design Check เพิ่ม Suggested standard size และ Peak BMS check
- Final Engineering Report แสดง Battery Selection summary

### Important engineering distinction
- Minimum Ah = ความจุขั้นต่ำตามพลังงาน/DoD/Reserve
- Suggested Ah = ขนาดมาตรฐานที่ผ่าน Energy + C-rate target
- Candidate Battery = แบตจริงที่กำลังจะซื้อ ต้องกรอก current rating จากร้าน/ผู้ผลิต
- Controller current setting อาจเป็น motor/phase current ไม่ใช่ battery current โดยตรง จึงแสดงเป็น conservative indicator แยกต่างหาก

### Regression Gate
Windows regression test เพิ่มการตรวจ:
- Suggested Ah ≥ design requirement
- Candidate fields sync กับ Battery+BMS
- Candidate ที่ต่ำเกินต้องขึ้น NOT READY
- Candidate ที่ผ่าน Energy + Continuous + Peak ต้องขึ้น READY TO VERIFY DATASHEET
- Standard-size comparison table ทำงาน
- ระบบเดิมทั้งหมด Torque / Trip Summary / Electrical / Winch / Stability / Control Logic / Hardware I/O / PDF / Updater ยังผ่าน test เหมือนเดิม

หมายเหตุ: Suggested size ไม่ใช่คำสั่งซื้ออัตโนมัติ ต้องยืนยัน Pack voltage, chemistry, cell current rating, BMS continuous/peak, connector, fuse, charger และ VESC battery-current limit ก่อนซื้อจริง
