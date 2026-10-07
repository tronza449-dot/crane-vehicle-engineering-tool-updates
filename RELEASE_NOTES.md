# Crane Vehicle Engineering Tool V53.8.46

## Calculation explanation redesign

This release urgently redesigns the user-facing Calculation Trace so the purpose is immediately understandable.

### New visible name
**ดูที่มาของคำตอบ / สูตรทีละขั้น**

The technical term "Calculation Trace" is retained only as a secondary description.

### What the page now answers
Every module is explained in the same five-step reading order:
1. ค่าที่ใช้ / Inputs used
2. สูตรที่ใช้ / Formula
3. แทนค่าจริง / Numeric substitution
4. คำตอบ / Result
5. ตรวจสอบ / PASS-FAIL or interpretation

### Desktop
- Renamed the Project Tools tab.
- Replaced technical module names with Thai-first labels.
- Added a clear explanation that this page does not use a second calculation engine.
- Drive, Ramp, Main Battery, Winch and Stability now explain where the displayed answer comes from.

### Web
- Renamed the Engineering Decision Tools card.
- Added Thai-first module choices and a "แสดงที่มาของคำตอบ" button.
- Reworded loading and completion messages.
- Keeps the existing audited step renderers and calculation APIs.

### Calculation integrity
No engineering formulas were changed by this UI redesign.
The page continues to expose results from the same audited Torque, Ramp, Battery, Winch and Stability calculations.
