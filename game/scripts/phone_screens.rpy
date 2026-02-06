# Phone UI System
# A smartphone interface with apps for Contacts, Map, Tasks, Health, and Wardrobe

default phone_current_app = None
default phone_selected_contact = None
default phone_selected_slot = None

# --- PHONE HOME SCREEN ---
screen phone_screen():
    # Phone frame background (transparency handled by router)
    # add Solid("#111118") # Removed to allow dimming from router
    
    frame:
        align (0.5, 0.5)
        background "#1a1a2a"
        xsize 420
        ysize 750
        padding (15, 15)
        
        # Rounded corners effect via nested frame
        vbox:
            spacing 15
            
            # Status Bar
            hbox:
                xfill True
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
                        # Custom Map Button (Full Screen)
                        button:
                            action [Hide("phone_router"), Show("map_browser")]
                            xsize 100
                            ysize 100
                            vbox at phone_visual_hover:
                                align (0.5, 0.5)
                                spacing 8
                                frame:
                                    background "#2a2a3a"
                                    xsize 70
                                    ysize 70
                                    xalign 0.5
                                    text "🗺️" size 35 align (0.5, 0.5)
                                text "Map" size 14 color "#aaa" xalign 0.5
                        use phone_app_icon("📋", "Tasks", "tasks")
                    
                    # Row 2
                    hbox:
                        spacing 30
                        xalign 0.5
                        use phone_app_icon("❤️", "Health", "health")
                        use phone_app_icon("👕", "Wardrobe", "wardrobe")
                    
                    # Row 3
                    hbox:
                        spacing 30
                        xalign 0.5
                        use phone_app_icon("🔍", "Search", "search")
            
            # Home button removed in favor of click-outside-to-close
            null height 20

screen phone_app_icon(icon, label, app_id):
    button:
        action SetVariable("phone_current_app", app_id)
        xsize 100
        ysize 100
        
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

# App Container - Wraps all apps
screen phone_app_container(title):
    # App-specific background
    add Solid("#111118")
    
    frame:
        align (0.5, 0.5)
        background "#1a1a2a"
        xsize 420
        ysize 750
        padding (0, 0)
        
        vbox:
            # App Header
            frame:
                background "#252535"
                xfill True
                ysize 60
                padding (15, 10)
                
                hbox:
                    xfill True
                    textbutton "◀":
                        action SetVariable("phone_current_app", None)
                        text_size 24
                        text_color "#888"
                        text_hover_color "#fff"
                    
                    text title size 22 color "#fff" xalign 0.5 yalign 0.5
                    
                    # Spacer
                    null width 30
            
            # App Content
            frame:
                background "#0d0d15"
                xfill True
                yfill True
                padding (10, 10)
                
                transclude

# --- CONTACTS APP ---
screen phone_contacts_app():
    use phone_app_container("Contacts"):
        if phone_selected_contact:
            use phone_contact_detail
        else:
            use phone_contact_list

screen phone_contact_list():
    viewport:
        mousewheel True
        scrollbars "vertical"
        vbox:
            spacing 5
            for char_id, char in rpg_world.characters.items():
                if char.name != "Player":
                    button:
                        action SetVariable("phone_selected_contact", char)
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
        
        # Actions
        hbox:
            spacing 10
            xalign 0.5
            
            textbutton "💬 Text":
                action Notify("Messaging coming soon!")
                text_size 14
            
            if char.location_id:
                textbutton "📍 Visit":
                    action [Function(rpg_world.move_to, char.location_id), Hide("phone_router"), SetVariable("phone_current_app", None), SetVariable("phone_selected_contact", None)]
                    text_size 14

