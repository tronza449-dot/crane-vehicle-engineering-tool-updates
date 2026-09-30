# Crane Vehicle Engineering Tool V53.1.0

## ESP32 WiFi Live Telemetry

เพิ่มการส่งข้อมูลจาก ESP32 มาที่โปรแกรมผ่าน WiFi โดยตรง ไม่ต้องเสียบ USB Serial ระหว่างใช้งานรถ

### Transport ใหม่
ในหน้า Live Telemetry เลือก Source ได้ 3 แบบ:
- Simulation / Demo
- ESP32 Serial JSON
- ESP32 WiFi UDP JSON

WiFi mode ใช้ UDP แบบ receive-only:
- โปรแกรมเปิด Listener บน PC
- ESP32 ส่ง JSON telemetry มาที่ PC IP + UDP Port
- ค่าเริ่มต้น UDP Port = 4210
- แสดง Remote ESP32 IP และ Packet Rate แบบสด
- ถ้า Listener เปิดแต่ยังไม่มี packet จะแสดง LISTENING
- เมื่อรับข้อมูลจริงจะแสดง LIVE

### ข้อมูลที่รองรับ
- Battery voltage
- Battery percent
- Battery current
- Vehicle speed
- IMU tilt
- Left / Right RPM
- VESC current
- RC throttle / steering
- Limit Left / Right
- E-stop
- RC OK / failsafe
- WiFi RSSI
- Device ID
- Sequence number
- ESP32 uptime
- State

### WiFi Setup ในโปรแกรม
เพิ่ม:
- เลือก PC IP
- Refresh PC IP
- ตั้ง UDP Port
- Device ID filter
- Test WiFi Packet
- Remote IP / packet Hz dashboard
- WiFi Setup / Safety tab
- Windows Firewall guidance

### ESP32 WiFi Sender Template
หน้า ESP32 Protocol / Code จะเปลี่ยนตาม Source:
- Serial mode → Serial JSON sketch
- WiFi mode → WiFiUDP sketch

WiFi template สร้างให้อัตโนมัติตาม:
- PC IP ที่เลือก
- UDP Port
- Sender rate
- Device ID

ใช้เฉพาะ:
- WiFi.h
- WiFiUdp.h

ไม่ต้องติดตั้ง ArduinoJson เพิ่ม และมีช่อง TODO สำหรับต่อข้อมูลจริงจาก VESC / BNO086 / RC / Limit switches

### Data Logger
CSV เพิ่ม metadata:
- device
- transport
- source_ip / source_port
- seq
- uptime_ms
- wifi_rssi_dbm
- battery_pct

### Safety architecture
WiFi channel ในรุ่นนี้เป็น TELEMETRY RECEIVE-ONLY:
- ไม่ส่ง Drive command
- ไม่สั่ง Crane
- ไม่สั่ง Winch
- ไม่แทน RC failsafe / E-stop

UDP ไม่มี encryption/authentication ในตัว จึงควรใช้บน LAN/WiFi ที่ไว้ใจได้
Device ID เป็นตัวกรอง packet ไม่ใช่ security key

### Windows Regression Gate
ก่อน Release ต้องผ่าน:
- Simulation telemetry
- Serial JSON parser/template
- UDP listener bind
- UDP packet จริงผ่าน 127.0.0.1 loopback
- Device ID filter
- WiFi metadata parsing
- Built-in Test WiFi Packet
- WiFi ESP32 template generation
- CSV export
- clean UDP disconnect
- ระบบ Torque / Battery / Winch / Stability / Control Logic / GPIO / Flowchart / Engineering Suite / PDF / Auto Update เดิมทั้งหมด

หมายเหตุ: ถ้า Windows Firewall ถามครั้งแรก ให้เปิดเฉพาะ Private network ที่ไว้ใจได้สำหรับการทดสอบใน LAN.
