---
type: quest
id: silent_tide
name: The Silent Tide
desc: Follow the sleepers' rhythm to craft a non-violent way to guide them away from the city.
tags: [origin]
---

# Started
```flow
PLAYER theo
ZONE temple
Your logbook is full of patterns. The sleepers drift to the same pulse each night.
A priestess asks you to keep your steps soft and your breaths even.
The tide of sleepers drifts in a steady pulse, and you set out to learn why.
theo: I should look for the clerk.
QUEST_SHOW #ordinary-world
```

# Goals

## Ordinary World
```yaml
type: goal
desc: Look for the $clerk at the $shop.
mark: [shop, clerk]
trigger:
  event: CHAR_MET
  state: { character: clerk }
```
```flow
The records in the shop are endless, their weight familiar and heavy.
The archives are quiet, the records heavy, and the city survives by listening more than shouting.
theo: Perhaps the clerk knows something about the patterns in our city.
clerk: The archives hold many secrets. Few listen anymore.
# PLAY theo nod
QUEST_TICK #ordinary-world
QUEST_SHOW #call-to-adventure
```

## Call to Adventure
```yaml
type: goal
desc: Check out the $market.
mark: [market]
trigger:
  event: LOCATION_ENTERED
  state: { location: market }
```
```flow
A new rhythm rises from the harbor. Track it before it swells.
A sound rises from the harbor—not quite music, not quite breathing.
theo: There's a rhythm here... something old and patient.
NOTIFY "You sense a pattern in the air, pulling your attention to the sea."
QUEST_TICK #call-to-adventure
QUEST_SHOW #refusal-of-the-call
```

## Refusal of the Call
```yaml
type: goal
desc: Visit the $clerk at the $shop.
mark: [shop]
trigger:
  event: LOCATION_ENTERED
  state: { character: theo, location: shop }
```
```flow
The safety of the archives calls you back. Outside, the unknown waits.
Leaving the stacks feels like leaving the past. The risk is real, and so is the fear.
theo: Maybe it's safer to stay here. Record, catalog, preserve.
clerk: The city has always needed watchers, not hunters.
You feel the weight of habit holding you in place.
QUEST_TICK #refusal-of-the-call
QUEST_SHOW #meeting-the-mentor
```

## Meeting the Mentor
```yaml
type: goal
desc: Talk to $ash at the $tavern.
mark: [tavern, ash]
trigger:
  event: CHAR_MET
  state: { a: theo, b: ash }
```
```flow
QUEST_TICK #meeting-the-mentor
Ash sits quietly, listening to a sound only they can hear.
theo: I've been tracking the rhythm from the harbor. Do you hear it?
ash: For years. It's an old music, and the sleepers are its instrument.
ash: Move slow. Breathe low. The tide carries wisdom, not anger.
NOTIFY "Ash taught you the ways of the drift."
QUEST_SHOW #crossing-the-threshold
```

## Crossing the Threshold
```yaml
type: goal
desc: Visit the docks.
mark: [docks]
trigger:
  event: LOCATION_ENTERED
  state: { character: theo, location: docks }
```
```flow
QUEST_TICK #crossing-the-threshold
The docks are vast and still. No ships move. No voices rise. Only the pulse.
theo: Here. I feel it strongest here.
The sleepers drift nearby, their steps synchronized to something unseen.
NOTIFY "The rhythm grows clearer at the threshold between city and sea."
QUEST_SHOW #tests-and-allies
```

## Tests and Allies
```yaml
type: goal
mark: [tavern]
trigger:
  event: LOCATION_ENTERED
  state: { character: theo, location: tavern }
```
```flow
QUEST_TICK #tests-and-allies
You return to gather stories from those who witness the sleepers' rhythm.
theo: I need to hear what others know about the tide. Will you tell me?
ash: Every keeper in this city hears it differently. That's the secret.
The testimonies weave together like a pattern only visible from far away.
NOTIFY "Testimonies recorded: The rhythm is collective, not singular."
QUEST_SHOW #approach
```

## Approach
```yaml
type: goal
mark: [mage_tower]
trigger:
  event: LOCATION_ENTERED
  state: { character: theo, location: mage_tower }
```
```flow
QUEST_TICK #approach
The tower looms above the city, its old transmitters silent but still potent.
theo: The rhythm connects to the signal corridors. They all run through the tower.
You trace the pulse lines on ancient maps, seeing the architecture of sound.
NOTIFY "Signal corridors mapped: The broadcast system still remembers how to sing."
QUEST_SHOW #ordeal
```

