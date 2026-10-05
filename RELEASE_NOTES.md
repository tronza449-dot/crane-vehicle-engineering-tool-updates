# Crane Vehicle Engineering Tool V53.8.23

## Web Current Semantics + Measured Ramp Default

ปรับแก้หลัง Web Calculation Audit V53.8.22 เพื่อให้การเลือก BMS, การแสดงค่ามอเตอร์ และค่าเริ่มต้นทางลาดตรงกับความหมายทางวิศวกรรมมากขึ้น

### Main Battery / BMS
- แยก Continuous current ออกจาก Peak current อย่างชัดเจน
- Continuous = ค่าสูงสุดของ steady uphill current และ Pivot-turn average current
- Peak = ค่าสูงสุดระหว่าง Continuous และ Drive Torque design-current reference
- Drive Torque reference ไม่ถูกนำไปพองค่า Continuous อีกต่อไป
- ตาราง Candidate Battery / BMS และ C-rate ใช้ Continuous/Peak คนละค่าตามความหมายจริง

### Web UI
- Current-check notice แสดง Continuous และ Peak แยกกันพร้อมที่มาของค่า
- Vehicle Parameters / Drive Motors ดึงจำนวนมอเตอร์และกำลังมอเตอร์จากหน้า Drive Torque โดยตรง
- เพิ่มช่อง Motor rated power (W / motor) ในหน้า Drive Torque
- แก้ข้อความแหล่งข้อมูล Drive Motors ให้ตรงกับค่าที่ใช้จริง

### Measured ramp baseline
สำหรับข้อมูลวัด h=55 cm และ run=280 cm:
- θ = atan(55/280) ≈ 11.11°
- Slope ≈ 19.64%
- ใช้ 11.11° เป็น Web default สำหรับ Drive, Main Battery และ Slope Stability
- 19.64 ใช้เป็น % grade เท่านั้น ไม่ใช้แทนองศา
- เพิ่ม one-time migration: ถ้า Browser ยังเก็บค่า legacy 19° ครบทั้ง 3 โมดูลและ Ramp ยังเป็น 55/280 cm จะเปลี่ยนเป็น 11.11° อัตโนมัติ

### Regression
- ปรับ regression ให้ตรวจว่า Continuous ไม่ถูกบังคับให้เท่ากับ Drive Torque design-current
- ตรวจว่า Peak ครอบคลุม Drive Torque reference
- ยังคง Desktop ↔ Web Stability parity และ regression ชุดเดิมทั้งหมด

### Calculation scope
ยังเป็น Preliminary engineering calculation
ควรยืนยันน้ำหนักจริง, CG จริง, rolling resistance, traction และกระแสจริงจากการทดสอบก่อนผลิตใช้งาน
