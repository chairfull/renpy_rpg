---
type: story_origin
id: scholar
name: The Medic
description: A calm clinician who knows how to soothe panic and treat the sick.
pc_id: scholar
image: chars/male_thin.png
intro_label: SCENE__scholar__intro
---

```flow
$ renpy.store.td_manager.setup(rpg_world.current_location)
FLAG SET origin medic
EVENT GAME_STARTED origin=medic

The clinic is already awake. You wash your hands and check the supplies.
Outside, the sleepers drift past the window like a slow tide.
Today you take the first steps toward a cure.
$ renpy.jump("world_loop")
```
---
