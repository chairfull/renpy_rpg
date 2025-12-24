# AUTOMATICALLY GENERATED LABELS - DO NOT EDIT
label SCENE__intro__start:
    "Welcome to the town of AI."
    "A small place with big potential."
    "You stand in the Town Square, looking around."
    $ achievements.unlock("started_game")
    jump world_loop

label ITEM__apple__inspect:
    "It's a bright red apple, slightly bruised on one side."
    "It smells sweet and fresh."
    return

label ITEM__potion__inspect:
    "The red liquid inside the glass vial bubbles occasionally."
    "A faint scent of cinnamon and iron wafts from the cork."
    return

label ITEM__sword__inspect:
    "You hold the iron sword in your hand."
    "It's heavy, well-balanced, and has a slight nick in the pommel."
    "\"This has seen some use,\" you mutter."
    return

label CHAR__shopkeeper__talk:
    shopkeeper "Welcome! I'll have some items for you soon."
    jump world_loop

label CHAR__mayor__talk:
    mayor "Welcome to our town, traveler!"
    mayor "I hope you find everything to your liking."
    $ mayor.mark_as_met()
    $ mayor.items.append(Item("Town Map", "A map of the local area."))
    jump world_loop

label QUEST__apple_hunt__started:
    "I should look for some food before I leave."
    "I heard the General Store sells apples."
    jump world_loop

label QUEST__apple_hunt__visit_the_shop:
    "Ah, this must be the place."
    jump world_loop

label QUEST__apple_hunt__buy_apples:
    "That should be enough apples for now."
    jump world_loop

label QUEST__apple_hunt__passed:
    "Great! I am all set."
    $ achievements.unlock("found_food")
    jump world_loop

