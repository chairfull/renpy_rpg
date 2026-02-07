---
type: origin
id: long_dawn
name: The Long Dawn
description: A runner's start at the quarantine line, chasing a signal of hope.
pc_id: warrior
image: chars/male_fit.png
intro_label: SCENE__long_dawn__intro
---

```flow
$ renpy.store.td_manager.setup(rpg_world.current_location)
FLAG SET origin long_dawn
EVENT GAME_STARTED origin=long_dawn
QUEST START long_dawn

You check your route map and count the turns to the Broadcast Tower.
mayor: The signal shifted again. Bring back anything you learn.
JUMP world_loop
```
