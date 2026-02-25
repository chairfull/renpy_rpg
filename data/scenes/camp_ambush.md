---
type: scene
id: camp_ambush
name: Night Alarm
---

# Start
```flow
A soft shuffling outside your tarp.
You hold your breath and listen.
#CHECK dexterity 12
```

# Steady
```flow
You stay still. The sound fades.
E#VENT CAMP_AMBUSH outcome=steady
```

# Panic
```flow
You stumble in the dark and bang the kettle.
NOTIFY "You strain your ankle."
STAT flu 60
#EVENT CAMP_AMBUSH outcome=panic
```