## Ordeal
```yaml
type: goal
desc: Visit the $mage_tower.
mark: [mage_tower]
trigger:
  event: LOCATION_ENTERED
  state: { character: theo, location: mage_tower }
  flags: { broadcast_tower_reached: true }
```
```flow
QUEST_TICK #ordeal
The stairwell is labyrinthine, and the sleepers are everywhere here, drifting in spirals.
theo: Stay calm. Move like the tide moves. Don't disturb the drift.
Your breath synchronizes with theirs. Your steps match their steps. You become part of the rhythm.
NOTIFY "You are one voice in the tide now."
At last, you reach the inner console, untouched and still humming.
QUEST_SHOW #reward
```

## Reward
```yaml
type: goal
name: Find the Harmonic Key
trigger:
  event: FLAG_CHANGED
  flags: { harmonic_key_obtained: true }
```
```flow
QUEST_TICK #reward
The console yields its secret—a frequency pattern written in old code, waiting generations for this moment.
theo: Here. This is how to guide them, not drag them.
The harmonic key sings in your hands, no longer a weapon but a song.
NOTIFY "The Harmonic Key obtained: A frequency that guides without force."
QUEST_SHOW #the-road-back
```

## The Road Back
```yaml
type: goal
desc: Head back to temple.
mark: [temple]
trigger:
  event: LOCATION_ENTERED
  state: { character: theo, location: temple }
```
```flow
QUEST_TICK #the-road-back
The temple is a place where voices gather. You carry something precious back to it.
theo: I have a teaching to share. Will you listen?
The gathered fold listen as you explain the rhythm, the pattern, the way forward.
NOTIFY "The pattern is translated: From archive to action, from silence to song."
QUEST_SHOW #resurrection
```

## Resurrection
```yaml
type: goal
desc: Visit the market.
mark: [market]
trigger:
  event: LOCATION_ENTERED
  state: { character: theo, location: market }
  flags: { broadcast_success: true }
```
```flow
QUEST_SHOW #resurrection
The harmonic frequency spreads through the city via signal corridors old and new.
theo: Does it work? Do they follow the new rhythm?
The sleepers shift, slower, gentler, guided by a frequency that respects their choice.
NOTIFY "The broadcast succeeds: No force, no violence, only the rhythm continuing."
QUEST_SHOW #return-with-the-elixer
```

## Return with the Elixir
```yaml
type: goal
mark: temple
trigger:
  event: LOCATION_ENTERED
  state: { character: theo, location: temple }
```
```flow
QUEST_TICK #return-with-the-elixir
The city assembles in the temple. The wisdom you bring is not conquest but coexistence.
theo: The sleepers are not our enemy. They are part of the rhythm we all share.
A new way of being settles over the city like fog becoming rain.
NOTIFY "The Elixir shared: Wisdom without dominion, listening without control."
QUEST_COMPLETE silent-tide
```

## Passed
```flow
The Silent Tide becomes a living practice, and the city learns to survive without violence.
```

# Choices

## Ask the Clerk
```yaml
type: choice
menu: clerk
id: ask_clerk
text: "Ask the clerk about the sleepers' rhythm."
flags: { asked_clerk: ~ }
```
```flow
theo: Excuse me — have you noticed the sleepers' rhythm?
clerk: It's old as the docks. Folks hush and follow it when the moon leans right.
FLAG asked_clerk=true
NOTIFY "Clerk: They remember a tune from the sea."
```

## Share the Pattern with Ash
```yaml
type: choice
menu: ash
id: share_with_ash
text: "Share the pattern you've recorded with Ash."
cond: friendship.between(ash, theo) > 10
```
```flow
theo: I tracked the tide lines — I think I can shape them without force.
ash: If you can hum it slow enough, maybe they follow a kinder path.
FLAG shared_with_ash=true
NOTIFY "Ash: We can try a gentle frequency."
```

## Attempt Harmonic Broadcast
```yaml
type: choice
menu: clerk
id: attempt_broadcast
text: "Offer to run the harmonic broadcast (requires harmonic key)."
cond: has_flag(harmonic_key_obtained)
```
```flow
theo: I can try the harmonic broadcast — hand me the key.
clerk: If it works, it could guide them. If it fails...
FLAG broadcast_attempted
GAIN protocol_deciphered 
```