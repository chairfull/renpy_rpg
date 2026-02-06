---
type: quest
id: scholars_secret
name: The Scholar's Secret
description: Scholar Theo is looking for an ancient text.
---

# Started
```trigger
event: CHAR_MET
char: scholar
```
```flow
scholar: My research has stalled. I know there are records of an ancient history nearby...
scholar: If you find anything, please bring word to me.
```

# Goals

## Find the Ancient Note
```trigger
event: NOTE_UNLOCKED
note: note_ancient_history
```
```flow
pc: This must be what Theo was talking about. It looks very old.
```

# Passed
```flow
$ achievements.unlock("lore_keeper")
scholar: Remarkable! This confirms my theories about the Great Migration.
scholar: You have a keen eye for discovery.
```
