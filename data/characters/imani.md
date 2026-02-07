---
type: character
id: imani
name: Imani
description: A high-level policy lead tracking route safety, ration efficiency, and drift probability.
base_image: chars/female_fit.png
location: market
pos: 900,600
factions:
  - merchants
tags:
  - planner
  - leader
  - logistics
---
# Talk
```flow
imani: We balance the data points: food, water, and Silence. If any one drops, the settlement falls.
imani: If you've been outside, report any changes in the sleeper patterns immediately. Every pulse counts.
$ imani.mark_as_met()
```
