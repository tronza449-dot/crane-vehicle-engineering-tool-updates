# Crane Vehicle Engineering Tool V53.6.1

## Main Battery 72 V — Purchase Check + Reverse Runtime

อัปเดตรอบนี้เพิ่ม 3 ส่วนตามที่ต้องการสำหรับการเลือกแบตรถจริง

### 1) BMS Continuous / Peak Check
โปรแกรมแสดงค่ากระแสที่แบตและ BMS ต้องรองรับ:
- Continuous current requirement
- Peak current requirement
- Recommended BMS floor (ปัดขึ้นทีละ 5 A)
- Candidate BMS Continuous = PASS / CHECK
- Candidate BMS Peak = PASS / CHECK

ยังคงเตือนว่าต้องยืนยัน Battery Current limit ของ VESC และ datasheet ของ Pack/BMS จริงก่อนซื้อ

### 2) Compare Battery Size
หน้า Battery Selection เปรียบเทียบขนาดมาตรฐานหลายขนาดพร้อมกัน:
- Capacity Ah
- Rated Wh
- Estimated runtime
- Full operating rounds
- Capacity margin เทียบกับเป้าหมาย
- Required continuous C-rate
- Required peak C-rate
- PASS / ENERGY LOW / C-RATE CHECK

Runtime ใช้ Operating Cycle ปัจจุบัน:
Drive + Lift time + Other stop + Auxiliary

พลังงาน Winch 12 V ยังแยกออกจาก Main Battery 72 V เหมือนเดิม

### 3) Reverse Calculation
เมื่อกรอก Candidate Battery เช่น 72 V 40 Ah โปรแกรมคำนวณย้อนกลับ:
- ใช้งานได้ประมาณกี่ชั่วโมง
- ทำงานได้กี่รอบเต็ม
- พลังงานที่ใช้ได้ตาม DoD + Reserve
- Capacity margin เทียบกับเป้าหมาย 3 ชั่วโมง

สูตรหลัก:
`Load budget = V × Ah × DoD / (1 + Reserve)`

`Runtime ≈ Load budget / Average operating power`

`Full rounds = floor(Runtime / Round time)`

### Desktop
- ปรับ Battery Selection table เป็น 8 คอลัมน์
- Candidate section แสดง Reverse Runtime และ Full Rounds
- Suggested Battery แสดง Runtime โดยประมาณ
- แสดง BMS minimum ชัดเจน

### Web
หน้า Main Battery เพิ่มช่อง:
- Target continuous C
- Target peak C
- Candidate Ah
- Candidate BMS continuous A
- Candidate BMS peak A

และเพิ่ม:
- Reverse Calculation
- Candidate BMS Check
- Compare Battery Size table
- Suggested standard battery

### หมายเหตุ
ผล Reverse Runtime เป็นค่าประมาณเชิงออกแบบจากโมเดลปัจจุบัน ยังต้องยืนยันด้วย VESC log, กระแสจริง, pack voltage sag, อุณหภูมิ และสเปกแบตจริงก่อนซื้อ
