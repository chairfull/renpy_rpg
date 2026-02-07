---
type: character
id: kael
name: Kael
description: A high-risk courier who uses kinetic force to clear 'Sleeper' blockades.
base_image: chars/male_fit.png
location: market
items:
  - sword
  - protein_bar
  - water_flask
  - multitool
  - lockpick_set
stats:
  - strength: 14
  - dexterity: 12
  - intelligence: 8
  - charisma: 10
factions:
  - perimeter_watch
tags:
  - breacher
  - combat
gender: male
age: 30
height: 185 cm
weight: 85 kg
hair_color: dark brown
hair_style: cropped
eye_color: hazel
face_shape: angular
skin_tone: tan
build: muscular
body_type: humanoid
breast_size: n/a
dick_size: average
foot_size: 44
distinctive_feature: scarred knuckles
equipment:
  head: watch_cap
  torso: patrol_jacket
  pants: patrol_pants
  feet: patrol_boots
  main_hand: sword
---

# Talk
```flow
kael: Don't just stand there making noise. Noise is death.
kael: Unless you're making it to clear a path. You looking for a piece of the next breach?
$ kael.mark_as_met()
```

# Dialogue

## Ask About Breaching
```yaml
short: Ask about breaching
long: How do you clear a block of Sleepers?
tags:
  - Lore
memory: true
cond: true
```

```flow
kael: You don't clear them all. You find the resonance point, hit it hard, and run through the gap before they reset.
kael: It's about timing and weight. Stay heavy, move fast.
```
