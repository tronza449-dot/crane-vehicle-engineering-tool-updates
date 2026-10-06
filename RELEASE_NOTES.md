# Crane Vehicle Engineering Tool V53.8.26

## Battery PDF Report — Presentation-first Redesign

ปรับรายงาน Battery Calculation PDF ให้เข้าใจง่ายขึ้น โดยคงสูตรเดิม แต่เปลี่ยนลำดับการเล่าเรื่องจาก “สูตรยาวต่อเนื่อง” เป็น “คำตอบก่อน → เหตุผล → สูตรละเอียด”

### New report order
1. Executive Summary / สรุปคำตอบก่อน
2. Input & Assumptions
3. One Cycle Energy Breakdown
4. Runtime & Number of Cycles
5. Battery Sizing Flow: Wh → Ah
6. Current / BMS Check
7. What Is / Is Not Included
8. Appendix A — Detailed Formula & Substitution

### Executive Summary
หน้าแรกแสดงทันที:
- Wh/Cycle
- จำนวน Cycle เต็ม
- พลังงานรวม Wh
- Ah ขั้นต่ำ
- Ah practical / ขนาดมาตรฐานเบื้องต้น
- BMS Continuous ขั้นต่ำ
- BMS Peak ขั้นต่ำ
- สถานะ Turning Energy

### One Cycle Energy Breakdown
รวมข้อมูลเที่ยวไป/กลับไว้ในตารางเดียว:
- Flat outbound
- Uphill
- Downhill
- Flat return
- Differential/Pivot
- Drive subtotal
- Auxiliary
- Total Wh/Cycle
พร้อมเปอร์เซ็นต์ Drive vs Auxiliary เพื่อเห็นว่าส่วนใดเป็นโหลดหลักใน Scenario ปัจจุบัน

### Battery Sizing Flow
แสดง Flow เดียว:
E_cycle × N_cycle → E_total → DoD → Reserve → Ah_min → Kb → Ah_practical → standard Ah

### Current / BMS
- Continuous = max(steady uphill, pivot average)
- Peak = max(Continuous, Drive Torque design-current reference)
- ป้องกันกรณี Peak ต่ำกว่า Continuous
- แสดง BMS floor แยกจาก Energy/Ah sizing

### Turning section
- ถ้า Turning Disabled: แสดงเฉพาะสถานะและค่าที่เป็น 0 แบบสั้น
- ถ้า Turning Enabled: จึงแสดงสูตรและ substitution เต็ม

### Removed duplication
- Battery PDF ไม่ต่อท้าย “คำอธิบายภาษาไทยเพิ่มเติม” ซ้ำอีกครั้ง
- สูตรเต็มเก็บใน Appendix เพื่อใช้อ้างอิงเมื่ออาจารย์ต้องการดูที่มาของตัวเลข

### Engineering notes
- Downhill ≈ 0 Wh หมายถึง traction energy บนช่วงลาด ไม่ได้หมายความว่าเที่ยวกลับใช้ 0 Wh
- Kb เป็น Preliminary Design Allowance ไม่ใช่ค่ามาตรฐานตายตัว
- Winch 12 V energy ยังแยกจาก Main Battery 72 V; เวลายกสามารถรวมใน Cycle time ได้
- เป็น Preliminary engineering calculation ต้องยืนยันด้วยข้อมูลจริงก่อนผลิตใช้งาน
