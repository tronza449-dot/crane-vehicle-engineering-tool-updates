# Crane Vehicle Engineering Tool V53.2.3

## Updater reliability hotfix

แก้กรณีโปรแกรมแจ้งว่า “เป็นเวอร์ชันล่าสุดแล้ว” ทั้งที่ GitHub มีเวอร์ชันใหม่กว่า

### Updater fixes
- เพิ่ม cache-busting query ทุกครั้งที่อ่าน latest.json
- ส่ง Cache-Control / Pragma no-cache
- เพิ่มปุ่ม Repair Update เพื่อรีเซ็ต Manifest URL กลับไป official GitHub แล้วตรวจใหม่ทันที
- แสดง Current version, Latest version และ Source URL ที่อ่านจริง
- ระบบ HTTPS และ SHA256 installer verification ยังคงเดิม

### Included UI fixes from V53.2.2
- proportional Flowchart canvas / uniform scale
- Fit Width
- readable Flowchart text
- wider left navigation
- Hardware I/O tab layout improvements
