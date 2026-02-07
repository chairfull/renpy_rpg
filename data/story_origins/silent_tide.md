---
type: story_origin
id: silent_tide
name: The Silent Tide
description: A mysterious signal from the depths calls you to the edge of the world.
image: chars/male_fit.png
---

# Started
```flow
The docks are slick with salt and memories. You've spent your life watching the waves, but today, they're watching back.
A strange, rhythmic humming is vibrating through the wooden piers. It's coming from the deep.
jace: You feel that too, don't you? The tide is changing.

GOAL SHOW call_to_adventure
```

# Goals

## Call to Adventure
```trigger
event: CHAR_MET
char: jace
```
```flow
jace: Beyond the reef, there's a chime that shouldn't be there. I'm too old to chase ghosts, but you... you have the look of someone with nothing to lose.
```

## Refusal of the Call
```trigger
event: ITEM_GAINED
item: stone
total: 3
```
```flow
pc: I should probably just stick to the nets. I'll need some weights if I'm going to brace the hull against the swell.
```

## Meeting the Mentor
```trigger
event: CHAR_MET
char: theo
```
```flow
theo: The deep doesn't just hold water, boy. It holds the echoes of what we were. If you follow the chime, listen for the gaps between the notes.
```

## Crossing the Threshold
```trigger
event: LOCATION_VISITED
location: forest_edge
```
```flow
pc: The salt spray is a mile behind me now. The air is thick with the scent of damp earth and something older. Step by step, the shore fades.
```

## Tests and Allies
```trigger
event: CHAR_MET
char: hakim
```
```flow
hakim: Looking for shiny things in dark places? You'll need more than just a sturdy boat for where you're headed.
```

## Approach to the Inmost Cave
```trigger
event: LOCATION_VISITED
location: mage_tower
```
```flow
pc: The tower stands like a spear thrust into the sky. The humming from the docks is a roar here, vibrating in my very bones.
```

## The Ordeal
```trigger
event: LOCATION_VISITED
location: mage_tower_f1
```
```flow
pc: Shadows flicker in the corners of my vision. The 'Sleepers' are here, but they aren't sleeping. They're waiting. I must be silent as the tide.
```

## The Reward
```trigger
event: ITEM_GAINED
item: ancient_relic
```
```flow
pc: It's cold, so cold it burns. The relic pulses in rhythm with my own heart. The signal... it's coming from within this.
```

## The Road Back
```trigger
event: LOCATION_VISITED
location: docks
```
```flow
pc: The sea is tumultuous, reflecting the storm within the relic. I have to get this to someone who understands what it's whispering.
```

## Resurrection
```trigger
event: CHAR_MET
char: mara
```
```flow
mara: You brought it back. I haven't seen one of these since I was a child. The tide isn't coming for us—it's coming *through* us.
```

## Return with the Elixir
```trigger
event: ITEM_GAINED
item: protocol_deciphered
```
```flow
pc: The silence of the deep is no longer a void. It's a bridge. We are the architects of the new world.
```

# Passed
```flow
The Silent Tide has reached its peak.
The light from the relic bathes the docks in a soft, blue glow.
The Survivor stands by the water, no longer just a watcher of the waves, but their master.
```
