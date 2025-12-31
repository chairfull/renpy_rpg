---
type: character
name: Mayor
description: The leader of our fine town.
location: square
pos: 800,600
factions: town_guard, merchants
tags: important, noble
---

# Talk
```flow
mayor: Welcome to our town, traveler!
mayor: I hope you find everything to your liking.
$ mayor.mark_as_met()
$ mayor.items.append(Item("Town Map", "A map of the local area."))
```
