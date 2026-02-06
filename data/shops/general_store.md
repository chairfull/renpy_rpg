---
type: shop
id: general_store
name: Relief Depot
description: The main distribution point for rations and repair kits.
buy_mult: 1.1
sell_mult: 0.6
items:
  - apple
  - apple
  - potion
  - potion
  - camp_kit
  - camp_kit
  - sword
  - club
---

# Talk
```flow
"Check the crate tags before you take anything."
$ renpy.store.general_store.interact()
```
