---
type: character
name: Innkeeper
id: innkeeper
description: A jovial fellow who runs the Rusty Tankard.
location: tavern
pos: 300,350
factions:
  - merchants
tags:
  - merchant
  - friendly
affinity: 10
---

# Talk
```flow
innkeeper: Welcome to the Rusty Tankard, friend!
innkeeper: We've got ale, rooms, and fresh gossip.
$ innkeeper.mark_as_met()
```
