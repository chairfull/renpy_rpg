# AUTOMATICALLY GENERATED LABELS - DO NOT EDIT
label CHAR__mayor__talk:
    $ mayor = rpg_world.characters.get("Mayor")
    mayor "Welcome to our town, traveler!"
    mayor "I hope you find everything to your liking."
    $ mayor.mark_as_met()
    $ mayor.items.append(Item("Town Map", "A map of the local area."))
    jump world_loop

label CHAR__shopkeeper__talk:
    $ shopkeeper = rpg_world.characters.get("Shopkeeper")
    shopkeeper "Welcome! I'll have some items for you soon."
    jump world_loop

label SCENE__intro__start:
    "Welcome to the town of AI."
    "A small place with big potential."
    "You stand in the Town Square, looking around."
    $ achievements.unlock("started_game")
    $ scene_manager.unlock('intro')
    jump world_loop

label QUEST__apple_hunt__started:
    "I should look for some food before I leave."
    "I heard there are apples near the shop."
    jump world_loop

label QUEST__apple_hunt__find_the_shop:
    "\"Ah, here it is.\""
    jump world_loop

label QUEST__apple_hunt__collect_apples:
    "That should be enough apples for now."
    jump world_loop

label QUEST__apple_hunt__passed:
    "Great! I am all set."
    $ achievements.unlock("found_food")
    jump world_loop

