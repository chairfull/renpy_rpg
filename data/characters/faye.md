---
type: character
name: Faye
id: faye
description: Manages the rationed cots and the only filtered-air room in the district.
location: tavern
pos: 300,350
factions:
  - merchants
tags:
  - host
  - friendly
  - logistics
affinity: 10
---

# Talk
```flow
faye: You look like you've been breathing too much static. Sit, eat your rations, then move on.
faye: Space is tight, but I can find a cot if you need to let your frequency drop for a while.
$ faye.mark_as_met()
```
