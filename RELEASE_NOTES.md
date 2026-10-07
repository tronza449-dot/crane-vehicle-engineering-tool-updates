# Crane Vehicle Engineering Tool V53.8.29

## Stability Web Hotfix + Web-like Desktop Buttons / Mode Cards

### 1. Web Stability hotfix
แก้ error ที่หน้า Stability:
- `$(...).map is not a function`
- สาเหตุ: selector บางจุดคืน element เดียว แต่ถูกนำไปใช้ .map() / .forEach()
- แก้เป็น querySelectorAll collection โดยตรงสำหรับ:
  - Component Mass rows
  - Mode A / Mode B cards
  - Mass mode radio inputs
  - Component Mass input listeners

เพิ่ม cache-busting เป็น `?v=53.8.29` เพื่อบังคับ browser โหลด JS/CSS ใหม่ ไม่ค้างไฟล์ V53.8.28

### 2. Desktop button animation — Web style
ปรับปุ่ม Desktop ให้ฟีลเหมือน Web:
- Mouse press: opacity ลดลงแบบ smooth
- Release: opacity กลับ 100%
- Click acknowledgement: blue flash สั้น ๆ แบบ Web btn-ack
- ปุ่ม Action ยังคง Busy → Success / Error ตามเดิม
- Animation ใช้ QPropertyAnimation + QGraphicsOpacityEffect จึงไม่ถูก Qt Layout ดึงตำแหน่งกลับ

### 3. Desktop Stability Mode selector — Web card style
เปลี่ยนการเลือกโหมด Stability/Tipping จาก Combo/Radio แบบเดิม เป็นการ์ดกดเลือกเหมือน Web:
- Mode A — Total Mass
- Mode B — Component Mass
- การ์ดที่เลือกมีพื้นฟ้า + กรอบน้ำเงิน
- Hover state ชัดเจน
- ทั้งหน้า Crane Mode และ Component Mass ใช้หน้าตาเดียวกัน
- โหมดทั้งสองหน้าซิงก์กันอัตโนมัติ

### Regression coverage
เพิ่มการตรวจ:
- Stability Web ต้องใช้ querySelectorAll collection
- ห้ามกลับไปใช้ single-element selector กับ .map / .forEach
- Desktop press animation ต้องสร้าง opacity effect และ animation จริง
- Stability mode cards ต้องสลับ A/B และซิงก์กันได้
