---
type: character
name: Faye
id: faye
desc: Manages the rationed cots and the only filtered-air room in the district.
location: tavern
pos: 300,350
factions:
  - supply_union
tags:
  - host
  - friendly
  - logistics
affinity: 10
gender: female
age: 31
height: 165 cm
weight: 58 kg
hair_color: auburn
hair_style: braided
eye_color: green
face_shape: heart
skin_tone: light
build: slim
body_type: humanoid
breast_size: small
dick_size: n/a
foot_size: 37
distinctive_feature: freckled nose
equipment:
  head: bandana
  torso: supply_apron
  pants: work_pants
  feet: work_boots
items:
  - ration_pack
  - water_flask
  - note_card
  - sewing_kit
---

# Talk
```flow
faye: You look like you've been breathing too much static. Sit, eat your rations, then move on.
faye: Space is tight, but I can find a cot if you need to let your frequency drop for a while.
$ faye.mark_as_met()
```
