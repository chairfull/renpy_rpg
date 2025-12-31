---
type: location
id: home
name: Your Home
description: A cozy little house.
map_image: "#1a1a2a"
# Map Data
map_type: structure
map_x: 1000
map_y: 1000
zoom_range: 2.0, 5.0
entities:
  - id: square
    type: link
    x: 200
    y: 540
    spawn: [200, 540]
  - id: bed
    type: object
    name: Bed
    description: A comfortable-looking bed.
    label: sleep_interaction
    x: 300
    y: 500
    sprite: "images_topdown/chars/theo.png"
  - id: mirror
    type: object
    name: Mirror
    description: You look great today!
    label: mirror_interaction
    x: 1400
    y: 300
    sprite: "images_topdown/chars/theo.png"
  - id: closet
    type: container
    name: Bedroom Closet
    description: A sturdy wooden closet for your belongings.
    x: 0
    y: 0
    items: [sword, potion]
    sprite: "images_topdown/chars/theo.png"
---

# Bed
```flow
I'm not tired right now.
```

# Mirror
```flow
You look great today!
```