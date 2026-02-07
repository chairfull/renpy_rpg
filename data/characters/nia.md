---
type: character
name: Nia
id: nia
description: A sharp-eyed orphan who navigates the crawlspaces and service tunnels to avoid the 'Sleeper' drifts.
location: market
pos: 200,600
factions: []
tags:
  - child
  - scavenger
  - runner
affinity: 0
gender: female
age: 12
height: 145 cm
weight: 38 kg
hair_color: black
hair_style: short curls
eye_color: brown
face_shape: round
skin_tone: medium
build: slight
body_type: humanoid
breast_size: n/a
dick_size: n/a
foot_size: 35
distinctive_feature: scuffed knees
equipment:
  head: knit_cap
  torso: signal_hoodie
  pants: track_pants
  feet: sneakers
items:
  - glow_stick
  - protein_bar
  - water_flask
  - note_card
---

# Talk
```flow
nia: You move like you're wearing heavy boots. You'll wake the whole block up like that.
nia: If you ever need a route that doesn't involve walking through a drift, I know where the ducts still hold.
$ nia.mark_as_met()
```
