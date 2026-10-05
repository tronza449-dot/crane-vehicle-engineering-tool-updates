# Crane Vehicle Engineering Tool V53.8.20

## Updater Reliability Fix

แก้ปัญหาเครื่องผู้ใช้บางเครื่องกดอัปเดตแล้วตรวจเวอร์ชันหรือดาวน์โหลดไม่สำเร็จ แม้ GitHub Release และ latest.json จะถูกต้อง

### Update check
- อ่าน Update Source ที่ผู้ใช้ตั้งไว้ก่อน
- ถ้าเป็น custom/stale source จะเทียบกับ official GitHub manifest อัตโนมัติ
- เพิ่ม GitHub Contents API fallback เพื่อข้ามปัญหา raw.githubusercontent.com / CDN / cache
- เลือก manifest ที่มีเวอร์ชันใหม่ที่สุดจาก source ที่อ่านได้

### Download
- เพิ่ม retry ดาวน์โหลด installer สูงสุด 3 ครั้ง
- เพิ่ม timeout เป็น 120 วินาทีต่อ attempt
- ลบไฟล์ดาวน์โหลดค้างก่อน retry
- ยังตรวจ SHA256 ก่อนติดตั้งเหมือนเดิม

### Repair Update
- Repair Update ยังรีเซ็ต source กลับ official
- หลังแก้รุ่นนี้ updater จะมี fallback เพิ่ม แม้ raw GitHub มีปัญหา

### Security
- Remote update ยังบังคับ HTTPS
- SHA256 validation ยังทำงานก่อนเปิด installer
- ไม่ลดการตรวจสอบความถูกต้องของไฟล์

### Existing features
- Live Web FBD จาก V53.8.19 คงอยู่ครบ
- Desktop FBD / PDF / Battery / Stability ไม่มีการเปลี่ยนสูตรหลัก
