# Quest & Story Origin System

This document describes how to create and manage quests and story origins in the AI-RPG engine.

## Story Origins vs Quests

-   **Quests (`type: quest`)**: Standard mission-based logic with goals and triggers. They can be found in `data/quests/`.
-   **Story Origins (`type: story_origin`)**: Special files used during NEW GAME selection.
    -   They define the player's initial setting, character (`pc_id`), and intro cinematic.
    -   **Important**: If a `story_origin` shares an ID with a `quest`, that quest will **automatically start** when the origin is chosen.

---

## File Structure

Both file types use Markdown with YAML frontmatter.

### Story Origin Example
```markdown
---
type: story_origin
id: long_dawn
name: The Long Dawn
pc_id: survivor
intro_label: QUEST__long_dawn__started
---
# Started
```flow
QUEST START long_dawn
GOAL SHOW call_to_adventure
```
```

### Quest Example
```markdown
---
type: quest
id: apple_hunt
name: Ration Run
description: Gather rations for the shelter.
---
# Goals

## Collect Apples
```trigger
event: ITEM_GAINED
item: apple
total: 5
```
```flow
PC: "That should be enough to feed everyone for a few days."
```
```

---

## Writing Goals (`##`)

Each Goal in a quest is defined by a level-2 header (`##`).
-   The name of the header becomes the Goal's internal ID (slugified, e.g., `## Collect Apples` -> `collect_apples`).
-   Goals can contain `trigger` blocks and `flow` blocks.

### Trigger Blocks
Triggers define what events complete a goal.
```markdown
```trigger
event: ITEM_GAINED | CHAR_MET | LOCATION_VISITED
item: item_id (required for ITEM_GAINED)
char: char_id (required for CHAR_MET)
location: loc_id (required for LOCATION_VISITED)
total: 3 (optional, defaults to 1)
cond: "flag_get('some_flag') == True" (optional python condition)
```
```

---

## Flow Commands

Flow blocks allow you to execute logic using simple capitalized commands.

| Command | Syntax | Description |
| :--- | :--- | :--- |
| **QUEST** | `QUEST START <id>` \| `QUEST COMPLETE <id>` | Manage overall quest state. |
| **GOAL** | `GOAL SHOW <id>` \| `GOAL COMPLETE <id>` | Manage specific goals. If `<id>` is unique, it searches all active quests. |
| **FLAG** | `FLAG SET <name> <value>` \| `FLAG CLEAR <name>` | Update world flags. |
| **EVENT** | `EVENT <type> key=value` | Dispatch custom events to the event manager. |
| **GIVE/TAKE** | `GIVE <item_id> <count>` \| `TAKE <item_id> <count>` | Manage player inventory. |
| **GOLD** | `GOLD <amount>` | Add/remove gold (negative for removal). |
| **TRAVEL** | `TRAVEL <location_id>` | Move the player to a new location. |
| **JUMP/CALL** | `JUMP <label>` \| `CALL <label>` | Navigate to a Ren'Py label. |
| **CHECK**| `CHECK <stat> <dc> <pass_label> <fail_label>`| Perform a stat check. |
| **NOTIFY**| `NOTIFY "Message Text"` | Show a small notification at the top. |

---

## Quest States
-   **unknown**: Quest is not yet discovered.
-   **active**: Quest is in progress.
-   **passed**: Quest is successfully finished.
-   **failed**: Quest is no longer achievable.
