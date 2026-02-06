---
type: quest
id: iron_and_fire
name: Iron and Fire
description: Blacksmith Greta needs some materials to test your worth.
---

# Started
```trigger
event: CHAR_MET
char: blacksmith
```
```flow
blacksmith: You look like you could use a real weapon.
blacksmith: Bring me some wood and stone, and maybe I'll show you how it's done.
```

# Goals

## Collect Wood
```trigger
event: ITEM_GAINED
item: Wood
total: 2
```
```flow
pc: That should be enough wood.
```

## Collect Stone
```trigger
event: ITEM_GAINED
item: Stone
total: 2
```
```flow
pc: Got the stone. Now back to Greta.
```

## Craft a Wooden Club
```trigger
event: ITEM_CRAFTED
recipe: club_recipe
```
```flow
blacksmith: Not bad for a beginner. It's crude, but it'll smash things.
```

# Passed
```flow
$ achievements.unlock("master_crafter")
pc: I've learned the basics of crafting.
```
