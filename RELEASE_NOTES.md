# Crane Vehicle Engineering Tool V52.1.0

## Trip Energy Summary / สรุปพลังงานไป-กลับ

เพิ่มหน้าสรุปแบบอ่านง่ายใน Electrical / Battery เพื่อให้เห็นทันทีว่า “รถวิ่งไป-กลับ 1 รอบใช้พลังงานเท่าไร” และ “สุดท้ายต้องใช้แบตกี่ Ah” โดยไม่ต้องไล่อ่าน Calculation Steps หลายหน้า

### หน้าสรุปใหม่
แสดงตัวเลขสำคัญหน้าเดียว:
- ระยะ 1 รอบไป-กลับ
- เวลา 1 รอบ
- จำนวนรอบในเวลาที่กำหนด
- พลังงานขับต่อ 1 รอบ (Wh/รอบ)
- พลังงานขับรวมทุก รอบ
- พลังงาน Auxiliary รวม
- พลังงานรวมก่อนเผื่อแบต
- Battery Design หลัง DoD + Reserve
- Required Ah @ Battery Voltage

### วิธีใช้งาน
ไปที่ Electrical / Battery → “สรุปไป-กลับ / Trip Summary”
หรือกดปุ่ม “ดูสรุปไป-กลับ / Trip Summary” จากหน้า Input

### สูตรที่สรุปในหน้าเดียว
- E_drive_per_trip = E_drive_total ÷ จำนวนรอบ
- E_load = E_drive + E_aux
- E_design = (E_load ÷ DoD) × (1 + Reserve)
- Ah = E_design ÷ V_battery

ค่า Auxiliary ต่อรอบที่แสดงเป็นค่าเฉลี่ยเทียบเท่า เพราะ Auxiliary เป็นโหลดตามเวลา ไม่ใช่โหลดตามระยะทางโดยตรง

### ระบบเดิมยังอยู่ครบ
- V52 Hardware I/O & Wiring Manager
- GPIO conflict / Voltage / Protection / ESP32 Pin Map
- Torque / Traction
- Electrical / Battery detailed calculation
- Winch
- Stability / Worst Case
- Control Logic
- PDF / Final Report
- Auto Save
- GitHub Auto Update

### Regression Gate
เพิ่มการทดสอบ Trip Summary บน Windows:
- มีค่า Wh/รอบ
- ค่า Wh/รอบตรงกับ Edrive ÷ cycles
- Required Ah ตรงกับ Electrical model
- หน้า Summary เปิดได้พร้อมระบบเดิมทั้งหมด

หมายเหตุ: ผลแบตเตอรี่เป็น Preliminary Engineering Calculation และยังต้องยืนยันกระแส/ประสิทธิภาพ/เส้นทางจริงจากการทดสอบรถก่อนเลือกแบตขั้นสุดท้าย
