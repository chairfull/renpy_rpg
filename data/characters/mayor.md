---
type: character
name: Coordinator Mara
id: mayor
description: The steady hand keeping the settlement running.
base_image: chars/male_fit.png
location: market
pos: 800,600
factions:
  - town_guard
  - merchants
tags:
  - important
  - leader
---

# Talk
```flow
mayor: You made it in. Good. We need fast legs and calm voices.
mayor: The signal from the old tower keeps repeating.
$ mayor.mark_as_met()
```

# Dialogue

## Offer Help
```yaml
short: Offer help
long: If you need someone fast, I can run it.
tags:
  - Quest
memory: true
cond: true
```

```flow
pc: If you need someone fast, I can run it.
mayor: Then take this route map and head to the Broadcast Tower when ready.
$ mayor.items.append(Item("Safe Route Map", "Marked safe corridors and quiet zones."))
FLAG SET long_dawn true
BOND ADD mayor trust 5
```

## Ask About The Signal
```yaml
short: Ask about the signal
long: What do we know about the repeating tone?
tags:
  - Lore
memory: true
cond: true
```

```flow
mayor: It started three nights ago. Same pattern, same hour.
mayor: If we can shape it, we can move the sleepers away from the walls.
```
