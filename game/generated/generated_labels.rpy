# AUTOMATICALLY GENERATED LABELS - DO NOT EDIT
label LOC__home__flow: # @data/locations/home.md:144
    $ rest(8) # @data/locations/home.md:144
    "You wake to the soft hum of the wall speakers." # @data/locations/home.md:145
    "You check for dust, bruises, and any new marks." # @data/locations/home.md:150
    "All clear." # @data/locations/home.md:151
    return # @data/locations/home.md:151

label LOC__home__bed: # @data/locations/home.md:144
    $ rest(8) # @data/locations/home.md:144
    "You wake to the soft hum of the wall speakers." # @data/locations/home.md:145
    return # @data/locations/home.md:145

label LOC__home__mirror: # @data/locations/home.md:150
    "You check for dust, bruises, and any new marks." # @data/locations/home.md:150
    "All clear." # @data/locations/home.md:151
    return # @data/locations/home.md:151

label LOC__market__flow: # @data/locations/market.md:47
    "A volunteer presses a ration bar into your hand." # @data/locations/market.md:47
    "\"Take it,\" she says. \"You look like you run far.\"" # @data/locations/market.md:48
    $ event_manager.dispatch('ITEM_GAINED', item='ration_bar', total=1) # @data/locations/market.md:49
    $ flag_set('market_swap', True) # @data/locations/market.md:50
    return # @data/locations/market.md:50

label LOC__market__encounter_swap: # @data/locations/market.md:47
    "A volunteer presses a ration bar into your hand." # @data/locations/market.md:47
    "\"Take it,\" she says. \"You look like you run far.\"" # @data/locations/market.md:48
    $ event_manager.dispatch('ITEM_GAINED', item='ration_bar', total=1) # @data/locations/market.md:49
    $ flag_set('market_swap', True) # @data/locations/market.md:50
    return # @data/locations/market.md:50

label LOC__forest_edge__flow: # @data/locations/forest_edge.md:28
    "The fence gives a soft rattle." # @data/locations/forest_edge.md:28
    "A sleeper drifts by, head tilted toward a far away tone." # @data/locations/forest_edge.md:29
    $ event_manager.dispatch('LOCATION_EVENT', location='forest_edge', tag='rattle') # @data/locations/forest_edge.md:30
    $ flag_set('fence_rattle', True) # @data/locations/forest_edge.md:31
    return # @data/locations/forest_edge.md:31

label LOC__forest_edge__encounter_rattle: # @data/locations/forest_edge.md:28
    "The fence gives a soft rattle." # @data/locations/forest_edge.md:28
    "A sleeper drifts by, head tilted toward a far away tone." # @data/locations/forest_edge.md:29
    $ event_manager.dispatch('LOCATION_EVENT', location='forest_edge', tag='rattle') # @data/locations/forest_edge.md:30
    $ flag_set('fence_rattle', True) # @data/locations/forest_edge.md:31
    return # @data/locations/forest_edge.md:31

label LOC__mage_tower_f1__flow: # @data/locations/mage_tower_f1.md:25
    pc "The screen is asking for an override." # @data/locations/mage_tower_f1.md:25
    pc "If I can pull the data now, maybe I can make it back before the sleepers shift." # @data/locations/mage_tower_f1.md:26
    notify 'Recovering protocol...' # @data/locations/mage_tower_f1.md:27
    $ give_item('broadcast_protocol', 1) # @data/locations/mage_tower_f1.md:28
    $ flag_set('protocol_recovered', True) # @data/locations/mage_tower_f1.md:29
    return # @data/locations/mage_tower_f1.md:29

label LOC__mage_tower_f1__console: # @data/locations/mage_tower_f1.md:25
    pc "The screen is asking for an override." # @data/locations/mage_tower_f1.md:25
    pc "If I can pull the data now, maybe I can make it back before the sleepers shift." # @data/locations/mage_tower_f1.md:26
    notify 'Recovering protocol...' # @data/locations/mage_tower_f1.md:27
    $ give_item('broadcast_protocol', 1) # @data/locations/mage_tower_f1.md:28
    $ flag_set('protocol_recovered', True) # @data/locations/mage_tower_f1.md:29
    return # @data/locations/mage_tower_f1.md:29

label CHAR__faye: # @data/characters/faye.md:44
    faye "You look like you've been breathing too much static. Sit, eat your rations, then move on." # @data/characters/faye.md:44
    faye "Space is tight, but I can find a cot if you need to let your frequency drop for a while." # @data/characters/faye.md:45
    $ faye.mark_as_met() # @data/characters/faye.md:46
    return # @data/characters/faye.md:46

label CHAR__faye__talk: # @data/characters/faye.md:44
    faye "You look like you've been breathing too much static. Sit, eat your rations, then move on." # @data/characters/faye.md:44
    faye "Space is tight, but I can find a cot if you need to let your frequency drop for a while." # @data/characters/faye.md:45
    $ faye.mark_as_met() # @data/characters/faye.md:46
    return # @data/characters/faye.md:46

label CHAR__theo: # @data/characters/theo.md:48
    theo "If we can chart the pattern decay of the Spire, we can predict when the next drift will peak." # @data/characters/theo.md:48
    theo "History isn't just about what we lost; it's about the frequencies we forgot how to tune into." # @data/characters/theo.md:49
    $ theo.mark_as_met() # @data/characters/theo.md:50
    return # @data/characters/theo.md:50

label CHAR__theo__talk: # @data/characters/theo.md:48
    theo "If we can chart the pattern decay of the Spire, we can predict when the next drift will peak." # @data/characters/theo.md:48
    theo "History isn't just about what we lost; it's about the frequencies we forgot how to tune into." # @data/characters/theo.md:49
    $ theo.mark_as_met() # @data/characters/theo.md:50
    return # @data/characters/theo.md:50

label CHAR__nia: # @data/characters/nia.md:43
    nia "You move like you're wearing heavy boots. You'll wake the whole block up like that." # @data/characters/nia.md:43
    nia "If you ever need a route that doesn't involve walking through a drift, I know where the ducts still hold." # @data/characters/nia.md:44
    $ nia.mark_as_met() # @data/characters/nia.md:45
    return # @data/characters/nia.md:45

label CHAR__nia__talk: # @data/characters/nia.md:43
    nia "You move like you're wearing heavy boots. You'll wake the whole block up like that." # @data/characters/nia.md:43
    nia "If you ever need a route that doesn't involve walking through a drift, I know where the ducts still hold." # @data/characters/nia.md:44
    $ nia.mark_as_met() # @data/characters/nia.md:45
    return # @data/characters/nia.md:45

