# Crane Vehicle Engineering Tool V53.8.28

## Desktop Button Press Animation + Separate Web Battery Systems

### Desktop — Press animation
เพิ่ม animation ตอนกดปุ่มในโปรแกรม Desktop ให้รู้สึกเหมือนปุ่มถูกกดจริง:
- กดแล้วปุ่มยุบ/เลื่อนเล็กน้อย
- ปล่อยแล้วเด้งกลับแบบ smooth
- ยังคงสถานะ Pressed / Busy / Success / Error เดิม
- ใช้ QPropertyAnimation + QEasingCurve

### Web — แยกแบตรถและแบตวินช์
ปรับ Web จากเดิมที่หน้า Winch มีทั้งกลไกและ Battery อยู่รวมกัน ให้แยกเป็น 3 โมดูลชัดเจน:
1. Main Battery 72 V
2. Winch / Lift
3. Winch Battery 12 V

### Main Battery 72 V
- ใช้พลังงาน Drive + Auxiliary ของรถ
- ใช้เวลา UP/DOWN จาก Winch เพื่อหา Cycle time เท่านั้น
- ไม่รวม Wh/Ah ของ Winch Battery
- มี badge: 72 V VEHICLE ONLY / WINCH ENERGY EXCLUDED

### Winch / Lift
- Load interpolation
- UP/DOWN time
- Current @ load
- Rope layer
- Operating Cycles
- ไม่มี Battery sizing ในหน้านี้

### Winch Battery 12 V
- แบตแยกสำหรับวินช์
- E_up / E_down / E_event / E_total
- Ah design
- Auto / Manual lift events
- Candidate capacity
- BMS Continuous / Peak check
- มี badge: 12 V WINCH ONLY

### Data sharing
Main Battery และ Winch Battery ไม่แชร์พลังงานกัน
ข้อมูลที่แชร์จาก Winch → Main Battery มีเฉพาะ:
- เวลา UP
- เวลา DOWN
- เวลา 1 งานยก
- จำนวนงานยกต่อ Operating Cycle
เพื่อให้จำนวน Cycle ใน 3 ชั่วโมงสมจริง

### Compatibility
- Web input เดิมของ Winch Battery จะถูก migrate ไป form ใหม่อัตโนมัติ
- Main Battery calculation engine ยังคง winch_energy_included = false
