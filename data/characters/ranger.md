---
type: character
name: Scout Lena
id: ranger
description: A quiet scout who reads the outskirts like a map.
location: forest_edge
pos: 400,300
factions:
  - town_guard
tags:
  - outdoors
  - scout
affinity: -5
---

# Talk
```flow
ranger: The sleepers follow sound more than sight.
ranger: Keep your steps light and your voice softer.
$ ranger.mark_as_met()
```

# Dialogue

## Ask For A Guide
```yaml
short: Ask for a guide
long: I could use a scout. Walk with me.
tags:
  - Companion
memory: true
cond: "not flag_get('scout_joined', False)"
reason: "Already traveling with you."
```

```flow
ranger: Fine. Keep up and keep quiet.
COMPANION ADD ranger
FLAG SET scout_joined true
BOND ADD ranger trust 3
```

## Ask To Part Ways
```yaml
short: Ask to part ways
long: Head back. I will manage from here.
tags:
  - Companion
memory: true
cond: "flag_get('scout_joined', False)"
reason: "Not traveling with you."
```

```flow
ranger: Understood. Stay safe.
COMPANION REMOVE ranger
FLAG SET scout_joined false
```
