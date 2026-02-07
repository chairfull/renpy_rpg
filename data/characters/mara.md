---
type: character
name: Mara
id: mara
description: The steady hand keeping the settlement's life-support and quarantine running.
base_image: chars/male_fit.png
location: market
pos: 800,600
factions:
  - town_guard
  - merchants
tags:
  - important
  - leader
  - coordinator
---

# Talk
```flow
mara: You made it in. Good. We need fast legs and even calmer voices.
mara: The signal from the old Spire is shifting. If we don't adapt the perimeter sonar, the sleepers will be at the gates by dawn.
$ mara.mark_as_met()
```

# Dialogue

## Offer Help
```yaml
short: Offer help
long: If you need someone to run the outskirts, I'm your person.
tags:
  - Quest
memory: true
cond: true
```

```flow
pc: If you need someone fast, I can run the perimeter.
mara: Good. We're blind out there. Take this route map—it's marked with the latest safe-zones and frequency dead-spots.
$ mara.items.append(Item("Safe Route Map", "Marked safe corridors and quiet zones."))
$ quest_manager.start_quest("long_dawn")
BOND ADD mara trust 5
```

## Ask About The Signal
```yaml
short: Ask about the signal
long: What's the latest on the Spire's transmission?
tags:
  - Lore
memory: true
cond: true
```

```flow
mara: It started three nights ago. A rhythmic, low-frequency pulse. 
mara: It's drawing the sleepers in from the plains. If we can't find a way to shift the frequency, we'll be overrun by the week's end.
```

## Report on Spire
```yaml
short: Report on Spire
long: I have the protocol drive from the Spire.
tags:
  - Quest
cond: "flag_get('protocol_recovered', False) and not flag_get('protocol_deciphered', False)"
```

```flow
pc: I have the protocol drive from the Spire. The lobby was full of them—it was like walking through a dream where nobody breathes.
mara: Every year we lose more to the drift. This drive... it's the first real data we've had on their resonance in a decade.
mara: Give me a moment to patch it into the main console. We need to see if we can broadcast a counter-tone.
NOTIFY "Deciphering protocol..."
GIVE protocol_deciphered 1
FLAG SET protocol_deciphered true
mara: There. It's not just a signal. It's a bridge. We can lead them away, or we can shut their cognitive resonance down entirely.
```
