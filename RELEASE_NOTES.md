# Crane Vehicle Engineering Tool V53.5.0

## Full Calculation Web + Updater Release

อัปเดตรอบนี้นำเว็บคำนวณแบบละเอียดเข้า Update Channel อย่างเป็นทางการ เพื่อให้ปุ่ม Check Update ในโปรแกรมสามารถดาวน์โหลดเวอร์ชันนี้ได้โดยตรง

### Web Calculation
เพิ่มตารางคำนวณแบบละเอียดในทุกโมดูลหลัก:
- ตัวแปร / รายการ
- สูตรสัญลักษณ์
- แทนค่าตัวเลขอัตโนมัติ
- ผลลัพธ์
- หน่วย
- คำนวณหาอะไร
- อธิบายสูตรแบบง่าย

### Drive Torque
- ความเร็ว SI
- รัศมีล้อ
- ความเร่ง
- แรงจากความชัน
- แรงต้านการกลิ้ง
- แรงเร่ง
- แรงรวมและแรงออกแบบ
- แรง/มอเตอร์
- Torque/มอเตอร์
- Wheel RPM
- Mechanical/Electrical Power
- Battery Current
- Traction Margin

### Main Battery 72V
- ระยะและเวลาต่อรอบ
- จำนวนรอบเชิงทฤษฎี
- ทางราบ / ทางลาด
- กำลังทางราบ / ขึ้นลาด / ช่วงเร่ง
- Drive Energy
- Auxiliary Energy
- DoD
- Reserve
- Design Wh
- Design Ah
- Standard Ah
- Uphill / Acceleration Current
- No Regen

### Winch 12V
- Datasheet interpolation
- Rope layer / line pull check
- เวลา UP / DOWN
- Auto / Manual จำนวนงานยก
- จำนวนรอบในเวลาทำงาน
- พลังงานต่อ 1 งานยก
- พลังงานรวม
- Ah used / Ah design
- Standard battery capacity
- BMS continuous / peak check

### Stability / Tipping
- Side / Front / Rear SF
- Pivot
- Load / Boom position
- Overturning Moment
- Resisting Moment
- Crane / Load longitudinal position
- คำเตือนให้ยืนยัน CG จริงและ Dynamic Load

### Updater
- V53.5.0 ถูกปล่อยผ่าน GitHub Update Channel
- Check Update จะอ่าน latest.json แล้วพบ V53.5.0
- Installer และ CraneVehicleWebServer.exe ถูกสร้างและเผยแพร่ผ่าน GitHub Actions
