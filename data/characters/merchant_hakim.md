---
type: character
name: Quartermaster Hakim
id: merchant_hakim
description: Manages the ration crates and barter ledgers.
location: market
pos: 600,550
factions:
  - merchants
tags:
  - merchant
  - organizer
affinity: 5
---

# Talk
```flow
merchant_hakim: Every bar is counted. Every kit is signed for.
merchant_hakim: If you trade, trade fair, and we both sleep.
$ merchant_hakim.mark_as_met()
```
