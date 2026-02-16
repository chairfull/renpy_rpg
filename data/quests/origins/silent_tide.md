````markdown
---
type: quest
id: silent_tide
name: The Silent Tide
description: Follow the sleepers' rhythm to craft a non-violent way to guide them away from the city.
category: main
origin: true
character: theo
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
```flow
GOAL_SHOW silent_tide
STORY The records in the shop are endless, their weight familiar and heavy.
theo: Perhaps the clerk knows something about the patterns in our city.
clerk: The archives hold many secrets. Few listen anymore.
PLAY theo nod
GOAL_TICK silent_tide
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
```flow
GOAL_SHOW silent_tide
CAMERA pan market_to_harbor
STORY A sound rises from the harbor—not quite music, not quite breathing.
theo: There's a rhythm here... something old and patient.
NOTIFY "You sense a pattern in the air, pulling your attention to the sea."
ANIM pulse_waves harbor
GOAL_TICK silent_tide
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
```flow
GOAL_SHOW silent_tide
ANIM pc_hesitate
STORY The safety of the archives calls you back. Outside, the unknown waits.
theo: Maybe it's safer to stay here. Record, catalog, preserve.
clerk: The city has always needed watchers, not hunters.
STORY You feel the weight of habit holding you in place.
ANIM fade_to_shadows
GOAL_TICK silent_tide
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
```flow
GOAL_SHOW silent_tide
ANIM pc_enter_tavern
STORY Ash sits quietly, listening to a sound only they can hear.
theo: I've been tracking the rhythm from the harbor. Do you hear it?
ash: For years. It's an old music, and the sleepers are its instrument.
ash: Move slow. Breathe low. The tide carries wisdom, not anger.
ANIM ash_hand_gesture_slow
NOTIFY "Ash taught you the ways of the drift."
GOAL_TICK silent_tide
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
```flow
GOAL_SHOW silent_tide
ANIM camera_approach_docks
STORY The docks are vast and still. No ships move. No voices rise. Only the pulse.
theo: Here. I feel it strongest here.
STORY The sleepers drift nearby, their steps synchronized to something unseen.
ANIM sleepers_appear_distant
NOTIFY "The rhythm grows clearer at the threshold between city and sea."
ANIM pc_steady_breath
GOAL_TICK silent_tide
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
```flow
GOAL_SHOW silent_tide
STORY You return to gather stories from those who witness the sleepers' rhythm.
theo: I need to hear what others know about the tide. Will you tell me?
ash: Every keeper in this city hears it differently. That's the secret.
ANIM pc_listen_gesture
STORY The testimonies weave together like a pattern only visible from far away.
NOTIFY "Testimonies recorded: The rhythm is collective, not singular."
ANIM threads_weave_together
GOAL_TICK silent_tide
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
```flow
GOAL_SHOW silent_tide
ANIM camera_pan_to_tower
STORY The tower looms above the city, its old transmitters silent but still potent.
theo: The rhythm connects to the signal corridors. They all run through the tower.
STORY You trace the pulse lines on ancient maps, seeing the architecture of sound.
ANIM pc_draw_pattern
NOTIFY "Signal corridors mapped: The broadcast system still remembers how to sing."
ANIM glow_lines_pulse
GOAL_TICK silent_tide
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
```flow
GOAL_SHOW silent_tide
ANIM darkness_descend tower_interior
STORY The stairwell is labyrinthine, and the sleepers are everywhere here, drifting in spirals.
theo: Stay calm. Move like the tide moves. Don't disturb the drift.
STORY Your breath synchronizes with theirs. Your steps match their steps. You become part of the rhythm.
ANIM pc_fade_into_crowd
NOTIFY "You are one voice in the tide now."
ANIM harmony_achieved
STORY At last, you reach the inner console, untouched and still humming.
GOAL_TICK silent_tide
```
The stairwell is still. You reach the inner console without waking the drift.


## Reward
```yaml
trigger:
  event: FLAG_SET
  flag: "harmonic_key_obtained"
```
```flow
GOAL_SHOW silent_tide
ANIM light_break_console
STORY The console yields its secret—a frequency pattern written in old code, waiting generations for this moment.
theo: Here. This is how to guide them, not drag them.
STORY The harmonic key sings in your hands, no longer a weapon but a song.
ANIM key_resonates_light
NOTIFY "The Harmonic Key obtained: A frequency that guides without force."
ANIM aura_harmonic
GOAL_TICK silent_tide
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
```flow
GOAL_SHOW silent_tide
ANIM pc_walk_toward_temple
STORY The temple is a place where voices gather. You carry something precious back to it.
theo: I have a teaching to share. Will you listen?
STORY The gathered fold listen as you explain the rhythm, the pattern, the way forward.
ANIM circle_form_light
NOTIFY "The pattern is translated: From archive to action, from silence to song."
ANIM knowledge_spreads
GOAL_TICK silent_tide
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
```flow
GOAL_SHOW silent_tide
ANIM broadcast_frequency_activate
STORY The harmonic frequency spreads through the city via signal corridors old and new.
theo: Does it work? Do they follow the new rhythm?
STORY The sleepers shift, slower, gentler, guided by a frequency that respects their choice.
ANIM sleepers_redirect_slow
NOTIFY "The broadcast succeeds: No force, no violence, only the rhythm continuing."
ANIM city_harmonize
GOAL_TICK silent_tide
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
```flow
GOAL_SHOW silent_tide
ANIM temple_gather_all
STORY The city assembles in the temple. The wisdom you bring is not conquest but coexistence.
theo: The sleepers are not our enemy. They are part of the rhythm we all share.
STORY A new way of being settles over the city like fog becoming rain.
ANIM healing_light_spread
NOTIFY "The Elixir shared: Wisdom without dominion, listening without control."
ANIM city_transforms_gentle
GOAL_TICK silent_tide
```
You teach the city to listen, and the sleepers to follow a gentler path.


# Passed
```flow
The Silent Tide becomes a living practice, and the city learns to survive without violence.
```

# Choices

## Ask the Clerk
```yaml
menu: clerk
id: ask_clerk
text: "Ask the clerk about the sleepers' rhythm."
cond: "True"
```
```flow
theo: Excuse me — have you noticed the sleepers' rhythm?
clerk: It's old as the docks. Folks hush and follow it when the moon leans right.
FLAG SET asked_clerk True
NOTIFY "Clerk: They remember a tune from the sea."
```

## Share the Pattern with Ash
```yaml
menu: ash
id: share_with_ash
text: "Share the pattern you've recorded with Ash."
cond: "bond_get_stat('theo','ash','affinity') > 10"
```
```flow
theo: I tracked the tide lines — I think I can shape them without force.
ash: If you can hum it slow enough, maybe they follow a kinder path.
FLAG SET shared_with_ash True
NOTIFY "Ash: We can try a gentle frequency."
```

## Attempt Harmonic Broadcast
```yaml
menu: clerk
id: attempt_broadcast
text: "Offer to run the harmonic broadcast (requires harmonic key)."
cond: "flag_get('harmonic_key_obtained')"
```
```flow
theo: I can try the harmonic broadcast — hand me the key.
clerk: If it works, it could guide them. If it fails...
EVENT GAME_STARTED broadcast_attempt=true
FLAG SET broadcast_attempted True
GIVE protocol_deciphered 1
```

````
