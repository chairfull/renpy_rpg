---
type: shop
id: general_store
name: Relief Depot
description: The main distribution point for rations and repair kits.
buy_mult: 1.1
sell_mult: 0.6
items:
  - ration_bar
  - ration_bar
  - antiseptic_ampoule
  - antiseptic_ampoule
  - camp_kit
  - camp_kit
  - utility_pry_bar
  - signal_baton

---

# Talk
```flow
"Check the crate tags before you take anything."
$ renpy.store.general_store.interact()
```
