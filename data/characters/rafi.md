---
type: character
name: Rafi
id: rafi
description: The firm voice at the quarantine gate, ensuring no 'Drift' enters the settlement.
location: guardhouse
pos: 600,400
factions:
  - town_guard
tags:
  - authority
  - watch
  - guard
affinity: 0
---

# Talk
```flow
rafi: Keep your steps light and your voice lower. The fence only holds if the noise stays inside.
rafi: We keep the line so others can sleep without waking up as one of them.
$ rafi.mark_as_met()
```

# Dialogue

## Request Gate Pass
```yaml
short: Request gate pass
long: I need a clearance pass for the Dead Zone fence. (Requires Charisma 10)
tags:
  - Gate
memory: true
cond: pc.stats.charisma >= 10
reason: "Needs Charisma 10."
```

```flow
rafi: I can log a short-term pass. If the sensors pick up a spike in your frequency, don't expect us to open the gate when you come back.
FLAG SET gate_pass true
BOND ADD rafi respect 3
NOTIFY "Gate pass logged."
```

## Report a Quiet Route
```yaml
short: Report quiet route
long: I've mapped a path with significantly lower Sleeper density.
tags:
  - Patrol
memory: true
cond: true
```

```flow
rafi: Good. Every quiet route is a lifeline. I'll update the patrol logs.
BOND ADD rafi trust 2
```
