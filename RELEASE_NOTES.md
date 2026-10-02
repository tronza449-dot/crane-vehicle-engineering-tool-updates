# Crane Vehicle Engineering Tool V53.5.2

## Web Link Display Fix

แก้ปัญหา V53.5.1 เปิด Web Server แล้วผู้ใช้ไม่เห็นลิงก์ในหน้าหลักของโปรแกรม

### สิ่งที่แก้
- Web Server ส่งสถานะกลับมาที่โปรแกรมหลัก
- แสดง URL จริงในแผง WEB SERVER ทันทีเมื่อพร้อม
- เพิ่มปุ่ม **เปิดลิงก์**
- เพิ่มปุ่ม **คัดลอกลิงก์**
- แสดงสถานะระหว่างติดตั้ง/Login Tailscale/เปิด Funnel
- ถ้า Funnel เปิดไม่สำเร็จ โปรแกรมหลักจะแสดงสาเหตุแทนที่จะปล่อยให้ผู้ใช้รอ
- รองรับการแสดง URL ทั้ง:
  - FREE PERMANENT LINK — Tailscale Funnel
  - QUICK PUBLIC LINK — Cloudflare
  - LAN / Wi-Fi
  - LOCAL

### Permanent Link
เมื่อ Tailscale Funnel พร้อม โปรแกรมจะแสดงลิงก์รูปแบบประมาณ:

`https://cvet.<tailnet>.ts.net`

ไม่ต้องไปหาลิงก์ในหน้าต่าง Console อีกต่อไป
