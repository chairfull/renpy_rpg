# AUTOMATICALLY GENERATED LABELS - DO NOT EDIT
label LOC__home__flow:
    "I'm not tired right now."
    "You look great today!"
    return

label LOC__home__bed:
    "I'm not tired right now."
    return

label LOC__home__mirror:
    "You look great today!"
    return

label CHAR__lady:
    lady "Oh, hello there. Are you also looking for rare spices?"
    lady "The market here is surprisingly well-stocked today."
    return

label CHAR__lady__talk:
    lady "Oh, hello there. Are you also looking for rare spices?"
    lady "The market here is surprisingly well-stocked today."
    return

label CHAR__warrior:
    "You sharpen your blade, contemplating your next contract."
    return

label CHAR__warrior__talk:
    "You sharpen your blade, contemplating your next contract."
    return

label CHAR__shopkeeper:
    shopkeeper "Welcome to my shop! Take a look at my wares."
    $ renpy.store.general_store.interact()
    return

label CHAR__shopkeeper__talk:
    shopkeeper "Welcome to my shop! Take a look at my wares."
    $ renpy.store.general_store.interact()
    return

label CHAR__scholar:
    "You think about your next research project."
    return

label CHAR__scholar__talk:
    "You think about your next research project."
    return

label CHAR__mayor:
    mayor "Welcome to our town, traveler!"
    mayor "I hope you find everything to your liking."
    $ mayor.mark_as_met()
    $ mayor.items.append(Item("Town Map", "A map of the local area."))
    pc "You look professional today, Mayor."
    mayor "Thank you, you look great too!."
    pc "Where did you get that outfit?"
    mayor "It's a gift from the king."
    pc "He has good taste."
    pc "This town has been here for a long time. I'd like to know how it all started."
    mayor "Well, it started a long time ago, when the first settlers arrived."
    mayor "They built this town to be a safe place for travelers."
    mayor "It's been here ever since."
    return

label CHAR__mayor__talk:
    mayor "Welcome to our town, traveler!"
    mayor "I hope you find everything to your liking."
    $ mayor.mark_as_met()
    $ mayor.items.append(Item("Town Map", "A map of the local area."))
    return

label CHAR__mayor__charisma_test:
    pc "You look professional today, Mayor."
    mayor "Thank you, you look great too!."
    pc "Where did you get that outfit?"
    mayor "It's a gift from the king."
    pc "He has good taste."
    return

label CHAR__mayor__history:
    pc "This town has been here for a long time. I'd like to know how it all started."
    mayor "Well, it started a long time ago, when the first settlers arrived."
    mayor "They built this town to be a safe place for travelers."
    mayor "It's been here ever since."
    return

label CHOICE__mayor_charisma_test:
    pc "You look professional today, Mayor."
    mayor "Thank you, you look great too!."
    pc "Where did you get that outfit?"
    mayor "It's a gift from the king."
    pc "He has good taste."
    return

label CHOICE__mayor_history:
    pc "This town has been here for a long time. I'd like to know how it all started."
    mayor "Well, it started a long time ago, when the first settlers arrived."
    mayor "They built this town to be a safe place for travelers."
    mayor "It's been here ever since."
    return

label SCENE__warrior__intro:
    $ renpy.store.td_manager.setup(rpg_world.current_location)
    "You arrive at the market square, your sword heavy at your side."
    "The air is thick with the smell of spices and the sound of bartering."
    "Your journey as a mercenary begins here."
    $ renpy.jump("world_loop")
    return

label SCENE__scholar__intro:
    $ renpy.store.td_manager.setup(rpg_world.current_location)
    "You wake up in your familiar study, surrounded by stacks of ancient parchment."
    "The sunlight filters through the window, illuminating dust motes in the air."
    "Today is the day you begin your grand research into the town's history."
    $ renpy.jump("world_loop")
    return

label SHOP__general_store__flow:
    "\"Welcome to my shop! Take a look at my wares.\""
    $ renpy.store.general_store.interact()
    return

label SHOP__general_store__talk:
    "\"Welcome to my shop! Take a look at my wares.\""
    $ renpy.store.general_store.interact()
    return

