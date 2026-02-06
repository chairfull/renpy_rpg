---
type: character
name: Mechanic Greta
id: blacksmith
description: Keeps alarms, doors, and rigs working with a steady hand.
location: market
pos: 400,500
factions:
  - merchants
tags:
  - crafter
  - mechanic
affinity: 0
---

# Talk
```flow
blacksmith: I can quiet a hinge or wake the block with one tap.
blacksmith: Bring wood and stone if you want a signal baton.
$ blacksmith.mark_as_met()
```
