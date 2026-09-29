# Crane Vehicle Engineering Tool V51.0.6

## Full Program Audit / ตรวจระบบทั้งโปรแกรม

รอบนี้เป็นการตรวจทั้ง UI, สูตรวิศวกรรม, Control Logic, PDF, Auto Update และ Windows build ก่อนให้ผู้ใช้อัปเดต

### Engineering calculation fixes
- แก้ Side Stability ให้ Payload และ Boom ที่ยังอยู่ด้านในแนว Pivot ช่วยสร้างโมเมนต์ต้านอย่างถูกต้อง
- Dynamic Factor ของ Payload ใช้เฉพาะด้านที่ทำให้คว่ำ ไม่ใช้เพิ่มโมเมนต์ต้าน เพื่อไม่สร้าง Safety Factor สูงเกินจริง
- แก้ Front/Rear Stability ให้ใช้หลักเดียวกัน: Payload ใช้ Kdyn เฉพาะเมื่อเป็นโมเมนต์คว่ำ
- แยก Base vehicle CG x ออกจาก Driving combined CG x เพื่อไม่ให้ Payload/Boom ถูกนับซ้ำใน Crane tipping
- Mass Mode B ส่ง Combined CG ไปใช้กับ Driving/Slope Mode โดยไม่เขียนทับ Base vehicle CG
- แก้ Slope Stability ให้ใช้ตำแหน่ง Combined CG จริงเทียบกับเพลาหลัง ไม่สมมติว่า CG อยู่กึ่งกลางรถเสมอ
- แก้ผลความเร่งบนทางลาดให้ใช้ a/(g cosα) และเพิ่ม Safety Factor เชิงโมเมนต์สำหรับ uphill driving
- แก้ Traction limit ให้ใช้แรงกดบน “ล้อขับ” N_drive แทน N_total ทั้งคัน
- เพิ่ม Driven-wheel load fraction (%) ค่าเริ่มต้น 50% เพื่อให้ตรวจ traction ไม่สูงเกินจริง
- Electrical/Battery เพิ่มพลังงานขาลงเมื่อ rolling resistance ยังต้องใช้แรงขับ และยังคง No Regen ไม่หักพลังงานคืน
- เวลาเร่ง t_acc ถูกนำไปใช้ตรวจ Peak acceleration force/current จริง
- BMS Peak Check รวม calculated acceleration peak current
- เพิ่ม Design Check ตรวจ m_total ≥ m_payload + m_boom

### Control Logic fixes
- Differential steering รองรับ Pivot Turn ด้วย Steering แม้ Throttle = 0
- Battery Low + Inhibit ล็อกเฉพาะ Drive ตามชื่อ policy; Crane/Winch ยังผ่าน interlock ของตน
- เพิ่ม Safety regression cases สำหรับ Pivot Turn และ Low Battery behavior
- E-stop, RC Failsafe, IMU Tilt, Drive/Crane Interlock และ Limit ±90° ยังคงตรวจครบ

### UI / usability fixes
- ลด minimum height ของ 3D/FBD/Graphs เพื่อใช้งานบนจอ Laptop ได้ดีขึ้น
- Crane right panel เลื่อนได้ และปุ่ม 3D View จัดเป็น Grid ไม่ล้นหน้าจอ
- แยกชื่อ Base vehicle CG และ Driving combined CG ให้ชัดเจน
- ปรับคำอธิบาย/Calculation Steps/Help ให้ตรงกับสูตรล่าสุด
- คง Responsive UI, Sidebar, Font Scale A-/A+/100% และ Scrollable Inputs จากรุ่นก่อน

### PDF / report fixes
- แก้ปุ่ม Export PDF หน้า Torque ที่เดิมเรียก Stability report ผิดหน้า
- เพิ่ม Drive Torque PDF exporter โดยตรง
- Stability PDF เปลี่ยนเป็น Qt PDF และให้ผู้ใช้เลือกโฟลเดอร์ ไม่เขียนลง Program Files
- ถอด ReportLab/Korean CID font ที่ไม่เหมาะกับภาษาไทยออก
- Winch/Battery/Torque/Stability/Final Report ใช้ฟอนต์ UI ที่มีใน Windows
- Temp report files ถูกล้างด้วย finally และตรวจว่า PDF ถูกสร้างจริง

### Updater / installer fixes
- Installer silent update จะเปิดโปรแกรมกลับหลังอัปเดตเสร็จ
- ชื่อ Setup ภายใน build ถูกทำให้คงที่
- คง AppId เดิม จึงติดตั้งทับ V51 เดิมได้โดยไม่ต้องถอน
- SHA256 verification และ HTTPS update channel ยังทำงานเหมือนเดิม

### Release gate
ก่อนสร้าง Setup.exe รุ่นนี้ GitHub Actions จะ:
- py_compile + AST duplicate-method audit
- เปิด App จริงบน Windows แบบ offscreen
- ทดสอบหน้าต่าง 1024×650, 1280×720, 1366×768, 1600×900
- ทดสอบ Font Scale 90%, 100%, 120%, 130%
- เปิดทุก Main Mode และทุก Internal Tab
- ทดสอบ Torque / Battery / Winch / Stability / Safety Logic
- ทดสอบ Project state round-trip
- ทดสอบ Local updater + SHA256
- สร้าง PDF จริงครบ 5 แบบและตรวจขนาดไฟล์

หมายเหตุ: ผลทางวิศวกรรมยังเป็น Preliminary Engineering Calculation ต้องยืนยันมวล/CG จริง, Torque-Speed curve, กระแสจริง, โครงสร้าง, จุดยึด, Slewing Bearing, ระบบเบรกวินช์, ยาง/พื้น และ Dynamic Shock ก่อนผลิตจริง
