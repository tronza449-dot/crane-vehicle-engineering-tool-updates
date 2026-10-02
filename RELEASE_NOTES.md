# Crane Vehicle Engineering Tool V53.7.0

## Ramp Geometry / การคำนวณองศาและความชันทางลาด

เพิ่มการคำนวณตามค่าที่วัดจริงของทางลาดโดยตรง ทั้งใน Desktop และ Web

### Input
ค่าเริ่มต้นตามข้อมูลที่วัด:
- ความสูง h = 55 cm
- ระยะราบ x = 280 cm
- ความยาวทางลาดที่วัดได้ = 290 cm
- มวลรถสำหรับตรวจ F_slope = 300 kg (Web)
- Desktop สามารถเลือกใช้มวลจาก Main Battery ได้

### 1) ความยาวทางลาดจากพีทาโกรัส
สูตร:
`L = sqrt(x^2 + h^2)`

สำหรับ h = 55 cm, x = 280 cm:
- L = 285.35 cm
- L = 2.854 m
- เทียบค่าที่วัด 290 cm ต่างประมาณ 4.65 cm

### 2) มุมทางลาด
สูตร:
`theta = atan(h/x)`

ผล:
- theta ≈ 11.11°

### 3) เปอร์เซ็นต์ความชัน
สูตร:
`Slope (%) = (h/x) × 100`

ผล:
- Slope ≈ 19.64%

โปรแกรมแสดงคำเตือนชัดเจนว่า:
- 19.64% คือเปอร์เซ็นต์ความชัน
- ไม่ใช่ 19.64°
- สูตร sin/cos ของมอเตอร์ต้องใช้ 11.11°

### 4) แรงจากความชัน
โปรแกรมคำนวณและตรวจซ้ำสองสมการ:
`F_slope = m g sin(theta)`

และ

`F_slope = m g (h/L)`

ทั้งสองวิธีต้องให้ผลเท่ากันจากรูปสามเหลี่ยมทฤษฎี

### Desktop
เพิ่มส่วน Ramp Geometry ใน:
Stability → Slope

มีปุ่ม:
- คำนวณ Ramp Geometry
- ใช้มุมนี้กับ Torque + Main Battery + Stability
- ใช้ L ทฤษฎีกับ Slope Length ใน Main Battery

เพิ่มความละเอียดมุมเป็น 2 ตำแหน่ง และ Slope Length เป็น 3 ตำแหน่ง

### Web
เพิ่มเมนู:
- Ramp Geometry

พร้อม:
- รูปสามเหลี่ยมทางลาด
- h / x / L
- มุม theta
- Slope %
- ค่าความต่างระหว่าง L ที่วัดกับ L ทฤษฎี
- F_slope
- สูตร + แทนค่า
- ปุ่มส่งมุมไป Drive Torque + Main Battery
- ปุ่มส่ง L ทฤษฎีไป Main Battery

ค่า Input ของหน้า Ramp ถูกจำไว้ใน Browser เช่นเดียวกับหน้าคำนวณอื่น

### Regression
เพิ่มการทดสอบอัตโนมัติสำหรับกรณี:
h = 55 cm, x = 280 cm, L_measured = 290 cm

ยืนยันว่า:
- L ≈ 285.35 cm
- theta ≈ 11.11°
- Slope ≈ 19.64%
- Difference ≈ 4.65 cm
- m g sin(theta) = m g h/L
