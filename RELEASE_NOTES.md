# Crane Vehicle Engineering Tool V53.8.27

## Battery PDF — Guided STEP Cards + Thai Formula Reading

ปรับส่วนคำนวณใน Battery PDF ให้มองง่ายขึ้นด้วยกรอบ STEP ใหญ่ และเพิ่มคำอธิบายภาษาไทยใต้สูตรทุกสูตรหลัก

### New STEP layout
รายงานหลักเรียงเป็น:
- STEP 1 — แบ่งเส้นทางของ 1 Cycle
- STEP 2 — หาแรงและพลังงานของแต่ละช่วง
- STEP 3 — รวมพลังงานให้เป็น 1 Cycle
- STEP 4 — หาเวลา 1 Cycle และจำนวน Cycle
- STEP 5 — แปลงพลังงานรวมจาก Wh เป็น Ah
- STEP 6 — ตรวจ Continuous / Peak Current และ BMS

### Formula presentation inside each STEP
ทุกสูตรหลักเรียงรูปแบบเดียวกัน:
1. สูตร
2. อ่านสูตรแบบภาษาไทย
3. แทนค่า
4. ผลลัพธ์ + หน่วย
5. ผล STEP

ตัวอย่าง:
F_flat = Crr × m × g
อ่านสูตรแบบภาษาไทย:
แรงต้านทางราบ = ค่าสัมประสิทธิ์แรงต้านการกลิ้ง × มวลรถ × แรงโน้มถ่วง

### Thai explanations added
ครอบคลุม:
- แรงต้านทางราบ
- พลังงานทางราบ
- แรงขึ้นทางลาด
- พลังงานขึ้นลาด
- แรงลงทางลาด
- พลังงานลงลาด
- พลังงานเที่ยวไป / เที่ยวกลับ
- Drive energy / Auxiliary energy / Total Cycle energy
- เวลา Cycle / จำนวน Cycle
- E_total / DoD / Reserve
- Ah_min / Ah_practical
- Continuous current / Peak current / BMS

### Visual hierarchy
- กรอบใหญ่ 1 กรอบต่อ STEP
- สูตรเป็นแถบสีน้ำเงินอ่อน
- คำอธิบายภาษาไทยเป็นแถบสีเหลืองอ่อน
- แทนค่าเป็นแถบสีม่วงอ่อน
- ผล STEP เป็นกล่องสีเขียวอ่อน

### Engineering logic
- BMS Continuous/Peak semantics ยังคงตาม V53.8.26
- Downhill ≈ 0 Wh ยังอธิบายแยกชัดเจน
- Kb ยังระบุว่าเป็น Preliminary Design Allowance
- Appendix สูตรเต็มยังคงอยู่สำหรับตรวจสอบรายละเอียด
