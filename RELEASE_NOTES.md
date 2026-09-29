# Crane Vehicle Engineering Tool V52.0.0

## Hardware I/O & Wiring Manager

V52 เพิ่มระบบสำหรับวางแผนการต่อ ESP32 และตรวจความผิดพลาดของ Hardware ก่อนประกอบจริง โดยยังคงระบบ Torque, Battery, Winch, Stability, Control Logic, Report และ Auto Update จาก V51 ครบทั้งหมด

### Device / GPIO Manager
- ตารางอุปกรณ์ FlySky iBUS, SN65HVD230 CAN TX/RX, BNO086 SDA/SCL, OMRON Limit ±90°, Buzzer และ LED
- เปิด/ปิดอุปกรณ์แต่ละรายการได้
- เลือก ESP32 GPIO ได้เอง
- ตรวจ GPIO ซ้ำอัตโนมัติ
- รองรับ Reserved GPIO list สำหรับขาที่จอ/Touch/USB/SD หรือวงจรบนบอร์ดใช้อยู่แล้ว
- มี Board Profile สำหรับ Generic ESP32-S3, Waveshare ESP32-S3 7-inch Type B และ Custom ESP32
- Suggested Generic Map เป็นเพียงจุดเริ่มต้น และจะยกเลิกสถานะ Board Verified ทุกครั้งจนกว่าผู้ใช้ตรวจ pinout จริง

### Voltage & Signal Checker
- ตรวจ Supply rail 3.3 V / 5 V / 12 V / 72 V
- ตรวจ Logic level ก่อนเข้า ESP32 3.3 V
- เตือนเมื่อ 5/12/72 V ถูกตั้งให้ต่อ Direct เข้า GPIO
- iBUS 5 V logic ต้องมี Level Shifter / Divider หรือวงจร conditioning
- Limit ±90° ใช้ PC817 isolation ตาม architecture ของโปรเจกต์
- Buzzer 5 V ใช้ MOSFET / Driver
- CAN ใช้ SN65HVD230 ระหว่าง ESP32 กับ VESC

### Wiring Protection Checker
ตรวจ checklist:
- Main 72 V BMS
- Main fuse
- Hardware E-stop / traction enable cut
- 72 V → regulated 5 V
- Regulated 5 V for RC receiver
- Limit switch isolation
- Buzzer MOSFET
- Separate 12 V winch battery
- Winch fuse
- Reversing contactor current rating

พร้อมสรุปเส้นทาง:
72 V Battery → BMS → Main Fuse → E-stop → Flipsky Dual 75100 → QS Hub Motors
72 V → DC-DC 5 V → ESP32 / RC / Logic
ESP32 → SN65HVD230 → CANH/CANL → VESC
Limit ±90° → PC817 → ESP32
Separate 12 V Battery → Fuse → Reversing Contactor → Winch

### System Check Dashboard
แสดง:
- GPIO CONFLICT
- VOLTAGE ERROR
- MISSING PIN
- PROTECTION
- READY FOR CODE

READY FOR CODE จะเป็น YES เมื่อไม่มี conflict/error/missing protection และผู้ใช้ยืนยันว่าได้ตรวจ GPIO กับ pinout/datasheet ของบอร์ดจริงแล้ว

### ESP32 Pin Map Generator
- สร้าง C/C++ header อัตโนมัติ
- #define PIN_IBUS_RX
- PIN_CAN_TX / PIN_CAN_RX
- PIN_I2C_SDA / PIN_I2C_SCL
- PIN_LIMIT_LEFT / PIN_LIMIT_RIGHT
- PIN_BUZZER / PIN_LED
- Copy code ได้
- Export เป็น .h ได้

### Project Integration
- Hardware mapping ถูกบันทึกใน Project JSON
- Auto Save จดจำ GPIO, voltage, protection และ enable state
- Hardware readiness ถูกเพิ่มเข้า Integrated Design Check / Final Project Verification
- เพิ่ม Hardware I/O เป็นเมนูด้านซ้ายและ Card หน้า Home

### Regression Gate
GitHub Actions จะทดสอบก่อนออก Setup.exe:
- เปิด Hardware page บน Windows
- Suggested map ต้องไม่มี duplicate/missing/voltage error
- Duplicate GPIO ต้องถูกตรวจพบ
- Reserved GPIO ต้องถูกตรวจพบ
- Direct 5 V iBUS → ESP32 ต้องถูกเตือน
- Waveshare profile ต้องมี reserved GPIO verification
- Generated header ต้องมี macro ครบ
- Hardware state ต้อง Save/Load Project ได้
- ทดสอบ UI ทุกความละเอียดและทุก Font Scale
- ทดสอบ Torque/Battery/Winch/Stability/Safety/PDF/Updater เดิมครบก่อน Release

หมายเหตุ: Hardware checker เป็น Preliminary Wiring Design Tool ไม่แทน datasheet/pinout จริงของ ESP32 board, FlySky receiver, BNO086 breakout, VESC หรืออุปกรณ์กำลัง ต้องตรวจพิกัดแรงดัน/กระแส/สายไฟ/Fuse/grounding ก่อนจ่ายไฟจริง
