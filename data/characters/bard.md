---
type: character
id: bard
name: Signalist Jun
description: A calm voice who keeps the shelter steady with tone and timing.
location: tavern
pos: 500,300
factions: []
tags:
  - signal
  - tech
affinity: 10
---

# Talk
```flow
bard: The hall is loud inside, quiet outside. The right tone keeps it that way.
bard: If you can carry a message, I can teach you a cadence.
$ bard.mark_as_met()
```

# Dialogue

## Learn Cadence
```yaml
short: Learn cadence
long: Teach me a calming signal pattern.
tags:
  - Signal
memory: true
cond: "not flag_get('cadence_learned', False)"
reason: "You already learned it."
```

```flow
bard: Three beats, then a breath. Keep it even.
PERK ADD silver_tongue
FLAG SET cadence_learned true
```
