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

label LOC__mage_tower_f1__flow:
    pc "The screen is asking for an override."
    pc "If I can pull the data now, maybe I can make it back before the sleepers shift."
    $ renpy.notify('Recovering protocol...')
    $ give_item('broadcast_protocol', 1)
    $ flag_set('protocol_recovered', True)
    return

label LOC__mage_tower_f1__console:
    pc "The screen is asking for an override."
    pc "If I can pull the data now, maybe I can make it back before the sleepers shift."
    $ renpy.notify('Recovering protocol...')
    $ give_item('broadcast_protocol', 1)
    $ flag_set('protocol_recovered', True)
    return

label CHAR__faye:
    faye "You look like you've been breathing too much static. Sit, eat your rations, then move on."
    faye "Space is tight, but I can find a cot if you need to let your frequency drop for a while."
    $ faye.mark_as_met()
    return

label CHAR__faye__talk:
    faye "You look like you've been breathing too much static. Sit, eat your rations, then move on."
    faye "Space is tight, but I can find a cot if you need to let your frequency drop for a while."
    $ faye.mark_as_met()
    return

label CHAR__theo:
    theo "If we can chart the pattern decay of the Spire, we can predict when the next drift will peak."
    theo "History isn't just about what we lost; it's about the frequencies we forgot how to tune into."
    $ theo.mark_as_met()
    return

label CHAR__theo__talk:
    theo "If we can chart the pattern decay of the Spire, we can predict when the next drift will peak."
    theo "History isn't just about what we lost; it's about the frequencies we forgot how to tune into."
    $ theo.mark_as_met()
    return

label CHAR__nia:
    nia "You move like you're wearing heavy boots. You'll wake the whole block up like that."
    nia "If you ever need a route that doesn't involve walking through a drift, I know where the ducts still hold."
    $ nia.mark_as_met()
    return

label CHAR__nia__talk:
    nia "You move like you're wearing heavy boots. You'll wake the whole block up like that."
    nia "If you ever need a route that doesn't involve walking through a drift, I know where the ducts still hold."
    $ nia.mark_as_met()
    return

label CHAR__hakim:
    hakim "Every nutrition bar is counted. Every medical kit is signed for by the Coordinator."
    hakim "If you want to barter, bring something the settlement can actually use—scrap tech, clean water, or data logs."
    $ hakim.mark_as_met()
    return

label CHAR__hakim__talk:
    hakim "Every nutrition bar is counted. Every medical kit is signed for by the Coordinator."
    hakim "If you want to barter, bring something the settlement can actually use—scrap tech, clean water, or data logs."
    $ hakim.mark_as_met()
    return

label CHAR__clerk:
    clerk "Take what you've been rationed for, and make sure you log your exchange in the book. No credit in the Silence."
    $ renpy.store.general_store.interact()
    $ clerk.mark_as_met()
    return

label CHAR__clerk__talk:
    clerk "Take what you've been rationed for, and make sure you log your exchange in the book. No credit in the Silence."
    $ renpy.store.general_store.interact()
    $ clerk.mark_as_met()
    return

label CHAR__greta:
    greta "I can quiet a rusty hinge or wake the whole block with one frequency tap."
    greta "If you're heading out, you'll need a signal baton. Bring me enough scrap wood and stone weights, and I'll rig one for you."
    $ greta.mark_as_met()
    return

label CHAR__greta__talk:
    greta "I can quiet a rusty hinge or wake the whole block with one frequency tap."
    greta "If you're heading out, you'll need a signal baton. Bring me enough scrap wood and stone weights, and I'll rig one for you."
    $ greta.mark_as_met()
    return

label CHAR__lena:
    lena "The sleepers follow sound more than sight. If you're going to survive the forest edge, you need to learn to walk between the beats."
    lena "Keep your steps light and your voice softer. The drift is sensitive today."
    $ lena.mark_as_met()
    lena "Fine. But if you start humming or dragging your feet, I'm leaving you as bait. Keep up."
    $ companion_add('lena')
    $ flag_set('scout_joined', True)
    $ bond_add_stat(pc.id, 'lena', 'trust', 3)
    lena "Understood. I'll recalibrate the markers on my way back. Stay quiet."
    $ companion_remove('lena')
    $ flag_set('scout_joined', False)
    return

