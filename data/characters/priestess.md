---
type: character
name: Priestess Elena
id: priestess
description: A serene healer devoted to the old gods.
location: temple
pos: 500,300
factions:
  - temple
tags:
  - healer
  - religious
affinity: 20
---

# Talk
```flow
priestess: May the light guide your path, traveler.
priestess: If you seek healing or wisdom, you have come to the right place.
$ priestess.mark_as_met()
```
