# Crane Vehicle Engineering Tool V52.6.0

## ESP32 / VESC Hardware I/O + Real-Time Telemetry / Data Logger

รุ่นนี้ทำ 2 ระบบที่ผู้ใช้เลือกต่อจากแผนพัฒนาเดิม:
- **2) ESP32 / VESC Hardware I/O Manager**
- **4) Real-Time Telemetry / Data Logger**

และเปลี่ยน Main Controller ของโปรเจกต์ให้เริ่มจาก **ESP32 DevKit V1 / ESP-WROOM-32 (Classic ESP32)** ก่อน แทนการเริ่มจาก ESP32-S3

### 1. Project Main Controller = ESP32
หน้า Hardware I/O เปิดครั้งแรกจะเลือก:
- ESP32 DevKit V1 / ESP-WROOM-32
- 34 physical GPIO
- แสดง Input-only GPIO
- แสดง Boot/Strapping pins
- แสดง UART0 shared pins
- Board Animation / Used / Free / Conflict เดิมยังทำงานครบ

Suggested project map สำหรับ ESP32:
- iBUS RX → GPIO16
- CAN TX → GPIO21
- CAN RX → GPIO22
- I2C SDA → GPIO18
- I2C SCL → GPIO19
- Limit Left → GPIO32
- Limit Right → GPIO33
- Buzzer → GPIO25
- LED → GPIO26

CAN ยังต้องผ่าน CAN Transceiver เช่น SN65HVD230 ก่อนต่อ CANH/CANL ไป VESC

ESP32-S3 / Waveshare 7B profiles ยังเก็บไว้ในโปรแกรมสำหรับ Reference หรือเปลี่ยนบอร์ดภายหลัง

### 2. ESP32 / VESC Hardware I/O Manager
ระบบเดิมถูกคงไว้และผูกกับ ESP32 project target:
- Animated GPIO Board
- GPIO conflict checker
- Voltage / logic level checker
- Protection checker
- Custom Device / I/O Builder
- Generate ESP32 Pin Map
- Save / Load Project
- Auto Save
- VESC CAN mapping
- BNO086 I2C
- FlySky iBUS
- Limit ±90°
- Buzzer / LED

### 3. Real-Time Telemetry Dashboard
เพิ่มเมนูใหม่:
**Home → LIVE TELEMETRY**
หรือเมนูซ้าย:
**Live Telemetry**

รองรับข้อมูล:
- Battery voltage (V)
- Battery current (A)
- Vehicle speed (km/h)
- BNO086 / IMU tilt (deg)
- Left motor RPM
- Right motor RPM
- VESC current (A)
- RC throttle
- RC steering
- Left / Right limit switch
- E-stop
- RC status
- System state

### 4. Live Graph
กราฟสดในโปรแกรม 3 ชุด:
- Battery / VESC Current vs Time
- Vehicle Speed vs Time
- IMU Tilt vs Time

เก็บ live buffer ล่าสุด 600 samples

### 5. ESP32 USB Serial Connection
รองรับ Windows COM Port ผ่าน pyserial:
- Refresh COM Port
- Baud 115200 / 230400 / 460800 / 921600
- Sample rate 1–20 Hz
- Connect / Disconnect

Protocol เป็น JSON 1 บรรทัดต่อ sample เช่น:
`{"battery_v":72.4,"battery_a":12.3,"speed_kmh":1.0,"tilt_deg":2.1,"left_rpm":12.0,"right_rpm":12.1,"state":"DRIVE"}`

### 6. Simulation / Demo
ถ้ายังไม่ได้ต่อ ESP32 จริง สามารถกด:
**Source → Simulation / Demo → Connect / Start**

โปรแกรมจะสร้างข้อมูลจำลองเพื่อ:
- ทดสอบ UI
- ทดสอบกราฟ
- ทดสอบ Data Logger
- ใช้อธิบายระบบต่ออาจารย์ก่อนรถจริงพร้อม

### 7. CSV Data Logger
เพิ่ม:
- Start Logging
- Stop Logging
- Clear Data
- Export CSV

CSV เก็บ:
- Timestamp
- Battery V/A
- Speed
- Tilt
- RPM L/R
- VESC current
- RC throttle/steer
- Limit L/R
- E-stop
- RC OK
- State

รองรับสูงสุด 200,000 rows ต่อ session ใน memory logger

### 8. ESP32 Telemetry Sender Template
หน้า Telemetry มี:
- Copy ESP32 Sender Template
- Export .ino

Template จะดึง GPIO map ปัจจุบันจาก Hardware I/O Manager และสร้างโครง Arduino/ESP32 สำหรับส่ง JSON ผ่าน Serial

ผู้ใช้สามารถแทน TODO ด้วยค่าจริงจาก:
- VESC CAN
- BNO086
- FlySky iBUS
- Limit switches
- Battery sensor

### 9. Safety display
Live Dashboard แจ้งสถานะ:
- E-STOP
- RC LOST
- LEFT LIMIT
- RIGHT LIMIT
- TILT LIMIT

หมายเหตุ: Dashboard เป็น Monitoring / Validation tool ไม่ใช่วงจร Safety-rated controller

### 10. Project migration
เมื่ออัปเดตจากเวอร์ชันก่อน V52.6:
- Auto Save ปัจจุบันจะย้าย Main Board target ไป Classic ESP32 อัตโนมัติ
- Project file เก่าที่ผู้ใช้เปิดเองยังคง Board Profile เดิม เพื่อไม่ทำลายงานเก่า

### Regression Gate
ก่อนสร้าง Setup.exe Windows Full Regression จะตรวจ:
- Project default = ESP32 DevKit / ESP-WROOM-32
- Classic ESP32 GPIO count = 34
- GPIO / VESC mapping
- Hardware conflict / voltage / custom I/O
- pyserial พร้อมใช้งานใน Windows build
- Telemetry Simulation
- JSON parser
- Live chart render
- Data Logger start/stop
- CSV export
- ESP32 sender template
- ระบบเดิม Torque / Battery / Winch / Stability / Control Logic / Flowchart / PDF / Updater ทั้งหมด

หมายเหตุ: ก่อนต่อฮาร์ดแวร์จริงต้องตรวจ pinout ของบอร์ด ESP32 ที่ซื้อจริง, logic 3.3 V, VESC CAN wiring, BNO086 breakout voltage, iBUS signal level, BMS/Fuse และ Grounding อีกครั้ง