label CHAR__lena__talk:
    lena "The sleepers follow sound more than sight. If you're going to survive the forest edge, you need to learn to walk between the beats."
    lena "Keep your steps light and your voice softer. The drift is sensitive today."
    $ lena.mark_as_met()
    return

label CHAR__lena__ask_for_a_guide:
    lena "Fine. But if you start humming or dragging your feet, I'm leaving you as bait. Keep up."
    $ companion_add('lena')
    $ flag_set('scout_joined', True)
    $ bond_add_stat(pc.id, 'lena', 'trust', 3)
    return

label CHAR__lena__ask_to_part_ways:
    lena "Understood. I'll recalibrate the markers on my way back. Stay quiet."
    $ companion_remove('lena')
    $ flag_set('scout_joined', False)
    return

label CHAR__mara:
    mara "You made it in. Good. We need fast legs and even calmer voices."
    mara "The signal from the old Spire is shifting. If we don't adapt the perimeter sonar, the sleepers will be at the gates by dawn."
    $ mara.mark_as_met()
    pc "If you need someone fast, I can run the perimeter."
    mara "Good. We're blind out there. Take this route map—it's marked with the latest safe-zones and frequency dead-spots."
    $ mara.items.append(Item("Safe Route Map", "Marked safe corridors and quiet zones."))
    $ quest_manager.start_quest("long_dawn")
    $ bond_add_stat(pc.id, 'mara', 'trust', 5)
    mara "It started three nights ago. A rhythmic, low-frequency pulse."
    mara "It's drawing the sleepers in from the plains. If we can't find a way to shift the frequency, we'll be overrun by the week's end."
    pc "I have the protocol drive from the Spire. The lobby was full of them—it was like walking through a dream where nobody breathes."
    mara "Every year we lose more to the drift. This drive... it's the first real data we've had on their resonance in a decade."
    mara "Give me a moment to patch it into the main console. We need to see if we can broadcast a counter-tone."
    $ renpy.notify('Deciphering protocol...')
    $ give_item('protocol_deciphered', 1)
    $ flag_set('protocol_deciphered', True)
    mara "There. It's not just a signal. It's a bridge. We can lead them away, or we can shut their cognitive resonance down entirely."
    return

label CHAR__mara__talk:
    mara "You made it in. Good. We need fast legs and even calmer voices."
    mara "The signal from the old Spire is shifting. If we don't adapt the perimeter sonar, the sleepers will be at the gates by dawn."
    $ mara.mark_as_met()
    return

label CHAR__mara__offer_help:
    pc "If you need someone fast, I can run the perimeter."
    mara "Good. We're blind out there. Take this route map—it's marked with the latest safe-zones and frequency dead-spots."
    $ mara.items.append(Item("Safe Route Map", "Marked safe corridors and quiet zones."))
    $ quest_manager.start_quest("long_dawn")
    $ bond_add_stat(pc.id, 'mara', 'trust', 5)
    return

label CHAR__mara__ask_about_the_signal:
    mara "It started three nights ago. A rhythmic, low-frequency pulse."
    mara "It's drawing the sleepers in from the plains. If we can't find a way to shift the frequency, we'll be overrun by the week's end."
    return

label CHAR__mara__report_on_spire:
    pc "I have the protocol drive from the Spire. The lobby was full of them—it was like walking through a dream where nobody breathes."
    mara "Every year we lose more to the drift. This drive... it's the first real data we've had on their resonance in a decade."
    mara "Give me a moment to patch it into the main console. We need to see if we can broadcast a counter-tone."
    $ renpy.notify('Deciphering protocol...')
    $ give_item('protocol_deciphered', 1)
    $ flag_set('protocol_deciphered', True)
    mara "There. It's not just a signal. It's a bridge. We can lead them away, or we can shut their cognitive resonance down entirely."
    return

label CHAR__jace:
    jace "No ships coming in, just the wind and the sound of the structural rust groaning."
    jace "If the tide brings in a drift from the Spire, I ring the chime and we all evacuate to the higher districts."
    $ jace.mark_as_met()
    return

