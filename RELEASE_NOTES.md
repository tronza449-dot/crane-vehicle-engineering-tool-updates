# Crane Vehicle Engineering Tool V52.5.0

## Final System Flowchart / Animated Control Sequence

เพิ่มหน้าใหม่ในโปรแกรมสำหรับอธิบายลำดับการทำงานของรถและเครนแบบ Final โดยใช้ Flowchart แบบ Interactive + Animation และเชื่อมกับ Control Logic Simulator

### System Flowchart ใหม่
เข้าได้จาก Home → SYSTEM FLOWCHART หรือเมนูซ้าย → System Flowchart

Flow หลัก:
1. Start / Power ON
2. Initialize ESP32, RC, IMU, CAN/VESC และ Limit Switch
3. Read Remote + IMU + Limit Switch + VESC Status
4. Safety Check: RC / E-stop / VESC Fault / Tilt
5. ถ้ามี Drive command:
   - Stop Crane Rotation
   - Differential Mix
   - Speed Limit + Soft Start
   - Send Left/Right command to VESC
6. ถ้าไม่มี Drive command:
   - Send Drive = 0 to VESC
   - ตรวจ Vehicle stopped ≥ 0.5 s
   - จึงอนุญาต Crane LEFT/RIGHT
   - ตรวจ Limit ±90° ก่อนสั่งหมุน
7. ทุกเส้นทางกลับ Connector A เพื่ออ่าน Input รอบใหม่

Winch ยังคงเป็นระบบแยก: ใช้รีโมทของชุดวินช์ + แบต 12 V แยก ไม่อยู่ใน ESP32 Control Flow หลัก

### Interactive / Animation
- Scenario selector: Drive, Idle, Crane Left/Right, RC/E-stop, VESC Fault, Tilt Fault, Vehicle not stopped, Left/Right Limit
- ปุ่ม Prev / Next
- ปุ่ม Play/Stop animation
- Node ปัจจุบันเรือง/กระพริบ
- Sync from Control Logic: ดึงสถานะจาก Simulator แล้วเลือกเส้นทาง Flowchart ให้อัตโนมัติ
- Export Flowchart เป็น PNG ได้จากในโปรแกรม

### Safety Logic improvements
- เพิ่ม VESC / Motor Fault input
- VESC Fault → Drive = 0, Crane STOP, Alarm
- เพิ่ม Vehicle stopped ≥ 0.5 s input
- Crane command จะยังไม่ทำงานจนกว่ารถหยุดนิ่งครบ 0.5 s
- Limit -90°/+90° ยังห้ามหมุนต่อเข้า Limit แต่อนุญาตให้หมุนย้อนออก
- Differential steering / Pivot Turn ยังทำงานเหมือนเดิม
- Self-Test เพิ่มเป็น 15 scenarios

### Presentation use
Flowchart นี้ออกแบบให้ใช้ทั้ง:
- อธิบายโปรแกรมต่ออาจารย์
- ตรวจ Logic ก่อนเขียนลง ESP32
- เชื่อมความเข้าใจระหว่าง Control Logic, VESC, RC, IMU และ Crane interlock
- Export เป็นรูปเพื่อนำไปใส่รายงานหรือสไลด์

### Regression Gate
ก่อนสร้าง Setup.exe รุ่นนี้ Windows full regression จะตรวจ:
- เปิดหน้า Flowchart ในทุก resolution/font scale
- Render Flowchart จริงแบบ offscreen
- ทุก Scenario มี path ถูกต้อง
- VESC Fault เข้าสถานะ Safe Stop
- Crane ถูกล็อกเมื่อ stationary < 0.5 s
- Crane ทำงานเมื่อ stationary ≥ 0.5 s
- Sync จาก Control Logic → Flowchart
- Safety Self-Test 15/15
- ระบบเดิม Torque / Battery / Winch / Stability / Hardware I/O / PDF / Updater ยังต้องผ่านก่อน Release

หมายเหตุ: Flowchart และ Control Logic เป็น Preliminary Control Design / Simulator ไม่ใช่ Safety PLC หรือระบบที่ได้รับการรับรอง ต้องทดสอบ E-stop, VESC fault handling, braking, RC failsafe, limit switches และ interlock บนฮาร์ดแวร์จริงก่อนใช้งาน
