---
type: character
name: Greta
id: greta
description: Keeps the shelter's alarms, air filtration, and signal rigs working with scrap-tech.
location: market
pos: 400,500
factions:
  - merchants
tags:
  - crafter
  - mechanic
  - scraptech
affinity: 0
---

# Talk
```flow
greta: I can quiet a rusty hinge or wake the whole block with one frequency tap.
greta: If you're heading out, you'll need a signal baton. Bring me enough scrap wood and stone weights, and I'll rig one for you.
$ greta.mark_as_met()
```
