# Crane Vehicle Engineering Tool V53.5.5

## CAR ANIMAL Web Dashboard

อัปเดตรอบนี้เน้น 2 อย่างตามที่เลือก:
1. ทำหน้าเว็บให้มีชื่อโปรเจกต์และภาพลักษณ์จริง
2. เพิ่ม Dashboard หน้าแรกสำหรับเข้าแต่ละโมดูลได้ง่าย

### 1) Project Branding
หน้าเว็บด้านบนแสดง:
- CAR ANIMAL • SENIOR PROJECT
- Crane Vehicle Engineering Tool
- ระบบคำนวณวิศวกรรมสำหรับรถขนซากสัตว์พร้อมเครน
- Mechatronics Engineering
- Mahanakorn University of Technology
- Server Online / Offline
- CVET Version
- Project name

### 2) Engineering Dashboard
หน้าแรกเปลี่ยนเป็น Dashboard และมีการ์ด:
- Drive Torque
- Main Battery 72 V
- Winch Battery
- Stability
- Vehicle Parameters
- Live Telemetry
- Project Summary

การ์ดสามารถกดเพื่อเปิดหน้าที่เกี่ยวข้องได้ทันที

### Vehicle Parameters
เพิ่มหน้าแสดง Project Baseline เช่น:
- Vehicle 1000 × 1500 mm
- Mass ≤ 300 kg
- Payload 100 kg
- Main Battery 72 V
- 2 × 1500 W Hub Motor
- Main Slope 19°
- Runtime 3 h
- Crane ±90°
- Crane arm 1.2 m
- Winch supply 12 V separate

### Live Telemetry
เพิ่มหน้า UI สำหรับ:
- Speed
- Battery %
- Tilt Angle
- Drive State
- E-stop
- IMU Alarm

หมายเหตุ: V53.5.5 เพิ่มหน้า Telemetry Dashboard ก่อน แต่ยังไม่ได้ผูก Public Web Server เข้ากับ ESP32 telemetry stream โดยตรง จึงจะแสดง -- จนกว่าจะเพิ่ม Telemetry API/WebSocket ในอัปเดตถัดไป

### Project Summary
เพิ่มหน้าสรุป:
- Vehicle Platform
- Crane & Winch
- Electrical Architecture
- Safety Logic
- Engineering Calculations
- Web Architecture

### Responsive
Dashboard ใหม่รองรับ Desktop / Tablet / Mobile
