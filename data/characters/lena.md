---
type: character
name: Lena
id: lena
description: A veteran scout who reads the perimeter drifts like a topography map.
location: forest_edge
pos: 400,300
factions:
  - town_guard
tags:
  - outdoors
  - scout
  - tracker
affinity: -5
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
