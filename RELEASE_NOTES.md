# Crane Vehicle Engineering Tool V53.8.39

## Stability FBD Direction Fix — Critical Case Is Now the Default

### 1. Why Side Right showed M_O = 0
The calculation itself was not globally zero.

The Web and Desktop FBD pages previously opened in **Current Angle Snapshot** mode by default.
For example, when the current crane angle is -90° (boom points left):
- Side Left has an overturning moment
- Side Right correctly has no overturning moment at that same snapshot angle
- Front/Rear may also show M_O = 0 depending on geometry

That behavior is mathematically correct for a snapshot, but it is confusing when the user selects “Side Right / Front / Rear” expecting the directional tipping design case.

### 2. Critical Case is now the default
Both Desktop and Web Stability FBD now open in:

**Critical Case / มุมวิกฤตของด้านที่เลือก**

So:
- Side Left automatically uses its worst angle
- Side Right automatically uses its worst angle
- Front automatically uses its worst angle
- Rear searches the permitted crane range -90° to +90°
- Current Angle Snapshot remains available as a separate view

### 3. Directional validation using the project geometry
Regression now validates this exact engineering example:

Inputs:
- total mass = 300 kg
- base vehicle = 180 kg
- boom = 20 kg
- payload = 100 kg
- track = 1.10 m
- boom length = 1.20 m
- dynamic factor = 1.20

At current crane angle -90°:
- Side Right current M_O = 0 — correct because the boom is pointing left
- Side Left current M_O > 0

For Side Right **Critical Case**, the scanner must find +90° and produce approximately:
- M_O = 774.99 N·m
- M_R = 971.19 N·m
- SF = 1.253

The release build fails if this directional behavior changes.

### 4. Clear zero-M_O explanation
When M_O = 0:
- Current view now says the current crane angle does not create overturning in that direction and recommends switching to Critical Case.
- Critical view says no overturning was found in that direction within the permitted crane range -90° to +90°.

This is especially important for Rear tipping: with a crane restricted to ±90°, a rear-mounted axis that remains inside the rear support line may legitimately have no rear overturning moment from the boom/payload.

### 5. Desktop/Web consistency
Desktop FBD default:
- Critical Case

Web FBD default:
- Critical Case

All previous Desktop ↔ Web numerical parity tests remain enabled.
