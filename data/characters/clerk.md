---
type: character
id: clerk
name: Clerk
description: A no-nonsense clerk who manages the official settlement exchange and logbooks.
base_image: chars/male_average.png
location: shop
tags:
  - trader
  - logistics
---
# Talk
```flow
clerk: Take what you've been rationed for, and make sure you log your exchange in the book. No credit in the Silence.
$ renpy.store.general_store.interact()
$ clerk.mark_as_met()
```
