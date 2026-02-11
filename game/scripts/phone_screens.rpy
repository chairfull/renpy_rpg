# Phone UI System
# A smartphone interface with apps for Contacts, Map, Tasks, Health, and Wardrobe

default phone_current_app = None
default phone_selected_contact = None
default phone_selected_slot = None
default phone_tasks_filter = "all"
default phone_selected_quest = None
default phone_state = "mini"
default phone_transition = None

init python:
    import math

    def quest_next_tick(q):
        # Prefer active/shown ticks; fall back to first incomplete.
        for t in q.ticks:
            if t.state in ["active", "shown"]:
                return t
        for t in q.ticks:
            if t.state != "complete":
                return t
        return None

    def quest_status_label(q):
        if q.state == "active":
            return "ACTIVE"
        if q.state == "passed":
            return "COMPLETED"
        if q.state == "failed":
            return "FAILED"
        if q.state == "known":
            return "KNOWN"
        return "HIDDEN"

    def _clamp01(val):
        if val < 0.0:
            return 0.0
        if val > 1.0:
            return 1.0
        return val

    def _ease_in_out_sine(val):
        return 0.5 - (math.cos(math.pi * val) * 0.5)

    def _lerp(a, b, t):
        return a + (b - a) * t

    def phone_anim_portrait_open(tf, st, at):
        t = _ease_in_out_sine(_clamp01(st / 0.25))
        tf.xanchor = 0.5
        tf.yanchor = 0.5
        tf.xalign = _lerp(0.06, 0.5, t)
        tf.yalign = _lerp(0.94, 0.5, t)
        tf.zoom = _lerp(0.35, 1.0, t)
        tf.alpha = _lerp(0.0, 1.0, t)
        return 0

    def phone_anim_portrait_close(tf, st, at):
        t = _ease_in_out_sine(_clamp01(st / 0.22))
        tf.xanchor = 0.5
        tf.yanchor = 0.5
        tf.xalign = _lerp(0.5, 0.06, t)
        tf.yalign = _lerp(0.5, 0.94, t)
        tf.zoom = _lerp(1.0, 0.35, t)
        tf.alpha = _lerp(1.0, 0.0, t)
        return 0

    def phone_anim_rotate_to_landscape(tf, st, at):
        t = _ease_in_out_sine(_clamp01(st / 0.25))
        tf.xanchor = 0.5
        tf.yanchor = 0.5
        tf.xalign = 0.5
        tf.yalign = 0.5
        tf.rotate = _lerp(0.0, 90.0, t)
        tf.zoom = _lerp(1.0, 1.15, t)
        tf.alpha = 1.0
        return 0

    def phone_anim_landscape_open(tf, st, at):
        t = _ease_in_out_sine(_clamp01(st / 0.18))
        tf.xanchor = 0.5
        tf.yanchor = 0.5
        tf.xalign = 0.5
        tf.yalign = 0.5
        tf.zoom = _lerp(0.95, 1.0, t)
        tf.alpha = _lerp(0.0, 1.0, t)
        return 0

    def phone_anim_landscape_close(tf, st, at):
        t = _ease_in_out_sine(_clamp01(st / 0.22))
        tf.xanchor = 0.5
        tf.yanchor = 0.5
        tf.xalign = _lerp(0.5, 0.06, t)
        tf.yalign = _lerp(0.5, 0.94, t)
        tf.rotate = _lerp(90.0, 0.0, t)
        tf.zoom = _lerp(1.15, 0.35, t)
        tf.alpha = _lerp(1.0, 0.0, t)
        return 0

