---
type: character
name: Jace
id: jace
desc: A lookout at the rusted harbor who watches for 'Drifter' anomalies in the fog.
location: docks
pos: 700,500
factions: []
tags:
  - lookout
  - worker
affinity: 5
gender: male
age: 28
height: 182 cm
weight: 76 kg
hair_color: sandy blond
hair_style: messy
eye_color: gray-blue
face_shape: long
skin_tone: light
build: lean
body_type: humanoid
breast_size: n/a
dick_size: average
foot_size: 44
distinctive_feature: weathered hands
equipment:
  head: watch_cap
  torso: rain_shell
  pants: cargo_pants
  feet: rubber_boots
items:
  - signal_chalk
  - glow_stick
  - water_flask
  - protein_bar
---

# Talk
```flow
jace: No ships coming in, just the wind and the sound of the structural rust groaning.
jace: If the tide brings in a drift from the Spire, I ring the chime and we all evacuate to the higher districts.
$ jace.mark_as_met()
```
