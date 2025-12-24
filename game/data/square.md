---
type: location
id: square
name: Town Square
description: The heart of the town.
map_image: "#333"
obstacles: 10,10|10,11|11,10|11,11
entities:
  - id: home
    type: link
    x: 200
    y: 540
    spawn: [200, 540]
  - id: shop
    type: link
    x: 1600
    y: 540
    spawn: [960, 800]
  - id: dummy
    type: object
    name: Training Dummy
    description: Looks tough.
    label: test_minigame
    x: 400
    y: 300
    sprite: "images_topdown/chars/theo.png"
---
