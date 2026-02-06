# AUTOMATICALLY GENERATED LABELS - DO NOT EDIT
label LOC__home__flow:
    $ rest(8)
    "You wake to the soft hum of the wall speakers."
    "You check for dust, bruises, and any new marks."
    "All clear."
    return

label LOC__home__bed:
    $ rest(8)
    "You wake to the soft hum of the wall speakers."
    return

label LOC__home__mirror:
    "You check for dust, bruises, and any new marks."
    "All clear."
    return

label LOC__market__flow:
    "A volunteer presses a ration bar into your hand."
    "\"Take it,\" she says. \"You look like you run far.\""
    $ event_manager.dispatch('ITEM_GAINED', item='apple', total=1)
    $ flag_set('market_swap', True)
    return

label LOC__market__encounter_swap:
    "A volunteer presses a ration bar into your hand."
    "\"Take it,\" she says. \"You look like you run far.\""
    $ event_manager.dispatch('ITEM_GAINED', item='apple', total=1)
    $ flag_set('market_swap', True)
    return

label LOC__forest_edge__flow:
    "The fence gives a soft rattle."
    "A sleeper drifts by, head tilted toward a far away tone."
    $ event_manager.dispatch('LOCATION_EVENT', location='forest_edge', tag='rattle')
    $ flag_set('fence_rattle', True)
    return

label LOC__forest_edge__encounter_rattle:
    "The fence gives a soft rattle."
    "A sleeper drifts by, head tilted toward a far away tone."
    $ event_manager.dispatch('LOCATION_EVENT', location='forest_edge', tag='rattle')
    $ flag_set('fence_rattle', True)
    return

label CHAR__lady:
    lady "We keep people moving and the sleepers drifting."
    lady "If you hear a new pattern, report it fast."
    return

label CHAR__lady__talk:
    lady "We keep people moving and the sleepers drifting."
    lady "If you hear a new pattern, report it fast."
    return

label CHAR__ranger:
    ranger "The sleepers follow sound more than sight."
    ranger "Keep your steps light and your voice softer."
    $ ranger.mark_as_met()
    ranger "Fine. Keep up and keep quiet."
    $ companion_add('ranger')
    $ flag_set('scout_joined', True)
    $ bond_add_stat(pc.id, 'ranger', 'trust', 3)
    ranger "Understood. Stay safe."
    $ companion_remove('ranger')
    $ flag_set('scout_joined', False)
    return

label CHAR__ranger__talk:
    ranger "The sleepers follow sound more than sight."
    ranger "Keep your steps light and your voice softer."
    $ ranger.mark_as_met()
    return

label CHAR__ranger__ask_for_a_guide:
    ranger "Fine. Keep up and keep quiet."
    $ companion_add('ranger')
    $ flag_set('scout_joined', True)
    $ bond_add_stat(pc.id, 'ranger', 'trust', 3)
    return

label CHAR__ranger__ask_to_part_ways:
    ranger "Understood. Stay safe."
    $ companion_remove('ranger')
    $ flag_set('scout_joined', False)
    return

label CHAR__merchant_hakim:
    merchant_hakim "Every bar is counted. Every kit is signed for."
    merchant_hakim "If you trade, trade fair, and we both sleep."
    $ merchant_hakim.mark_as_met()
    return

label CHAR__merchant_hakim__talk:
    merchant_hakim "Every bar is counted. Every kit is signed for."
    merchant_hakim "If you trade, trade fair, and we both sleep."
    $ merchant_hakim.mark_as_met()
    return

label CHAR__guard_captain:
    guard_captain "Keep your steps light and your voice lower."
    guard_captain "We keep the line so others can sleep."
    $ guard_captain.mark_as_met()
    guard_captain "I can log a short pass. Do not linger."
    $ flag_set('gate_pass', True)
    $ bond_add_stat(pc.id, 'guard_captain', 'respect', 3)
    $ renpy.notify('Gate pass logged.')
    guard_captain "Good. That keeps the line intact."
    $ bond_add_stat(pc.id, 'guard_captain', 'trust', 2)
    return

label CHAR__guard_captain__talk:
    guard_captain "Keep your steps light and your voice lower."
    guard_captain "We keep the line so others can sleep."
    $ guard_captain.mark_as_met()
    return