# --- PHONE HOME SCREEN ---
screen phone_screen():
    modal True

    frame:
        background "#1a1a2a"
        xsize 520
        ysize 860
        padding (15, 15)
        
        # Rounded corners effect via nested frame
        vbox:
            spacing 15
            
            # Status Bar
            hbox:
                spacing 10
                $ selected = phone_selected_quest or quest_manager.get_active_quest()
                $ next_tick = quest_next_tick(selected) if selected else None
                if next_tick:
                    vbox:
                        spacing 8
                        text "Goal: [next_tick.name]" size 16 color "#c9d3dd"
                        if getattr(next_tick, 'required_value', None) and getattr(next_tick, 'current_value', None) is not None:
                            $ cur = float(next_tick.current_value or 0.0)
                            $ req = float(next_tick.required_value or 1.0)
                            bar value (cur/ max(1.0, req)) xmaximum 420 yminimum 12
                            text "Progress: [int(cur)] / [int(req)]" size 14 color "#c9d3dd"
                        if next_tick.guidance and next_tick.guidance.get('location'):
                            hbox:
                                spacing 8
                                textbutton "Jump To Location":
                                    action [Function(rpg_world.move_to, next_tick.guidance.get('location')), SetVariable('phone_transition', 'to_mini'), SetVariable('phone_selected_quest', None)]
                                    text_size 14
                null xminimum 8
                text "📱" size 18 color "#666"
                text "[time_manager.time_string]" size 18 color "#888" xalign 0.5
                text "🔋" size 18 color "#666" xalign 1.0
            
            # App Grid
            frame:
                background "#0d0d15"
                xfill True
                ysize 550
                padding (20, 30)
                
                vbox:
                    spacing 25
                    xalign 0.5
                    
                    # Row 1
                    hbox:
                        spacing 30
                        xalign 0.5
                        use phone_app_icon("📞", "Contacts", "contacts")
                        use phone_app_icon("🗺️", "Map", "map")
                        use phone_app_icon("📋", "Tasks", "tasks")
                    
                    # Row 2
                    hbox:
                        spacing 30
                        xalign 0.5
                        use phone_app_icon("❤️", "Health", "health")
                        use phone_app_icon("🎒", "Inventory", "inventory")
                        use phone_app_icon("🛡️", "Equipment", "equipment")
                    
                    # Row 3
                    hbox:
                        spacing 30
                        xalign 0.5
                        use phone_app_icon("🔍", "Search", "search")
                        use phone_app_icon("👥", "Team", "companions")
                        use phone_app_icon("📘", "Journal", "journal")
                    
                    # Row 4
                    hbox:
                        spacing 30
                        xalign 0.5
                        use phone_app_icon("🏆", "Achievements", "achievements")
            
            # Home button removed in favor of click-outside-to-close
            null height 20

screen phone_app_icon(icon, label, app_id):
    button:
        action [SetVariable("phone_current_app", app_id), SetVariable("phone_transition", "to_landscape"), SetVariable("phone_selected_quest", None)]
        xsize 100
        ysize 100
        tooltip label
        hovered Function(set_tooltip, label)
        unhovered Function(set_tooltip, None)
        
        vbox at phone_visual_hover:
            align (0.5, 0.5)
            spacing 8
            
            frame:
                background "#2a2a3a"
                xsize 70
                ysize 70
                xalign 0.5
                text icon size 35 align (0.5, 0.5)
            
            text label size 14 color "#aaa" xalign 0.5

# Top navigation icon for landscape mode
screen phone_nav_icon(icon, label, app_id):
    $ is_selected = (phone_current_app == app_id)
    button:
        action SetVariable("phone_current_app", app_id)
        xsize 110
        ysize 56
        tooltip label
        hovered Function(set_tooltip, label)
        unhovered Function(set_tooltip, None)
        background ("#2a2a3a" if is_selected else "#1a1a25")
        hover_background "#2f3442"
        padding (6, 6)
        vbox:
            align (0.5, 0.5)
            spacing 2
            text icon size 22 xalign 0.5
            text label size 12 color ("#ffd700" if is_selected else "#aaa") xalign 0.5

# Landscape phone shell + content
screen phone_landscape_ui():
    frame:
        background "#1a1a2a"
        xsize 1680
        ysize 900
        padding (16, 16)
        
        vbox:
            spacing 12
            
            # Top icon row (single line)
            hbox:
                spacing 12
                xfill True
                use phone_nav_icon("📞", "Contacts", "contacts")
                use phone_nav_icon("🗺️", "Map", "map")
                use phone_nav_icon("📋", "Tasks", "tasks")
                use phone_nav_icon("❤️", "Health", "health")
                use phone_nav_icon("🎒", "Inventory", "inventory")
                use phone_nav_icon("🛡️", "Equipment", "equipment")
                use phone_nav_icon("🔍", "Search", "search")
                use phone_nav_icon("👥", "Team", "companions")
                use phone_nav_icon("📘", "Journal", "journal")
                use phone_nav_icon("🏆", "Achieve", "achievements")
                text "[time_manager.time_string]" size 16 color "#9bb2c7" xalign 1.0
            
            frame:
                background "#0d0d15"
                xfill True
                yfill True
                padding (12, 12)
                use phone_landscape_content

