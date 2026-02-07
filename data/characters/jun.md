---
type: character
id: jun
name: Jun
description: A calm voice who keeps the shelter steady with rhythmic cadence and signal-dampening tones.
location: tavern
pos: 500,300
factions: []
tags:
  - signal
  - tech
  - signalist
affinity: 10
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
