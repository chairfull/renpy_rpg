# Event Reference Guide

The AI-RPG engine uses an event-based system for triggering quest goals, achievements, and world reactions. This document lists the core events dispatched by the system.

## Standard Game Events

These events are automatically dispatched by the engine during core gameplay.

| Event | Parameters | Description |
| :--- | :--- | :--- |
| **GAME_STARTED** | `origin=id` | Dispatched when a new game starts with a specific story origin. |
| **LOCATION_VISITED**| `location=id` | Dispatched every time the player enters a location (even if previously visited). |
| **LOCATION_DISCOVERED**| `location=id`| Dispatched only the *first* time the player visits a location. |
| **CHAR_MET** | `char=name` | Dispatched the first time the player talks to a character. |
| **ITEM_GAINED** | `item=name`, `total=count` | Dispatched whenever an item is added to the player's inventory. |
| **ITEM_CRAFTED** | `item=name`, `recipe=id` | Dispatched when a crafting recipe is completed. |
| **NOTE_UNLOCKED** | `note=id` | Dispatched when a new lore note or journal entry is added. |
| **SCAVENGED** | `location=id`, `items=list` | Dispatched after a successful scavenging attempt. |
| **RESTED** | `hours=int`, `location=id` | Dispatched after the player rests/sleeps. |
| **CAMP_USED** | `location=id` | Dispatched when a camping kit is used in the world. |
| **CAMP_AMBUSH** | `location=id` | Dispatched if a rest is interrupted by a combat event. |

---

## Dispatching Custom Events

You can trigger custom events manually inside `flow` blocks using the `EVENT` command. This is useful for scripted story moments or unique quest triggers.

```flow
# Example: Dispatched after a specific dialogue choice
EVENT SECRET_REVEALED type=lore importance=high
```

### Scripting equivalent (Python)
```python
event_manager.dispatch("SECRET_REVEALED", type="lore", importance="high")
```

---

## Listening for Events (Triggers)

Quest goals use `trigger` blocks to listen for these events. The goal completes when the event type and its parameters match the trigger definition.

```markdown
```trigger
event: CHAR_MET
char: mara
```
```
