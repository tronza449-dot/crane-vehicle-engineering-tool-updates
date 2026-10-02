# Crane Vehicle Engineering Tool V53.5.3

## Tailscale Funnel First-Run Fix

แก้ปัญหาที่เห็นใน V53.5.2:
`tailscale funnel ... timed out after 45 seconds`

### สาเหตุ
ครั้งแรกที่ใช้ Tailscale Funnel ระบบต้องให้เจ้าของ Tailnet กด **Enable Funnel** ใน Browser ก่อน แต่ V53.5.2 ใช้คำสั่งแบบรอผล 45 วินาทีและเก็บ output ไว้ ทำให้ลิงก์อนุญาตของ Tailscale ไม่ถูกเปิดให้ผู้ใช้เห็น จึงหมดเวลา

### สิ่งที่แก้
- อ่าน output ของ Tailscale แบบสด (stream)
- ตรวจจับลิงก์อนุญาต Funnel ทันที
- เปิด Browser ไปหน้า **Enable Funnel** อัตโนมัติ
- แสดงสถานะในหน้า CVET ว่า “ต้องอนุญาต Funnel ครั้งแรก”
- รอผู้ใช้กดอนุญาตได้นานถึง 5 นาที แทน 45 วินาที
- หลังอนุญาตแล้ว โปรแกรมลองเปิด Funnel ต่อให้อัตโนมัติ
- ตรวจสถานะ Funnel ระหว่างรอ
- เมื่อสำเร็จ แสดงลิงก์ `https://cvet.<tailnet>.ts.net` ในหน้าโปรแกรม พร้อมปุ่มเปิด/คัดลอกลิงก์

### หมายเหตุ
การกด Enable Funnel เป็นการยืนยันบัญชี Tailscale ครั้งแรกเท่านั้น หลังจากนั้นการเปิด Permanent Link ครั้งต่อไปไม่ควรถามซ้ำ
