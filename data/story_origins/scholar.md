---
type: story_origin
id: scholar
name: The Scholar
description: A seeker of truth and ancient knowledge. Weaker in combat but highly intelligent and charismatic.
pc_id: scholar
image: characters/male_thin.png
intro_label: SCENE__scholar__intro
---

```flow
$ renpy.store.td_manager.setup(rpg_world.current_location)

You wake up in your familiar study, surrounded by stacks of ancient parchment.
The sunlight filters through the window, illuminating dust motes in the air.
Today is the day you begin your grand research into the town's history.
$ renpy.jump("world_loop")
```
---
