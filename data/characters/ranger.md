---
type: character
name: Ranger Thorne
id: ranger
description: A taciturn woodsman who patrols the forest roads.
location: forest_edge
pos: 400,300
factions:
  - rangers
tags:
  - outdoorsman
  - soldier
affinity: -5
---

# Talk
```flow
ranger: You shouldn't wander the forest alone.
ranger: Wolves, bandits... and worse things lurk in the shadows.
$ ranger.mark_as_met()
```
