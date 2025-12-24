---
type: location
id: home
name: Your Home
description: A cozy little house.
map_image: "#1a1a2a"
links:
  - id: square
    x: 200
    y: 540
    spawn: [100, 500]
entities:
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
