---
type: character
name: Jace
id: jace
description: A lookout at the rusted harbor who watches for 'Drifter' anomalies in the fog.
location: docks
pos: 700,500
factions: []
tags:
  - lookout
  - worker
affinity: 5
---

# Talk
```flow
jace: No ships coming in, just the wind and the sound of the structural rust groaning.
jace: If the tide brings in a drift from the Spire, I ring the chime and we all evacuate to the higher districts.
$ jace.mark_as_met()
```
