---
type: location
id: mage_tower_f1
name: Broadcast Tower Lobby
description: Dusty consoles and a sealed control room.
map_type: floor
parent: mage_tower
map_x: 1200
map_y: 800
zoom_range: 3.0, 5.0
floor_idx: 1
entities:
  - id: signal_console
    type: object
    name: Signal Console
    description: A flickering screen covered in grime. It hums with a steady rhythm.
    label: console_interaction
    x: 800
    y: 400
    sprite: "images/topdown/chars/male_base.png"
---

# Console
```flow
pc: The screen is asking for an override.
pc: If I can pull the data now, maybe I can make it back before the sleepers shift.
NOTIFY "Recovering protocol..."
GIVE broadcast_protocol 1
FLAG SET protocol_recovered true
```
