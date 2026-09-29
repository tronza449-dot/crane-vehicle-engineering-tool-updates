# Crane Vehicle Engineering Tool V52.3.0

## Animated ESP32 GPIO Board Map

ปรับระบบ GPIO ใหม่ตามที่ต้องการ: ไม่ได้มีแค่ตารางเลือก GPIO แต่เพิ่ม “รูปบอร์ดแบบ Interactive + Animation” ที่แสดง GPIO ทั้งหมดของ Profile และเปลี่ยนสถานะทันทีเมื่อผู้ใช้เลือกขาให้โปรเจกต์

### Board Animation / GPIO Map
- วาดบอร์ด ESP32 แบบ vector ภายในโปรแกรม
- GPIO ที่โปรเจกต์ใช้อยู่จะเรือง/กระพริบ (animated pulse)
- คลิก GPIO บนรูปเพื่อดูรายละเอียดขานั้น
- เมื่อ GPIO ถูกใช้ซ้ำจะแสดงสีแดง CONFLICT บนรูปทันที
- แสดง USED / FREE / ONBOARD / SHARED / CAUTION / MEMORY / CONFLICT
- Board Summary แสดงจำนวน GPIO และจำนวนขาแต่ละสถานะ

### ESP32 profiles
1. Generic ESP32-S3
   - 45 physical GPIO
   - GPIO0–21 และ GPIO26–48
   - แก้บั๊กเดิม: GPIO22–25 ไม่ใช่ GPIO ของ ESP32-S3 จึงไม่ให้เลือกอีกต่อไป
   - แสดง strapping / USB-JTAG / memory-related pins เป็น Caution

2. Waveshare ESP32-S3-Touch-LCD-7B
   - ใช้ข้อมูล pin allocation จากเอกสาร Waveshare
   - LCD RGB pins แสดง ONBOARD
   - Touch/I2C GPIO4/8/9
   - TF card GPIO11/12/13
   - RS485 GPIO15/16
   - CAN/USB shared GPIO19/20
   - UART0 GPIO43/44
   - GPIO6 แสดงเป็น GP6 external GPIO
   - Flash/PSRAM-related GPIO แสดง MEMORY
   - Suggested Map จะไม่สร้าง GPIO ปลอมเพื่อยัดทุกสัญญาณ หากขาบอร์ดไม่พอจะปล่อย MISSING เพื่อให้เห็นข้อจำกัดจริง

3. Custom ESP32-S3
   - 45 physical GPIO พร้อม manual mapping

4. ESP32 DevKit V1 / ESP-WROOM-32
   - 34 physical GPIO
   - แสดง Input-only GPIO และ boot/strapping caution
   - รูปบอร์ดแนว DevKit สำหรับการอ้างอิงแบบภาพที่ผู้ใช้ต้องการ

### Project-aware visualization
- Device Manager กับ Board Animation ใช้ข้อมูลชุดเดียวกัน
- เปลี่ยน GPIO ในตาราง → รูปบอร์ดเปลี่ยนทันที
- คลิกขาที่ใช้แล้ว → เลือก row ของ Device Manager ที่ใช้ขานั้น
- Manual Reserved GPIO แสดงบนบอร์ด
- Board Profile เปลี่ยน → รายการ GPIO ใน ComboBox เปลี่ยนตามชิปจริง
- Invalid pin / board-reserved pin / memory pin ถูกตรวจอัตโนมัติ

### Waveshare 7B engineering note
บอร์ด 7B ใช้ GPIO จำนวนมากกับจอและอุปกรณ์ onboard. พอร์ตที่เปิดออกมาสำหรับงานภายนอกมีจำกัด:
- GP6
- I2C GPIO8/9 (shared)
- UART0 GPIO43/44
- CAN/USB GPIO19/20 (shared/mux)

ดังนั้นสัญญาณตรงของโปรเจกต์ เช่น Limit Left/Right, Buzzer, LED อาจมีขาไม่พอหากใช้บอร์ดนี้เป็น Main Controller ทั้งหมด. โปรแกรมจะแสดง MISSING/CONFLICT แทนการแนะนำขาที่ไม่พร้อมใช้งาน เพื่อให้พิจารณา I/O expander หรือ Controller แยกอย่างถูกต้อง.

### Data sources used for profile model
- Espressif ESP32-S3 GPIO documentation
- Espressif ESP32 GPIO documentation
- Waveshare ESP32-S3-Touch-LCD-7B official interface documentation / schematic

### Regression Gate
Windows full regression เพิ่มการตรวจ:
- ESP32-S3 = 45 GPIO และไม่มี GPIO22–25
- Waveshare onboard LCD pin map
- Waveshare I2C/CAN/UART shared pins
- Classic ESP32 = 34 GPIO
- Input-only pin classification
- Duplicate/reserved pin → CONFLICT
- Animated board renders successfully in offscreen Windows test
- Clicked pin detail works
- Hardware project state, PDF, updater, Torque, Battery, Winch, Stability และ Control Logic เดิมต้องผ่านก่อน Release

หมายเหตุ: Board Animation เป็น engineering visualization ไม่ใช่ภาพ PCB สำหรับใช้เดินลายวงจร. ก่อนต่อของจริงต้องตรวจ revision ของบอร์ดและ datasheet/schematic อีกครั้ง.