label CHAR__guard_captain__request_gate_pass:
    guard_captain "I can log a short pass. Do not linger."
    $ flag_set('gate_pass', True)
    $ bond_add_stat(pc.id, 'guard_captain', 'respect', 3)
    $ renpy.notify('Gate pass logged.')
    return

label CHAR__guard_captain__report_a_quiet_route:
    guard_captain "Good. That keeps the line intact."
    $ bond_add_stat(pc.id, 'guard_captain', 'trust', 2)
    return

label CHAR__bard:
    bard "The hall is loud inside, quiet outside. The right tone keeps it that way."
    bard "If you can carry a message, I can teach you a cadence."
    $ bard.mark_as_met()
    bard "Three beats, then a breath. Keep it even."
    $ perk_add('silver_tongue', None)
    $ flag_set('cadence_learned', True)
    return

label CHAR__bard__talk:
    bard "The hall is loud inside, quiet outside. The right tone keeps it that way."
    bard "If you can carry a message, I can teach you a cadence."
    $ bard.mark_as_met()
    return

label CHAR__bard__learn_cadence:
    bard "Three beats, then a breath. Keep it even."
    $ perk_add('silver_tongue', None)
    $ flag_set('cadence_learned', True)
    return

label CHAR__stranger:
    stranger "The city moves when you find the right sound."
    stranger "If you go out, go light."
    $ stranger.mark_as_met()
    return

label CHAR__stranger__talk:
    stranger "The city moves when you find the right sound."
    stranger "If you go out, go light."
    $ stranger.mark_as_met()
    return

label CHAR__warrior:
    "You check your gear and plan your next run."
    return

label CHAR__warrior__talk:
    "You check your gear and plan your next run."
    return

label CHAR__fisherman:
    fisherman "No ships, just wind and rust."
    fisherman "If the sleepers turn, I ring the bell and we all move."
    $ fisherman.mark_as_met()
    return

label CHAR__fisherman__talk:
    fisherman "No ships, just wind and rust."
    fisherman "If the sleepers turn, I ring the bell and we all move."
    $ fisherman.mark_as_met()
    return

label CHAR__blacksmith:
    blacksmith "I can quiet a hinge or wake the block with one tap."
    blacksmith "Bring wood and stone if you want a signal baton."
    $ blacksmith.mark_as_met()
    return

label CHAR__blacksmith__talk:
    blacksmith "I can quiet a hinge or wake the block with one tap."
    blacksmith "Bring wood and stone if you want a signal baton."
    $ blacksmith.mark_as_met()
    return

label CHAR__shopkeeper:
    shopkeeper "Take what you need, log what you take."
    $ renpy.store.general_store.interact()
    return

label CHAR__shopkeeper__talk:
    shopkeeper "Take what you need, log what you take."
    $ renpy.store.general_store.interact()
    return

label CHAR__scholar:
    scholar "If we can chart the patterns, we can predict the drift."
    return

label CHAR__scholar__talk:
    scholar "If we can chart the patterns, we can predict the drift."
    return

label CHAR__priestess:
    priestess "Slow breaths. Clean hands. That keeps people alive."
    priestess "If you feel sick, tell me before you go out."
    $ priestess.mark_as_met()
    priestess "Hold still."
    $ status_remove('flu')
    $ renpy.notify('You feel steadier.')
    return

label CHAR__priestess__talk:
    priestess "Slow breaths. Clean hands. That keeps people alive."
    priestess "If you feel sick, tell me before you go out."
    $ priestess.mark_as_met()
    return

label CHAR__priestess__checkup:
    priestess "Hold still."
    $ status_remove('flu')
    $ renpy.notify('You feel steadier.')
    return

label CHAR__orphan:
    orphan "You look like you can move fast."
    orphan "If you ever need a shortcut, I know one."
    $ orphan.mark_as_met()
    return

label CHAR__orphan__talk:
    orphan "You look like you can move fast."
    orphan "If you ever need a shortcut, I know one."
    $ orphan.mark_as_met()
    return

label CHAR__mayor:
    mayor "You made it in. Good. We need fast legs and calm voices."
    mayor "The signal from the old tower keeps repeating."
    $ mayor.mark_as_met()
    pc "If you need someone fast, I can run it."
    mayor "Then take this route map and head to the Broadcast Tower when ready."
    $ mayor.items.append(Item("Safe Route Map", "Marked safe corridors and quiet zones."))
    $ flag_set('long_dawn', True)
    $ bond_add_stat(pc.id, 'mayor', 'trust', 5)
    mayor "It started three nights ago. Same pattern, same hour."
    mayor "If we can shape it, we can move the sleepers away from the walls."
    return