label CHAR__jace__talk:
    jace "No ships coming in, just the wind and the sound of the structural rust groaning."
    jace "If the tide brings in a drift from the Spire, I ring the chime and we all evacuate to the higher districts."
    $ jace.mark_as_met()
    return

label CHAR__ash:
    ash "The city isn't dead. It's just listening for the right frequency to scream."
    ash "If you go out into the drift, go light. The Silence doesn't like heavy footsteps."
    $ ash.mark_as_met()
    return

label CHAR__ash__talk:
    ash "The city isn't dead. It's just listening for the right frequency to scream."
    ash "If you go out into the drift, go light. The Silence doesn't like heavy footsteps."
    $ ash.mark_as_met()
    return

label CHAR__rafi:
    rafi "Keep your steps light and your voice lower. The fence only holds if the noise stays inside."
    rafi "We keep the line so others can sleep without waking up as one of them."
    $ rafi.mark_as_met()
    rafi "I can log a short-term pass. If the sensors pick up a spike in your frequency, don't expect us to open the gate when you come back."
    $ flag_set('gate_pass', True)
    $ bond_add_stat(pc.id, 'rafi', 'respect', 3)
    $ renpy.notify('Gate pass logged.')
    rafi "Good. Every quiet route is a lifeline. I'll update the patrol logs."
    $ bond_add_stat(pc.id, 'rafi', 'trust', 2)
    return

label CHAR__rafi__talk:
    rafi "Keep your steps light and your voice lower. The fence only holds if the noise stays inside."
    rafi "We keep the line so others can sleep without waking up as one of them."
    $ rafi.mark_as_met()
    return

label CHAR__rafi__request_gate_pass:
    rafi "I can log a short-term pass. If the sensors pick up a spike in your frequency, don't expect us to open the gate when you come back."
    $ flag_set('gate_pass', True)
    $ bond_add_stat(pc.id, 'rafi', 'respect', 3)
    $ renpy.notify('Gate pass logged.')
    return

label CHAR__rafi__report_a_quiet_route:
    rafi "Good. Every quiet route is a lifeline. I'll update the patrol logs."
    $ bond_add_stat(pc.id, 'rafi', 'trust', 2)
    return

label CHAR__imani:
    imani "We balance the data points: food, water, and Silence. If any one drops, the settlement falls."
    imani "If you've been outside, report any changes in the sleeper patterns immediately. Every pulse counts."
    $ imani.mark_as_met()
    return

label CHAR__imani__talk:
    imani "We balance the data points: food, water, and Silence. If any one drops, the settlement falls."
    imani "If you've been outside, report any changes in the sleeper patterns immediately. Every pulse counts."
    $ imani.mark_as_met()
    return

label CHAR__kael:
    kael "Don't just stand there making noise. Noise is death."
    kael "Unless you're making it to clear a path. You looking for a piece of the next breach?"
    $ kael.mark_as_met()
    kael "You don't clear them all. You find the resonance point, hit it hard, and run through the gap before they reset."
    kael "It's about timing and weight. Stay heavy, move fast."
    return

label CHAR__kael__talk:
    kael "Don't just stand there making noise. Noise is death."
    kael "Unless you're making it to clear a path. You looking for a piece of the next breach?"
    $ kael.mark_as_met()
    return

label CHAR__kael__ask_about_breaching:
    kael "You don't clear them all. You find the resonance point, hit it hard, and run through the gap before they reset."
    kael "It's about timing and weight. Stay heavy, move fast."
    return

label CHAR__survivor:
    pc "I've walked the quiet roads since the first pattern broke. These 'Sleepers'... they're just echoes of us, waiting for the right tone to wake up."
    return

label CHAR__survivor__talk:
    pc "I've walked the quiet roads since the first pattern broke. These 'Sleepers'... they're just echoes of us, waiting for the right tone to wake up."
    return

