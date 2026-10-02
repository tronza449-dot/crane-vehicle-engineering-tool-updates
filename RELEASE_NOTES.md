# Crane Vehicle Engineering Tool V53.5.7

## Real ESP32 Telemetry Verification

แก้พฤติกรรม Live Telemetry ที่กด Connect แล้วขึ้นเหมือนเชื่อมต่อสำเร็จทั้งที่ยังไม่มี ESP32 จริง

### หลักการใหม่
คำว่า **CONNECTED** หมายถึง:
- โปรแกรมได้รับ Telemetry packet จริงจาก ESP32 แล้ว
- Packet มีโครงสร้าง CVET telemetry ที่ถูกต้อง
- WiFi mode ต้องมี Device ID ตรงกับค่าที่ตั้งไว้
- ข้อมูลล่าสุดต้องไม่เก่าเกิน 2.5 วินาที

แค่เปิด COM Port หรือเปิด UDP Port สำเร็จ **ไม่ถือว่าเชื่อมต่อ ESP32**

### สถานะใหม่
- OFFLINE — ยังไม่ได้เปิดช่องทางรับข้อมูล
- WAITING ESP32 — เปิด Serial/UDP listener แล้ว แต่ยังไม่ได้รับข้อมูลจาก ESP32 จริง
- CONNECTED ESP32 — ได้รับและตรวจสอบ packet จาก ESP32 จริง
- DEMO / NO ESP32 — ข้อมูลจำลอง ไม่ใช่ฮาร์ดแวร์จริง

### WiFi UDP
- ค่าเริ่มต้นของหน้า Telemetry เปลี่ยนเป็น ESP32 WiFi UDP
- โปรแกรมขึ้น WAITING จนกว่า ESP32 จะส่ง packet จริง
- ตรวจ Device ID เช่น `CVET-ESP32`
- เพิ่ม protocol marker `CVET1`
- ถ้า ESP32 หยุดส่งเกิน 2.5 s จะไม่ค้าง CONNECTED
- ค่าจากรถจะถูกซ่อนเมื่อ link ไม่สด

### Serial
- เปิด COM Port ได้ = WAITING เท่านั้น
- ต้องได้รับ CVET telemetry JSON จริงจึงขึ้น CONNECTED
- Template ใหม่เพิ่ม `protocol: CVET1` และ `device: CVET-ESP32`

### Test WiFi Packet
ปุ่ม Test WiFi Packet ทดสอบเฉพาะ UDP listener ในคอม
และ **จะไม่ทำให้โปรแกรมขึ้นว่า ESP32 CONNECTED**

### Simulation
เปลี่ยนชื่อเป็น:
`Simulation / Demo (NO ESP32)`

และมีข้อความเตือนชัดเจนว่าข้อมูลเป็นข้อมูลจำลอง


### Build / Regression
- ปรับชุดทดสอบอัตโนมัติให้ตรวจหลักการใหม่อย่างถูกต้อง
- ยืนยันว่าเปิด UDP listener อย่างเดียวต้องยังเป็น WAITING
- ยืนยันว่า packet จริงจาก ESP32 จึงเปลี่ยนเป็น CONNECTED
- ยืนยันว่า Local Test Packet ไม่สร้าง fake hardware connection
