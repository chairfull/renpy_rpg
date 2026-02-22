init -1300 python:
    from classes import MetaMenu
    meta_menu = MetaMenu()
    meta_menu.add_tab("crafting", "🪡", "Craft")
    meta_menu.add_tab("characters", "📞", "Characters")
    meta_menu.add_tab("inventory", "🎒", "Inventory")
    meta_menu.add_tab("quests", "📋", "Quests")
    meta_menu.add_tab("zones", "🗺️", "Locations")
    meta_menu.add_tab("stats", "❤️", "Stats")
    meta_menu.add_tab("perks", "✨", "Perks")

screen meta_menu_mini_button():
    button:
        action [Function(renpy.show_layer_at, bg_blur, layer="topdown"), Function(renpy.notify, "Pee")]
        align (0.06, 0.94)
        padding (12, 8)
        background Frame(Solid("#0f141bcc"), 8, 8)
        hover_background Frame(Solid("#1b2733"), 8, 8)
        hbox:
            spacing 6
            text "📱" size 18
            text "PHONE" size 14 color "#c9d3dd"

screen meta_menu_screen():
    modal (meta_menu.minimised == False) # Only block input when the menu is open
    zorder 150

    # Click-outside closes to mini
    if meta_menu.minimised == False:
        button:
            action Function(meta_menu.close)
            xfill True
            yfill True

    frame:
        background "#1a1a2a"
        xsize 1680
        ysize 900
        padding (16, 16)
        
        vbox:
            spacing 12
            
            hbox:
                spacing 12
                xfill True
                for mm_id in meta_menu.tabs:
                    $ mm_data = meta_menu.tabs[mm_id]
                    textbutton f"{mm_data.emoji} {mm_data.name}" action Function(open_meta_menu, to=mm_id) style "phone_button":
                        if meta_menu.selected == mm_id:
                            background "#3a3a4a"
                        else:
                            background "#2a2a3a"
                        hover_background "#3a3a4a"
                        padding (15, 10)
                        text_size 16
                        text_color "#ffffff"
                text "[time_manager.time_string]" size 16 color "#9bb2c7" xalign 1.0
            
            fixed:
                xsize 1680
                ysize 900
                align (0.5, 0.5)
                at phone_landscape_static
                # Block clicks inside the phone frame so they don't close the phone.
                button:
                    xfill True
                    yfill True
                    background None
                    action NullAction()
                
                if meta_menu.selected:
                    $ mm = meta_menu.tabs[meta_menu.selected]
                    $ mms = mm.screen
                    use expression mms(mm)
                else:
                    text "Select an app above." size 18 color "#888" xalign 0.5

#region Crafting
screen meta_menu_crafting_screen():
    default selected_craft = None
    hbox:
        spacing 20
        frame:
            background "#222"
            xsize 400
            ysize 600
            viewport:
                scrollbars "vertical"
                mousewheel True
                vbox:
                    spacing 5
                    for craft in all_crafts.values():
                        textbutton "[craft.name]":
                            action SetScreenVariable("selected_craft", craft)
                            xfill True
                            background ("#333" if selected_craft == craft else "#111")
                            text_style "inventory_item_text"

        # Crafting details.
        frame:
            background "#222"
            xsize 620
            ysize 600
            padding (20, 20)
            
            if selected_craft:
                vbox:
                    spacing 15
                    text "[selected_craft.name]" size 30 color "#ffd700"
                    
                    text "Requires:" size 24 color "#ffffff"
                    for item, count in selected_craft.inputs.items():
                        # Check count in inventory
                        $ have = player.get_item_count(item)
                        
                        hbox:
                            text "• [itm_name] x[count]" size 20 color ("#50fa7b" if have >= count else "#ff5555")
                            text " (Have [have])" size 18 color "#888"
                            
                    null height 20
                    
                    textbutton "CRAFT":
                        action [Function(craft.craft, player), Function(renpy.restart_interaction)]
                        background "#444" padding (30, 15)
                        text_style "tab_button_text"

            else:
                text "Select a recipe to view details." align (0.5, 0.5) color "#666666"
