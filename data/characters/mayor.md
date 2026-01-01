---
type: character
name: Mayor
description: The leader of our fine town.
base_image: characters/male_fit.png
location: market
pos: 800,600
factions:
  - town_guard
  - merchants
tags:
  - important
  - noble
---

# Talk
```flow
mayor: Welcome to our town, traveler!
mayor: I hope you find everything to your liking.
$ mayor.mark_as_met()
$ mayor.items.append(Item("Town Map", "A map of the local area."))
```

# Dialogue

## Charisma Test
```yaml
short: Compliment outfit
long: You look very professional today, Mayor. (Requires Charisma 12)
emoji: ✨
tags:
  - Charisma
memory: false
cond: pc.stats.charisma >= 12
```

```flow
pc: You look professional today, Mayor.
mayor: Thank you, you look great too!.
pc: Where did you get that outfit?
mayor: It's a gift from the king.
pc: He has good taste.
```

## History
```yaml
short: Ask about history
long: This town has been here for a long time. I'd like to know how it all started.
emoji: 📖
tags:
  - History
  - Lore
memory: true
cond: true
```

```flow
pc: This town has been here for a long time. I'd like to know how it all started.
mayor: Well, it started a long time ago, when the first settlers arrived.
mayor: They built this town to be a safe place for travelers.
mayor: It's been here ever since.
```
