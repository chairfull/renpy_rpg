# AUTOMATICALLY GENERATED LABELS - DO NOT EDIT
label char_mayor_talk:
    $ mayor = rpg_world.characters.get("Mayor")
    mayor "Welcome to our town, traveler!"
    mayor "I hope you find everything to your liking."
    $ mayor.mark_as_met()
    $ mayor.items.append(Item("Town Map", "A map of the local area."))
    jump world_loop

label char_shopkeeper_talk:
    $ shopkeeper = rpg_world.characters.get("Shopkeeper")
    shopkeeper "Welcome! I'll have some items for you soon."
    jump world_loop

label scene_intro_start:
    "Welcome to the town of AI."
    "A small place with big potential."
    "You stand in the Town Square, looking around."
    $ achievements.unlock("started_game")
    $ scene_manager.unlock('intro')
    jump world_loop

