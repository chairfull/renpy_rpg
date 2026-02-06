---
type: character
name: Guard Captain
id: guard_captain
description: A stern but fair leader of the town guard.
location: city_center
pos: 600,400
factions:
  - town_guard
tags:
  - authority
  - soldier
affinity: 0
---

# Talk
```flow
guard_captain: Halt! State your business, traveler.
guard_captain: Hmm, you look harmless enough. Welcome to the city.
$ guard_captain.mark_as_met()
```