screen phone_landscape_content():
    if not phone_current_app:
        text "Select an app above." size 18 color "#888" xalign 0.5
    elif phone_current_app == "contacts":
        use phone_contacts_content
    elif phone_current_app == "map":
        use phone_map_content
    elif phone_current_app == "tasks":
        use phone_tasks_fullscreen
    elif phone_current_app == "health":
        use phone_health_content
    elif phone_current_app == "search":
        use phone_scavenge_content
    elif phone_current_app == "companions":
        use phone_companions_content
    elif phone_current_app == "inventory":
        use inventory_content
    elif phone_current_app == "equipment":
        use equipment_content
    elif phone_current_app == "stats":
        use phone_health_content
    elif phone_current_app == "journal":
        use journal_content
    elif phone_current_app == "achievements":
        use achievements_content
    else:
        text "App not available." size 18 color "#888" xalign 0.5
# --- CONTACTS APP ---
screen phone_contacts_content():
    if phone_selected_contact:
        use phone_contact_detail
    else:
        use phone_contact_list

screen phone_contact_list():
    default hovered_contact = None
    vbox:
        spacing 8
        if hovered_contact:
            $ bond = bond_manager.get_between(pc.id, hovered_contact.id)
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
                                text "[sname!c]: [sval] ([bond_level(pc.id, hovered_contact.id, sname)])" size 12 color "#ccc"
                    else:
                        text "No bond yet." size 12 color "#666"
        viewport:
            mousewheel True
            scrollbars "vertical"
            vbox:
                spacing 5
                for char_id, char in rpg_world.characters.items():
                    if char.name != "Player":
                        # Show only characters we've met or whose location has been revealed
                        $ met = (str(char_id) in (persistent.met_characters or set()))
                        $ known_loc = (persistent.known_character_locations and str(char_id) in persistent.known_character_locations)
                        if not (met or known_loc):
                            continue
                        button:
                            action SetVariable("phone_selected_contact", char)
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
                                    $ loc_name = rpg_world.locations.get(char.location_id, None)
                                    if loc_name:
                                        text "📍 [loc_name.name]" size 12 color "#666"
                                    elif known_loc:
                                        $ known_id = persistent.known_character_locations.get(str(char_id))
                                        $ known_loc_obj = rpg_world.locations.get(known_id)
                                        if known_loc_obj:
                                            text "📍 [known_loc_obj.name] (reported)" size 12 color "#888"

screen phone_contact_detail():
    $ char = phone_selected_contact
    vbox:
        spacing 15
        
        # Back button
        textbutton "◀ Back":
            action SetVariable("phone_selected_contact", None)
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
                text char.description size 14 color "#888" xalign 0.5 text_align 0.5
                
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
                $ bond = bond_manager.get_between(pc.id, char.id)
                if bond:
                    null height 10
                    text "BOND" size 14 color "#ffd700" xalign 0.5
                    if bond.tags:
                        $ tags_str = ", ".join(sorted(list(bond.tags)))
                        text tags_str size 12 color "#aaa" xalign 0.5
                    if bond.stats:
                        for sname, sval in bond.stats.items():
                            text "[sname!c]: [sval] ([bond_level(pc.id, char.id, sname)])" size 12 color "#ccc" xalign 0.5
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
                    action [Function(rpg_world.move_to, char.location_id), SetVariable("phone_transition", "to_mini"), SetVariable("phone_selected_contact", None)]
                    text_size 14

# --- MAP APP ---
screen phone_map_content():
    use phone_map_menu

# --- TASKS APP (LANDSCAPE CONTENT) ---
screen phone_tasks_fullscreen():
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
                                    action SetVariable("phone_selected_quest", q)
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
            $ selected = phone_selected_quest or quest_manager.get_active_quest()
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
                    text selected.description size 16 color "#c9d3dd"
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
                                    $ loc = rpg_world.locations.get(guidance.get('location')) if guidance.get('location') else None
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

