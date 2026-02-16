---
type: character
name: Elena
id: elena
base_image: chars/female_fit.png
description: A high-tension combat medic who specializes in frequency-induced trauma and Sleeper-bite stabilization.
location: temple
pos: 500,300
factions:
  - field_meds
tags:
  - medic
  - clinician
  - healer
affinity: 20
gender: female
age: 34
height: 170 cm
weight: 62 kg
hair_color: black
hair_style: tight bun
eye_color: gray
face_shape: oval
skin_tone: olive
build: athletic
body_type: humanoid
breast_size: medium
dick_size: n/a
foot_size: 38
distinctive_feature: clinic tattoo behind ear
equipment:
  head: surgical_cap
  torso: medical_coat
  pants: scrub_pants
  feet: clinic_shoes
items:
  - med_patch
  - antiseptic_wipe
  - bandage_roll
  - water_flask
---

# Talk
```flow
elena: Slow breaths. Keep your hands where I can see them. Clean hands keep people on this side of the pulse.
elena: If you feel the 'Static' in your head, report to the clinic immediately. We can't afford a sleeper waking up inside the walls.
$ elena.mark_as_met()
```

# Dialogue

## Checkup
```yaml
short: Ask for a checkup
long: I've been hearing a low hum... can you check my resonance levels?
tags:
  - Medical
memory: true
cond: true
```

```flow
elena: Hold still. It's just a diagnostic sweep.
STATUS REMOVE flu
NOTIFY "Your cognitive resonance stabilizes."
```

# Give

## Battery Cell
```flow
elena: Good. I can keep the clinic lights stable for another night.
GIVE battery_cell from=character to=elena count=1
NOTIFY "You gave Elena a Battery Cell."
```
