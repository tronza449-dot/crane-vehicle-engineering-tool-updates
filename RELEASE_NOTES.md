# Crane Vehicle Engineering Tool V53.2.5

## System Flowchart removed

นำฟังก์ชัน System Flowchart ออกจากโปรแกรมตามคำขอ เนื่องจากหน้าวาด Flowchart ทำให้ UI มีปัญหาซ้ำบน Windows display scaling บางเครื่อง

### Removed from active application
- ไม่สร้างหน้า System Flowchart ตอนเปิดโปรแกรม
- ลบ System Flowchart ออกจากเมนูซ้าย
- ลบการ์ด System Flowchart จากหน้า Home
- ลบ Flowchart ออกจาก dynamic page navigation
- ลบการ sync อัตโนมัติจาก Control Logic ไป Flowchart
- ปรับ GitHub regression test ไม่ให้สร้างหรือทดสอบ Flowchart อีก

### Still available
- Control Logic / Safety Simulator
- Hardware I/O / GPIO Manager
- WiFi / Live Telemetry
- Drive Torque
- Battery / Electrical
- Winch
- Stability
- Engineering Suite
- Variables / Project Report
- Auto Update

หมายเหตุ: Logic ความปลอดภัยของรถและเครนยังอยู่ใน Control Logic; การถอดครั้งนี้เป็นการถอดเฉพาะ UI/visual System Flowchart ออกจาก active application.