# --- MAP APP ---
screen phone_map_app():
    use phone_app_container("Map"):
        viewport:
            mousewheel True
            scrollbars "vertical"
            vbox:
                spacing 8
                for loc_id, loc in rpg_world.locations.items():
                    $ is_current = (rpg_world.current_location_id == loc_id)
                    $ can_travel = allow_unvisited_travel or loc.visited or is_current
                    button:
                        action [Function(map_manager.travel_to_location, loc), Hide("phone_router"), SetVariable("phone_current_app", None)]
                        xfill True
                        background ("#2a3a2a" if is_current else "#1a1a25")
                        hover_background "#252535"
                        padding (15, 15)
                        sensitive (not is_current and can_travel)
                        tooltip ("Travel" if can_travel else "Undiscovered")
                        
                        hbox:
                            xfill True
                            vbox:
                                text loc.name size 18 color ("#4f4" if is_current else "#fff")
                                text loc.description size 12 color "#666"
                            
                            if is_current:
                                text "📍" size 24 yalign 0.5
                            elif loc.visited:
                                text "✓" size 18 color "#4a4" yalign 0.5

# --- TASKS APP ---
screen phone_tasks_app():
    use phone_app_container("Tasks"):
        viewport:
            mousewheel True
            scrollbars "vertical"
            vbox:
                spacing 10
                for q in sorted(quest_manager.quests.values(), key=lambda x: (x.state != "active", x.name)):
                    if q.state not in ["unknown"]:
                        frame:
                            background ("#1a2a1a" if q.state == "passed" else "#1a1a25")
                            xfill True
                            padding (12, 12)
                            
                            vbox:
                                spacing 8
                                hbox:
                                    xfill True
                                    text q.name size 16 color ("#4f4" if q.state == "passed" else "#ffd700")
                                    text ("✅" if q.state == "passed" else "🔄") size 16
                                
                                if q.state == "active":
                                    for tick in q.ticks:
                                        if tick.state != "hidden":
                                            hbox:
                                                spacing 8
                                                text ("✓" if tick.state == "complete" else "○") size 14 color ("#4a4" if tick.state == "complete" else "#888")
                                                text tick.name size 13 color ("#666" if tick.state == "complete" else "#ccc")

# --- HEALTH APP ---
screen phone_health_app():
    use phone_app_container("Health"):
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
                    
                    $ stat_list = [("💪", "STR", stats.strength), ("🏹", "DEX", stats.dexterity), ("🧠", "INT", stats.intelligence), ("✨", "CHA", stats.charisma)]
                    for icon, name, val in stat_list:
                        hbox:
                            xfill True
                            text "[icon] [name]" size 15 color "#aaa"
                            text "[val]" size 15 color "#00bfff" xalign 1.0
            
            # Gold
            frame:
                background "#1a1a25"
                xfill True
                padding (15, 15)
                
                hbox:
                    xfill True
                    text "💰 Gold" size 16 color "#ffd700"
                    text "[pc.gold]" size 16 color "#ffd700" xalign 1.0
            
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
screen phone_scavenge_app():
    use phone_app_container("Search"):
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

# --- WARDROBE APP ---
screen phone_wardrobe_app():
    use phone_app_container("Wardrobe"):
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
                            for item in pc.items:
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
                                    
                                    hbox:
                                        xfill True
                                        text item.name size 14 color "#fff"
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
# This screen routes to the current app or shows home
screen phone_router():
    modal True
    zorder 150
    
    # Full-screen dimming background with Click-to-Close
    button:
        action [Hide("phone_router"), SetVariable("phone_current_app", None)]
        background Solid("#000000aa")
        xfill True
        yfill True
        at phone_fade_in
    
    # Wrap content in a frame that applies the transition
    frame at phone_transition:
        background None
        xfill True
        yfill True
        
        if phone_current_app == "contacts":
            use phone_contacts_app
        elif phone_current_app == "map":
            use phone_map_app
        elif phone_current_app == "tasks":
            use phone_tasks_app
        elif phone_current_app == "health":
            use phone_health_app
        elif phone_current_app == "wardrobe":
            use phone_wardrobe_app
        elif phone_current_app == "search":
            use phone_scavenge_app
        else:
            use phone_screen
        
        use phone_equip_picker

# --- TRANSITIONS ---
transform phone_fade_in:
    on show:
        alpha 0.0
        ease 0.3 alpha 1.0
    on hide:
        ease 0.2 alpha 0.0

transform phone_transition:
    on show:
        yoffset 800 alpha 0.0
        easein 0.3 yoffset 0 alpha 1.0
    on hide:
        easeout 0.2 yoffset 800 alpha 0.0

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
