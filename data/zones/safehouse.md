---
type: zone
name: Safehouse
desc: A quiet multi-level safehouse assigned to you within the quarantine block.
tags: [safe]
zone_type: structure
position: [1000, 0, 1000]
zoom_range: [2.0, 5.0]
entities:
  - id: market
    type: link
    x: 200
    y: 540
    spawn: [200, 540]
---

# Locations
## Attic
```yaml
type: zone
name: Attic
desc: A cramped attic full of stored crates and old insulation.
zone_type: floor
floor: 3
```

## Top Floor
```yaml
type: zone
name: Top Floor
desc: Quiet sleeping quarters and the bathroom.
zone_type: floor
floor: 2
```

### Main Bedroom
```yaml
type: zone
desc: Your assigned room with a narrow cot and a small mirror.
zone_type: room
entities:
  - id: bed
    type: object
    name: Cot
    desc: A narrow cot with a clean blanket.
    x: 300
    y: 500
    sprite: "images/topdown/chars/male_base.png"
  - id: mirror
    type: object
    name: Small Mirror
    desc: Check your face and move on.
    x: 1400
    y: 300
    sprite: "images/topdown/chars/male_base.png"
  - id: closet
    type: container
    name: Supply Locker
    desc: A battered locker for your essentials.
    x: 0
    y: 0
    items: [camp_kit, ration_bar, antiseptic_ampoule]
    sprite: "images/topdown/chars/male_base.png"
```

### Guest Bedroom
```yaml
type: zone
desc: A spare room kept ready for visitors or injured runners.
zone_type: room
```

### Kids Bedroom
```yaml
type: zone
desc: A small room with mismatched blankets and hand-drawn maps.
zone_type: room
```

### Bathroom
```yaml
type: zone
desc: A compact washroom with a trickling filter line.
zone_type: room
```

## Main Floor
```yaml
type: zone
name: Main Floor
desc: The day-to-day living space, with work areas and a garage.
zone_type: floor
floor: 1
```

### Garage
```yaml
type: zone
desc: A converted bay for carts, tools, and quiet repairs.
zone_type: room
```

### Kitchen
```yaml
type: zone
desc: A narrow galley for ration prep and shared meals.
zone_type: room
```

### Living Room
```yaml
type: zone
desc: A low-lit common area with patched couches and old screens.
zone_type: room
```

### Office
```yaml
type: zone
desc: A cramped desk space for logs, maps, and comms.
zone_type: room
```

## Basement
```yaml
type: zone
name: Basement
desc: Utility space with old ducting and supply cages.
zone_type: floor
floor: 0
```

### Furnace Room
```yaml
type: zone
desc: The heat hub, lined with filters and rumbling vents.
zone_type: room
```

### Supply Room
```yaml
type: zone
desc: Locked shelves of spare parts and emergency stocks.
zone_type: room
```

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
