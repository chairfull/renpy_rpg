---
type: character
name: Mysterious Stranger
id: stranger
description: A cloaked figure who seems to know more than they let on.
location: tavern
pos: 150,400
factions:
  - unknown
tags:
  - mysterious
  - quest_giver
affinity: -10
---

# Talk
```flow
stranger: ...
stranger: You have a curious look about you.
stranger: Perhaps we'll speak again when the time is right.
$ stranger.mark_as_met()
```
