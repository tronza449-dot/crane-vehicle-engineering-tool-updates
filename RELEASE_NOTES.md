# Crane Vehicle Engineering Tool V53.0.0

## Engineering Integration Suite

V53 รวมระบบที่ใช้ “ออกแบบ → ต่อวงจร → ทดสอบ → วินิจฉัย → คุมต้นทุน → เก็บ Revision → ตรวจ Final” ไว้ในโปรแกรมเดียว และเพิ่ม Device Library ที่ผู้ใช้เพิ่มอุปกรณ์ใหม่เองได้

### 1) Device Library / เพิ่มอุปกรณ์เอง
เพิ่มหน้า Device Library:
- Add / Edit / Duplicate / Delete device
- Category: Sensor, Actuator, Communication, Switch/Input, Display/HMI, Power, Safety, Other
- Signal / Interface / Supply / Logic / Protection / Note
- 1 device มีหลาย signal ได้ โดยเพิ่มหลายแถวชื่อ Device เดียวกัน
- Add to Hardware I/O ได้ทันที
- Add to BOM ได้ทันที
- Device Library ถูก Save/Load และ Auto Save พร้อม Project

เมื่อส่งไป Hardware I/O:
- ขึ้นบน Animated ESP32 GPIO Board
- ตรวจ GPIO conflict / reserved / voltage / protection เหมือนอุปกรณ์มาตรฐาน
- Generate ESP32 Pin Map ได้เหมือนเดิม

### 2) Test & Validation Center
เพิ่มระบบเปรียบเทียบ Calculated vs Measured:
- Vehicle speed
- Required wheel torque
- Uphill battery current
- Drive energy per round trip
- Winch lift time
- Winch load speed
- IMU zero tilt
- เพิ่ม Test ใหม่เองได้
- กำหนด Tolerance %
- คำนวณ Error %
- PASS / FAIL / PENDING อัตโนมัติ
- Fill from Latest Telemetry สำหรับ Speed / Battery Current / Tilt
- ข้อมูล Validation เข้า Final Verification และ Final PDF

### 3) Fault & Diagnostic Center
กด Run Diagnostics แล้วตรวจ:
- E-stop / RC failsafe / VESC fault / Tilt / Interlock
- GPIO conflict / Voltage error / Missing pin / Protection
- Design Check FAIL
- Main battery capacity / Continuous / Peak current
- Validation failures
- Latest ESP32 Telemetry: E-stop / RC lost / Tilt over limit
- Fault log พร้อมเวลาและ Recommended Action

### 4) BOM + Cost + Weight
เพิ่ม BOM Manager:
- Item
- Category
- Qty
- Unit Cost (THB)
- Unit Mass (kg)
- Supplier / URL
- Status
- Note
- Load Project Baseline BOM
- Add/Delete item
- รวม Cost และ Mass อัตโนมัติ
- เตือนถ้ามวลที่กรอกเกิน 300 kg
- บอกจำนวนรายการที่ยังไม่ได้กรอก Mass/Cost
- Device Library สามารถส่งอุปกรณ์เข้า BOM ได้

### 5) Design Revision Manager
เพิ่ม Revision/Snapshot:
- Capture Revision
- Name + Note + Timestamp + Version
- Apply revision กลับมาใช้งาน
- Delete revision
- Compare 2 revisions
- เปรียบเทียบ Mass / Track / Wheelbase / Boom / Slope / Speed / Battery / Runtime / Payload
- Revision ถูกเก็บใน Project JSON โดยป้องกัน recursive snapshot

### 6) Final Project Verification
หน้า Final Verification รวม:
- Integrated Design Check
- Hardware GPIO / Voltage / Protection
- Validation
- Diagnostics
- BOM / Cost / Weight
- Revision history
- Telemetry/Data Logger

แสดง:
- PASS
- CHECK
- FAIL
- READY FOR FINAL REVIEW / REVIEW REQUIRED / NOT READY

### 7) Final Engineering PDF
Final PDF เพิ่ม:
- Final Project Verification
- Test & Validation
- Fault & Diagnostics
- BOM / Cost / Weight
- Revision list
- GPIO Board image (เมื่อมี)
- System Flowchart image (เมื่อมี)
พร้อม Drive, Battery, Winch, Stability, BMS และรูปเดิมทั้งหมด

### 8) ระบบเดิมยังอยู่ครบ
- Drive Torque / Traction
- Trip Energy Summary
- Battery Selection
- Winch
- Stability / Worst Case / FBD
- Control Logic Simulator
- Animated System Flowchart
- ESP32 Hardware I/O + Add New I/O
- Animated GPIO Board Map
- Real-Time ESP32 Serial Telemetry
- CSV Data Logger
- Auto Save
- GitHub Auto Update

### Windows Regression Gate
ก่อน Release จะทดสอบเพิ่ม:
- เปิด Engineering Suite ทุกหน้าบนหลาย resolution/font scale
- เพิ่ม Device Library item และส่งเข้า Hardware I/O
- Validation target + measured values
- Fill measured values จาก latest telemetry
- Baseline BOM + cost/mass totals
- Revision snapshot ไม่มี recursive history
- Diagnostics render
- Final Verification render
- Save/Load integration data round-trip
- Final PDF พร้อมระบบใหม่
รวมกับ regression เดิมทั้งหมดก่อน Build Setup.exe

หมายเหตุ: Diagnostics / Verification / Validation เป็น engineering support tools ไม่ใช่ safety certification. ต้องยืนยัน datasheet, wiring, current rating, actual test data และโครงสร้างจริงก่อนใช้งานเครื่องจักร.
