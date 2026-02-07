---
type: character
id: kael
name: Kael
description: A high-risk courier who uses kinetic force to clear 'Sleeper' blockades.
base_image: chars/male_fit.png
location: market
items:
  - sword
stats:
  - strength: 14
  - dexterity: 12
  - intelligence: 8
  - charisma: 10
factions:
  - town_guard
tags:
  - breacher
  - combat
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