#endregion

#region Characters
screen meta_menu_characters_screen():
    if selected_character:
        use meta_menu_character_detail_screen
    else:
        use meta_menu_character_list_screen

screen meta_menu_character_list_screen():
    default hovered_contact = None
    vbox:
        spacing 8
        if hovered_contact:
            $ bond = bond_manager.get_between(character.id, hovered_contact.id)
            frame:
                background "#1a1a25"
                xfill True
                padding (10, 8)
                vbox:
                    text "Hover: [hovered_contact.name]" size 14 color "#ffd700"
                    if bond:
                        if bond.tags:
                            $ tags_str = ", ".join(sorted(list(bond.tags)))
                            text "Tags: [tags_str]" size 12 color "#aaa"
                        if bond.stats:
                            for sname, sval in bond.stats.items():
                                text "[sname!c]: [sval] ([bond_level(character.id, hovered_contact.id, sname)])" size 12 color "#ccc"
                    else:
                        text "No bond yet." size 12 color "#666"
        viewport:
            mousewheel True
            scrollbars "vertical"
            vbox:
                spacing 5
                for char_id, char in world.characters.items():
                    if char.name != "Player":
                        # Show only characters we've met or whose location has been revealed
                        $ met = (str(char_id) in (persistent.met_characters or set()))
                        $ known_loc = (persistent.known_character_locations and str(char_id) in persistent.known_character_locations)
                        if not (met or known_loc):
                            continue
                        button:
                            action SetVariable("selected_contact", char)
                            hovered SetVariable("hovered_contact", char)
                            unhovered SetVariable("hovered_contact", None)
                            xfill True
                            background "#1a1a25"
                            hover_background "#252535"
                            padding (15, 12)
                            
                            hbox:
                                spacing 15
                                text "👤" size 30 yalign 0.5
                                vbox:
                                    text char.name size 18 color "#fff"
                                    $ loc_name = world.locations.get(char.location_id, None)
                                    if loc_name:
                                        text "📍 [loc_name.name]" size 12 color "#666"
                                    elif known_loc:
                                        $ known_id = persistent.known_character_locations.get(str(char_id))
                                        $ known_loc_obj = world.locations.get(known_id)
                                        if known_loc_obj:
                                            text "📍 [known_loc_obj.name] (reported)" size 12 color "#888"

screen meta_menu_character_detail_screen():
    $ char = selected_contact
    vbox:
        spacing 15
        
        # Back button
        textbutton "◀ Back":
            action SetVariable("selected_contact", None)
            text_size 16
            text_color "#888"
        
        # Contact Card
        frame:
            background "#1a1a25"
            xfill True
            padding (20, 20)
            
            vbox:
                spacing 10
                xalign 0.5
                
                text "👤" size 60 xalign 0.5
                text char.name size 24 color "#ffd700" xalign 0.5
                text char.desc size 14 color "#888" xalign 0.5 text_align 0.5
                
                null height 10
                
                # Factions
                if char.factions:
                    hbox:
                        xalign 0.5
                        spacing 5
                        for f in list(char.factions)[:3]:
                            frame:
                                background "#333"
                                padding (8, 4)
                                text f size 12 color "#aaa"
                
                # Bond info
                $ bond = bond_manager.get_between(character.id, char.id)
                if bond:
                    null height 10
                    text "BOND" size 14 color "#ffd700" xalign 0.5
                    if bond.tags:
                        $ tags_str = ", ".join(sorted(list(bond.tags)))
                        text tags_str size 12 color "#aaa" xalign 0.5
                    if bond.stats:
                        for sname, sval in bond.stats.items():
                            text "[sname!c]: [sval] ([bond_level(character.id, char.id, sname)])" size 12 color "#ccc" xalign 0.5
                else:
                    null height 10
                    text "No bond yet." size 12 color "#666" xalign 0.5
        
        # Actions
        hbox:
            spacing 10
            xalign 0.5
            
            textbutton "💬 Text":
                action Notify("Messaging coming soon!")
                text_size 14
            
            if char.location_id:
                textbutton "📍 Visit":
                    action [Function(world.move_to, char.location_id), SetVariable("phone_transition", "to_mini"), SetVariable("selected_contact", None)]
                    text_size 14
