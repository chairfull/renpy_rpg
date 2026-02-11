# Quest & Origin System

This document describes how to create and manage quests and origins in the AI-RPG engine.

## Origins vs Quests

- **Quests (`type: quest`)**: Standard mission logic with goals and triggers. They live in `data/quests/`.
- **Origins (`type: origin`)**: New-game starting points. They live in `data/quests/origins/`.
  - Required: `character` (character id) and `intro_label` (label to jump to).
  - Optional: `image` (shown on the selection screen).
  - Origins should contain a single ` ```flow` block for the intro.
- If a quest with the same `id` exists in `data/quests/`, it will auto-start when that origin is chosen. Otherwise, call `QUEST START <id>` in the origin flow.

---

## Origin Example
```markdown
---
type: origin
id: long_dawn
name: The Long Dawn
character: warrior
intro_label: SCENE__long_dawn__intro
image: chars/male_fit.png
---

```flow
$ renpy.store.td_manager.setup(rpg_world.current_location)
FLAG SET origin long_dawn
EVENT GAME_STARTED origin=long_dawn
QUEST START long_dawn
JUMP world_loop
```
```

## Quest Example
```markdown
---
type: quest
id: apple_hunt
name: Ration Run
description: Gather rations for the shelter.
---
# Goals

## Collect Rations
```trigger
event: ITEM_GAINED
item: Ration Bar
total: 5
```
```flow
pc: That should be enough for today.
```
```

---

## Writing Goals (`##`)

Each goal is defined by a level-2 header (`##`).
- The header text becomes the goal's internal ID (slugified, e.g., `## Collect Rations` -> `collect_rations`).
- Goals can contain `trigger` blocks and optional `flow` blocks.

### Trigger Blocks
Triggers define what events complete a goal.
```markdown
```trigger
event: ITEM_GAINED | CHAR_MET | LOCATION_VISITED
item: <Item name> (required for ITEM_GAINED)
char: <character id> (required for CHAR_MET)
location: <location id> (required for LOCATION_VISITED)
total: 3 (optional, defaults to 1)
cond: "flag_get('some_flag') == True" (optional)
```
```

---

## Flow Commands

Flow blocks allow you to execute logic using simple ALLCAPS commands.

| Command | Syntax | Description |
| :--- | :--- | :--- |
| **QUEST** | `QUEST START <id>` \| `QUEST COMPLETE <id>` | Start or complete a quest. |
| **GOAL** | `GOAL SHOW <goal_id>` \| `GOAL SHOW <quest_id> <goal_id>` \| `GOAL COMPLETE <goal_id>` | Set goal state by id. |
| **FLAG** | `FLAG SET <name> <value>` \| `FLAG CLEAR <name>` | Update world flags. |
| **EVENT** | `EVENT <type> key=value` | Dispatch custom events to the event manager. |
| **GIVE/TAKE** | `GIVE <item_id> <count>` \| `TAKE <item_id> <count>` | Manage player inventory. |
| **GOLD** | `GOLD <amount>` | Add/remove gold (negative for removal). |
| **TRAVEL** | `TRAVEL <location_id>` | Move the player to a new location. |
| **REST** | `REST <hours>` | Advance time by hours. |
| **SCAVENGE** | `SCAVENGE` | Perform a scavenge roll at the current location. |
| **JUMP/CALL** | `JUMP <label>` \| `CALL <label>` | Navigate to a Ren'Py label. |
| **COND** | `COND "<expr>" <label_true> <label_false>` | Branch based on a condition. |
| **CHECK** | `CHECK <stat> <dc> <pass_label> <fail_label>` | Perform a stat check. |
| **NOTIFY** | `NOTIFY "Message Text"` | Show a notification. |
| **PERK** | `PERK ADD <id> [minutes]` \| `PERK REMOVE <id>` | Add or remove a perk. |
| **STATUS** | `STATUS ADD <id> [minutes]` \| `STATUS REMOVE <id>` | Add or remove a status effect. |
| **COMPANION** | `COMPANION ADD <id>` \| `COMPANION REMOVE <id>` | Manage companions. |
| **BOND** | `BOND ADD <char_id> <stat> <delta>` \| `BOND TAG <char_id> <tag>` | Modify bond stats or tags. |

---

## Quest States
- **unknown**: Quest is not yet discovered.
- **active**: Quest is in progress.
- **passed**: Quest is successfully finished.
- **failed**: Quest is no longer achievable.
