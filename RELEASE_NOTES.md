# Crane Vehicle Engineering Tool V52.4.0

## Custom Device / Input / Output Builder

เพิ่มความสามารถให้ผู้ใช้เพิ่มอุปกรณ์ใหม่และ Input/Output ใหม่เองจากในโปรแกรม โดยไม่ต้องแก้โค้ด Python

### วิธีใช้
Hardware I/O & Wiring → GPIO / Device Manager → + Add New I/O

กรอก:
- Device / ชื่ออุปกรณ์
- Signal / ชื่อ Input-Output
- Interface
- Device supply
- Signal logic to ESP32
- ESP32 GPIO
- Protection / Driver
- Note

รองรับ Interface:
- Digital IN / OUT
- ADC IN
- PWM OUT
- UART RX / TX
- I2C SDA / SCL
- CAN RX / TX
- SPI MISO / MOSI / SCK
- Interrupt IN
- Other

### Custom I/O controls
- + Add New I/O
- Edit Selected
- Duplicate
- Delete Custom
- รายการมาตรฐานลบไม่ได้ แต่ปิด Use ได้

### Live integration
เมื่อเพิ่ม I/O ใหม่:
- แสดงเป็นแถวใหม่ใน Device Manager
- ขึ้น USED บน Board Animation ทันที
- ตรวจ GPIO Conflict / Reserved / Invalid pin
- ตรวจ 5/12/24/72 V logic ต่อเข้า ESP32 ผิดระดับ
- รองรับ Level Shifter / Divider, PC817, Optocoupler, MOSFET, CAN Transceiver, Relay/Contactor
- Generate #define PIN_xxx ใน ESP32 header อัตโนมัติ
- Save/Load Project และ Auto Save ได้
- เปลี่ยน Board Profile แล้ว GPIO list ปรับตามบอร์ด

### Custom device workflow
ถ้าอุปกรณ์หนึ่งมีหลายสัญญาณ เช่น Encoder A/B:
1. Add New I/O → Encoder A
2. กด Duplicate
3. Edit Selected → เปลี่ยนเป็น Encoder B
4. เลือก GPIO คนละขา

### Safety checks
- Custom device supply สามารถเป็น 3.3 / 5 / 12 / 24 / 72 V ได้
- แต่ Signal logic เข้า ESP32 ยังต้องปลอดภัยที่ 3.3 V หรือผ่านวงจร conditioning/isolation
- Direct 12/24/72 V → ESP32 GPIO จะขึ้น Voltage Error
- GPIO ซ้ำกับอุปกรณ์เดิมหรือ Custom I/O อื่นจะขึ้น CONFLICT บนตารางและ Board Animation

### Project compatibility
- Project เก่าจาก V52.3 เปิดได้ตามเดิม
- Project ใหม่เก็บ metadata ของ Custom I/O: device, signal, interface, supply, logic, GPIO, protection และ note
- โหลด Project แล้ว Custom I/O จะถูกสร้างกลับให้อัตโนมัติ

### Regression Gate
Windows full regression เพิ่มการทดสอบ:
- เพิ่ม Custom 12 V proximity sensor + isolated 3.3 V input
- Custom pin ต้องขึ้น USED บน Board Animation
- Direct 12 V logic ต้องถูกตรวจเป็น Voltage Error
- Duplicate custom row ต้องได้ key ใหม่และ GPIO ยังไม่ถูกกำหนด
- Save Project → ลบ custom rows → Load Project ต้องสร้าง custom rows กลับครบ
- Generated ESP32 header ต้องมี custom macro
- ระบบเดิมทั้งหมดยังต้องผ่านก่อนสร้าง Setup.exe

หมายเหตุ: Hardware Manager เป็นเครื่องมือออกแบบเบื้องต้น การต่ออุปกรณ์จริงยังต้องตรวจ datasheet, pinout, logic voltage, current, pull-up/down, isolation และ protection ของอุปกรณ์จริงก่อนจ่ายไฟ
