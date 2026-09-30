# Crane Vehicle Engineering Tool V53.2.4

## Hardware I/O + Flowchart visual layout fix

แก้จากภาพหน้าจอ V53.2.3 ที่ Hardware I/O ยังดูบีบ/ยืดและสัดส่วนไม่เป็นธรรมชาติ

### Hardware I/O
- ESP32 Board Animation เปลี่ยนเป็น fixed logical canvas 1080×720
- หน้าต่างย่อ/ขยายจะไม่บีบหรือยืดรูปบอร์ดอีก
- ใส่ Board Canvas ใน QScrollArea; พื้นที่ไม่พอให้ scroll แทนการ deform
- Board / Summary เปลี่ยนเป็น QSplitter ปรับสัดส่วนซ้าย-ขวาได้
- Summary pane มีความกว้างขั้นต่ำ/สูงสุดที่อ่านง่ายกว่าเดิม
- ปรับ Clicked Pin pane ให้สมดุลกับ Summary
- แก้ชื่อ tab ให้แสดง “Voltage & Wiring” จริง (escape Qt mnemonic)

### System Flowchart
- เพิ่ม logical side margins รอบแผนผัง
- Fit Width รองรับพื้นที่กว้างขึ้นโดยยังรักษาสัดส่วน
- Zoom range สูงสุดเพิ่มเป็น 135%
- เพิ่มปุ่ม Reset 100%
- บังคับ viewport background เป็นสีขาวเพื่อไม่ให้เกิดแถบสี/พื้นที่โปร่งแปลก ๆ
- Canvas ยังเป็น fixed proportional canvas + scroll; ไม่ยืด X/Y คนละอัตรา

### Included updater fixes
- no-cache latest.json
- Repair Update
- Current / Latest / Source visibility
