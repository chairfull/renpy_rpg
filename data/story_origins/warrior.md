---
type: story_origin
id: warrior
name: The Mercenary
description: A battle-hardened veteran seeking coin and glory. High physical stats but less silver-tongued.
pc_id: warrior
image: chars/male_fit.png
intro_label: SCENE__warrior__intro
---

```flow
$ renpy.store.td_manager.setup(rpg_world.current_location)
@flag set origin warrior
@event GAME_STARTED origin=warrior

You arrive at the market square, your sword heavy at your side.
The air is thick with the smell of spices and the sound of bartering.
Your journey as a mercenary begins here.
$ renpy.jump("world_loop")
```
---
