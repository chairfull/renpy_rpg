---
type: location
id: home
name: Safehouse Room
description: Your assigned bunk inside the quarantine block.
map_image: "#1a1a2a"
# Map Data
map_type: structure
map_x: 1000
map_y: 1000
zoom_range: 2.0, 5.0
tags: [safe]
entities:
  - id: market
    type: link
    x: 200
    y: 540
    spawn: [200, 540]
  - id: bed
    type: object
    name: Cot
    description: A narrow cot with a clean blanket.
    label: sleep_interaction
    x: 300
    y: 500
    sprite: "images/topdown/chars/male_base.png"
  - id: mirror
    type: object
    name: Small Mirror
    description: Check your face and move on.
    label: mirror_interaction
    x: 1400
    y: 300
    sprite: "images/topdown/chars/male_base.png"
  - id: closet
    type: container
    name: Supply Locker
    description: A battered locker for your essentials.
    x: 0
    y: 0
    items: [camp_kit, apple, potion]
    sprite: "images/topdown/chars/male_base.png"
---

# Bed
```flow
REST 8
You wake to the soft hum of the wall speakers.
```

# Mirror
```flow
You check for dust, bruises, and any new marks.
All clear.
```
