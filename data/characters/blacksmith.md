---
type: character
name: Blacksmith Greta
id: blacksmith
description: A muscular woman with arms like tree trunks and a fiery temper.
location: market
pos: 400,500
factions:
  - merchants
  - craftsmen
tags:
  - merchant
  - crafter
affinity: 0
---

# Talk
```flow
blacksmith: Need something forged? I make the best blades in the realm!
blacksmith: Don't waste my time with small talk though.
$ blacksmith.mark_as_met()
```
