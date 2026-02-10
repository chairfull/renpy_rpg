---
type: quest
id: silent_tide
name: The Silent Tide
description: Follow the sleepers' rhythm to craft a non-violent way to guide them away from the city.
category: main
origin: true
pc_id: theo
image: chars/male_thin.png
---

# Started
```flow
Your logbook is full of patterns. The sleepers drift to the same pulse each night.
A priestess asks you to keep your steps soft and your breaths even.
The tide of sleepers drifts in a steady pulse, and you set out to learn why.
```

# Goals

## Ordinary World
```yaml
guidance:
  location: shop
  objects: [clerk]
trigger:
  event: CHAR_MET
  char_id: clerk
```
The archives are quiet, the records heavy, and the city survives by listening more than shouting.


## Call to Adventure
```yaml
guidance:
  location: market
trigger:
  event: LOCATION_VISITED
  location: market
```
A new rhythm rises from the harbor. Track it before it swells.


## Refusal of the Call
```yaml
guidance:
  location: shop
trigger:
  event: LOCATION_VISITED
  location: shop
```
Leaving the stacks feels like leaving the past. The risk is real, and so is the fear.


## Meeting the Mentor
```yaml
guidance:
  location: tavern
  objects: [ash]
trigger:
  event: CHAR_MET
  char_id: ash
```
Ash shares drift wisdom - move slow, breathe low, and let the sleepers pass.


## Crossing the Threshold
```yaml
guidance:
  location: docks
trigger:
  event: LOCATION_VISITED
  location: docks
```
You step onto the silent docks, where the tide hums against empty hulls.


## Tests and Allies
```yaml
guidance:
  location: tavern
trigger:
  event: LOCATION_VISITED
  location: tavern
```
Gather quiet testimonies from the tavern and the clinic. The pattern is shared, not owned.


## Approach
```yaml
guidance:
  location: mage_tower
trigger:
  event: LOCATION_VISITED
  location: mage_tower
```
You chart the pulse lines back toward the Broadcast Tower and the old signal corridors.


## Ordeal
```yaml
guidance:
  location: mage_tower
trigger:
  event: LOCATION_VISITED
  location: mage_tower
  cond: "flag_get('broadcast_tower_reached')"
```
The stairwell is still. You reach the inner console without waking the drift.


## Reward
```yaml
trigger:
  event: FLAG_SET
  flag: "harmonic_key_obtained"
```
The harmonic key is clear at last - a tone that guides, not commands.


## The Road Back
```yaml
guidance:
  location: temple
trigger:
  event: LOCATION_VISITED
  location: temple
```
Bring the pattern to the settlement and translate it for those who only hear silence.


## Resurrection
```yaml
guidance:
  location: market
trigger:
  event: LOCATION_VISITED
  location: market
  cond: "flag_get('broadcast_success')"
```
The first broadcast is a trial of trust. The tide turns without panic.


## Return with the Elixir
```yaml
guidance:
  location: temple
trigger:
  event: LOCATION_VISITED
  location: temple
```
You teach the city to listen, and the sleepers to follow a gentler path.


# Passed
```flow
The Silent Tide becomes a living practice, and the city learns to survive without violence.
```
