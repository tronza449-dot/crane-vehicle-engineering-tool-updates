# Crane Vehicle Engineering Tool V51.0.4

## Bug Fix & Responsive UI Audit
- แก้หน้า Control Logic Simulator ที่ช่อง Input ซ้อนทับกัน โดยเปลี่ยนเป็น Splitter + Scrollable Input
- ปรับ System State / Output ให้ยืดหดได้ดีขึ้นบนจอ 1366×768
- แก้ความหมาย Drive Permit: READY + CH5 ON จะแสดงว่าอนุญาต Drive แม้ Throttle = 0
- ขณะ Winch ทำงาน จะล็อก Drive Permit เพื่อคงเงื่อนไขรถหยุด
- ปรับ Electrical / Battery Input ให้เลื่อนได้และจำกัดความกว้างช่องกรอก
- ปรับ Torque Input ให้เลื่อนได้ ลดปัญหาหน้าจอเตี้ย/ข้อมูลล้น
- ปรับ Crane parameter panel ให้เลื่อนได้
- ลดความสูง Input/Button เล็กน้อยเพื่ออ่านง่ายแต่ไม่กินพื้นที่เกิน
- ลดความกว้าง Sidebar และลด minimum window size เพื่อรองรับจอ Laptop
- เปิด Scroll Buttons + Elide สำหรับ Tab ที่ชื่อยาว
- แก้ Calculated uphill current ให้ใช้ Estimated drive efficiency เดียวกับ Calculated energy model
- คง Hotfix Winch Variable Dictionary จาก V51.0.3

## Build Reliability
- เพิ่ม Windows offscreen UI smoke test ก่อนสร้าง Installer
- Smoke test เปิด App จริง, รัน Torque/Battery/Winch/Stability/Variables/Project Tools/Safety Logic
- ตรวจ key contract ของ Winch และ READY Drive Permit ก่อนอนุญาตให้ Release

หมายเหตุ: Logic Simulator เป็นเครื่องมือจำลองเงื่อนไขก่อนนำ Logic ไปเขียน ESP32 ไม่ได้สั่งฮาร์ดแวร์จริง
