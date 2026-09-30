# Crane Vehicle Engineering Tool V53.2.0

## Flowchart Final + Responsive UI Fix

ปรับหน้า System Flowchart ใหม่ตามเอกสาร “คำอธิบาย Flowchart รถและเครน Final” ที่ผู้ใช้ส่งมา และแก้ UI เดิมที่แน่น/เส้นย้อนกลับไขว้กัน

### Flowchart sequence
Flowchart ใหม่แยกขั้นตอนตามเอกสาร Final:
- Start / Power ON
- Start System
- Read Remote Signal
- Remote OK?
- Read Tilt (IMU)
- Read Crane Limits Left/Right
- Read Motor Status (VESC)
- Motor System OK?
- Vehicle Tilt Too High?
- Warning ON / OFF
- Read Driving Command
- Calculate Left / Right Motor Speed
- Limit Speed to 1 km/h + Soft Start / Stop
- Drive Command Active?
- Stop Crane Rotation before Drive
- Send Drive Command to VESC
- Send Stop Command to VESC
- Vehicle Still Moving?
- Stopped for at least 0.5 s?
- Control Crane
- Crane Direction LEFT / STOP / RIGHT
- Directional Left / Right Limit checks
- Connector A returns to Read Remote Signal on the next loop

### Important behavior from submitted Final document
- Vehicle moving → Crane rotation is not allowed
- Crane may rotate only after the vehicle has been stationary continuously for at least 0.5 s
- Differential Steering is calculated before the VESC command
- Maximum speed is limited to approximately 1 km/h with Soft Start / Stop
- Tilt above the limit is shown as Warning ON (Buzzer + LED) in the Flowchart Final and the flow continues to Driving Command
- Hitting a crane limit blocks further travel into that limit but still allows movement back out

This release changes the Flowchart visualization to match the submitted Final document. It does not silently replace the separate Control Logic simulator's existing tilt policy.

### UI fixes
- Removed the cramped horizontal Flowchart/Explanation splitter
- Flowchart and Explanation are now separate tabs
- Added 60 / 70 / 80 / 90 / 100 / 115% Flowchart zoom
- Added Fit Laptop mode
- Replaced long crossing return wires with local Connector A symbols like the Final reference
- Fixed overlap around Vehicle Still Moving / 0.5 s stop gate
- Scenario controls are arranged in a responsive two-row grid
- Step description remains visible above the diagram
- Export PNG remains available

### Scenario animation
Includes:
- Drive Forward
- Idle / Ready
- Crane LEFT
- Crane RIGHT
- Remote Fault
- Motor / VESC Fault
- Tilt Warning
- Vehicle Still Moving
- Stopped < 0.5 s
- LEFT Limit Active
- RIGHT Limit Active

### Windows regression gate
Before release the Windows test verifies:
- every Final Flowchart scenario renders
- old merged Safety node is not used by the Final Flowchart
- Tilt Warning continues to Driving Command
- Vehicle Still Moving and 0.5 s gate are separate branches
- LEFT / RIGHT limit paths remain directional
- local Connector A nodes exist
- Flowchart and Explanation tabs open at all supported UI scales
- zoom modes render successfully
- all previous Torque, Battery, Winch, Stability, Hardware I/O, Telemetry, Integration, PDF and Updater tests still pass

หมายเหตุ: Flowchart หน้านี้เป็นการแสดงลำดับโปรแกรมตามเอกสาร Final ที่ผู้ใช้ส่งมา ไม่ใช่การรับรองระบบ Safety hardware จริง