label CHAR__jun:
    jun "The hall is loud inside, but the Silence is louder outside. The right cadence keeps the drift from noticing we're still here."
    jun "If you can carry a signal baton, I can teach you a dampening cadence."
    $ jun.mark_as_met()
    jun "Three beats, then a breath. Let the frequency settle between your steps. Keep it even."
    $ perk_add('silver_tongue', None)
    $ flag_set('cadence_learned', True)
    return

label CHAR__jun__talk:
    jun "The hall is loud inside, but the Silence is louder outside. The right cadence keeps the drift from noticing we're still here."
    jun "If you can carry a signal baton, I can teach you a dampening cadence."
    $ jun.mark_as_met()
    return

label CHAR__jun__learn_cadence:
    jun "Three beats, then a breath. Let the frequency settle between your steps. Keep it even."
    $ perk_add('silver_tongue', None)
    $ flag_set('cadence_learned', True)
    return

label CHAR__elena:
    elena "Slow breaths. Keep your hands where I can see them. Clean hands keep people on this side of the pulse."
    elena "If you feel the 'Static' in your head, report to the clinic immediately. We can't afford a sleeper waking up inside the walls."
    $ elena.mark_as_met()
    elena "Hold still. It's just a diagnostic sweep."
    $ status_remove('flu')
    $ renpy.notify('Your cognitive resonance stabilizes.')
    return

label CHAR__elena__talk:
    elena "Slow breaths. Keep your hands where I can see them. Clean hands keep people on this side of the pulse."
    elena "If you feel the 'Static' in your head, report to the clinic immediately. We can't afford a sleeper waking up inside the walls."
    $ elena.mark_as_met()
    return

label CHAR__elena__checkup:
    elena "Hold still. It's just a diagnostic sweep."
    $ status_remove('flu')
    $ renpy.notify('Your cognitive resonance stabilizes.')
    return

label CHOICE__lena_ask_for_a_guide:
    lena "Fine. But if you start humming or dragging your feet, I'm leaving you as bait. Keep up."
    $ companion_add('lena')
    $ flag_set('scout_joined', True)
    $ bond_add_stat(pc.id, 'lena', 'trust', 3)
    return

label CHOICE__lena_ask_to_part_ways:
    lena "Understood. I'll recalibrate the markers on my way back. Stay quiet."
    $ companion_remove('lena')
    $ flag_set('scout_joined', False)
    return

label CHOICE__mara_offer_help:
    pc "If you need someone fast, I can run the perimeter."
    mara "Good. We're blind out there. Take this route map—it's marked with the latest safe-zones and frequency dead-spots."
    $ mara.items.append(Item("Safe Route Map", "Marked safe corridors and quiet zones."))
    $ quest_manager.start_quest("long_dawn")
    $ bond_add_stat(pc.id, 'mara', 'trust', 5)
    return

label CHOICE__mara_ask_about_the_signal:
    mara "It started three nights ago. A rhythmic, low-frequency pulse."
    mara "It's drawing the sleepers in from the plains. If we can't find a way to shift the frequency, we'll be overrun by the week's end."
    return

label CHOICE__mara_report_on_spire:
    pc "I have the protocol drive from the Spire. The lobby was full of them—it was like walking through a dream where nobody breathes."
    mara "Every year we lose more to the drift. This drive... it's the first real data we've had on their resonance in a decade."
    mara "Give me a moment to patch it into the main console. We need to see if we can broadcast a counter-tone."
    $ renpy.notify('Deciphering protocol...')
    $ give_item('protocol_deciphered', 1)
    $ flag_set('protocol_deciphered', True)
    mara "There. It's not just a signal. It's a bridge. We can lead them away, or we can shut their cognitive resonance down entirely."
    return

label CHOICE__rafi_request_gate_pass:
    rafi "I can log a short-term pass. If the sensors pick up a spike in your frequency, don't expect us to open the gate when you come back."
    $ flag_set('gate_pass', True)
    $ bond_add_stat(pc.id, 'rafi', 'respect', 3)
    $ renpy.notify('Gate pass logged.')
    return

label CHOICE__rafi_report_a_quiet_route:
    rafi "Good. Every quiet route is a lifeline. I'll update the patrol logs."
    $ bond_add_stat(pc.id, 'rafi', 'trust', 2)
    return

