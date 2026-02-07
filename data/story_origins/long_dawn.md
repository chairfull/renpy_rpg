---
type: story_origin
id: long_dawn
name: The Long Dawn
description: A journey to find the signal and lead the sleepers home.
image: chars/male_fit.png
---

# Started
```flow
The settlement is a cage of routine and fear. You've walked the perimeter until every stone is a familiar face.
 Coordinator Mara is watching the horizon again. The signal from the Spire is changing.
Mara: If you're looking for a way out, Survivor, this is it. Go to the Spire.

GOAL SHOW call_to_adventure
```

# Goals

## Call to Adventure
```trigger
event: CHAR_MET
char: mayor
```
```flow
mara: We need to know what that signal is before the peace breaks. You know the outskirts.
```

## Refusal of the Call
```trigger
event: ITEM_GAINED
item: Wood
total: 5
```
```flow
pc: I'll need more than just hope to survive the night out there. I should gather wood for markers and heat.
```

## Meeting the Mentor
```trigger
event: CHAR_MET
char: priestess
```
```flow
elena: If you seek the Spire, seek the silence first. The sleepers don't hunt; they drift. Use the rhythm, don't break it.
```

## Crossing the Threshold
```trigger
event: LOCATION_VISITED
location: forest_edge
```
```flow
pc: The district gates are behind me. The air here tastes like static and old rain. No turning back.
```

## Tests and Allies
```trigger
event: CHAR_MET
char: ranger
```
```flow
lena: You're either brave or desperate. Keep your light low and your breathing steady.
```

## Approach to the Inmost Cave
```trigger
event: LOCATION_VISITED
location: mage_tower
```
```flow
pc: The Spire. It looms over the city like a rusted needle. The signal is deafening here.
```

## The Ordeal
```trigger
event: LOCATION_VISITED
location: mage_tower_f1
```
```flow
pc: The lobby is full of them. Dozens of sleepers, swaying to the tone. I have to move through without waking the storm.
```

## The Reward
```trigger
event: ITEM_GAINED
item: broadcast_protocol
```
```flow
pc: The drive is humming in my hand. Years of data, frequencies, the heartbeat of the city.
```

## The Road Back
```trigger
event: LOCATION_VISITED
location: forest_edge
```
```flow
pc: I have to get this back to Mara. The signal is shifting again—I can hear them stirring behind me.
```

## Resurrection
```trigger
event: ITEM_GAINED
item: protocol_deciphered
```
```flow
pc: I see it now. The city and the silence aren't separate. We just forgot how to listen.
```


# Passed
```flow
The settlement broadcasts the bridge signal.
The sleepers don't vanish, but they find peace. They move toward the plains, away from the walls.
The Survivor stands at the gate, no longer a scout, but the guide of a new dawn.
```
