---
type: dialogue
id: mayor_charisma_test
short: Compliment outfit
long: You look very professional today, Mayor. (Requires Charisma 12)
emoji: ✨
chars: mayor
tags: [Charisma]
memory: False
cond: pc.stats.charisma >= 12
---

```flow
pc: You look professional today, Mayor.
mayor: Thank you, you look great too!.
pc: Where did you get that outfit?
mayor: It's a gift from the king.
pc: He has good taste.
```