label CHOICE__kael_ask_about_breaching:
    kael "You don't clear them all. You find the resonance point, hit it hard, and run through the gap before they reset."
    kael "It's about timing and weight. Stay heavy, move fast."
    return

label CHOICE__jun_learn_cadence:
    jun "Three beats, then a breath. Let the frequency settle between your steps. Keep it even."
    $ perk_add('silver_tongue', None)
    $ flag_set('cadence_learned', True)
    return

label CHOICE__elena_checkup:
    elena "Hold still. It's just a diagnostic sweep."
    $ status_remove('flu')
    $ renpy.notify('Your cognitive resonance stabilizes.')
    return

label QUEST__long_dawn__started:
    "The settlement is a cage of routine and fear. You've walked the perimeter until every stone is a familiar face."
    "Mara is watching the horizon again. The signal from the Spire is changing."
    mara "If you're looking for a way out, Survivor, this is it. Go to the Spire."
    $ quest_manager.update_goal('None' if 'None' != 'None' else None, 'call_to_adventure', 'active')
    mara "We need to know what that signal is before the peace breaks. You know the outskirts."
    pc "I'll need more than just hope to survive the night out there. I should gather wood for markers and heat."
    elena "If you seek the Spire, seek the silence first. The sleepers don't hunt; they drift. Use the rhythm, don't break it."
    pc "The district gates are behind me. The air here tastes like static and old rain. No turning back."
    lena "You're either brave or desperate. Keep your light low and your breathing steady."
    pc "The Spire. It looms over the city like a rusted needle. The signal is deafening here."
    pc "The lobby is full of them. Dozens of sleepers, swaying to the tone. I have to move through without waking the storm."
    pc "The drive is humming in my hand. Years of data, frequencies, the heartbeat of the city."
    pc "I have to get this back to Mara. The signal is shifting again—I can hear them stirring behind me."
    pc "I see it now. The city and the silence aren't separate. We just forgot how to listen."
    "The settlement broadcasts the bridge signal."
    "The sleepers don't vanish, but they find peace. They move toward the plains, away from the walls."
    "The Survivor stands at the gate, no longer a scout, but the guide of a new dawn."
    return

label QUEST__long_dawn__call_to_adventure:
    mara "We need to know what that signal is before the peace breaks. You know the outskirts."
    return

label QUEST__long_dawn__refusal_of_the_call:
    pc "I'll need more than just hope to survive the night out there. I should gather wood for markers and heat."
    return

label QUEST__long_dawn__meeting_the_mentor:
    elena "If you seek the Spire, seek the silence first. The sleepers don't hunt; they drift. Use the rhythm, don't break it."
    return

label QUEST__long_dawn__crossing_the_threshold:
    pc "The district gates are behind me. The air here tastes like static and old rain. No turning back."
    return

label QUEST__long_dawn__tests_and_allies:
    lena "You're either brave or desperate. Keep your light low and your breathing steady."
    return

label QUEST__long_dawn__approach_to_the_inmost_cave:
    pc "The Spire. It looms over the city like a rusted needle. The signal is deafening here."
    return

label QUEST__long_dawn__the_ordeal:
    pc "The lobby is full of them. Dozens of sleepers, swaying to the tone. I have to move through without waking the storm."
    return

label QUEST__long_dawn__the_reward:
    pc "The drive is humming in my hand. Years of data, frequencies, the heartbeat of the city."
    return

label QUEST__long_dawn__the_road_back:
    pc "I have to get this back to Mara. The signal is shifting again—I can hear them stirring behind me."
    return

label QUEST__long_dawn__resurrection:
    pc "I see it now. The city and the silence aren't separate. We just forgot how to listen."
    return

label QUEST__long_dawn__passed:
    "The settlement broadcasts the bridge signal."
    "The sleepers don't vanish, but they find peace. They move toward the plains, away from the walls."
    "The Survivor stands at the gate, no longer a scout, but the guide of a new dawn."
    return

