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

label CHAR__ranger:
    ranger "You shouldn't wander the forest alone."
    ranger "Wolves, bandits... and worse things lurk in the shadows."
    $ ranger.mark_as_met()
    return

label CHAR__ranger__talk:
    ranger "You shouldn't wander the forest alone."
    ranger "Wolves, bandits... and worse things lurk in the shadows."
    $ ranger.mark_as_met()
    return

label CHAR__merchant_hakim:
    merchant_hakim "Salaam, my friend! Come, look at my wares!"
    merchant_hakim "I have silks, spices, and treasures from across the sea!"
    $ merchant_hakim.mark_as_met()
    return

label CHAR__merchant_hakim__talk:
    merchant_hakim "Salaam, my friend! Come, look at my wares!"
    merchant_hakim "I have silks, spices, and treasures from across the sea!"
    $ merchant_hakim.mark_as_met()
    return

label CHAR__guard_captain:
    guard_captain "Halt! State your business, traveler."
    guard_captain "Hmm, you look harmless enough. Welcome to the city."
    $ guard_captain.mark_as_met()
    return

label CHAR__guard_captain__talk:
    guard_captain "Halt! State your business, traveler."
    guard_captain "Hmm, you look harmless enough. Welcome to the city."
    $ guard_captain.mark_as_met()
    return

label CHAR__bard:
    bard "Ah, a new face! Perhaps you'd like to hear a song?"
    bard "I know ballads from every corner of the realm!"
    $ bard.mark_as_met()
    return

label CHAR__bard__talk:
    bard "Ah, a new face! Perhaps you'd like to hear a song?"
    bard "I know ballads from every corner of the realm!"
    $ bard.mark_as_met()
    return

label CHAR__stranger:
    stranger "..."
    stranger "You have a curious look about you."
    stranger "Perhaps we'll speak again when the time is right."
    $ stranger.mark_as_met()
    return

label CHAR__stranger__talk:
    stranger "..."
    stranger "You have a curious look about you."
    stranger "Perhaps we'll speak again when the time is right."
    $ stranger.mark_as_met()
    return

label CHAR__warrior:
    "You sharpen your blade, contemplating your next contract."
    return

label CHAR__warrior__talk:
    "You sharpen your blade, contemplating your next contract."
    return

label CHAR__fisherman:
    fisherman "Ahoy there! Looking for fish or for stories?"
    fisherman "Either way, I've got plenty of both!"
    $ fisherman.mark_as_met()
    return

label CHAR__fisherman__talk:
    fisherman "Ahoy there! Looking for fish or for stories?"
    fisherman "Either way, I've got plenty of both!"
    $ fisherman.mark_as_met()
    return

label CHAR__blacksmith:
    blacksmith "Need something forged? I make the best blades in the realm!"
    blacksmith "Don't waste my time with small talk though."
    $ blacksmith.mark_as_met()
    return

label CHAR__blacksmith__talk:
    blacksmith "Need something forged? I make the best blades in the realm!"
    blacksmith "Don't waste my time with small talk though."
    $ blacksmith.mark_as_met()
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

label CHAR__priestess:
    priestess "May the light guide your path, traveler."
    priestess "If you seek healing or wisdom, you have come to the right place."
    $ priestess.mark_as_met()
    return

label CHAR__priestess__talk:
    priestess "May the light guide your path, traveler."
    priestess "If you seek healing or wisdom, you have come to the right place."
    $ priestess.mark_as_met()
    return

label CHAR__orphan:
    orphan "Hey mister! Got any spare coins?"
    orphan "I can show you secret places if you've got food!"
    $ orphan.mark_as_met()
    return

label CHAR__orphan__talk:
    orphan "Hey mister! Got any spare coins?"
    orphan "I can show you secret places if you've got food!"
    $ orphan.mark_as_met()
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

label CHAR__innkeeper:
    innkeeper "Welcome to the Rusty Tankard, friend!"
    innkeeper "We've got ale, rooms, and fresh gossip."
    $ innkeeper.mark_as_met()
    return

label CHAR__innkeeper__talk:
    innkeeper "Welcome to the Rusty Tankard, friend!"
    innkeeper "We've got ale, rooms, and fresh gossip."
    $ innkeeper.mark_as_met()
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

