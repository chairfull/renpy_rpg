---
type: character
id: theo
name: Theo
description: Dedicated to preserving pre-fall data logs and charting the decay of the global transmission grid.
base_image: chars/male_thin.png
location: city_center
pos: 500,500
stats:
  - strength: 8
  - dexterity: 10
  - intelligence: 16
  - charisma: 14
tags:
  - archivist
  - lore
  - researcher
---
# Talk
```flow
theo: If we can chart the pattern decay of the Spire, we can predict when the next drift will peak.
theo: History isn't just about what we lost; it's about the frequencies we forgot how to tune into.
$ theo.mark_as_met()
```