label CHAR__hakim: # @data/characters/hakim.md:43
    hakim "Every nutrition bar is counted. Every medical kit is signed for by the Coordinator." # @data/characters/hakim.md:43
    hakim "If you want to barter, bring something the settlement can actually use—scrap tech, clean water, or data logs." # @data/characters/hakim.md:44
    $ hakim.mark_as_met() # @data/characters/hakim.md:45
    return # @data/characters/hakim.md:45

label CHAR__hakim__talk: # @data/characters/hakim.md:43
    hakim "Every nutrition bar is counted. Every medical kit is signed for by the Coordinator." # @data/characters/hakim.md:43
    hakim "If you want to barter, bring something the settlement can actually use—scrap tech, clean water, or data logs." # @data/characters/hakim.md:44
    $ hakim.mark_as_met() # @data/characters/hakim.md:45
    return # @data/characters/hakim.md:45

label CHAR__clerk: # @data/characters/clerk.md:39
    clerk "Take what you've been rationed for, and make sure you log your exchange in the book. No credit in the Silence." # @data/characters/clerk.md:39
    $ renpy.store.general_store.interact() # @data/characters/clerk.md:40
    $ clerk.mark_as_met() # @data/characters/clerk.md:41
    return # @data/characters/clerk.md:41

label CHAR__clerk__talk: # @data/characters/clerk.md:39
    clerk "Take what you've been rationed for, and make sure you log your exchange in the book. No credit in the Silence." # @data/characters/clerk.md:39
    $ renpy.store.general_store.interact() # @data/characters/clerk.md:40
    $ clerk.mark_as_met() # @data/characters/clerk.md:41
    return # @data/characters/clerk.md:41

label CHAR__greta: # @data/characters/greta.md:43
    greta "I can quiet a rusty hinge or wake the whole block with one frequency tap." # @data/characters/greta.md:43
    greta "If you're heading out, you'll need a signal baton. Bring me enough scrap wood and stone weights, and I'll rig one for you." # @data/characters/greta.md:44
    $ greta.mark_as_met() # @data/characters/greta.md:45
    return # @data/characters/greta.md:45

label CHAR__greta__talk: # @data/characters/greta.md:43
    greta "I can quiet a rusty hinge or wake the whole block with one frequency tap." # @data/characters/greta.md:43
    greta "If you're heading out, you'll need a signal baton. Bring me enough scrap wood and stone weights, and I'll rig one for you." # @data/characters/greta.md:44
    $ greta.mark_as_met() # @data/characters/greta.md:45
    return # @data/characters/greta.md:45

label CHAR__lena: # @data/characters/lena.md:44
    lena "The sleepers follow sound more than sight. If you're going to survive the forest edge, you need to learn to walk between the beats." # @data/characters/lena.md:44
    lena "Keep your steps light and your voice softer. The drift is sensitive today." # @data/characters/lena.md:45
    $ lena.mark_as_met() # @data/characters/lena.md:46
    lena "Fine. But if you start humming or dragging your feet, I'm leaving you as bait. Keep up." # @data/characters/lena.md:63
    $ companion_add('lena') # @data/characters/lena.md:64
    $ flag_set('scout_joined', True) # @data/characters/lena.md:65
    $ bond_add_stat(pc.id, 'lena', 'trust', 3) # @data/characters/lena.md:66
    lena "Understood. I'll recalibrate the markers on my way back. Stay quiet." # @data/characters/lena.md:81
    $ companion_remove('lena') # @data/characters/lena.md:82
    $ flag_set('scout_joined', False) # @data/characters/lena.md:83
    return # @data/characters/lena.md:83

label CHAR__lena__talk: # @data/characters/lena.md:44
    lena "The sleepers follow sound more than sight. If you're going to survive the forest edge, you need to learn to walk between the beats." # @data/characters/lena.md:44
    lena "Keep your steps light and your voice softer. The drift is sensitive today." # @data/characters/lena.md:45
    $ lena.mark_as_met() # @data/characters/lena.md:46
    return # @data/characters/lena.md:46

label CHAR__lena__dialogue__ask_for_a_guide: # @data/characters/lena.md:63
    lena "Fine. But if you start humming or dragging your feet, I'm leaving you as bait. Keep up." # @data/characters/lena.md:63
    $ companion_add('lena') # @data/characters/lena.md:64
    $ flag_set('scout_joined', True) # @data/characters/lena.md:65
    $ bond_add_stat(pc.id, 'lena', 'trust', 3) # @data/characters/lena.md:66
    return # @data/characters/lena.md:66

label CHAR__lena__dialogue__ask_to_part_ways: # @data/characters/lena.md:81
    lena "Understood. I'll recalibrate the markers on my way back. Stay quiet." # @data/characters/lena.md:81
    $ companion_remove('lena') # @data/characters/lena.md:82
    $ flag_set('scout_joined', False) # @data/characters/lena.md:83
    return # @data/characters/lena.md:83

label CHAR__mara: # @data/characters/mara.md:45
    mara "You made it in. Good. We need fast legs and even calmer voices." # @data/characters/mara.md:45
    mara "The signal from the old Spire is shifting. If we don't adapt the perimeter sonar, the sleepers will be at the gates by dawn." # @data/characters/mara.md:46
    $ mara.mark_as_met() # @data/characters/mara.md:47
    pc "If you need someone fast, I can run the perimeter." # @data/characters/mara.md:63
    mara "Good. We're blind out there. Take this route map—it's marked with the latest safe-zones and frequency dead-spots." # @data/characters/mara.md:64
    $ mara.items.append(Item("Safe Route Map", "Marked safe corridors and quiet zones.")) # @data/characters/mara.md:65
    $ quest_manager.start_quest("long_dawn") # @data/characters/mara.md:66
    $ bond_add_stat(pc.id, 'mara', 'trust', 5) # @data/characters/mara.md:67
    mara "It started three nights ago. A rhythmic, low-frequency pulse." # @data/characters/mara.md:81
    mara "It's drawing the sleepers in from the plains. If we can't find a way to shift the frequency, we'll be overrun by the week's end." # @data/characters/mara.md:82
    pc "I have the protocol drive from the Spire. The lobby was full of them—it was like walking through a dream where nobody breathes." # @data/characters/mara.md:95
    mara "Every year we lose more to the drift. This drive... it's the first real data we've had on their resonance in a decade." # @data/characters/mara.md:96
    mara "Give me a moment to patch it into the main console. We need to see if we can broadcast a counter-tone." # @data/characters/mara.md:97
    notify 'Deciphering protocol...' # @data/characters/mara.md:98
    $ give_item('protocol_deciphered', 1) # @data/characters/mara.md:99
    $ flag_set('protocol_deciphered', True) # @data/characters/mara.md:100
    mara "There. It's not just a signal. It's a bridge. We can lead them away, or we can shut their cognitive resonance down entirely." # @data/characters/mara.md:101
    return # @data/characters/mara.md:101

