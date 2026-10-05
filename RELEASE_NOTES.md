# Crane Vehicle Engineering Tool V53.8.11

## Battery Practical Factor + Differential/Pivot Turning Energy

อัปเดตต่อจาก V53.8.10 โดยเพิ่มการเผื่อขนาดแบตสำหรับการใช้งานจริง และเพิ่มพลังงานจากการหมุนแบบ Differential Steering ลงใน Simple Cycle model

### Battery Design Factor
เพิ่มตัวแปร:
- Kb = Battery Design Factor
- ค่าเริ่มต้น = 3.0
- Calculated minimum: Ah_min = E_design / V
- Practical recommendation: Ah_practical = Ah_min × Kb
- โปรแกรมปัดขึ้นเป็นขนาดแบตมาตรฐานให้

จุดประสงค์คือแยกให้ชัดระหว่าง:
- ค่าขั้นต่ำที่ได้จากแบบจำลองหยาบ
- ขนาดที่ควรพิจารณาใช้งานจริง

### Differential / Pivot Turn Energy
เพิ่มตัวเลือกเปิด/ปิด Turning Energy และ Inputs:
- จำนวนครั้งหมุนต่อ Cycle
- มุมหมุนต่อครั้ง
- เวลาหมุนต่อครั้ง
- Track width W
- Effective turn/scrub coefficient Cturn

สูตรแบบง่ายสำหรับ Pivot Turn:
- phi = turn angle in radians
- s_turn = (W/2) × phi
- F_turn = Cturn × m × g
- E_turn,event = F_turn × s_turn / (eta × 3600)
- E_turn,cycle = E_turn,event × N_turn
- E_drive,cycle = E_go + E_return + E_turn,cycle
- E_cycle = E_drive,cycle + E_aux,cycle

Turning time ถูกเพิ่มในเวลา 1 Cycle:
- t_cycle = t_drive + t_lift + t_other + t_turn

### Important limitation
Cturn เป็น effective empirical coefficient ของการต้านการหมุน/การไถล
ผลจริงขึ้นกับ:
- พื้นผิว
- ยาง
- น้ำหนักกดแต่ละล้อ
- Track width
- ล้อพยุง
- รัศมีเลี้ยว
- ความเร็วตอนหมุน

สำหรับรถที่ใช้ล้อพยุงแบบ non-swivel การไถลระหว่างหมุนอาจสูง จึงควรวัดกระแสจริงแล้วปรับ Cturn

### Battery Selection
- Battery Selection ใช้ Ah_practical เป็นเกณฑ์พลังงาน
- ยังแสดง Ah_min เพื่ออธิบายค่าทฤษฎี
- BMS current check รวม current reference จากการหมุน
- Final report และ Integrated Design Check แสดง practical battery target

### Windows + Web
เพิ่มสูตรเดียวกันทั้ง:
- Windows application
- Web calculator
- Variables
- Calculation Steps
- Thai explanation
- Battery results
- Battery selection

### Regression example
ทดสอบ:
- m = 300 kg
- W = 0.70 m
- 2 pivot turns / Cycle
- 180 deg / turn
- Cturn = 0.20
- eta = 60%

ได้โดยประมาณ:
- E_turn,event = 0.300 Wh
- E_turn,cycle = 0.599 Wh
- Ah_min ≈ 5.99 Ah
- Kb = 3
- Ah_practical ≈ 17.96 Ah
- Standard suggestion = 20 Ah

ค่าตัวอย่างนี้ใช้ตรวจสมการ ไม่ใช่ค่ารับรองการใช้งานจริง.
