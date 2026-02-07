---
type: character
name: Elena
id: elena
description: A high-tension combat medic who specializes in frequency-induced trauma and Sleeper-bite stabilization.
location: temple
pos: 500,300
factions: []
tags:
  - medic
  - clinician
  - healer
affinity: 20
---

# Talk
```flow
elena: Slow breaths. Keep your hands where I can see them. Clean hands keep people on this side of the pulse.
elena: If you feel the 'Static' in your head, report to the clinic immediately. We can't afford a sleeper waking up inside the walls.
$ elena.mark_as_met()
```

# Dialogue

## Checkup
```yaml
short: Ask for a checkup
long: I've been hearing a low hum... can you check my resonance levels?
tags:
  - Medical
memory: true
cond: true
```

```flow
elena: Hold still. It's just a diagnostic sweep.
STATUS REMOVE flu
NOTIFY "Your cognitive resonance stabilizes."
```
