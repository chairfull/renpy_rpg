---
type: scene
id: camp_ambush
name: Midnight Ambush
---

# Start
```flow
A rustle in the dark jerks you awake.
$ contested_check("dexterity", 12, success_label="SCENE__camp_ambush__escape", fail_label="SCENE__camp_ambush__hurt")
```

# Escape
```flow
You spring up and the shadow slips away into the brush.
@event CAMP_AMBUSH outcome=escape
```

# Hurt
```flow
You stumble and take a hit in the dark.
$ pc.stats.hp = max(1, pc.stats.hp - 10)
@event CAMP_AMBUSH outcome=hurt
```
