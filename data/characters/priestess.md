---
type: character
name: Clinician Elena
id: priestess
description: A careful medic who keeps panic low and recovery high.
location: temple
pos: 500,300
factions: []
tags:
  - healer
  - medic
affinity: 20
---

# Talk
```flow
priestess: Slow breaths. Clean hands. That keeps people alive.
priestess: If you feel sick, tell me before you go out.
$ priestess.mark_as_met()
```

# Dialogue

## Checkup
```yaml
short: Ask for a checkup
long: Can you take a quick look at me?
tags:
  - Medical
memory: true
cond: true
```

```flow
priestess: Hold still.
STATUS REMOVE flu
NOTIFY "You feel steadier."
```