label CHAR__mara__talk: # @data/characters/mara.md:45
    mara "You made it in. Good. We need fast legs and even calmer voices." # @data/characters/mara.md:45
    mara "The signal from the old Spire is shifting. If we don't adapt the perimeter sonar, the sleepers will be at the gates by dawn." # @data/characters/mara.md:46
    $ mara.mark_as_met() # @data/characters/mara.md:47
    return # @data/characters/mara.md:47

label CHAR__mara__dialogue__offer_help: # @data/characters/mara.md:63
    pc "If you need someone fast, I can run the perimeter." # @data/characters/mara.md:63
    mara "Good. We're blind out there. Take this route map—it's marked with the latest safe-zones and frequency dead-spots." # @data/characters/mara.md:64
    $ mara.items.append(Item("Safe Route Map", "Marked safe corridors and quiet zones.")) # @data/characters/mara.md:65
    $ quest_manager.start_quest("long_dawn") # @data/characters/mara.md:66
    $ bond_add_stat(pc.id, 'mara', 'trust', 5) # @data/characters/mara.md:67
    return # @data/characters/mara.md:67

label CHAR__mara__dialogue__ask_about_the_signal: # @data/characters/mara.md:81
    mara "It started three nights ago. A rhythmic, low-frequency pulse." # @data/characters/mara.md:81
    mara "It's drawing the sleepers in from the plains. If we can't find a way to shift the frequency, we'll be overrun by the week's end." # @data/characters/mara.md:82
    return # @data/characters/mara.md:82

label CHAR__mara__dialogue__report_on_spire: # @data/characters/mara.md:95
    pc "I have the protocol drive from the Spire. The lobby was full of them—it was like walking through a dream where nobody breathes." # @data/characters/mara.md:95
    mara "Every year we lose more to the drift. This drive... it's the first real data we've had on their resonance in a decade." # @data/characters/mara.md:96
    mara "Give me a moment to patch it into the main console. We need to see if we can broadcast a counter-tone." # @data/characters/mara.md:97
    notify 'Deciphering protocol...' # @data/characters/mara.md:98
    $ give_item('protocol_deciphered', 1) # @data/characters/mara.md:99
    $ flag_set('protocol_deciphered', True) # @data/characters/mara.md:100
    mara "There. It's not just a signal. It's a bridge. We can lead them away, or we can shut their cognitive resonance down entirely." # @data/characters/mara.md:101
    return # @data/characters/mara.md:101

label CHAR__jace: # @data/characters/jace.md:42
    jace "No ships coming in, just the wind and the sound of the structural rust groaning." # @data/characters/jace.md:42
    jace "If the tide brings in a drift from the Spire, I ring the chime and we all evacuate to the higher districts." # @data/characters/jace.md:43
    $ jace.mark_as_met() # @data/characters/jace.md:44
    return # @data/characters/jace.md:44

label CHAR__jace__talk: # @data/characters/jace.md:42
    jace "No ships coming in, just the wind and the sound of the structural rust groaning." # @data/characters/jace.md:42
    jace "If the tide brings in a drift from the Spire, I ring the chime and we all evacuate to the higher districts." # @data/characters/jace.md:43
    $ jace.mark_as_met() # @data/characters/jace.md:44
    return # @data/characters/jace.md:44

label CHAR__ash: # @data/characters/ash.md:43
    ash "The city isn't dead. It's just listening for the right frequency to scream." # @data/characters/ash.md:43
    ash "If you go out into the drift, go light. The Silence doesn't like heavy footsteps." # @data/characters/ash.md:44
    $ ash.mark_as_met() # @data/characters/ash.md:45
    return # @data/characters/ash.md:45

label CHAR__ash__talk: # @data/characters/ash.md:43
    ash "The city isn't dead. It's just listening for the right frequency to scream." # @data/characters/ash.md:43
    ash "If you go out into the drift, go light. The Silence doesn't like heavy footsteps." # @data/characters/ash.md:44
    $ ash.mark_as_met() # @data/characters/ash.md:45
    return # @data/characters/ash.md:45

label CHAR__rafi: # @data/characters/rafi.md:44
    rafi "Keep your steps light and your voice lower. The fence only holds if the noise stays inside." # @data/characters/rafi.md:44
    rafi "We keep the line so others can sleep without waking up as one of them." # @data/characters/rafi.md:45
    $ rafi.mark_as_met() # @data/characters/rafi.md:46
    rafi "I can log a short-term pass. If the sensors pick up a spike in your frequency, don't expect us to open the gate when you come back." # @data/characters/rafi.md:63
    $ flag_set('gate_pass', True) # @data/characters/rafi.md:64
    $ bond_add_stat(pc.id, 'rafi', 'respect', 3) # @data/characters/rafi.md:65
    notify 'Gate pass logged.' # @data/characters/rafi.md:66
    rafi "Good. Every quiet route is a lifeline. I'll update the patrol logs." # @data/characters/rafi.md:80
    $ bond_add_stat(pc.id, 'rafi', 'trust', 2) # @data/characters/rafi.md:81
    return # @data/characters/rafi.md:81

label CHAR__rafi__talk: # @data/characters/rafi.md:44
    rafi "Keep your steps light and your voice lower. The fence only holds if the noise stays inside." # @data/characters/rafi.md:44
    rafi "We keep the line so others can sleep without waking up as one of them." # @data/characters/rafi.md:45
    $ rafi.mark_as_met() # @data/characters/rafi.md:46
    return # @data/characters/rafi.md:46

label CHAR__rafi__dialogue__request_gate_pass: # @data/characters/rafi.md:63
    rafi "I can log a short-term pass. If the sensors pick up a spike in your frequency, don't expect us to open the gate when you come back." # @data/characters/rafi.md:63
    $ flag_set('gate_pass', True) # @data/characters/rafi.md:64
    $ bond_add_stat(pc.id, 'rafi', 'respect', 3) # @data/characters/rafi.md:65
    notify 'Gate pass logged.' # @data/characters/rafi.md:66
    return # @data/characters/rafi.md:66

label CHAR__rafi__dialogue__report_a_quiet_route: # @data/characters/rafi.md:80
    rafi "Good. Every quiet route is a lifeline. I'll update the patrol logs." # @data/characters/rafi.md:80
    $ bond_add_stat(pc.id, 'rafi', 'trust', 2) # @data/characters/rafi.md:81
    return # @data/characters/rafi.md:81

