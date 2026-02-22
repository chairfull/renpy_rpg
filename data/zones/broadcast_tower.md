---
type: zone
name: Broadcast Tower
desc: A concrete spire that once blanketed the city with signal.
subtype: structure
position: [1200, 0, 800]
entities: []
---


# Locations
## Lobby
```yaml
type: zone
name: Broadcast Tower Lobby
desc: Dusty consoles and a sealed control room.
subtype: floor
position: [1200, 0, 800]
floor: 1
entities:
  - id: signal_console
    type: object
    name: Signal Console
    desc: A flickering screen covered in grime. It hums with a steady rhythm.
    label: console_interaction
    x: 800
    y: 400
    sprite: "images/topdown/chars/male_base.png"
```
### Console
```flow
player: The screen is asking for an override.
player: If I can pull the data now, maybe I can make it back before the sleepers shift.
NOTIFY "Recovering protocol..."
GAIN broadcast_protocol
FLAG_SET protocol_recovered true
```