# --- HEALTH APP ---
screen phone_health_content():
    vbox:
        spacing 15
            
        # Vitals Card
        frame:
            background "#1a1a25"
            xfill True
            padding (15, 15)
            
            vbox:
                spacing 10
                text "Vitals" size 18 color "#ffd700"
                
                $ stats = pc.stats
                hbox:
                    xfill True
                    text "❤️ HP" size 16 color "#ff6666"
                    text "[stats.hp] / [stats.max_hp]" size 16 color "#fff" xalign 1.0
                
                bar value stats.hp range stats.max_hp:
                    xfill True
                    ysize 12
                    left_bar Solid("#ff4444")
                    right_bar Solid("#333")
        
        # Stats Card
        frame:
            background "#1a1a25"
            xfill True
            padding (15, 15)
            
            vbox:
                spacing 8
                text "Attributes" size 18 color "#ffd700"
                
                $ stat_list = [("💪", "STR", "strength"), ("🏹", "DEX", "dexterity"), ("🧠", "INT", "intelligence"), ("✨", "CHA", "charisma")]
                for icon, name, key in stat_list:
                    hbox:
                        xfill True
                        text "[icon] [name]" size 15 color "#aaa"
                        text "[pc.get_stat_total(key)]" size 15 color "#00bfff" xalign 1.0
        
        # Gold
        frame:
            background "#1a1a25"
            xfill True
            padding (15, 15)
            
            hbox:
                xfill True
                text "💰 Gold" size 16 color "#ffd700"
                text "[pc.gold]" size 16 color "#ffd700" xalign 1.0
        
        # Perks / Status
        frame:
            background "#1a1a25"
            xfill True
            padding (15, 15)
            
            vbox:
                spacing 6
                text "Perks" size 16 color "#ffd700"
                if pc.active_perks:
                    for p in pc.active_perks:
                        $ perk = perk_manager.get(p["id"])
                        text "[perk.name]" size 14 color "#ccc"
                else:
                    text "None" size 14 color "#666"
                text "Status" size 16 color "#ffd700"
                if pc.active_statuses:
                    for s in pc.active_statuses:
                        $ st = status_manager.get(s["id"])
                        text "[st.name]" size 14 color "#ccc"
                else:
                    text "None" size 14 color "#666"
        
        frame:
            background "#1a1a25"
            xfill True
            padding (15, 15)
            
            hbox:
                spacing 10
                text "Rest" size 16 color "#ffd700"
                textbutton "1h":
                    action Function(rest, 1)
                    text_size 14
                textbutton "8h":
                    action Function(rest, 8)
                    text_size 14

# --- SEARCH APP ---
screen phone_scavenge_content():
    $ loc = rpg_world.current_location
    $ key = f"{loc.id}:{time_manager.day}" if loc else None
    vbox:
        spacing 10
        if not loc:
            text "No location available." size 16 color "#888"
        else:
            text "Location: [loc.name]" size 18 color "#ffd700"
            if not getattr(loc, "scavenge", None):
                text "Nothing useful to find here." size 14 color "#666"
            else:
                if scavenge_history.get(key):
                    text "Already searched here today." size 14 color "#888"
                else:
                    textbutton "Search area":
                        action Function(scavenge_location, loc)
                        text_size 16
                        text_color "#fff"
                viewport:
                    mousewheel True
                    scrollbars "vertical"
                    ysize 400
                    vbox:
                        spacing 6
                        for entry in loc.scavenge:
                            if isinstance(entry, dict):
                                $ item_id = entry.get("item", "?")
                                $ item = item_manager.get(item_id)
                                $ name = item.name if item else item_id
                                $ chance = entry.get("chance", 1.0)
                                $ count = entry.get("count", None)
                                $ lo = entry.get("min", None)
                                $ hi = entry.get("max", None)
                                $ qty = f"{lo}-{hi}" if lo or hi else (str(count) if count else "1")
                                hbox:
                                    xfill True
                                    text name size 14 color "#ddd"
                                    text f"x{qty}" size 14 color "#888" xalign 1.0

