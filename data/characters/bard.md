---
type: character
name: Traveling Bard
id: bard
description: A flamboyant musician who performs for coin and applause.
location: tavern
pos: 500,300
factions: []
tags:
  - entertainer
  - traveler
affinity: 15
---

# Talk
```flow
bard: Ah, a new face! Perhaps you'd like to hear a song?
bard: I know ballads from every corner of the realm!
$ bard.mark_as_met()
```
