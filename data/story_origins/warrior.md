---
type: story_origin
id: warrior
name: The Courier
description: A fast runner trusted with dangerous routes and fragile messages.
pc_id: warrior
image: chars/male_fit.png
intro_label: SCENE__warrior__intro
---

```flow
$ renpy.store.td_manager.setup(rpg_world.current_location)
FLAG SET origin courier
EVENT GAME_STARTED origin=courier

You arrive at the Relief Exchange, breath steady, pack light.
The settlement needs a runner more than a fighter.
Today you carry a message that could change everything.
$ renpy.jump("world_loop")
```
---
