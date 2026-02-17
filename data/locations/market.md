---
type: location
id: market
name: Relief Exchange
desc: Lines of crates and a steady flow of supplies.
map_image: "#333"
map_type: city
map_x: 1100
map_y: 900
zoom_range: [0.5, 3.0]
obstacles:
  - [10, 10]
  - [10, 11]
  - [11, 10]
  - [11, 11]
entities:
  # Links
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
  # Objects
  - id: console
    type: object
    name: Signal Console
    desc: A cracked screen with a faint repeating tone.
    label: test_minigame
    x: 400
    y: 300
    sprite: "images/topdown/chars/male_base.png"
encounters:
  - id: market_swap
    label: LOC__market__encounter_swap
    chance: 0.35
    once: true
    cond: "not flag_get('market_swap', False)"
---

# encounter_swap
```flow
A volunteer presses a ration bar into your hand.
"Take it," she says. "You look like you run far."
EVENT ITEM_GAINED item=ration_bar total=1
FLAG SET market_swap true
```
