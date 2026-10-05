# Crane Vehicle Engineering Tool V53.8.10

## Main Battery — Simple Energy per Cycle

อัปเดตต่อจาก V53.8.9 เพื่อทำการคำนวณแบตเตอรี่รถ 72 V ให้เข้าใจง่ายและตรงกับแนวทางคำนวณทีละ Cycle

### Route / Cycle Model
- 1 Cycle = เที่ยวไป + เที่ยวกลับ
- ค่าเริ่มต้นเส้นทางตัวอย่าง:
  - ระยะเที่ยวเดียว = 30.0 m
  - ทางลาดต่อเที่ยว = 2.9 m
  - ทางราบต่อเที่ยว = 27.1 m
- เที่ยวไป = ทางราบ + ขึ้นทางลาด
- เที่ยวกลับ = ลงทางลาด + ทางราบ
- ดังนั้นเที่ยวกลับไม่ถูกถือเป็น 0 Wh

### Simple Energy Equations
- F_flat = Crr m g
- F_up = m g sin(theta) + Crr m g cos(theta)
- F_down = max(0, Crr m g cos(theta) - m g sin(theta))
- E = F s / (eta × 3600)
- E_go = E_flat,oneway + E_up
- E_return = E_down + E_flat,oneway
- E_drive,cycle = E_go + E_return
- E_cycle = E_drive,cycle + E_aux,cycle
- E_total = E_cycle × N_cycle
- E_design = (E_total / DoD) × (1 + Reserve)
- Ah = E_design / V_battery

### Simplified Scope
ตัดออกจากการคำนวณพลังงานหลัก:
- พลังงานช่วงออกตัว / kinetic start energy
- Rated-motor worst-case energy model
- การนำพลังงานช่วงลงทางลาดมาหักคืนแบตเตอรี่

หมายเหตุ: ช่วงลงทางลาดอาจมี E_down = 0 Wh เมื่อแรงโน้มถ่วงช่วยให้รถลงได้เอง
แต่เที่ยวกลับยังใช้พลังงานบนทางราบตามปกติ

### UI / Report
- Input เหลือเฉพาะตัวแปรที่จำเป็นสำหรับ Simple Cycle
- Trip Summary แสดง:
  - Energy เที่ยวไป
  - Energy เที่ยวกลับ
  - Wh/Cycle
  - จำนวน Cycle
  - Total Wh
  - Design Wh / Ah
- Variables และ Calculation Steps เปลี่ยนเป็น Cycle model
- PDF Battery Report ใช้สูตร Cycle แบบเดียวกัน
- Web Calculator ใช้สูตรเดียวกับ Windows app

### Winch
- Winch 12 V ยังใช้แบตเตอรี่แยก
- เวลายกสามารถนำไปคิดเวลา/Cycle และจำนวน Cycle ได้
- พลังงานวินช์ไม่รวมใน Main Battery 72 V

### Validation
ทดสอบกรณี 30 m/เที่ยว, ทางลาด 2.9 m, ทางราบ 27.1 m:
- Return-trip energy > 0 Wh
- Downhill slope energy สามารถเป็น 0 Wh ได้โดยไม่ทำให้ทั้งเที่ยวกลับเป็น 0 Wh
- Windows และ Web ให้โครงสร้างการคำนวณแบบเดียวกัน