# --- COMPANIONS APP ---
screen phone_companions_content():
    vbox:
        spacing 10
        if not party_manager.get_followers():
            text "No companions following you." size 16 color "#888"
        else:
            for c in party_manager.get_followers():
                frame:
                    background "#1a1a25"
                    xfill True
                    padding (10, 8)
                    hbox:
                        xfill True
                        vbox:
                            text c.name size 16 color "#fff"
                            if c.companion_mods:
                                $ mods = ", ".join([f"{k}+{v}" for k, v in c.companion_mods.items()])
                                text mods size 12 color "#aaa"
                        textbutton "Dismiss":
                            action Function(companion_remove, c.id)
                            text_size 14

# --- WARDROBE APP ---
screen phone_wardrobe_content():
    vbox:
        spacing 10
        
        # Equipment Slots
        frame:
            background "#1a1a25"
            xfill True
            padding (12, 12)
            
            vbox:
                spacing 8
                text "Equipped" size 16 color "#ffd700"
                
                $ body_slots = slot_registry.get_slots_for_body(pc.body_type)
                for slot_id in body_slots:
                    $ slot_def = slot_registry.slots.get(slot_id, {})
                    $ equipped = pc.equipped_slots.get(slot_id)
                    hbox:
                        xfill True
                        text slot_def.get("name", slot_id) size 14 color "#888"
                        if equipped:
                            textbutton equipped.name:
                                action Function(pc.unequip, slot_id)
                                text_size 14
                                text_color "#4af"
                        else:
                            text "—" size 14 color "#444" xalign 1.0
        
        # Inventory
        frame:
            background "#1a1a25"
            xfill True
            yfill True
            padding (12, 12)
            
            vbox:
                spacing 5
                text "Inventory" size 16 color "#ffd700"
                
                viewport:
                    mousewheel True
                    scrollbars "vertical"
                    yfill True
                    vbox:
                        spacing 4
                        python:
                            grouped = {}
                            for itm in pc.items:
                                item_id = item_manager.get_id_of(itm)
                                key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
                                if key not in grouped:
                                    label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
                                    grouped[key] = {"item": itm, "qty": 0, "label": label}
                                grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
                        for key, entry in grouped.items():
                            $ item = entry["item"]
                            $ count = entry["qty"]
                            button:
                                xfill True
                                background "#252535"
                                hover_background "#353545"
                                padding (10, 8)
                                
                                # Show equip menu if item has slots
                                if item.equip_slots:
                                    action SetVariable("phone_selected_slot", item)
                                else:
                                    action Notify(f"{item.name}: {item.description}")
                                
                                tooltip item_tooltip_text(item, count)
                                hovered Function(set_tooltip, item_tooltip_text(item, count))
                                unhovered Function(set_tooltip, None)
                                
                                hbox:
                                    xfill True
                                    text "[entry['label']] (x[count])" size 14 color "#fff"
                                    if item.equip_slots:
                                        text "⚔" size 14 color "#4af" xalign 1.0

# Equip slot picker overlay
screen phone_equip_picker():
    if phone_selected_slot:
        modal True
        zorder 152
        
        add Solid("#00000088")
        
        frame:
            align (0.5, 0.5)
            background "#1a1a25"
            padding (20, 20)
            xsize 300
            
            vbox:
                spacing 15
                text "Equip [phone_selected_slot.name] to:" size 18 color "#ffd700" xalign 0.5
                
                vbox:
                    spacing 8
                    for slot_id in phone_selected_slot.equip_slots:
                        $ slot_def = slot_registry.slots.get(slot_id, {})
                        $ can_use = slot_id in slot_registry.get_slots_for_body(pc.body_type)
                        textbutton slot_def.get("name", slot_id):
                            action [Function(pc.equip, phone_selected_slot, slot_id), SetVariable("phone_selected_slot", None), Notify("Equipped!")]
                            sensitive can_use
                            text_size 16
                            text_color ("#fff" if can_use else "#444")
                            xalign 0.5
                
                textbutton "Cancel":
                    action SetVariable("phone_selected_slot", None)
                    text_size 14
                    text_color "#888"
                    xalign 0.5

