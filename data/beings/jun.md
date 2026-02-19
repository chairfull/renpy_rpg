---
type: being
id: jun
name: Jun
desc: A calm voice who keeps the shelter steady with rhythmic cadence and signal-dampening tones.
location: tavern
pos: 500,300
factions: []
tags:
  - signal
  - tech
  - signalist
affinity: 10
gender: male
age: 26
height: 171 cm
weight: 63 kg
hair_color: black
hair_style: straight medium
eye_color: brown
face_shape: oval
skin_tone: light-medium
build: slender
body_type: humanoid
breast_size: n/a
dick_size: average
foot_size: 41
distinctive_feature: inked signal lines on wrist
equipment:
  head: knit_cap
  torso: signal_hoodie
  pants: track_pants
  feet: sneakers
items:
  - radio_receiver
  - battery_cell
  - signal_chalk
  - water_flask
---

# Talk
```flow
jun: The hall is loud inside, but the Silence is louder outside. The right cadence keeps the drift from noticing we're still here.
jun: If you can carry a signal baton, I can teach you a dampening cadence.
$ jun.mark_as_met()
```

# Dialogue

## Learn Cadence
```yaml
short: Learn cadence
long: Teach me a dampening signal pattern to keep the sleepers at bay.
tags:
  - Signal
memory: true
cond: "not flag_get('cadence_learned', False)"
reason: "You already learned it."
```

```flow
jun: Three beats, then a breath. Let the frequency settle between your steps. Keep it even.
PERK ADD silver_tongue
FLAG SET cadence_learned true
```