#endregion

#region Inventory
screen meta_menu_inventory_screen():
    default page = 0
    $ columns = 4
    $ rows = 3
    $ per_page = columns * rows
    $ grid_spacing = 8
    $ cell_size = int(min((1100 - 40 - (columns - 1) * grid_spacing) / columns, (850 - 200 - (rows - 1) * grid_spacing) / rows))
    python:
        entries = build_inventory_entries(character)
        total_pages = max(1, (len(entries) + per_page - 1) // per_page)
        if tab.selected_page >= total_pages:
            tab.selected_page = total_pages - 1
        if tab.selected_page < 0:
            tab.selected_page = 0
        start = tab.selected_page * per_page
        page_entries = entries[start:start + per_page]
        grid_entries = []
        for entry in page_entries:
            item = entry["item"]
            qty = entry["qty"]
            grid_entries.append({
                "item": item,
                "qty": qty,
                "icon": get_item_icon(item),
                "tooltip": item_tooltip_text(item, qty),
                "action": [SetVariable("_return_to_inventory", True), Function(meta_menu.close), Function(queue_inspect_item, item), Return()],
                "sensitive": True,
            })
    frame at inventory_fade:
        background "#222"
        xfill True
        yfill True
        padding (20, 20)
        hbox:
            spacing 20
            xfill True
            yfill True
            
            # Equipped box removed from main inventory; use Equipment tab instead
            
            vbox:
                spacing 12
                xfill True
                yfill True
                $ inv_weight = player.get_total_weight()
                $ weight_max = player.max_weight
                $ slots_used = player.get_used_slots()
                $ slots_max = player.max_slots
                hbox:
                    spacing 20
                    xalign 0.5
                    if weight_max is not None:
                        text "Weight: [inv_weight:.1f] / [weight_max:.1f]" size 16 color "#999"
                    if slots_max is not None:
                        text "Slots: [slots_used] / [slots_max]" size 16 color "#999"
                use inventory_grid(grid_entries, columns=columns, cell_size=cell_size, total_slots=per_page, selected_item=selected_inventory_item, xspacing=grid_spacing, yspacing=grid_spacing)
                if total_pages > 1:
                    hbox:
                        spacing 20
                        xalign 0.5
                        if inventory_page > 0:
                            textbutton "◀ Prev":
                                action SetVariable("inventory_page", max(0, inventory_page - 1))
                                background "#333" hover_background "#555"
                                padding (20, 8)
                        text "Page [inventory_page + 1] / [total_pages]" size 16 color "#ddd"
                        if inventory_page < (total_pages - 1):
                            textbutton "Next ▶":
                                action SetVariable("inventory_page", min(total_pages - 1, inventory_page + 1))
                                background "#333" hover_background "#555"
                                padding (20, 8)
#endregion

#region Quest
screen meta_menu_quests_screen():
    default selected = None
    # Two-column layout
    hbox:
        spacing 20
        xfill True

        # Left: Quest List
        frame:
            background Frame(Solid("#0f141bcc"), 12, 12)
            xsize 560
            yfill True
            padding (16, 16)
            vbox:
                spacing 12
                text "QUESTS" size 20 color "#9bb2c7"
                viewport:
                    mousewheel True
                    scrollbars "vertical"
                    draggable True
                    vbox:
                        spacing 12
                        for q in sorted(quest_manager.quests.values(), key=lambda x: (x.state != "active", x.name)):
                            if q.state in ["active", "known", "passed", "failed"]:
                                $ next_tick = quest_next_tick(q)
                                $ status = quest_status_label(q)
                                $ is_active = (quest_manager.active_quest_id == q.id)
                                # Highlight entry if this quest has the active tick
                                $ entry_bg = ("#223326" if (next_tick and next_tick.state in ['active','shown']) else ("#1a2a1a" if q.state == "passed" else "#151a23"))
                                button:
                                    action SetVariable("selected_equipment_slot", q)
                                    xfill True
                                    background entry_bg
                                    hover_background "#1e2633"
                                    padding (14, 12)
                                    vbox:
                                        spacing 6
                                        hbox:
                                            xfill True
                                            text q.name size 18 color ("#4f4" if q.state == "passed" else "#ffd700")
                                            text status size 12 color ("#4f4" if q.state == "passed" else "#9bb2c7") xalign 1.0
                                        if next_tick:
                                            text "Next: [next_tick.name]" size 14 color "#c9d3dd"
                                            # Show compact progress if tick exposes values
                                            if getattr(next_tick, 'required_value', None) and getattr(next_tick, 'current_value', None) is not None:
                                                $ cur = float(next_tick.current_value or 0.0)
                                                $ req = float(next_tick.required_value or 1.0)
                                                hbox:
                                                    spacing 6
                                                    bar value (cur/ max(1.0, req)) xmaximum 140 yminimum 8
                                                    text "[int(cur)]/[int(req)]" size 12 color "#c9d3dd"
                                        hbox:
                                            xfill True
                                            textbutton "Active":
                                                action Function(quest_manager.set_active_quest, (None if is_active else q.id))
                                                text_size 12
                                                text_color ("#2ac7a7" if is_active else "#ffd700")
                                                xalign 1.0

        # Right: Quest Details
        frame:
            background Frame(Solid("#0f141bcc"), 12, 12)
            xfill True
            yfill True
            padding (18, 16)
            $ selected = selected_quest or quest_manager.get_active_quest()
            if not selected:
                $ active_list = [qq for qq in quest_manager.quests.values() if qq.state in ["active", "known", "passed", "failed"]]
                $ selected = active_list[0] if active_list else None
            if selected:
                $ next_tick = quest_next_tick(selected)
                $ is_active = (quest_manager.active_quest_id == selected.id)
                vbox:
                    spacing 12
                    hbox:
                        xfill True
                        text selected.name size 26 color ("#4f4" if selected.state == "passed" else "#ffd700")
                        text quest_status_label(selected) size 14 color "#9bb2c7" xalign 1.0
                    text selected.desc size 16 color "#c9d3dd"
                    hbox:
                        spacing 12
                        textbutton "Active":
                            action Function(quest_manager.set_active_quest, (None if is_active else selected.id))
                            text_size 14
                            text_color ("#2ac7a7" if is_active else "#ffd700")

                    if next_tick:
                        frame:
                            background "#151a23"
                            xfill True
                            padding (12, 10)
                            vbox:
                                spacing 6
                                text "Next Objective" size 14 color "#9bb2c7"
                                text next_tick.name size 18 color "#ffffff"
                                if next_tick.required_value > 1:
                                    text "Progress: [next_tick.current_value]/[next_tick.required_value]" size 13 color "#9bb2c7"
                                $ guidance = quest_manager.get_current_guidance()
                                if guidance and guidance.get('quest') == selected.id and guidance.get('tick') == next_tick.id:
                                    $ loc = world.locations.get(guidance.get('location')) if guidance.get('location') else None
                                    if loc:
                                        hbox:
                                            spacing 8
                                            text "Guidance:" size 13 color "#9bb2c7"
                                            text loc.name size 13 color "#fff"
                                            textbutton "Show on Map":
                                                action Function(map_manager.select_location, loc)
                                                text_size 13

                    text "Objectives" size 16 color "#9bb2c7"
                    vbox:
                        spacing 6
                        for t in selected.ticks:
                            if t.state != "hidden":
                                hbox:
                                    spacing 8
                                    text ("✓" if t.state == "complete" else "○") size 14 color ("#4a4" if t.state == "complete" else "#888")
                                    text t.name size 14 color ("#666" if t.state == "complete" else "#ccc")
            else:
                text "No quests to show yet." size 18 color "#888" xalign 0.5
#endregion

#region Zones
screen meta_menu_zones_screen():
    default mode = "overworld"
    default overworld = None
    default location = None
    default area = None
    frame:
        background "#0f141b"
        xfill True
        yfill True
        padding (16, 16)

        vbox:
            spacing 12

            # Top mode buttons
            hbox:
                spacing 10
                xalign 0.5
                button:
                    action SetScreenVariable("mode", "overworld")
                    background ("#2a2a3a" if mode == "overworld" else "#1a1a25")
                    hover_background "#2f3442"
                    padding (12, 8)
                    vbox:
                        spacing 2
                        text "OVERWORLD" size 18 color "#fff"
                        text (overworld.name or "-") size 12 color "#aaa"
                button:
                    action SetScreenVariable("mode", "location")
                    background ("#2a2a3a" if mode == "location" else "#1a1a25")
                    hover_background "#2f3442"
                    padding (12, 8)
                    vbox:
                        spacing 2
                        text "LOCATION" size 18 color "#fff"
                        text (location.name or "-") size 12 color "#aaa"
                button:
                    action SetScreenVariable("mode", "areas")
                    background ("#2a2a3a" if mode == "areas" else "#1a1a25")
                    hover_background "#2f3442"
                    padding (12, 8)
                    vbox:
                        spacing 2
                        text "AREAS" size 18 color "#fff"
                        text (area.name or "-") size 12 color "#aaa"

            # Grid
            frame:
                background "#111722"
                xfill True
                yfill True
                padding (12, 12)
                viewport:
                    mousewheel True
                    scrollbars "vertical"
                    draggable True
                    vpgrid:
                        cols 3
                        xspacing 10
                        yspacing 10
                        xfill True
                        python:
                            zones = list(all_zones.items())
                            if mode == "overworld":
                                zones = []
                            elif mode == "location":
                                zones = [l for l in locs if l.ltype not in ("room", "floor") and not l.parent_id]
                            else:
                                # areas: rooms under selected location (any depth)
                                if mmtab.location:
                                    zones = [l for l in zones if l.ltype == "room" and _loc_is_descendant(l, location)]
                                else:
                                    zones = []
                            zones = sorted(zones, key=lambda l: l.name)
                        for zn in zones:
                            $ can_travel = allow_unvisited_travel or zn.visited or (zone == zn)
                            button:
                                xfill True
                                ysize 110
                                background ("#1f2a38" if can_travel else "#151a22")
                                hover_background "#2a3646"
                                padding (10, 8)
                                action [
                                    If(mode == "overworld", SetScreenVariable("overworld", zone), NullAction()),
                                    If(mode == "location", SetVariable("location", zone), NullAction()),
                                    If(mode == "areas", SetVariable("area", zone), NullAction()),
                                    If(mode == "areas", Function(map_manager.select_location, zone), NullAction())
                                ]
                                vbox:
                                    spacing 4
                                    text "[zone.name]" size 16 color ("#fff" if can_travel else "#666")
                                    text "[zone.subtype!u]" size 12 color "#888"

    if selected:
        use meta_menu_zone_info_popup(selected)

# Location Info Popup Screen
screen meta_menu_zone_info_popup(zone):
    # Click outside to close - full screen button behind the popup
    button:
        xfill True
        yfill True
        action Function(map_manager.close_location_popup)
        background "#00000066"
    
    # Popup Frame
    frame:
        align (0.5, 0.5)
        xsize 500
        background "#1a1a2e"
        padding (30, 30)
        
        vbox:
            spacing 15
            
            # Header
            hbox:
                xfill True
                text "[zone.name]" size 28 color "#ffd700" bold True
                textbutton "✕":
                    align (1.0, 0.0)
                    action Function(map_manager.close_location_popup)
                    text_size 24
                    text_color "#888"
                    text_hover_color "#fff"
            
            # Type Badge
            frame:
                background "#333"
                padding (10, 5)
                text "[zone.subtype!u]" size 14 color "#aaa"
            
            null height 5
            
            # Description
            text "[zone.desc]" size 18 color "#ccc" text_align 0.0
            
            null height 15
            
            $ can_travel = allow_unvisited_travel or zone.visited or (player.zone == zone)
            if not can_travel:
                text "Undiscovered" size 16 color "#ff6666"

            # Travel Button
            textbutton "🚶 TRAVEL HERE":
                xfill True
                action Function(map_manager.travel_to_location, zone)
                sensitive can_travel
                background ("#2d5a27" if can_travel else "#222")
                hover_background ("#3d7a37" if can_travel else "#333")
                padding (20, 15)
                text_size 22
                text_color ("#fff" if can_travel else "#666")
                text_xalign 0.5
#endregion

#region Stats
screen meta_menu_stats_screen():
    $ states = player.get_traits(Stat)
    hbox:
        spacing 40
        xalign 0.5
        vbox:
            spacing 20
            frame:
                background "#222"
                padding (20, 20)
                xsize 300
                ysize 400
                vbox:
                    align (0.5, 0.5)
                    text "👤" size 150 xalign 0.5
                    text "[player.name]" size 30 xalign 0.5 color "#ffd700"
            frame:
                background "#222"
                padding (20, 20)
                xsize 300
                vbox:
                    spacing 5
                    # text "Gold: [character.gold]" size 22 color "#ffd700"
                    null height 10
                    $ outfit_name = getattr(player, "current_outfit", "Default")
                    text "Outfit: [outfit_name.capitalize()]" size 20 color "#ffffff"
                    for part, item in player.equipped_items.items():
                        text "[part.capitalize()]: [item.name]" size 16 color "#cccccc"
        frame:
            background "#222"
            padding (30, 30)
            xsize 500
            vbox:
                spacing 15
                text "Attributes" size 28 color "#ffd700"
                $ stats = player.stats
                python:
                    # Filter out HP stats and anything else starting with underscore
                    display_stats = sorted([s for s in stats.keys() if s not in ('hp', 'max_hp') and not s.startswith('_')])
                
                if not display_stats:
                    text "No special attributes" size 18 italic True color "#666"
                else:
                    for s_key in display_stats:
                        $ sname = get_stat_display_name(s_key)
                        $ sicon = get_stat_icon(s_key)
                        $ total = player.get_stat_total(s_key)
                        $ mod = player.get_stat_mod(s_key)
                        hbox:
                            xfill True
                            text "[sicon] [sname]" size 22 color "#ffffff"
                            text "[total] ([mod:+])" size 22 color "#00bfff" xalign 1.0

                null height 20
                text "Vitals" size 28 color "#ffd700"
                vbox:
                    spacing 5
                text "HP: [stats.hp] / [stats.max_hp]" size 18 color "#ffffff"
                bar value stats.hp range stats.max_hp:
                    xsize 440
                    ysize 20
                    left_bar Solid("#ff4444")
                    right_bar Solid("#333")
                
                null height 10
                text "Perks" size 22 color "#ffd700"
                if character.active_perks:
                    for p in character.active_perks:
                        $ perk = perk_manager.get(p["id"])
                        text "[perk.name]" size 16 color "#ccc"
                else:
                    text "None" size 16 color "#666"
                
                text "Status Effects" size 22 color "#ffd700"
                if character.active_statuses:
                    for s in character.active_statuses:
                        $ st = status_manager.get(s["id"])
                        text "[st.name]" size 16 color "#ccc"
                else:
                    text "None" size 16 color "#666"
#endregion

#region Perks
screen meta_menu_perks_screen():
    $ perks = character.get_traits(Perk)
    vbox:
        spacing 10
        xfill True
        yfill True
        if not perks:
            text "No perks acquired." size 16 color "#888"
        else:
            for perk_id in perks:
                $ p = perk_manager.perks.get(perk_id)
                if not p:
                    continue
                frame:
                    background "#1a1a25"
                    xfill True
                    padding (10, 8)
                    hbox:
                        xfill True
                        vbox:
                            text p.name size 16 color "#fff"
                            if p.desc:
                                text p.desc size 12 color "#aaa"
                        textbutton "Remove":
                            action Function(perk_remove, perk_id)
                            text_size 14
#endregion