label CHAR__imani: # @data/characters/imani.md:43
    imani "We balance the data points: food, water, and Silence. If any one drops, the settlement falls." # @data/characters/imani.md:43
    imani "If you've been outside, report any changes in the sleeper patterns immediately. Every pulse counts." # @data/characters/imani.md:44
    $ imani.mark_as_met() # @data/characters/imani.md:45
    return # @data/characters/imani.md:45

label CHAR__imani__talk: # @data/characters/imani.md:43
    imani "We balance the data points: food, water, and Silence. If any one drops, the settlement falls." # @data/characters/imani.md:43
    imani "If you've been outside, report any changes in the sleeper patterns immediately. Every pulse counts." # @data/characters/imani.md:44
    $ imani.mark_as_met() # @data/characters/imani.md:45
    return # @data/characters/imani.md:45

label CHAR__kael: # @data/characters/kael.md:50
    kael "Don't just stand there making noise. Noise is death." # @data/characters/kael.md:50
    kael "Unless you're making it to clear a path. You looking for a piece of the next breach?" # @data/characters/kael.md:51
    $ kael.mark_as_met() # @data/characters/kael.md:52
    kael "You don't clear them all. You find the resonance point, hit it hard, and run through the gap before they reset." # @data/characters/kael.md:69
    kael "It's about timing and weight. Stay heavy, move fast." # @data/characters/kael.md:70
    return # @data/characters/kael.md:70

label CHAR__kael__talk: # @data/characters/kael.md:50
    kael "Don't just stand there making noise. Noise is death." # @data/characters/kael.md:50
    kael "Unless you're making it to clear a path. You looking for a piece of the next breach?" # @data/characters/kael.md:51
    $ kael.mark_as_met() # @data/characters/kael.md:52
    return # @data/characters/kael.md:52

label CHAR__kael__dialogue__ask_about_breaching: # @data/characters/kael.md:69
    kael "You don't clear them all. You find the resonance point, hit it hard, and run through the gap before they reset." # @data/characters/kael.md:69
    kael "It's about timing and weight. Stay heavy, move fast." # @data/characters/kael.md:70
    return # @data/characters/kael.md:70

label CHAR__survivor: # @data/characters/survivor.md:50
    pc "I've walked the quiet roads since the first pattern broke. These 'Sleepers'... they're just echoes of us, waiting for the right tone to wake up." # @data/characters/survivor.md:50
    return # @data/characters/survivor.md:50

label CHAR__survivor__talk: # @data/characters/survivor.md:50
    pc "I've walked the quiet roads since the first pattern broke. These 'Sleepers'... they're just echoes of us, waiting for the right tone to wake up." # @data/characters/survivor.md:50
    return # @data/characters/survivor.md:50

label CHAR__jun: # @data/characters/jun.md:43
    jun "The hall is loud inside, but the Silence is louder outside. The right cadence keeps the drift from noticing we're still here." # @data/characters/jun.md:43
    jun "If you can carry a signal baton, I can teach you a dampening cadence." # @data/characters/jun.md:44
    $ jun.mark_as_met() # @data/characters/jun.md:45
    jun "Three beats, then a breath. Let the frequency settle between your steps. Keep it even." # @data/characters/jun.md:62
    $ perk_add('silver_tongue', None) # @data/characters/jun.md:63
    $ flag_set('cadence_learned', True) # @data/characters/jun.md:64
    return # @data/characters/jun.md:64

label CHAR__jun__talk: # @data/characters/jun.md:43
    jun "The hall is loud inside, but the Silence is louder outside. The right cadence keeps the drift from noticing we're still here." # @data/characters/jun.md:43
    jun "If you can carry a signal baton, I can teach you a dampening cadence." # @data/characters/jun.md:44
    $ jun.mark_as_met() # @data/characters/jun.md:45
    return # @data/characters/jun.md:45

label CHAR__jun__dialogue__learn_cadence: # @data/characters/jun.md:62
    jun "Three beats, then a breath. Let the frequency settle between your steps. Keep it even." # @data/characters/jun.md:62
    $ perk_add('silver_tongue', None) # @data/characters/jun.md:63
    $ flag_set('cadence_learned', True) # @data/characters/jun.md:64
    return # @data/characters/jun.md:64

label CHAR__elena: # @data/characters/elena.md:45
    elena "Slow breaths. Keep your hands where I can see them. Clean hands keep people on this side of the pulse." # @data/characters/elena.md:45
    elena "If you feel the 'Static' in your head, report to the clinic immediately. We can't afford a sleeper waking up inside the walls." # @data/characters/elena.md:46
    $ elena.mark_as_met() # @data/characters/elena.md:47
    elena "Hold still. It's just a diagnostic sweep." # @data/characters/elena.md:63
    $ status_remove('flu') # @data/characters/elena.md:64
    notify 'Your cognitive resonance stabilizes.' # @data/characters/elena.md:65
    return # @data/characters/elena.md:65

label GIVE__elena__battery_cell: # @data/characters/elena.md:72
    elena "Good. I can keep the clinic lights stable for another night." # @data/characters/elena.md:72
    $ give_item_between('battery_cell', 'pc', 'elena', 1) # @data/characters/elena.md:73
    notify 'You gave Elena a Battery Cell.' # @data/characters/elena.md:74
    return # @data/characters/elena.md:74

label CHAR__elena__talk: # @data/characters/elena.md:45
    elena "Slow breaths. Keep your hands where I can see them. Clean hands keep people on this side of the pulse." # @data/characters/elena.md:45
    elena "If you feel the 'Static' in your head, report to the clinic immediately. We can't afford a sleeper waking up inside the walls." # @data/characters/elena.md:46
    $ elena.mark_as_met() # @data/characters/elena.md:47
    return # @data/characters/elena.md:47

label CHAR__elena__dialogue__checkup: # @data/characters/elena.md:63
    elena "Hold still. It's just a diagnostic sweep." # @data/characters/elena.md:63
    $ status_remove('flu') # @data/characters/elena.md:64
    notify 'Your cognitive resonance stabilizes.' # @data/characters/elena.md:65
    return # @data/characters/elena.md:65

label ITEM__camp_kit__flow: # @data/items/camp_kit.md:15
    "A compact bedroll, a small firestarter, and a waterproof tarp." # @data/items/camp_kit.md:15
    "Useful for resting when the road is rough." # @data/items/camp_kit.md:16
    return # @data/items/camp_kit.md:16

label ITEM__camp_kit__inspect: # @data/items/camp_kit.md:15
    "A compact bedroll, a small firestarter, and a waterproof tarp." # @data/items/camp_kit.md:15
    "Useful for resting when the road is rough." # @data/items/camp_kit.md:16
    return # @data/items/camp_kit.md:16

