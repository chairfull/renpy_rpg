---
type: character
name: Greta
id: greta
desc: Keeps the shelter's alarms, air filtration, and signal rigs working with scrap-tech.
location: market
pos: 400,500
factions:
  - supply_union
tags:
  - crafter
  - mechanic
  - scraptech
affinity: 0
gender: female
age: 40
height: 172 cm
weight: 74 kg
hair_color: blonde
hair_style: tied back
eye_color: blue
face_shape: square
skin_tone: light
build: sturdy
body_type: humanoid
breast_size: medium
dick_size: n/a
foot_size: 39
distinctive_feature: oil-stained knuckles
equipment:
  head: bandana
  two_piece: coveralls
  feet: work_boots
items:
  - scrap_parts
  - battery_cell
  - multitool
  - tool_pouch
---

# Talk
```flow
greta: I can quiet a rusty hinge or wake the whole block with one frequency tap.
greta: If you're heading out, you'll need a signal baton. Bring me enough scrap wood and stone weights, and I'll rig one for you.
$ greta.mark_as_met()
```
