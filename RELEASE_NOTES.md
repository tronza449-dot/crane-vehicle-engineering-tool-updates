# Crane Vehicle Engineering Tool V53.6.5

## Shared Project Parameters Sync

แก้ปัญหา Vehicle Parameters ไม่เปลี่ยนตามค่าที่แก้ในบางหน้าคำนวณ โดยเฉพาะมุมทางลาด

### สาเหตุ
ก่อนหน้านี้ Vehicle Parameters อ่าน Main Slope จาก Main Battery เท่านั้น
ดังนั้นถ้าไปแก้มุมทางลาดใน Drive Torque ค่า Vehicle Parameters จะยังแสดงค่าจาก Main Battery เดิม

### พฤติกรรมใหม่
ค่าที่เป็น Project Parameter ร่วมจะ Sync กันอัตโนมัติระหว่างหน้า:
- Mass: Drive Torque ↔ Main Battery
- Slope angle: Drive Torque ↔ Main Battery
- Vehicle speed: Drive Torque ↔ Main Battery ↔ Winch
- Main battery voltage: Drive Torque ↔ Main Battery
- Number of motors: Drive Torque ↔ Main Battery
- One-way distance: Main Battery ↔ Winch
- Operating runtime: Main Battery ↔ Winch

เมื่อแก้ค่าจากหน้าใดหน้าหนึ่ง:
1. ค่าในหน้าที่เกี่ยวข้องจะเปลี่ยนตาม
2. Vehicle Parameters จะเปลี่ยนทันที
3. ค่าจะถูกจำไว้หลัง Refresh

### ตัวอย่าง
เปลี่ยน Slope จาก 19° เป็น 12° ใน Drive Torque:
- Main Battery Slope จะเปลี่ยนเป็น 12°
- Vehicle Parameters / Main Slope จะเปลี่ยนเป็น 12° ทันที

ค่าที่ยังเป็น Project Settings เช่น Vehicle width/length, Crane rotation และ Drive control ยังคงตั้งจากหน้า Vehicle Parameters
