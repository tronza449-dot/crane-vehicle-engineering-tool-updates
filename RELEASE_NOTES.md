# Crane Vehicle Engineering Tool V53.8.12

## Differential / Pivot Turning Mode — UI & Summary Polish

อัปเดตต่อจาก V53.8.11 โดยเก็บรายละเอียดโหมด Differential / Pivot Turning Energy ให้ใช้งานและอธิบายง่ายขึ้น โดยไม่เปลี่ยนสมการหลักของ Simple Cycle model

### Pivot mode behavior
- ค่าเริ่มต้นยังเป็น OFF
- OFF = ไม่รวมพลังงาน Pivot และไม่รวมเวลาหมุนใน Cycle
- ON = รวม E_turn,cycle และ t_turn,cycle ตามค่าที่ตั้ง
- เมื่อ OFF ช่องจำนวนครั้งหมุน, มุมหมุน, เวลาหมุน และ Cturn จะถูกปิดใช้งานใน Windows application
- Web calculator ปิดช่อง Pivot inputs เมื่อไม่ได้เปิด Turning Energy เช่นกัน

### Summary / Explanation
- Summary แสดงสถานะชัดเจนเป็น INCLUDED / NOT INCLUDED
- แสดง Turn/Cycle (Wh) แยกจาก Drive และ Auxiliary
- แสดง Turn time (s) แยกในเวลา 1 Cycle
- Trip Summary แสดง t_cycle = t_drive + t_lift + t_other + t_turn ครบทุกส่วน

### Calculation logic
สูตรหลักยังเหมือน V53.8.11:
- phi = turn angle in radians
- s_turn = (W/2) × phi
- F_turn = Cturn × m × g
- E_turn,event = F_turn × s_turn / (eta × 3600)
- E_turn,cycle = E_turn,event × N_turn
- E_drive,cycle = E_go + E_return + E_turn,cycle
- E_cycle = E_drive,cycle + E_aux,cycle

เมื่อปิดโหมด:
- N_turn = 0
- E_turn,event = 0 Wh
- E_turn,cycle = 0 Wh
- t_turn,cycle = 0 s

### Scope
Cturn ยังเป็น effective empirical coefficient สำหรับ preliminary sizing และควรปรับจากการวัดกระแสจริง โดยเฉพาะรถที่ใช้ล้อพยุงแบบ non-swivel ซึ่งอาจมี scrub resistance สูงระหว่าง Pivot Turn.
