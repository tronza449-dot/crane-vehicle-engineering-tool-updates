# Crane Vehicle Engineering Tool V53.8.15

## One-click Screenshot Tools

เพิ่มระบบแคปหน้าจอในโปรแกรมเพื่อลดการแคปเองทีละหน้า

### Global Capture
เพิ่มปุ่ม:
- 📸 Capture

ตำแหน่ง:
- Status bar ด้านล่างของโปรแกรม

การทำงาน:
- แคปหน้าต่าง CVET ที่กำลังเปิดอยู่เป็น PNG
- ไม่เปิด Save As ทุกครั้ง
- ตั้งชื่อไฟล์อัตโนมัติจากวันเวลา + หน้าที่กำลังเปิด
- บันทึกที่:
  Documents/CVET_Screenshots

ตัวอย่างชื่อไฟล์:
- 20261005_234501_Stability_Engineering_FBD.png
- 20261005_234530_Battery_Electrical.png

### Capture All FBD
เพิ่มปุ่มในหน้า Engineering FBD:
- 📸 Capture All FBD

กดครั้งเดียว โปรแกรมจะสร้างรูปอัตโนมัติ 6 รูป:
1. Geometry / Tipping-axis definition
2. Left Side critical FBD
3. Right Side critical FBD
4. Front critical FBD
5. Rear critical FBD
6. Uphill rear-tipping FBD

ไฟล์ถูกเก็บใน subfolder:
- Documents/CVET_Screenshots/<timestamp>_FBD_All

ชื่อไฟล์ระบุ case และ critical angle ให้อัตโนมัติ

### Workflow
- ไม่เปลี่ยน view ที่ผู้ใช้กำลังดู
- ไม่ต้องกดเปลี่ยน case ทีละหน้า
- เหมาะสำหรับส่งรูปตรวจงานหรือแนบรายงาน

### Regression
GitHub Actions ตรวจเพิ่ม:
- Capture Current Page สร้าง PNG ได้จริง
- Capture All FBD สร้างครบ 6 รูป
- ทุกไฟล์มีขนาดข้อมูลมากกว่า minimum regression threshold

### Stability calculation
ไม่มีการเปลี่ยนสูตร Stability / FBD calculation ในรุ่นนี้
