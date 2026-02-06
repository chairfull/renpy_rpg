---
type: location
id: market
name: Grand Market
description: The bustling heart of the town, filled with merchants hawking their wares.
map_image: "#333"
map_type: city
map_x: 1100
map_y: 900
zoom_range: 0.5, 3.0
obstacles: 10,10|10,11|11,10|11,11
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
  # NPC IDs (from the old locations/market.md)
  - mayor
  - blacksmith
  - orphan
  - merchant_hakim
  # Objects
  - id: dummy
    type: object
    name: Training Dummy
    description: Looks tough.
    label: test_minigame
    x: 400
    y: 300
    sprite: "images/topdown/chars/male_base.png"
encounters:
  - id: market_pickpocket
    label: LOC__market__encounter_pickpocket
    chance: 0.35
    once: true
    cond: "not flag_get('market_pickpocket', False)"
---

# encounter_pickpocket
```flow
A sudden jostle. Someone bumps your shoulder and vanishes into the crowd.
You check your belt pouch and find a bruised apple tucked inside.
$ pc.add_item(item_manager.get("apple"))
@event ITEM_GAINED item=apple total=1
@flag set market_pickpocket true
```
