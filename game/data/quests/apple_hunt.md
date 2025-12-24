---
type: quest
id: apple_hunt
name: The Great Apple Hunt
description: Gathering supplies for the journey.
---

# Started
```trigger
event:LOCATION_VISITED
location:square
```
```flow
I should look for some food before I leave.
I heard the General Store sells apples.
```

# Goals

## Visit the Shop
```trigger
event:LOCATION_VISITED
location:shop
```
```flow
Ah, this must be the place.
```

## Buy Apples
```trigger
event:ITEM_GAINED
item:Apple
total:3
```
```flow
That should be enough apples for now.
```

# Passed
```flow
Great! I am all set.
$ achievements.unlock("found_food")
```
