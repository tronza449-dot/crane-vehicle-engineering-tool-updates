# Crane Vehicle Engineering Tool V53.8.10

## Main Battery 72 V — Simple Cycle Energy

อัปเดตต่อจาก V53.8.9 โดยปรับการคำนวณแบตเตอรี่รถให้เป็นแบบหยาบและอธิบายง่ายตามแนวคิด “คำนวณต่อ 1 Cycle แล้วคูณจำนวน Cycle”

### Route model
- 1 Cycle = เที่ยวไป + เที่ยวกลับ
- ระยะเที่ยวเดียวเริ่มต้น 30 m
- ระยะทางลาดเริ่มต้น 2.9 m
- ระยะทางราบต่อเที่ยว = 30 - 2.9 = 27.1 m
- เที่ยวไป = ทางราบ + ขึ้นทางลาด
- เที่ยวกลับ = ลงทางลาด + ทางราบ

### Simple energy equations
- ทางราบ: F_flat = Crr m g
- ขึ้นลาด: F_up = m g sin(theta) + Crr m g cos(theta)
- ลงลาด: F_down = max(0, Crr m g cos(theta) - m g sin(theta))
- พลังงานแต่ละช่วง: E = F s / (eta × 3600)
- E_go = E_flat,oneway + E_up,slope
- E_return = E_down,slope + E_flat,oneway
- E_drive,cycle = E_go + E_return
- E_cycle = E_drive,cycle + E_aux,cycle
- E_total = E_cycle × N_cycle
- E_design = (E_total / DoD) × (1 + Reserve)
- Ah = E_design / V

### Important behavior
- ช่วงลงทางลาดอาจมี traction energy ≈ 0 Wh หากแรงโน้มถ่วงช่วยพารถลง
- แต่เที่ยวกลับไม่ใช่ 0 Wh เพราะยังมีทางราบ 27.1 m
- ไม่คิดพลังงานช่วงออกตัวใน Wh/Ah sizing
- ไม่ใช้ Rated Motor Power เป็น Worst-case energy model
- ไม่นำพลังงานจากช่วงลงทางลาดมาหักคืนแบตเตอรี่
- Winch 12 V ยังแยกพลังงานออกจาก Main Battery 72 V; ใช้เฉพาะเวลายกในการหาจำนวน Cycle

### UI / Report
- Input Battery ตัดช่องจำนวนครั้งออกตัว, เวลาเร่ง, Worst-case energy mode และ Uphill efficiency ออกจากหน้าหลัก
- Trip Summary แสดงพลังงานเที่ยวไป / เที่ยวกลับ / ต่อ Cycle
- Variables และ Calculation Steps ปรับเป็น Cycle model
- Thai Guide และ Battery PDF ใช้สูตรแบบเดียวกัน
- Web version ใช้ Cycle model เดียวกับ Windows

### Validation
- ตรวจเส้นทาง 30 m = slope 2.9 m + flat 27.1 m
- ตรวจว่า Return energy > 0 จากทางราบ
- ตรวจว่า acceleration setting ไม่เปลี่ยน Edrive/Edesign
- ตรวจ Windows + Web calculation และ JavaScript syntax ผ่าน

### Scope
เป็น Preliminary battery sizing แบบหยาบเพื่อใช้เลือกความจุและอธิบายหลักการ
ควรวัดกระแส/กำลังจริงของรถเพื่อปรับค่า Efficiency และยืนยัน Pack/BMS ก่อนซื้อใช้งานจริง.
