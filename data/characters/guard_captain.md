---
type: character
name: Watch Captain Rafi
id: guard_captain
description: The calm, firm voice at the quarantine gate.
location: guardhouse
pos: 600,400
factions:
  - town_guard
tags:
  - authority
  - watch
affinity: 0
---

# Talk
```flow
guard_captain: Keep your steps light and your voice lower.
guard_captain: We keep the line so others can sleep.
$ guard_captain.mark_as_met()
```

# Dialogue

## Request Gate Pass
```yaml
short: Request gate pass
long: I need access beyond the fence. (Requires Charisma 10)
tags:
  - Gate
memory: true
cond: pc.stats.charisma >= 10
reason: "Needs Charisma 10."
```

```flow
guard_captain: I can log a short pass. Do not linger.
FLAG SET gate_pass true
BOND ADD guard_captain respect 3
NOTIFY "Gate pass logged."
```

## Report a Quiet Route
```yaml
short: Report quiet route
long: I found a path with less noise and fewer sleepers.
tags:
  - Patrol
memory: true
cond: true
```

```flow
guard_captain: Good. That keeps the line intact.
BOND ADD guard_captain trust 2
```
