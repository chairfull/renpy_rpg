---
type: character
name: Hakim
id: hakim
desc: Manages the settlement's ration crates, medical supplies, and barter ledgers.
location: market
pos: 600,550
factions:
  - supply_union
tags:
  - merchant
  - organizer
  - logistics
gender: male
age: 45
height: 180 cm
weight: 82 kg
hair_color: black
hair_style: close-cropped
eye_color: brown
face_shape: rectangular
skin_tone: medium
build: solid
body_type: humanoid
breast_size: n/a
dick_size: average
foot_size: 43
distinctive_feature: trimmed beard
equipment:
  head: ball_cap
  torso: logistics_coat
  pants: slacks
  feet: work_boots
items:
  - ration_pack
  - note_card
  - keycard
  - water_flask
---

# Talk
```flow
hakim: Every nutrition bar is counted. Every medical kit is signed for by the Coordinator.
hakim: If you want to barter, bring something the settlement can actually use—scrap tech, clean water, or data logs. 
$ hakim.mark_as_met()
```
