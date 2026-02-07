---
type: character
name: Hakim
id: hakim
description: Manages the settlement's ration crates, medical supplies, and barter ledgers.
location: market
pos: 600,550
factions:
  - merchants
tags:
  - merchant
  - organizer
  - logistics
---

# Talk
```flow
hakim: Every nutrition bar is counted. Every medical kit is signed for by the Coordinator.
hakim: If you want to barter, bring something the settlement can actually use—scrap tech, clean water, or data logs. 
$ hakim.mark_as_met()
```
