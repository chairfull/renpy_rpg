---
type: location
id: forest_edge
name: Outskirts Line
desc: The fence line where the city thins into overgrowth and silent lots.
map_type: wilderness
map_x: 600
map_y: 500
zoom_range: [0.5, 3.0]
scavenge:
  - item: wood
    chance: 0.8
    min: 1
    max: 3
  - item: stone
    chance: 0.4
    min: 1
    max: 2
encounters:
  - id: fence_rattle
    label: LOC__forest_edge__encounter_rattle
    chance: 0.5
    cond: "not flag_get('fence_rattle', False)"
---

# encounter_rattle
```flow
The fence gives a soft rattle.
A sleeper drifts by, head tilted toward a far away tone.
EVENT LOCATION_EVENT location=forest_edge tag=rattle
FLAG SET fence_rattle true
```
