Locations

This document explains how to define locations in `data/locations/*.md` and how they are compiled/used internally.

File Format

Each location is a Markdown file with YAML front matter:

```
---
type: location
id: home
name: Safehouse
description: A quiet multi-level safehouse assigned to you within the quarantine block.
map_image: "#1a1a2a"

# Map Data
map_type: structure
map_x: 1000
map_y: 1000
zoom_range: 2.0, 5.0
floor_idx: 0
parent: city_center

tags: [safe]
factions: [supply_union]

entities:
  - id: market
    type: link
    x: 200
    y: 540
    spawn: [200, 540]
  - id: bed
    type: object
    name: Cot
    description: A narrow cot with a clean blanket.
    label: LOC__home__bed
    x: 300
    y: 500
    sprite: "images/topdown/chars/male_base.png"
---
```

Front Matter Fields

- `type`: must be `location`.
- `id`: location id (lowercase recommended).
- `name`: display name.
- `description`: short description.
- `map_image`: optional map image or color.
- `parent`: optional parent location id (hierarchy).
- `map_type`: map layer type (`world`, `city`, `structure`, `floor`, `room`).
- `map_x` / `map_y`: map coordinates used for navigation UI.
- `zoom_range`: min/max zoom where this location appears (comma-separated).
- `floor_idx`: optional sort index for floors.
- `tags`, `factions`: for filtering and logic.
- `entities`: list of objects/links inside the location (see below).
- `encounters`, `scavenge`, `obstacles`: optional lists for content systems.

Entities

Entities live in the `entities:` YAML list. Common types:

- `link`: a link to another location, `id` should be a location id.
- `object`: interactable object, use `label` to connect to a flow label.
- `container`: interactable container, use `items` for seed items.

Entity labels link to labels generated from flow blocks. Example:

```
# Bed
```flow
REST 8
You wake to the soft hum of the wall speakers.
```
```

This produces a label like `LOC__home__bed`. Set `label: LOC__home__bed` on the entity to link it.

Nested Locations via `# Locations`

Inside a location file you can define nested locations with a `# Locations` section. Every subheading under it becomes a child location. Heading depth does not matter; nesting follows heading levels.

Example:

```
# Locations
## Top Floor
### Main Bedroom
### Bathroom
```

This creates:

- `home#top-floor`
- `home#top-floor#main-bedroom`
- `home#top-floor#bathroom`

Child IDs are built by joining the parent id with slugified headings using `#` (to mimic markdown links).

Child Definitions

Each child may include a YAML codeblock for configuration. The heading text is used as the name if `name` is not provided.

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
    label: LOC__home__bed
```
```

Notes:

- Rooms should set `map_type: room`.
- Child locations inherit `map_type`, `map_x`, `map_y`, `zoom_range`, and `floor_idx` from their parent unless overridden in the YAML block.
- The YAML block is optional; content outside of it becomes the child’s body for flow labels.
- Labels for child locations are sanitized internally so `#` in ids won’t break Ren’Py labels.

Internal Compilation Rules

`game/python/compile_data.py` compiles locations into JSON and labels:

- The primary location uses `id` directly (e.g., `home`).
- Child locations are added with `parent-id#child-id`.
- The `parent` field is set to the immediate parent id.
- `map_type` becomes the location’s `ltype` in `Location`.
- `map_x`/`map_y` and `zoom_range` control map visibility.
- Flow blocks create labels that are attached to entities or location sections.

Best Practices

- Keep `id` and heading names stable; changing them changes the generated child ids.
- Prefer `map_type: room` for interior rooms and `map_type: floor` for floor-level nodes.
- Use `entities` for interactables and link them to flow labels with `label`.
