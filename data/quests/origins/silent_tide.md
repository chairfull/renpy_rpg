---
type: origin
id: silent_tide
name: The Silent Tide
description: An archivist hears the sleepers' rhythm and follows it to the source.
pc_id: scholar
image: chars/male_thin.png
intro_label: SCENE__silent_tide__intro
---

```flow
$ renpy.store.td_manager.setup(rpg_world.current_location)
FLAG SET origin silent_tide
EVENT GAME_STARTED origin=silent_tide
QUEST START silent_tide

Your logbook is full of patterns. The sleepers drift to the same pulse each night.
priestess: Keep your steps soft and your breaths even. We can guide them.
JUMP world_loop
```
