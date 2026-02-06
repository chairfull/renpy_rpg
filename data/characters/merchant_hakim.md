---
type: character
name: Merchant Hakim
id: merchant_hakim
description: A foreign trader with exotic wares from distant lands.
location: market
pos: 600,550
factions:
  - merchants
  - foreign
tags:
  - merchant
  - traveler
affinity: 5
---

# Talk
```flow
merchant_hakim: Salaam, my friend! Come, look at my wares!
merchant_hakim: I have silks, spices, and treasures from across the sea!
$ merchant_hakim.mark_as_met()
```
