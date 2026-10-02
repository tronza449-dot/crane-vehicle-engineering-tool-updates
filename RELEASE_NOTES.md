# Crane Vehicle Engineering Tool V53.3.5

## Winch Battery — Separate UP / DOWN Energy

เพิ่มฟังก์ชันคำนวณแบตเตอรี่วินช์แบบแยกพลังงานขาขึ้นและขาลง เพื่อไม่บังคับให้การยกขึ้นและการลดลงกินพลังงานเท่ากัน

### New Battery tab
เพิ่มแท็บ:
- Battery / แบตวินช์

### Inputs
- System voltage (default 12 V)
- Lift events
- ใช้จำนวนงานยกจากหน้า รอบการทำงาน / 3h อัตโนมัติ
- DoD
- Reserve

Load และ Lift Distance ใช้ค่าปัจจุบันจาก Winch Spec + Battery

### DOWN Calculation Modes
1. Conservative — Down = Up
   - I_down = I_up
   - t_down = t_up

2. Measured / Custom
   - กรอก Down Current
   - เลือกคำนวณเวลาขาลงจาก Down Speed หรือกรอก Down Time โดยตรง

### Energy formulas
E_up = V × I_up × t_up / 3600

E_down = V × I_down × t_down / 3600

E_event = E_up + E_down

E_total = N_event × E_event

Ah_used = E_total / V

Ah_design = E_total × (1 + Reserve) / (V × DoD)

ทุกขั้นแสดง:
สูตร → ความหมาย → แทนค่าตัวเลข → ผลลัพธ์

### Operating-cycle integration
หน้า รอบการทำงาน ใช้ Down mode ที่เลือกใน Battery tab ด้วย
ดังนั้นเมื่อมีค่าขาลงที่วัดจริง เวลาต่อรอบและจำนวนงานใน 3 ชั่วโมงจะอัปเดตตามจริง

ค่า default Conservative ของโปรเจกต์:
- 1 km/h
- 30 m one-way
- 3 h
- Load 100 kg
- Lift 1.5 m
- 2 lift events/round

ให้ประมาณ:
- 32 รอบไป-กลับ
- 64 งานยกสัตว์
- 64 Winch UP
- 64 Winch DOWN

### Battery Check
เพิ่มช่องตรวจแบตที่จะซื้อ:
- Candidate Ah
- BMS Continuous Current
- BMS Peak Current

แสดงแยก:
- Energy Capacity PASS / FAIL
- Operating Continuous Current PASS / FAIL
- Manufacturer table maximum 140 A เป็น Reference
- Peak Current = CHECK เพราะใบสเปกไม่ระบุ Starting/Stall surge

หมายเหตุ:
140 A คือค่าสูงสุดใน First Layer table ที่ 2041 kg ไม่ใช่กระแสใช้งานปกติของโหลด 100 kg

### PDF
Winch PDF รวม Advanced Battery report พร้อม UP/DOWN energy และ Battery Check
