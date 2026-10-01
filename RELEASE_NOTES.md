# Crane Vehicle Engineering Tool V53.3.0

## Winch page redesigned from the supplied 4500LB specification sheet

เปลี่ยนเมนู Winch จากหน้ากรอกสมมติฐานหลายค่า เป็นหน้า Specification + Battery Calculator หน้าเดียว

### Manufacturer data shown as locked specification
- Rated line pull: 4500 lb (2041 kg), single line
- Motor: Permanent magnet, 1.4 kW / 1.9 hp
- Gear reduction: 136:1
- Gear train: Differential Planetary
- Cable: Ø5 mm × 10 m
- Control: Remote switch
- Drum: Ø37 mm × 72 mm
- Clutch: Sliding Ring Gear
- Braking: Automatic In-The-Drum
- Dimensions: 316 × 120 × 106 mm
- Mounting pattern: 166 × 76 mm, Ø9 mm
- Weight: N.W. 9 kg / G.W. 10 kg
- Packing: 43 × 30.5 × 36 cm, 2PC
- First-layer pull / speed / motor-current table
- Rope-layer pull / capacity table

### User-editable input
- จำนวนรอบขึ้น + ลง เท่านั้น

### Locked project assumptions
These are shown separately because they are not all stated in the visible specification sheet:
- Payload = 100 kg
- Lift distance = 1.00 m per travel
- Separate winch battery = 12 V
- DoD = 80%
- Reserve = 20%

### Battery calculation
- Interpolates first-layer speed and current at 100 kg from the manufacturer table
- 100 kg result is approximately 3.124 m/min and 22.57 A
- Calculates lift time, Wh/cycle, total Wh and design Ah from cycle count
- Shows minimum standard battery size and next extra-margin size
- Manufacturer table maximum current 140 A is used as the high-current BMS check reference

### Source limitation shown in the UI
The sheet does not provide separate lowering current/speed or starting/stall surge. V53.3 therefore uses the lifting current/speed for lowering as a conservative calculation assumption and clearly labels it as an assumption rather than manufacturer data.

### Other project changes retained
- System Flowchart remains removed from the active application
- Control Logic / Safety Simulator remains available
- Hardware I/O, WiFi Telemetry, Drive, Battery, Stability and Engineering Suite remain available
