# Crane Vehicle Engineering Tool V53.3.8

## Winch UI Cleanup — ตัดหน้าคำนวณที่ดูซ้ำ

ปรับหน้า Winch ให้เหลือเฉพาะหน้าที่มีหน้าที่ชัดเจน และไม่แสดงสูตร/ผลเดิมซ้ำหลายแท็บ

### Visible Winch tabs
1. Spec / Datasheet
2. รอบการทำงาน / 3h
3. Battery / แบตวินช์
4. สรุป / Summary

### สิ่งที่เปลี่ยน
- เอาแท็บ "สูตร + วิธีคำนวณ" ออกจากหน้าที่ผู้ใช้เห็น
- สูตรรอบรถอยู่ในหน้า "รอบการทำงาน" เท่านั้น
- สูตรพลังงาน Wh / Ah อยู่ในหน้า "Battery" เท่านั้น
- หน้า Summary แสดงเฉพาะผลสุดท้าย ไม่แสดงสูตรซ้ำ
- หน้า Spec ไม่คำนวณแบตเตอรี่
- จำนวนงานยกจาก Operating Cycles ส่งเข้า Battery อัตโนมัติ
- Battery ยังคงเป็นแหล่งคำนวณ E_up, E_down, E_event, E_total, Ah_used และ Ah_design เพียงชุดเดียว
- PDF ไม่ใส่ Formula section แยกอีกต่อไป เพราะสูตรมีอยู่แล้วใน Operating Cycles และ Battery

### Data flow
Spec / Datasheet → Operating Cycles → Battery → Summary

### Summary แสดงเฉพาะ
- Load / Lift Distance
- รอบไป-กลับ
- จำนวนเที่ยว
- จำนวนงานยกสัตว์
- Winch UP / DOWN
- พลังงานวินช์รวม
- Ah used
- Ah design
- Standard battery size
- Candidate battery PASS / FAIL