label ITEM__utility_pry_bar__flow: # @data/items/utility_pry_bar.md:18
    "Scuffed steel, a wrapped grip, and a few old paint flecks." # @data/items/utility_pry_bar.md:18
    "It is built to endure." # @data/items/utility_pry_bar.md:19
    return # @data/items/utility_pry_bar.md:19

label ITEM__utility_pry_bar__inspect: # @data/items/utility_pry_bar.md:18
    "Scuffed steel, a wrapped grip, and a few old paint flecks." # @data/items/utility_pry_bar.md:18
    "It is built to endure." # @data/items/utility_pry_bar.md:19
    return # @data/items/utility_pry_bar.md:19

label ITEM__ration_bar__flow: # @data/items/ration_bar.md:17
    call show_item('ration_bar') # @data/items/ration_bar.md:17
    "Sealed, {i}sweet{/i}, and a little chalky." # @data/items/ration_bar.md:18
    "It keeps you {i}moving{/i}." # @data/items/ration_bar.md:19
    "Weighs [ration_bar.weight] lbs." # @data/items/ration_bar.md:20
    call hide_item('ration_bar') # @data/items/ration_bar.md:21
    return # @data/items/ration_bar.md:21

label ITEM__ration_bar__inspect: # @data/items/ration_bar.md:17
    call show_item('ration_bar') # @data/items/ration_bar.md:17
    "Sealed, {i}sweet{/i}, and a little chalky." # @data/items/ration_bar.md:18
    "It keeps you {i}moving{/i}." # @data/items/ration_bar.md:19
    "Weighs [ration_bar.weight] lbs." # @data/items/ration_bar.md:20
    call hide_item('ration_bar') # @data/items/ration_bar.md:21
    return # @data/items/ration_bar.md:21

label ITEM__antiseptic_ampoule__flow: # @data/items/antiseptic_ampoule.md:17
    "Clear liquid, faint alcohol smell, and a sterile snap when opened." # @data/items/antiseptic_ampoule.md:17
    return # @data/items/antiseptic_ampoule.md:17

label ITEM__antiseptic_ampoule__inspect: # @data/items/antiseptic_ampoule.md:17
    "Clear liquid, faint alcohol smell, and a sterile snap when opened." # @data/items/antiseptic_ampoule.md:17
    return # @data/items/antiseptic_ampoule.md:17

label QUEST__iron_and_fire__flow: # @data/quests/iron_and_fire.md:10
    "Greta needs wood and stone for a signal baton." # @data/quests/iron_and_fire.md:10
    "That should be enough wood." # @data/quests/iron_and_fire.md:17
    "Got the stone. Back to Greta." # @data/quests/iron_and_fire.md:22
    greta "Not a weapon. A tool. It can guide sleepers away from people." # @data/quests/iron_and_fire.md:27
    "I can help without harming anyone." # @data/quests/iron_and_fire.md:32
    return # @data/quests/iron_and_fire.md:32

label QUEST__iron_and_fire__started: # @data/quests/iron_and_fire.md:10
    "Greta needs wood and stone for a signal baton." # @data/quests/iron_and_fire.md:10
    return # @data/quests/iron_and_fire.md:10

label QUEST__iron_and_fire__goals__collect_wood: # @data/quests/iron_and_fire.md:17
    "That should be enough wood." # @data/quests/iron_and_fire.md:17
    return # @data/quests/iron_and_fire.md:17

label QUEST__iron_and_fire__goals__collect_stone: # @data/quests/iron_and_fire.md:22
    "Got the stone. Back to Greta." # @data/quests/iron_and_fire.md:22
    return # @data/quests/iron_and_fire.md:22

label QUEST__iron_and_fire__goals__craft_a_signal_baton: # @data/quests/iron_and_fire.md:27
    greta "Not a weapon. A tool. It can guide sleepers away from people." # @data/quests/iron_and_fire.md:27
    return # @data/quests/iron_and_fire.md:27

label QUEST__iron_and_fire__passed: # @data/quests/iron_and_fire.md:32
    "I can help without harming anyone." # @data/quests/iron_and_fire.md:32
    return # @data/quests/iron_and_fire.md:32

label QUEST__theo_secret__flow: # @data/quests/theo_secret.md:10
    "Theo believes the first report was archived in a sealed record." # @data/quests/theo_secret.md:10
    "This looks like the first entry. The handwriting is frantic." # @data/quests/theo_secret.md:17
    theo "This confirms the first wave never turned violent." # @data/quests/theo_secret.md:22
    theo "We can use this." # @data/quests/theo_secret.md:23
    return # @data/quests/theo_secret.md:23

label QUEST__theo_secret__started: # @data/quests/theo_secret.md:10
    "Theo believes the first report was archived in a sealed record." # @data/quests/theo_secret.md:10
    return # @data/quests/theo_secret.md:10

label QUEST__theo_secret__goals__find_the_outbreak_note: # @data/quests/theo_secret.md:17
    "This looks like the first entry. The handwriting is frantic." # @data/quests/theo_secret.md:17
    return # @data/quests/theo_secret.md:17

label QUEST__theo_secret__passed: # @data/quests/theo_secret.md:22
    theo "This confirms the first wave never turned violent." # @data/quests/theo_secret.md:22
    theo "We can use this." # @data/quests/theo_secret.md:23
    return # @data/quests/theo_secret.md:23

label QUEST__formal_intro__flow: # @data/quests/formal_intro.md:10
    "Mara asked me to introduce myself to Captain Rafi at the Quarantine Gate." # @data/quests/formal_intro.md:10
    "Mara knows the state of every street and every gate." # @data/quests/formal_intro.md:17
    "This is where the lines are held and checked." # @data/quests/formal_intro.md:22
    "Rafi will decide if I can pass the outer line." # @data/quests/formal_intro.md:27
    "I know who holds the line. Now I can move." # @data/quests/formal_intro.md:32
    return # @data/quests/formal_intro.md:32

label QUEST__formal_intro__started: # @data/quests/formal_intro.md:10
    "Mara asked me to introduce myself to Captain Rafi at the Quarantine Gate." # @data/quests/formal_intro.md:10
    return # @data/quests/formal_intro.md:10

label QUEST__formal_intro__goals__speak_with_coordinator_mara: # @data/quests/formal_intro.md:17
    "Mara knows the state of every street and every gate." # @data/quests/formal_intro.md:17
    return # @data/quests/formal_intro.md:17

