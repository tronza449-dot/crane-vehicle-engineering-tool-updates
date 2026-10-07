# Crane Vehicle Engineering Tool V53.8.47

## Coupled System What-if + clearer calculation explanation

V53.8.47 includes the Thai-first calculation explanation redesign and replaces the old one-variable-at-a-time What-if with a coupled system scenario model.

### What-if redesign
The old Sensitivity / What-if changed one Stability input at a time while holding all other values fixed. That could be misleading for dependent quantities such as Payload and Total mass.

The new **What-if ทั้งระบบ / Coupled Scenario** compares a Baseline with one multi-variable Scenario and recalculates the connected engineering modules together.

### Deterministic relationships now propagated
- Total mass = Base vehicle mass + Boom mass + Payload system mass.
- The same derived Total mass is used by Drive Torque, Main Battery and Stability.
- Route Slope is propagated to Drive Torque, Main Battery and Slope Stability.
- Wheel track W affects Stability and Pivot/Differential turning energy when that energy mode is enabled.
- Operation speed affects route time, completed cycles and automatic Winch job count.
- Winch lift distance affects Winch time and therefore the operating-cycle timing.
- Winch load can be linked to Payload system mass or left as an independent scenario input.

### Relationships the program intentionally does not invent
The tool does not guess:
- how much frame mass increases when W or WB grows,
- how much Boom mass increases when Boom length L grows,
- how CG moves when geometry changes without component positions.

Those quantities remain explicit Scenario inputs or should be derived from Component Mass / CG data when real geometry is available.

### Baseline vs Scenario output
The What-if result now compares:
- total mass,
- torque per motor and motor power margin,
- Main Battery minimum/practical Ah and modeled Wh,
- completed route cycles,
- Winch lift time and 12 V battery Ah,
- worst lifting SF and critical case,
- Slope SF,
- overall governing stability.

The current project design is restored after every What-if evaluation; the scenario does not overwrite the saved design.

### Calculation explanation
The former Calculation Trace is now presented primarily as:
**ดูที่มาของคำตอบ / สูตรทีละขั้น**

It explains:
1. ค่าที่ใช้
2. สูตรที่ใช้
3. แทนค่าจริง
4. คำตอบ
5. ตรวจสอบ / PASS-FAIL

The technical name Calculation Trace is retained only as a secondary description.

### Regression
The release audit now verifies that reducing Payload also reduces derived Total mass by the same amount in the coupled scenario, and keeps the existing calculation, PDF, Save/Restore, updater and Desktop↔Web checks.
