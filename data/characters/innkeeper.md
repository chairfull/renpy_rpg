---
type: character
name: Shelter Host Faye
id: innkeeper
description: Keeps cots, soup, and rumors in the same warm room.
location: tavern
pos: 300,350
factions:
  - merchants
tags:
  - host
  - friendly
affinity: 10
---

# Talk
```flow
innkeeper: You look tired. Sit, eat, then move.
innkeeper: If you need a cot, I can find a corner.
$ innkeeper.mark_as_met()
```
