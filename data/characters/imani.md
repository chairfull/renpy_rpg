---
type: character
id: imani
name: Imani
desc: A high-level policy lead tracking route safety, ration efficiency, and drift probability.
base_image: chars/female_fit.png
location: market
pos: 900,600
factions:
  - supply_union
tags:
  - planner
  - leader
  - logistics
gender: female
age: 36
height: 168 cm
weight: 60 kg
hair_color: black
hair_style: short twists
eye_color: brown
face_shape: oval
skin_tone: dark
build: fit
body_type: humanoid
breast_size: small
dick_size: n/a
foot_size: 38
distinctive_feature: sharp cheekbones
equipment:
  head: ball_cap
  torso: logistics_coat
  pants: slacks
  feet: sneakers
items:
  - map_fragment
  - note_card
  - compass
  - water_flask
---
# Talk
```flow
imani: We balance the data points: food, water, and Silence. If any one drops, the settlement falls.
imani: If you've been outside, report any changes in the sleeper patterns immediately. Every pulse counts.
$ imani.mark_as_met()
```
