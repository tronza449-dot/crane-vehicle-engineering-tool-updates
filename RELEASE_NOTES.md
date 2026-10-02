# Crane Vehicle Engineering Tool V53.3.9

## Winch Battery — Auto / Manual Lift Events

เพิ่มการเลือกจำนวนงานยกในหน้า Battery ให้ชัดเจนขึ้น

### Lift Event Mode
มี 2 โหมด:

1. Auto — ใช้จำนวนงานยกจากรอบการทำงาน / 3h
- โปรแกรมดึงจำนวนงานยกจากหน้า Operating Cycles อัตโนมัติ
- ช่องกรอก Manual ถูกล็อก
- ตัวอย่างโปรเจกต์ 3 ชั่วโมง: 64 งานยก

2. Manual — กำหนดจำนวนงานยกเอง
- ผู้ใช้กรอกจำนวนงานยกเองได้
- โปรแกรมใช้จำนวนที่กรอกคำนวณ E_total, Ah_used และ Ah_design โดยตรง

### Definition
1 งานยก = วินช์ขึ้น 1 ครั้ง + วินช์ลง 1 ครั้ง

ตัวอย่าง:
- Manual = 50 งาน
- Winch UP = 50 ครั้ง
- Winch DOWN = 50 ครั้ง
- การเคลื่อนที่วินช์รวม = 100 ครั้ง

### UI Improvements
- เปลี่ยนจาก checkbox เดิมเป็น dropdown ที่เห็นชัด:
  - Auto — ใช้จำนวนงานยกจากรอบการทำงาน / 3h
  - Manual — กำหนดจำนวนงานยกเอง
- เปลี่ยนชื่อช่องเป็น “จำนวนงานยกที่กำหนดเอง / Manual events”
- แสดงข้อความอธิบาย 1 งาน = ขึ้น 1 + ลง 1
- Summary ระบุชัดว่ากำลังใช้ AUTO หรือ MANUAL และแสดงจำนวน UP / DOWN

### Calculation
ยังคงใช้ Battery calculator ชุดเดียว:
E_total = N_event × E_event

Ah_used = E_total / V

Ah_design = E_total × (1 + Reserve) / (V × DoD)