label QUEST__formal_intro__goals__visit_the_quarantine_gate: # @data/quests/formal_intro.md:22
    "This is where the lines are held and checked." # @data/quests/formal_intro.md:22
    return # @data/quests/formal_intro.md:22

label QUEST__formal_intro__goals__speak_with_captain_rafi: # @data/quests/formal_intro.md:27
    "Rafi will decide if I can pass the outer line." # @data/quests/formal_intro.md:27
    return # @data/quests/formal_intro.md:27

label QUEST__formal_intro__passed: # @data/quests/formal_intro.md:32
    "I know who holds the line. Now I can move." # @data/quests/formal_intro.md:32
    return # @data/quests/formal_intro.md:32

label QUEST__ration_run__flow: # @data/quests/ration_run.md:11
    "The pantry is low. The shelter needs rations for the sick." # @data/quests/ration_run.md:11
    "I should check the Supply Depot." # @data/quests/ration_run.md:12
    "This is the depot. If any rations remain, they will be here." # @data/quests/ration_run.md:19
    "That should be enough for today." # @data/quests/ration_run.md:24
    "The shelter will eat tonight." # @data/quests/ration_run.md:29
    return # @data/quests/ration_run.md:29

label QUEST__ration_run__started: # @data/quests/ration_run.md:11
    "The pantry is low. The shelter needs rations for the sick." # @data/quests/ration_run.md:11
    "I should check the Supply Depot." # @data/quests/ration_run.md:12
    return # @data/quests/ration_run.md:12

label QUEST__ration_run__goals__visit_the_supply_depot: # @data/quests/ration_run.md:19
    "This is the depot. If any rations remain, they will be here." # @data/quests/ration_run.md:19
    return # @data/quests/ration_run.md:19

label QUEST__ration_run__goals__collect_rations: # @data/quests/ration_run.md:24
    "That should be enough for today." # @data/quests/ration_run.md:24
    return # @data/quests/ration_run.md:24

label QUEST__ration_run__passed: # @data/quests/ration_run.md:29
    "The shelter will eat tonight." # @data/quests/ration_run.md:29
    return # @data/quests/ration_run.md:29

label QUEST__long_dawn__flow: # @data/quests/origins/long_dawn.md:14
    "You check your route map and count the turns to the Broadcast Tower." # @data/quests/origins/long_dawn.md:14
    "A mayor at the line says the signal shifted again and wants anything you learn." # @data/quests/origins/long_dawn.md:15
    "Mara sends a runner to learn why the Broadcast Tower changed its pulse and how to guide the sleepers without harm." # @data/quests/origins/long_dawn.md:16
    "Routines hold the line - logbooks, rations, and quiet rules." # @data/quests/origins/long_dawn.md:23
    "The Spire shifts again. Find the source and bring back a peaceful answer." # @data/quests/origins/long_dawn.md:28
    "The guardhouse warns that noise means danger. Doubt settles in before the gates." # @data/quests/origins/long_dawn.md:33
    "Lena teaches how to step between beats and mark safe lanes without drawing the drift." # @data/quests/origins/long_dawn.md:38
    "You pass the last sandbags and enter the overgrowth, counting your breaths." # @data/quests/origins/long_dawn.md:43
    "Greta needs wood and stone to tune a signal baton that guides instead of harms." # @data/quests/origins/long_dawn.md:48
    "The safe route narrows. The Broadcast Tower rises ahead, low and listening." # @data/quests/origins/long_dawn.md:53
    "Inside the lobby, sleepers drift like fog. You move quietly, hands open, heart steady." # @data/quests/origins/long_dawn.md:58
    "A data drive holds the broadcast pattern. It is warm with the city's memory." # @data/quests/origins/long_dawn.md:63
    "The return run favors patience over speed. Follow the dead zones home." # @data/quests/origins/long_dawn.md:68
    "Mara and Greta test a soft counter-tone. The sleepers turn without panic." # @data/quests/origins/long_dawn.md:73
    "Routes are updated, the new tone is logged, and the city breathes easier." # @data/quests/origins/long_dawn.md:78
    "The Spire remains a warning, but the settlement now knows how to guide the drift without violence." # @data/quests/origins/long_dawn.md:83
    return # @data/quests/origins/long_dawn.md:83

label QUEST__long_dawn__started: # @data/quests/origins/long_dawn.md:14
    "You check your route map and count the turns to the Broadcast Tower." # @data/quests/origins/long_dawn.md:14
    "A mayor at the line says the signal shifted again and wants anything you learn." # @data/quests/origins/long_dawn.md:15
    "Mara sends a runner to learn why the Broadcast Tower changed its pulse and how to guide the sleepers without harm." # @data/quests/origins/long_dawn.md:16
    return # @data/quests/origins/long_dawn.md:16

label QUEST__long_dawn__goals__ordinary_world: # @data/quests/origins/long_dawn.md:23
    "Routines hold the line - logbooks, rations, and quiet rules." # @data/quests/origins/long_dawn.md:23
    return # @data/quests/origins/long_dawn.md:23

label QUEST__long_dawn__goals__call_to_adventure: # @data/quests/origins/long_dawn.md:28
    "The Spire shifts again. Find the source and bring back a peaceful answer." # @data/quests/origins/long_dawn.md:28
    return # @data/quests/origins/long_dawn.md:28

label QUEST__long_dawn__goals__refusal_of_the_call: # @data/quests/origins/long_dawn.md:33
    "The guardhouse warns that noise means danger. Doubt settles in before the gates." # @data/quests/origins/long_dawn.md:33
    return # @data/quests/origins/long_dawn.md:33

label QUEST__long_dawn__goals__meeting_the_mentor: # @data/quests/origins/long_dawn.md:38
    "Lena teaches how to step between beats and mark safe lanes without drawing the drift." # @data/quests/origins/long_dawn.md:38
    return # @data/quests/origins/long_dawn.md:38

label QUEST__long_dawn__goals__crossing_the_threshold: # @data/quests/origins/long_dawn.md:43
    "You pass the last sandbags and enter the overgrowth, counting your breaths." # @data/quests/origins/long_dawn.md:43
    return # @data/quests/origins/long_dawn.md:43

label QUEST__long_dawn__goals__tests_and_allies: # @data/quests/origins/long_dawn.md:48
    "Greta needs wood and stone to tune a signal baton that guides instead of harms." # @data/quests/origins/long_dawn.md:48
    return # @data/quests/origins/long_dawn.md:48

label QUEST__long_dawn__goals__approach: # @data/quests/origins/long_dawn.md:53
    "The safe route narrows. The Broadcast Tower rises ahead, low and listening." # @data/quests/origins/long_dawn.md:53
    return # @data/quests/origins/long_dawn.md:53