label QUEST__silent_tide__started:
    "The docks are slick with salt and memories. You've spent your life watching the waves, but today, they're watching back."
    "A strange, rhythmic humming is vibrating through the wooden piers. It's coming from the deep."
    jace "You feel that too, don't you? The tide is changing."
    $ quest_manager.update_goal('None' if 'None' != 'None' else None, 'call_to_adventure', 'active')
    jace "Beyond the reef, there's a chime that shouldn't be there. I'm too old to chase ghosts, but you... you have the look of someone with nothing to lose."
    pc "I should probably just stick to the nets. I'll need some weights if I'm going to brace the hull against the swell."
    theo "The deep doesn't just hold water, boy. It holds the echoes of what we were. If you follow the chime, listen for the gaps between the notes."
    pc "The salt spray is a mile behind me now. The air is thick with the scent of damp earth and something older. Step by step, the shore fades."
    hakim "Looking for shiny things in dark places? You'll need more than just a sturdy boat for where you're headed."
    pc "The tower stands like a spear thrust into the sky. The humming from the docks is a roar here, vibrating in my very bones."
    pc "Shadows flicker in the corners of my vision. The 'Sleepers' are here, but they aren't sleeping. They're waiting. I must be silent as the tide."
    pc "It's cold, so cold it burns. The relic pulses in rhythm with my own heart. The signal... it's coming from within this."
    pc "The sea is tumultuous, reflecting the storm within the relic. I have to get this to someone who understands what it's whispering."
    mara "You brought it back. I haven't seen one of these since I was a child. The tide isn't coming for us—it's coming *through* us."
    pc "The silence of the deep is no longer a void. It's a bridge. We are the architects of the new world."
    "The Silent Tide has reached its peak."
    "The light from the relic bathes the docks in a soft, blue glow."
    "The Survivor stands by the water, no longer just a watcher of the waves, but their master."
    return

label QUEST__silent_tide__call_to_adventure:
    jace "Beyond the reef, there's a chime that shouldn't be there. I'm too old to chase ghosts, but you... you have the look of someone with nothing to lose."
    return

label QUEST__silent_tide__refusal_of_the_call:
    pc "I should probably just stick to the nets. I'll need some weights if I'm going to brace the hull against the swell."
    return

label QUEST__silent_tide__meeting_the_mentor:
    theo "The deep doesn't just hold water, boy. It holds the echoes of what we were. If you follow the chime, listen for the gaps between the notes."
    return

label QUEST__silent_tide__crossing_the_threshold:
    pc "The salt spray is a mile behind me now. The air is thick with the scent of damp earth and something older. Step by step, the shore fades."
    return

label QUEST__silent_tide__tests_and_allies:
    hakim "Looking for shiny things in dark places? You'll need more than just a sturdy boat for where you're headed."
    return

label QUEST__silent_tide__approach_to_the_inmost_cave:
    pc "The tower stands like a spear thrust into the sky. The humming from the docks is a roar here, vibrating in my very bones."
    return

label QUEST__silent_tide__the_ordeal:
    pc "Shadows flicker in the corners of my vision. The 'Sleepers' are here, but they aren't sleeping. They're waiting. I must be silent as the tide."
    return

label QUEST__silent_tide__the_reward:
    pc "It's cold, so cold it burns. The relic pulses in rhythm with my own heart. The signal... it's coming from within this."
    return

label QUEST__silent_tide__the_road_back:
    pc "The sea is tumultuous, reflecting the storm within the relic. I have to get this to someone who understands what it's whispering."
    return

label QUEST__silent_tide__resurrection:
    mara "You brought it back. I haven't seen one of these since I was a child. The tide isn't coming for us—it's coming *through* us."
    return

label QUEST__silent_tide__return_with_the_elixir:
    pc "The silence of the deep is no longer a void. It's a bridge. We are the architects of the new world."
    return

label QUEST__silent_tide__passed:
    "The Silent Tide has reached its peak."
    "The light from the relic bathes the docks in a soft, blue glow."
    "The Survivor stands by the water, no longer just a watcher of the waves, but their master."
    return

label SHOP__general_store__flow:
    "\"Check the crate tags before you take anything.\""
    $ renpy.store.general_store.interact()
    return

label SHOP__general_store__talk:
    "\"Check the crate tags before you take anything.\""
    $ renpy.store.general_store.interact()
    return

