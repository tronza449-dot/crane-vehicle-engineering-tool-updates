# Crane Vehicle Engineering Tool — Update Channel

Repository นี้ใช้เป็นช่องทางตรวจสอบเวอร์ชันใหม่ของโปรแกรม **Crane Vehicle Engineering Tool**

## Current version
- **V50.0.0**

## โปรแกรมตรวจอัปเดตอย่างไร
โปรแกรมจะอ่านไฟล์ `latest.json` จาก branch `main` แล้วเปรียบเทียบค่า `latest_version` กับเวอร์ชันที่ติดตั้งอยู่ในเครื่อง

Manifest URL:

`https://raw.githubusercontent.com/tronza449-dot/crane-vehicle-engineering-tool-updates/main/latest.json`

เมื่อมีเวอร์ชันใหม่ ให้แก้ `latest.json` เป็นเวอร์ชันใหม่ พร้อม:
- `download_url` ของ Setup.exe
- `sha256` ของ Setup.exe
- `notes` รายละเอียดการเปลี่ยนแปลง

> ตอนนี้ V50 เป็นเวอร์ชันล่าสุด และยังไม่ได้ผูกไฟล์ Setup.exe จริง จึงเว้น `download_url` และ `sha256` ไว้ก่อน
