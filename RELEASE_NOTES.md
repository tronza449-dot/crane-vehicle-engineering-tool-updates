# Crane Vehicle Engineering Tool V53.3.1

## Winch design inputs update

ปรับหน้า Winch จาก V53.3.0 ให้รองรับการเปลี่ยนแบบระหว่างออกแบบ โดยยังยึดใบ 4500LB. WINCH SPECIFICATION เป็นฐาน

### Editable Winch inputs
ผู้ใช้แก้ได้ 3 ค่า:
- Load / โหลดที่ยก (kg)
- Lift Distance / ระยะยก (m)
- Cycles / จำนวนรอบขึ้น+ลง

### Locked manufacturer / calculation settings
ข้อมูลจากใบสเปกยังล็อก:
- Rated pull 4500 lb / 2041 kg
- Motor 1.4 kW / 1.9 hp
- Gear ratio 136:1
- Rope Ø5 mm × 10 m
- Drum Ø37 mm × 72 mm
- First-layer pull / speed / current table
- Rope layer capacity / line-pull table

ค่าคำนวณที่ยังล็อก:
- Separate Winch battery = 12 V
- DoD = 80%
- Reserve = 20%

### Automatic recalculation
- เปลี่ยน Load → โปรแกรม interpolate ความเร็วและกระแสจาก First Layer table ใหม่ทันที
- เปลี่ยน Lift Distance → เวลา, Wh และ Ah เปลี่ยนตามระยะ
- เปลี่ยน Cycles → พลังงานรวมและ Ah เปลี่ยนตามจำนวนรอบ
- แสดง estimated ending rope layer จากตาราง rope capacity
- แสดง line-pull ของ layer นั้นเพื่อช่วยตรวจว่า Load อยู่ภายในข้อมูลบนใบสเปกหรือไม่
- ข้อมูลขาลงยังไม่อยู่ในใบสเปก จึงใช้ค่าเท่าขาขึ้นแบบ conservative และระบุชัดใน UI

### Regression tests
GitHub Actions ทดสอบว่า:
- Load / Lift Distance / Cycles เป็น input ที่แก้ได้
- ค่า spec อื่นยังล็อก
- 100 kg interpolation ถูกต้อง
- 454 kg ให้ 2.5 m/min และ 60 A ตามตาราง
- ระยะยกเพิ่ม 2 เท่า ทำให้เวลาและพลังงานเพิ่มตาม
- ระยะมากกว่า 1.5 m เปลี่ยนไปตรวจ rope layer 2
- จำนวนรอบเพิ่ม 2 เท่า ทำให้ Wh/Ah เพิ่ม 2 เท่า
