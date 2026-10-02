# Crane Vehicle Engineering Tool V53.6.4

## Dynamic Vehicle Parameters

แก้หน้า Vehicle Parameters ให้ไม่เป็นค่าคงที่อีกต่อไป

### ตอนนี้ค่าจะเปลี่ยนตาม Input ที่ตั้งจริง
- Mass → จาก Main Battery / Drive Input
- Payload → จาก Stability Input
- Main Battery Voltage → จาก Main Battery Input
- Drive Motors → จากจำนวนมอเตอร์ + กำลังมอเตอร์ใน Main Battery
- Main Slope → จาก Main Battery Input
- Run Time Target → จาก Main Battery Input
- Crane Arm → จาก Stability Input
- Support / Track → จาก Stability Input
- Winch Supply → จาก Winch Battery Input

### Project Settings
เพิ่มช่องสำหรับค่าที่ไม่มี Input ในหน้าคำนวณอื่น:
- Vehicle width
- Vehicle length
- Crane rotation limit / side
- Drive control

### Live Sync
เมื่อแก้ค่าจาก Drive Torque / Main Battery / Winch / Stability
หน้า Vehicle Parameters จะเปลี่ยนตามทันทีโดยไม่ต้องกรอกซ้ำ

### Remember Settings
ค่าที่กรอกในหน้าเว็บจะถูกเก็บใน Browser Local Storage
ดังนั้น Refresh หน้าเว็บแล้วค่าที่ตั้งไว้จะไม่กลับเป็นค่า Default

### หมายเหตุ
แต่ละโมดูลยังสามารถใช้ทดสอบ Scenario แยกกันได้
หน้า Vehicle Parameters จะแสดงค่าจากแหล่งที่ระบุใต้การ์ดแต่ละใบ