label QUEST__long_dawn__goals__ordeal: # @data/quests/origins/long_dawn.md:58
    "Inside the lobby, sleepers drift like fog. You move quietly, hands open, heart steady." # @data/quests/origins/long_dawn.md:58
    return # @data/quests/origins/long_dawn.md:58

label QUEST__long_dawn__goals__reward: # @data/quests/origins/long_dawn.md:63
    "A data drive holds the broadcast pattern. It is warm with the city's memory." # @data/quests/origins/long_dawn.md:63
    return # @data/quests/origins/long_dawn.md:63

label QUEST__long_dawn__goals__the_road_back: # @data/quests/origins/long_dawn.md:68
    "The return run favors patience over speed. Follow the dead zones home." # @data/quests/origins/long_dawn.md:68
    return # @data/quests/origins/long_dawn.md:68

label QUEST__long_dawn__goals__resurrection: # @data/quests/origins/long_dawn.md:73
    "Mara and Greta test a soft counter-tone. The sleepers turn without panic." # @data/quests/origins/long_dawn.md:73
    return # @data/quests/origins/long_dawn.md:73

label QUEST__long_dawn__goals__return_with_the_elixir: # @data/quests/origins/long_dawn.md:78
    "Routes are updated, the new tone is logged, and the city breathes easier." # @data/quests/origins/long_dawn.md:78
    return # @data/quests/origins/long_dawn.md:78

label QUEST__long_dawn__passed: # @data/quests/origins/long_dawn.md:83
    "The Spire remains a warning, but the settlement now knows how to guide the drift without violence." # @data/quests/origins/long_dawn.md:83
    return # @data/quests/origins/long_dawn.md:83

label QUEST__silent_tide__flow: # @data/quests/origins/silent_tide.md:14
    "Your logbook is full of patterns. The sleepers drift to the same pulse each night." # @data/quests/origins/silent_tide.md:14
    "A priestess asks you to keep your steps soft and your breaths even." # @data/quests/origins/silent_tide.md:15
    "The tide of sleepers drifts in a steady pulse, and you set out to learn why." # @data/quests/origins/silent_tide.md:16
    "The archives are quiet, the records heavy, and the city survives by listening more than shouting." # @data/quests/origins/silent_tide.md:23
    "A new rhythm rises from the harbor. Track it before it swells." # @data/quests/origins/silent_tide.md:28
    "Leaving the stacks feels like leaving the past. The risk is real, and so is the fear." # @data/quests/origins/silent_tide.md:33
    "Ash shares drift wisdom - move slow, breathe low, and let the sleepers pass." # @data/quests/origins/silent_tide.md:38
    "You step onto the silent docks, where the tide hums against empty hulls." # @data/quests/origins/silent_tide.md:43
    "Gather quiet testimonies from the tavern and the clinic. The pattern is shared, not owned." # @data/quests/origins/silent_tide.md:48
    "You chart the pulse lines back toward the Broadcast Tower and the old signal corridors." # @data/quests/origins/silent_tide.md:53
    "The stairwell is still. You reach the inner console without waking the drift." # @data/quests/origins/silent_tide.md:58
    "The harmonic key is clear at last - a tone that guides, not commands." # @data/quests/origins/silent_tide.md:63
    "Bring the pattern to the settlement and translate it for those who only hear silence." # @data/quests/origins/silent_tide.md:68
    "The first broadcast is a trial of trust. The tide turns without panic." # @data/quests/origins/silent_tide.md:73
    "You teach the city to listen, and the sleepers to follow a gentler path." # @data/quests/origins/silent_tide.md:78
    "The Silent Tide becomes a living practice, and the city learns to survive without violence." # @data/quests/origins/silent_tide.md:83
    return # @data/quests/origins/silent_tide.md:83

label QUEST__silent_tide__started: # @data/quests/origins/silent_tide.md:14
    "Your logbook is full of patterns. The sleepers drift to the same pulse each night." # @data/quests/origins/silent_tide.md:14
    "A priestess asks you to keep your steps soft and your breaths even." # @data/quests/origins/silent_tide.md:15
    "The tide of sleepers drifts in a steady pulse, and you set out to learn why." # @data/quests/origins/silent_tide.md:16
    return # @data/quests/origins/silent_tide.md:16

label QUEST__silent_tide__goals__ordinary_world: # @data/quests/origins/silent_tide.md:23
    "The archives are quiet, the records heavy, and the city survives by listening more than shouting." # @data/quests/origins/silent_tide.md:23
    return # @data/quests/origins/silent_tide.md:23

label QUEST__silent_tide__goals__call_to_adventure: # @data/quests/origins/silent_tide.md:28
    "A new rhythm rises from the harbor. Track it before it swells." # @data/quests/origins/silent_tide.md:28
    return # @data/quests/origins/silent_tide.md:28

label QUEST__silent_tide__goals__refusal_of_the_call: # @data/quests/origins/silent_tide.md:33
    "Leaving the stacks feels like leaving the past. The risk is real, and so is the fear." # @data/quests/origins/silent_tide.md:33
    return # @data/quests/origins/silent_tide.md:33

label QUEST__silent_tide__goals__meeting_the_mentor: # @data/quests/origins/silent_tide.md:38
    "Ash shares drift wisdom - move slow, breathe low, and let the sleepers pass." # @data/quests/origins/silent_tide.md:38
    return # @data/quests/origins/silent_tide.md:38

label QUEST__silent_tide__goals__crossing_the_threshold: # @data/quests/origins/silent_tide.md:43
    "You step onto the silent docks, where the tide hums against empty hulls." # @data/quests/origins/silent_tide.md:43
    return # @data/quests/origins/silent_tide.md:43

label QUEST__silent_tide__goals__tests_and_allies: # @data/quests/origins/silent_tide.md:48
    "Gather quiet testimonies from the tavern and the clinic. The pattern is shared, not owned." # @data/quests/origins/silent_tide.md:48
    return # @data/quests/origins/silent_tide.md:48

label QUEST__silent_tide__goals__approach: # @data/quests/origins/silent_tide.md:53
    "You chart the pulse lines back toward the Broadcast Tower and the old signal corridors." # @data/quests/origins/silent_tide.md:53
    return # @data/quests/origins/silent_tide.md:53

label QUEST__silent_tide__goals__ordeal: # @data/quests/origins/silent_tide.md:58
    "The stairwell is still. You reach the inner console without waking the drift." # @data/quests/origins/silent_tide.md:58
    return # @data/quests/origins/silent_tide.md:58