# --- PHONE ROUTER ---
# New phone state machine: mini -> portrait -> landscape
screen phone_router():
    modal (phone_state != "mini")
    zorder 150

    # Click-outside closes to mini
    if phone_state != "mini" and phone_transition is None and phone_current_app != "map":
        button:
            action SetVariable("phone_transition", "to_mini")
            xfill True
            yfill True

    if phone_transition == "to_portrait":
        use phone_transition_portrait
    elif phone_transition == "to_landscape":
        use phone_transition_landscape
    elif phone_transition == "to_mini":
        use phone_transition_mini
    else:
        if phone_state == "mini":
            use phone_mini_button
        elif phone_state == "portrait":
            fixed:
                xsize 520
                ysize 860
                align (0.5, 0.5)
                at phone_portrait_static
                # Block clicks inside the phone frame so they don't close the phone.
                button:
                    xfill True
                    yfill True
                    background None
                    action NullAction()
                use phone_screen
        elif phone_state == "landscape":
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
                use phone_landscape_ui

    use phone_equip_picker

transform bg_blur:
    blur 10

transform bg_unblur:
    blur 0

screen phone_mini_button():
    button:
        action [Function(renpy.show_layer_at, bg_blur, layer="topdown"), Function(renpy.notify, "Pee"), SetVariable("phone_state", "portrait"), SetVariable("phone_transition", "to_portrait"), SetVariable("phone_current_app", None)]
        align (0.06, 0.94)
        padding (12, 8)
        background Frame(Solid("#0f141bcc"), 8, 8)
        hover_background Frame(Solid("#1b2733"), 8, 8)
        hbox:
            spacing 6
            text "📱" size 18
            text "PHONE" size 14 color "#c9d3dd"

screen phone_transition_portrait():
    fixed:
        xfill True
        yfill True
        fixed:
            xsize 520
            ysize 860
            align (0.5, 0.5)
            at phone_portrait_open
            use phone_screen
    timer 0.26 action [SetVariable("phone_state", "portrait"), SetVariable("phone_transition", None), Function(set_tooltip, None)]

screen phone_transition_landscape():
    fixed:
        xfill True
        yfill True
        # Rotate the portrait phone out with icons
        fixed:
            xsize 520
            ysize 860
            align (0.5, 0.5)
            at phone_rotate_to_landscape
            use phone_screen
    timer 0.26 action [SetVariable("phone_state", "landscape"), SetVariable("phone_transition", None), Function(set_tooltip, None)]

screen phone_transition_mini():
    fixed:
        xfill True
        yfill True
        if phone_state == "landscape":
            fixed:
                xsize 1680
                ysize 900
                align (0.5, 0.5)
                at phone_landscape_close
                use phone_landscape_ui
        else:
            fixed:
                xsize 520
                ysize 860
                align (0.5, 0.5)
                at phone_portrait_close
                use phone_screen
    timer 0.24 action [SetVariable("phone_state", "mini"), SetVariable("phone_transition", None), SetVariable("phone_current_app", None)]

# --- TRANSITIONS ---
transform phone_portrait_open:
    function phone_anim_portrait_open

transform phone_portrait_static:
    anchor (0.5, 0.5)
    xalign 0.5
    yalign 0.5
    zoom 1.0
    alpha 1.0

transform phone_portrait_close:
    function phone_anim_portrait_close

transform phone_rotate_to_landscape:
    function phone_anim_rotate_to_landscape

transform phone_landscape_open:
    function phone_anim_landscape_open

transform phone_landscape_static:
    anchor (0.5, 0.5)
    xalign 0.5
    yalign 0.5
    zoom 1.0
    alpha 1.0

transform phone_landscape_close:
    function phone_anim_landscape_close

# --- HOVER EFFECTS ---
transform phone_visual_hover:
    on idle:
        parallel:
            ease 0.5 matrixcolor HueMatrix(0.0)
        parallel:
            ease 0.3 additive 0.0
    on hover:
        # Transition to opposite hue
        parallel:
            ease 0.5 matrixcolor HueMatrix(180.0)
        
        # Parallel brightness pulse via 'additive' property
        parallel:
            # Initial Flash: Fast up, Slow down
            additive 0.0
            ease 0.15 additive 0.3
            ease 0.4 additive 0.0
            
            block:
                # Loop: Fast up, Slow down
                ease 0.25 additive 0.15
                ease 0.55 additive 0.0
                repeat


# Styles for phone UI
style phone_button:
    background "#2a2a3a"
    hover_background "#3a3a4a"
    padding (15, 10)

style phone_button_text:
    size 16
    color "#ffffff"
