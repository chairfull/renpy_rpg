---
type: location
id: forest_edge
name: Forest Edge
description: The border between civilization and the wild woods beyond.
map_type: wilderness
map_x: 600
map_y: 500
zoom_range: 0.5, 3.0
entities: [ranger]
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
  - id: forest_rustle
    label: LOC__forest_edge__encounter_rustle
    chance: 0.5
    cond: "not flag_get('forest_rustle', False)"
---

# encounter_rustle
```flow
The bushes tremble. You catch a glimpse of a shadow before it slips away.
@event LOCATION_EVENT location=forest_edge tag=rustle
@flag set forest_rustle true
```
