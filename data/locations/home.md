---
type: location
id: home
name: Safehouse
desc: A quiet multi-level safehouse assigned to you within the quarantine block.
map_image: "#1a1a2a"
# Map Data
map_type: structure
map_x: 1000
map_y: 1000
zoom_range: [2.0, 5.0]
tags: [safe]
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
name: Attic
desc: A cramped attic full of stored crates and old insulation.
map_type: floor
floor_idx: 3
tags: [storage]
```

## Top Floor
```yaml
name: Top Floor
desc: Quiet sleeping quarters and the bathroom.
map_type: floor
floor_idx: 2
tags: [residential]
```

### Main Bedroom
```yaml
desc: Your assigned room with a narrow cot and a small mirror.
map_type: room
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
desc: A spare room kept ready for visitors or injured runners.
map_type: room
```

### Kids Bedroom
```yaml
desc: A small room with mismatched blankets and hand-drawn maps.
map_type: room
```

### Bathroom
```yaml
desc: A compact washroom with a trickling filter line.
map_type: room
```

## Main Floor
```yaml
name: Main Floor
desc: The day-to-day living space, with work areas and a garage.
map_type: floor
floor_idx: 1
```

### Garage
```yaml
desc: A converted bay for carts, tools, and quiet repairs.
map_type: room
```

### Kitchen
```yaml
desc: A narrow galley for ration prep and shared meals.
map_type: room
```

### Living Room
```yaml
desc: A low-lit common area with patched couches and old screens.
map_type: room
```

### Office
```yaml
desc: A cramped desk space for logs, maps, and comms.
map_type: room
```

## Basement
```yaml
name: Basement
desc: Utility space with old ducting and supply cages.
map_type: floor
floor_idx: 0
tags: [utility]
```

### Furnace Room
```yaml
desc: The heat hub, lined with filters and rumbling vents.
map_type: room
```

### Supply Room
```yaml
desc: Locked shelves of spare parts and emergency stocks.
map_type: room
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