label QUEST__silent_tide__goals__reward: # @data/quests/origins/silent_tide.md:63
    "The harmonic key is clear at last - a tone that guides, not commands." # @data/quests/origins/silent_tide.md:63
    return # @data/quests/origins/silent_tide.md:63

label QUEST__silent_tide__goals__the_road_back: # @data/quests/origins/silent_tide.md:68
    "Bring the pattern to the settlement and translate it for those who only hear silence." # @data/quests/origins/silent_tide.md:68
    return # @data/quests/origins/silent_tide.md:68

label QUEST__silent_tide__goals__resurrection: # @data/quests/origins/silent_tide.md:73
    "The first broadcast is a trial of trust. The tide turns without panic." # @data/quests/origins/silent_tide.md:73
    return # @data/quests/origins/silent_tide.md:73

label QUEST__silent_tide__goals__return_with_the_elixir: # @data/quests/origins/silent_tide.md:78
    "You teach the city to listen, and the sleepers to follow a gentler path." # @data/quests/origins/silent_tide.md:78
    return # @data/quests/origins/silent_tide.md:78

label QUEST__silent_tide__passed: # @data/quests/origins/silent_tide.md:83
    "The Silent Tide becomes a living practice, and the city learns to survive without violence." # @data/quests/origins/silent_tide.md:83
    return # @data/quests/origins/silent_tide.md:83

label CHOICE__lena_ask_for_a_guide: # @data/characters/lena.md:63
    lena "Fine. But if you start humming or dragging your feet, I'm leaving you as bait. Keep up." # @data/characters/lena.md:63
    $ companion_add('lena') # @data/characters/lena.md:64
    $ flag_set('scout_joined', True) # @data/characters/lena.md:65
    $ bond_add_stat(pc.id, 'lena', 'trust', 3) # @data/characters/lena.md:66
    return # @data/characters/lena.md:66

label CHOICE__lena_ask_to_part_ways: # @data/characters/lena.md:81
    lena "Understood. I'll recalibrate the markers on my way back. Stay quiet." # @data/characters/lena.md:81
    $ companion_remove('lena') # @data/characters/lena.md:82
    $ flag_set('scout_joined', False) # @data/characters/lena.md:83
    return # @data/characters/lena.md:83

label CHOICE__mara_offer_help: # @data/characters/mara.md:63
    pc "If you need someone fast, I can run the perimeter." # @data/characters/mara.md:63
    mara "Good. We're blind out there. Take this route map—it's marked with the latest safe-zones and frequency dead-spots." # @data/characters/mara.md:64
    $ mara.items.append(Item("Safe Route Map", "Marked safe corridors and quiet zones.")) # @data/characters/mara.md:65
    $ quest_manager.start_quest("long_dawn") # @data/characters/mara.md:66
    $ bond_add_stat(pc.id, 'mara', 'trust', 5) # @data/characters/mara.md:67
    return # @data/characters/mara.md:67

label CHOICE__mara_ask_about_the_signal: # @data/characters/mara.md:81
    mara "It started three nights ago. A rhythmic, low-frequency pulse." # @data/characters/mara.md:81
    mara "It's drawing the sleepers in from the plains. If we can't find a way to shift the frequency, we'll be overrun by the week's end." # @data/characters/mara.md:82
    return # @data/characters/mara.md:82

label CHOICE__mara_report_on_spire: # @data/characters/mara.md:95
    pc "I have the protocol drive from the Spire. The lobby was full of them—it was like walking through a dream where nobody breathes." # @data/characters/mara.md:95
    mara "Every year we lose more to the drift. This drive... it's the first real data we've had on their resonance in a decade." # @data/characters/mara.md:96
    mara "Give me a moment to patch it into the main console. We need to see if we can broadcast a counter-tone." # @data/characters/mara.md:97
    notify 'Deciphering protocol...' # @data/characters/mara.md:98
    $ give_item('protocol_deciphered', 1) # @data/characters/mara.md:99
    $ flag_set('protocol_deciphered', True) # @data/characters/mara.md:100
    mara "There. It's not just a signal. It's a bridge. We can lead them away, or we can shut their cognitive resonance down entirely." # @data/characters/mara.md:101
    return # @data/characters/mara.md:101

label CHOICE__rafi_request_gate_pass: # @data/characters/rafi.md:63
    rafi "I can log a short-term pass. If the sensors pick up a spike in your frequency, don't expect us to open the gate when you come back." # @data/characters/rafi.md:63
    $ flag_set('gate_pass', True) # @data/characters/rafi.md:64
    $ bond_add_stat(pc.id, 'rafi', 'respect', 3) # @data/characters/rafi.md:65
    notify 'Gate pass logged.' # @data/characters/rafi.md:66
    return # @data/characters/rafi.md:66

label CHOICE__rafi_report_a_quiet_route: # @data/characters/rafi.md:80
    rafi "Good. Every quiet route is a lifeline. I'll update the patrol logs." # @data/characters/rafi.md:80
    $ bond_add_stat(pc.id, 'rafi', 'trust', 2) # @data/characters/rafi.md:81
    return # @data/characters/rafi.md:81

label CHOICE__kael_ask_about_breaching: # @data/characters/kael.md:69
    kael "You don't clear them all. You find the resonance point, hit it hard, and run through the gap before they reset." # @data/characters/kael.md:69
    kael "It's about timing and weight. Stay heavy, move fast." # @data/characters/kael.md:70
    return # @data/characters/kael.md:70

label CHOICE__jun_learn_cadence: # @data/characters/jun.md:62
    jun "Three beats, then a breath. Let the frequency settle between your steps. Keep it even." # @data/characters/jun.md:62
    $ perk_add('silver_tongue', None) # @data/characters/jun.md:63
    $ flag_set('cadence_learned', True) # @data/characters/jun.md:64
    return # @data/characters/jun.md:64

label CHOICE__elena_checkup: # @data/characters/elena.md:63
    elena "Hold still. It's just a diagnostic sweep." # @data/characters/elena.md:63
    $ status_remove('flu') # @data/characters/elena.md:64
    notify 'Your cognitive resonance stabilizes.' # @data/characters/elena.md:65
    return # @data/characters/elena.md:65

label SHOP__general_store__flow: # @data/shops/general_store.md:22
    "\"Check the crate tags before you take anything.\"" # @data/shops/general_store.md:22
    $ renpy.store.general_store.interact() # @data/shops/general_store.md:23
    return # @data/shops/general_store.md:23

label SHOP__general_store__talk: # @data/shops/general_store.md:22
    "\"Check the crate tags before you take anything.\"" # @data/shops/general_store.md:22
    $ renpy.store.general_store.interact() # @data/shops/general_store.md:23
    return # @data/shops/general_store.md:23

