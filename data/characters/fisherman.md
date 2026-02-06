---
type: character
name: Old Fisherman
id: fisherman
description: A weathered sailor with tales from the sea.
location: docks
pos: 700,500
factions: []
tags:
  - commoner
  - storyteller
affinity: 5
---

# Talk
```flow
fisherman: Ahoy there! Looking for fish or for stories?
fisherman: Either way, I've got plenty of both!
$ fisherman.mark_as_met()
```