label CHAR__mayor__talk:
    mayor "You made it in. Good. We need fast legs and calm voices."
    mayor "The signal from the old tower keeps repeating."
    $ mayor.mark_as_met()
    return

label CHAR__mayor__offer_help:
    pc "If you need someone fast, I can run it."
    mayor "Then take this route map and head to the Broadcast Tower when ready."
    $ mayor.items.append(Item("Safe Route Map", "Marked safe corridors and quiet zones."))
    $ flag_set('long_dawn', True)
    $ bond_add_stat(pc.id, 'mayor', 'trust', 5)
    return

label CHAR__mayor__ask_about_the_signal:
    mayor "It started three nights ago. Same pattern, same hour."
    mayor "If we can shape it, we can move the sleepers away from the walls."
    return

label CHAR__innkeeper:
    innkeeper "You look tired. Sit, eat, then move."
    innkeeper "If you need a cot, I can find a corner."
    $ innkeeper.mark_as_met()
    return

label CHAR__innkeeper__talk:
    innkeeper "You look tired. Sit, eat, then move."
    innkeeper "If you need a cot, I can find a corner."
    $ innkeeper.mark_as_met()
    return

label CHOICE__ranger_ask_for_a_guide:
    ranger "Fine. Keep up and keep quiet."
    $ companion_add('ranger')
    $ flag_set('scout_joined', True)
    $ bond_add_stat(pc.id, 'ranger', 'trust', 3)
    return

label CHOICE__ranger_ask_to_part_ways:
    ranger "Understood. Stay safe."
    $ companion_remove('ranger')
    $ flag_set('scout_joined', False)
    return

label CHOICE__guard_captain_request_gate_pass:
    guard_captain "I can log a short pass. Do not linger."
    $ flag_set('gate_pass', True)
    $ bond_add_stat(pc.id, 'guard_captain', 'respect', 3)
    $ renpy.notify('Gate pass logged.')
    return

label CHOICE__guard_captain_report_a_quiet_route:
    guard_captain "Good. That keeps the line intact."
    $ bond_add_stat(pc.id, 'guard_captain', 'trust', 2)
    return

label CHOICE__bard_learn_cadence:
    bard "Three beats, then a breath. Keep it even."
    $ perk_add('silver_tongue', None)
    $ flag_set('cadence_learned', True)
    return

label CHOICE__priestess_checkup:
    priestess "Hold still."
    $ status_remove('flu')
    $ renpy.notify('You feel steadier.')
    return

label CHOICE__mayor_offer_help:
    pc "If you need someone fast, I can run it."
    mayor "Then take this route map and head to the Broadcast Tower when ready."
    $ mayor.items.append(Item("Safe Route Map", "Marked safe corridors and quiet zones."))
    $ flag_set('long_dawn', True)
    $ bond_add_stat(pc.id, 'mayor', 'trust', 5)
    return

label CHOICE__mayor_ask_about_the_signal:
    mayor "It started three nights ago. Same pattern, same hour."
    mayor "If we can shape it, we can move the sleepers away from the walls."
    return

label SCENE__warrior__intro:
    $ renpy.store.td_manager.setup(rpg_world.current_location)
    $ flag_set('origin', 'courier')
    $ event_manager.dispatch('GAME_STARTED', origin='courier')
    "You arrive at the Relief Exchange, breath steady, pack light."
    "The settlement needs a runner more than a fighter."
    "Today you carry a message that could change everything."
    $ renpy.jump("world_loop")
    return

label SCENE__scholar__intro:
    $ renpy.store.td_manager.setup(rpg_world.current_location)
    $ flag_set('origin', 'medic')
    $ event_manager.dispatch('GAME_STARTED', origin='medic')
    "The clinic is already awake. You wash your hands and check the supplies."
    "Outside, the sleepers drift past the window like a slow tide."
    "Today you take the first steps toward a cure."
    $ renpy.jump("world_loop")
    return

label SHOP__general_store__flow:
    "\"Check the crate tags before you take anything.\""
    $ renpy.store.general_store.interact()
    return

label SHOP__general_store__talk:
    "\"Check the crate tags before you take anything.\""
    $ renpy.store.general_store.interact()
    return

