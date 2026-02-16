# Renpy Odyssey Framework

> [!WARNING]
> Unstable. Mostly developed with AI.

The **Renpy Odyssey Framework** is a data-driven content system designed to separate narrative and world data from game logic. It uses **Markdown** files to define characters, locations, items, and dialogue flows, which are then compiled into Ren'Py scripts and JSON data.

## 📖 Documentation

-   Detailed guides and references are located in the [README/](file:///home/sh/Documents/renpy_stories/ai_rpg/README/) directory.
-   [Quest System Guide](file:///home/sh/Documents/renpy_stories/ai_rpg/README/quests.md)
-   [Event & Trigger Reference](file:///home/sh/Documents/renpy_stories/ai_rpg/README/events.md)

## 📁 File Structure

All data files are located in the `data/` directory:
- `data/locations/`: Map areas and world structure.
- `data/characters/`: NPCs, their stats, and interaction flows.
- `data/items/`: Equipment and consumable definitions.
- `data/quests/origins/`: Player background choices.

## 📝 Markdown Format

Each file consists of two main sections:

### 1. Frontmatter (YAML)
Located at the top between `---` markers. Defines the raw data properties.

#### **Character Example:**
```yaml
---
id: mayor
name: Mayor Thomas
description: The weary leader of this town.
location_id: market
base_image: "mayor_idle.png"
stats:
  charisma: 15
  intelligence: 12
factions: [town_council]
---
```

#### **Location Example:**
```yaml
---
id: market
name: Town Market
description: A bustling hub of trade.
map_image: "images/topdown/locations/market.png"
entities:
  - id: stall_1
    type: container
    name: Fruit Stall
    items: [apple, apple, gold_coin]
    x: 400
    y: 600
    sprite: "images/topdown/props/stall.png"
---
```

### 2. Flow Blocks (Narrative/Logic)
Located below the frontmatter. Uses standard Markdown headers and `flow` or `python` blocks.

#### **Dialogue Nesting:**
Use `# Dialogue` to start the main interaction hub. Use secondary headers for specific branches.

```markdown
# Dialogue
Welcome to our humble town. What brings you here?

- Option: [ASK_ABOUT_TOWER] (Ask about the Tower)
- Option: [GIVE_GOLD] (Donate 10 Gold)

# Sub-Dialogue: ASK_ABOUT_TOWER
The Tower? It has stood there since before my grandfather's time.

```flow
The Mayor sighs deeply as he looks toward the horizon.
```

### ✅ Flow Directives (ALLCAPS)
Inside ` ```flow` blocks you can write simple ALLCAPS commands (no Python needed):

```flow
FLAG SET met_mayor true
EVENT ITEM_GAINED item=gold_coin total=1
GIVE apple 2
TAKE potion 1
GOLD 10
REST 8
SCAVENGE
QUEST START long_dawn
GOAL SHOW call_to_adventure
PERK ADD silver_tongue
STATUS ADD flu 120
COMPANION ADD bard
BOND ADD mayor trust 5
BOND TAG mayor ally
TRAVEL market
JUMP SCENE__intro__flow
COND "flag_get('met_mayor', False)" SCENE__mayor__talk SCENE__mayor__locked
CHECK dexterity 12 SCENE__sneak_success SCENE__sneak_fail
NOTIFY "You feel a cold draft."
```

# Sub-Dialogue: GIVE_GOLD
Oh! Generous indeed. The town council will remember this.

```python
character.gold -= 10
mayor.relation += 5
```
```

## 🚀 Key Features

### **Top-Down Engine**
- Seamless transition from world-map exploration to character interaction.
- Automatic inventory handling for `container` type entities.
- Dynamic camera following and zoom-aware mouse interactions.

### **Interactive Hub**
- **Talk**: Triggers the `# Dialogue` block defined in the character's markdown.
- **Give**: Opens the item selection screen to gift items to NPCs.
- **Stats**: Real-time display of character attributes and social relations.

### **Container System**
- Side-by-side transfer UI for moving items between player and world objects (closets, chests, etc.).
- Automatic grouping and counting of duplicate items.

## 🛠️ Compilation
The system uses `game/python/compile_data.py` to watch for changes in the `data/` folder and rebuild the internal registry during the Ren'Py launch sequence.
