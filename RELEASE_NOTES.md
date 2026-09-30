# Crane Vehicle Engineering Tool V53.2.2

## Flowchart display + responsive UI fix

แก้ปัญหาหน้าจอจาก V53.2.1 ที่ Flowchart ถูกยืด/บีบและบางหน้ามีข้อความโดนตัดบนจอ Laptop / Windows scaling

### Flowchart UI
- เปลี่ยน Flowchart เป็น fixed-size canvas ตามค่า Zoom เพื่อไม่ให้ Qt ยืดแกน X/Y คนละอัตรา
- ใช้ uniform painter scale เพื่อรักษาสัดส่วนกล่อง, diamond และเส้น connector
- เปลี่ยน QScrollArea เป็น non-resizable canvas + vertical/horizontal scrolling ตามจริง
- Default Flowchart zoom เป็น 90%
- เปลี่ยน Fit Laptop เป็น Fit Width ที่คำนวณตาม viewport จริง
- ป้องกันการลดขนาด font ซ้ำตาม zoom ทำให้ข้อความอ่านง่ายขึ้น
- ลำดับ Flowchart Final และ Connector A เดิมยังคงไว้

### Main UI / Hardware I/O
- ขยายเมนูซ้ายจาก 185 px เป็น 225 px ลดการตัดชื่อเมนู
- เพิ่ม tooltip และความสูงขั้นต่ำให้ปุ่มเมนู
- ปิด tab text elision เพื่อไม่ให้ชื่อ tab กลายเป็น ...
- ย่อชื่อ Hardware tabs ให้เหมาะกับจอ Laptop
- ลด minimum width ของ Board GPIO Summary
- ลด margin หน้า Hardware I/O เพื่อเพิ่มพื้นที่ทำงาน

### Control logic retained
- Vehicle moving → Crane rotation not allowed
- Crane control requires vehicle stationary continuously for at least 0.5 s
- Tilt in the submitted Final flowchart remains Warning ON/OFF and does not automatically stop the vehicle in that visualization
- Crane limits remain directional: a hit limit blocks travel further into that side while allowing movement back out

### Release pipeline
GitHub Actions performs syntax, engineering calculation, responsive UI, Flowchart, Hardware I/O, Telemetry, updater and PDF regression checks before publishing the Windows installer.
