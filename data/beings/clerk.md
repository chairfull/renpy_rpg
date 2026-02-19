---
type: being
id: clerk
name: Clerk
desc: A no-nonsense clerk who manages the official settlement exchange and logbooks.
base_image: chars/male_average.png
location: shop
tags:
  - trader
  - logistics
gender: male
age: 38
height: 175 cm
weight: 78 kg
hair_color: brown
hair_style: neat short
eye_color: hazel
face_shape: square
skin_tone: light
build: average
body_type: humanoid
breast_size: ~
dick_size: average
foot_size: 42
distinctive_feature: ink-stained fingertips
equipment:
  head: ball_cap
  torso: logistics_coat
  pants: slacks
  feet: sneakers
items:
  - keycard
  - note_card
  - ration_pack
  - battery_cell
---

# Talk
```flow
clerk: Take what you've been rationed for, and make sure you log your exchange in the book. No credit in the Silence.
$ clerk.mark_as_met()
```
