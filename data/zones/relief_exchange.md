---
type: location
name: Relief Exchange
desc: Lines of crates and a steady flow of supplies.
image: "#333"
subtype: city
position: [1100, 0, 900]
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
---