---
type: character
name: Lena
id: lena
desc: A veteran scout who reads the perimeter drifts like a topography map.
location: forest_edge
pos: 400,300
factions:
  - perimeter_watch
tags:
  - outdoors
  - scout
  - tracker
affinity: -5
gender: female
age: 33
height: 176 cm
weight: 66 kg
hair_color: black
hair_style: braided ponytail
eye_color: amber
face_shape: diamond
skin_tone: olive
build: athletic
body_type: humanoid
breast_size: small
dick_size: n/a
foot_size: 39
distinctive_feature: sun-faded freckles
equipment:
  head: watch_cap
  torso: utility_jacket
  pants: cargo_pants
  feet: trail_boots
items:
  - map_fragment
  - compass
  - protein_bar
  - water_flask
---

# Talk
```flow
lena: The sleepers follow sound more than sight. If you're going to survive the forest edge, you need to learn to walk between the beats.
lena: Keep your steps light and your voice softer. The drift is sensitive today.
$ lena.mark_as_met()
```

# Dialogue

## Ask For A Guide
```yaml
short: Ask for a guide
long: I could use a scout who knows the frequency dead-spots. Walk with me.
tags:
  - Companion
memory: true
cond: "not flag_get('scout_joined', False)"
reason: "Already traveling with you."
```

```flow
lena: Fine. But if you start humming or dragging your feet, I'm leaving you as bait. Keep up.
COMPANION ADD lena
FLAG SET scout_joined true
BOND ADD lena trust 3
```

## Ask To Part Ways
```yaml
short: Ask to part ways
long: Head back to the settlement. I'll handle the rest of this signal run.
tags:
  - Companion
memory: true
cond: "flag_get('scout_joined', False)"
reason: "Not traveling with you."
```

```flow
lena: Understood. I'll recalibrate the markers on my way back. Stay quiet.
COMPANION REMOVE lena
FLAG SET scout_joined false
```
