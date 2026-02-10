default meta_menu_tab = "inventory"
default selected_inventory_item = None
default inventory_page = 0
default selected_quest = None
default selected_recipe = None
default journal_tab = "notes"
default selected_note = None
default selected_person = None
default quick_loot_tags = ["consumable", "food", "medical", "ammo", "currency", "component", "material"]
default quest_filter = "active"

# Functions moved to game/python/inventory_utils.py (Actually implemented below for now)
init python:
    def get_stat_icon(stat_name):
        icons = {
            "strength": "💪",
            "dexterity": "🏹",
            "intelligence": "🧠",
            "charisma": "✨",
            "perception": "👁️",
            "luck": "🍀",
            "willpower": "🛡️",
            "agility": "👟",
            "constitution": "🔋",
            "stamina": "🏃",
            "stealth": "👤",
            "hacking": "⌨️",
            "engineering": "🔧",
            "medical": "💊"
        }
        return icons.get(stat_name.lower(), "📊")

    def get_stat_display_name(stat_name):
        # Handle snake_case and capitalize
        return stat_name.replace("_", " ").title()


transform inventory_icon_idle:
    anchor (0.5, 0.5)
    linear 0.12 zoom 1.0 rotate 0.0

transform inventory_icon_hover:
    anchor (0.5, 0.5)
    zoom 1.0
    rotate 0.0
    parallel:
        block:
            ease 0.18 zoom 1.06
            ease 0.22 zoom 1.0
            repeat

transform inventory_fade:
    on show:
        alpha 0.0
        easein 0.15 alpha 1.0
    on hide:
        easeout 0.15 alpha 0.0
    parallel:
        block:
            ease 0.25 rotate 6.0
            ease 0.25 rotate -6.0
            repeat

screen meta_menu():
    tag menu
    on "show" action Function(set_tooltip, None)
    on "hide" action Function(set_tooltip, None)
    add "#0c0c0c"
    
    # Outer Container
    vbox:
        align (0.5, 0.5)
        xsize 1100
        ysize 850
        spacing 20
        
        # Tabs Header
        hbox:
            spacing 10
            xalign 0.5
            
            textbutton "Inventory":
                action SetVariable("meta_menu_tab", "inventory")
                style "tab_button"
                text_style "tab_button_text"
                selected (meta_menu_tab == "inventory")
                tooltip "View and manage items"
                hovered Function(set_tooltip, "View and manage items")
                unhovered Function(set_tooltip, None)
            
            textbutton "Stats":
                action SetVariable("meta_menu_tab", "stats")
                style "tab_button"
                text_style "tab_button_text"
                selected (meta_menu_tab == "stats")
                tooltip "Character stats and attributes"
                hovered Function(set_tooltip, "Character stats and attributes")
                unhovered Function(set_tooltip, None)
            
            textbutton "Crafting":
                action SetVariable("meta_menu_tab", "crafting")
                style "tab_button"
                text_style "tab_button_text"
                selected (meta_menu_tab == "crafting")
                tooltip "Combine items into new ones"
                hovered Function(set_tooltip, "Combine items into new ones")
                unhovered Function(set_tooltip, None)
            
            textbutton "Journal":
                action SetVariable("meta_menu_tab", "journal")
                style "tab_button"
                text_style "tab_button_text"
                selected (meta_menu_tab == "journal")
                tooltip "Quests, notes, and people"
                hovered Function(set_tooltip, "Quests, notes, and people")
                unhovered Function(set_tooltip, None)
            
            textbutton "🏆":
                action SetVariable("meta_menu_tab", "achievements")
                style "tab_button"
                text_style "tab_button_text"
                selected (meta_menu_tab == "achievements")
                tooltip "Unlocked achievements"
                hovered Function(set_tooltip, "Unlocked achievements")
                unhovered Function(set_tooltip, None)

        # Main Content Area
        frame:
            background "#1a1a1a"
            xfill True
            yfill True
            padding (20, 20)
            
            if meta_menu_tab == "inventory":
                use inventory_content
            elif meta_menu_tab == "stats":
                use stats_content
            elif meta_menu_tab == "crafting":
                use crafting_content
            elif meta_menu_tab == "journal":
                use journal_content
            elif meta_menu_tab == "achievements":
                use achievements_content

        # Footer
        textbutton "Close":
            action Return()
            xalign 0.5
            padding (20, 10)
            background "#444"

screen item_inspect_image():
    zorder 200
    frame:
        at item_popup_bounce
        xalign 0.5
        xsize 520
        ysize 360
        background "#111a"
        padding (20, 20)
        vbox:
            spacing 10
            if item_inspect_title:
                text "[item_inspect_title]" size 22 color "#ffd700" xalign 0.5
            if item_inspect_image:
                add item_inspect_image xalign 0.5 yalign 0.5
            else:
                text "No image available." size 16 color "#999" xalign 0.5

screen inventory_grid(entries, columns=5, cell_size=110, total_slots=None, selected_item=None, show_qty=True, slot_image="images/gui/inventory_slot.webp", empty_image="images/gui/inventory_slot_empty.webp", icon_scale=0.8, xspacing=8, yspacing=8):
    default hover_idx = None
    $ _entries = entries or []
    $ _total = total_slots if total_slots is not None else len(_entries)
    $ _total = max(_total, len(_entries))
    $ _icon_size = int(cell_size * icon_scale)
    $ _slot_bg = slot_image if renpy.loadable(slot_image) else None
    $ _empty_bg = empty_image if renpy.loadable(empty_image) else None
    $ _grid_w = columns * cell_size + (columns - 1) * xspacing
    $ _grid_h = ((_total + columns - 1) // columns) * cell_size + ((max(1, (_total + columns - 1) // columns) - 1) * yspacing)
    vpgrid:
        cols columns
        xspacing xspacing
        yspacing yspacing
        draggable False
        mousewheel False
        xsize _grid_w
        ysize _grid_h
        xalign 0.5
        yalign 0.5
        for idx in range(_total):
            if idx < len(_entries):
                $ e = _entries[idx]
                $ itm = e.get("item")
                $ qty = e.get("qty", 1)
                $ icon = e.get("icon") or get_item_icon(itm) or "images/items/unknown.webp"
                $ action = e.get("action") or NullAction()
                $ sensitive = e.get("sensitive", True)
                $ tip = e.get("tooltip")
                $ is_selected = (selected_item is not None and itm == selected_item)
                $ _alpha = 0.45 if not sensitive else 1.0
                button:
                    xsize cell_size
                    ysize cell_size
                    background None
                    action action
                    sensitive sensitive
                    tooltip tip
                    hovered [SetScreenVariable("hover_idx", idx), Function(set_tooltip, tip, True)]
                    unhovered [SetScreenVariable("hover_idx", None), Function(set_tooltip, None, True)]
                    focus_mask None
                    at phone_visual_hover
                    
                    if _slot_bg:
                        add _slot_bg xysize (cell_size, cell_size)
                    else:
                        add Solid("#2b2b2b") xysize (cell_size, cell_size)
                    
                    if icon:
                        $ _icon_at = inventory_icon_hover if hover_idx == idx else inventory_icon_idle
                        add icon:
                            xalign 0.5
                            yalign 0.5
                            xysize (_icon_size, _icon_size)
                            fit "contain"
                            alpha _alpha
                            at _icon_at
                    if not sensitive:
                        add Solid("#00000066")
                    
                    if show_qty and qty > 1:
                        text "[qty]":
                            align (0.88, 0.88)
                            size 18
                            color "#ffffff"
                            outlines text_outline_fx("#ffffff")
                    
                    if is_selected:
                        add Solid("#ffffff22")
            else:
                frame:
                    xsize cell_size
                    ysize cell_size
                    background None
                    if _empty_bg:
                        add _empty_bg xysize (cell_size, cell_size)
                    else:
                        add Solid("#1f1f1f") xysize (cell_size, cell_size)

screen inventory_content():
    on "show" action Function(set_tooltip, None)
    $ columns = 4
    $ rows = 3
    $ per_page = columns * rows
    $ grid_spacing = 8
    $ cell_size = int(min((1100 - 40 - (columns - 1) * grid_spacing) / columns, (850 - 200 - (rows - 1) * grid_spacing) / rows))
    python:
        entries = build_inventory_entries(pc)
        total_pages = max(1, (len(entries) + per_page - 1) // per_page)
        if store.inventory_page >= total_pages:
            store.inventory_page = total_pages - 1
        if store.inventory_page < 0:
            store.inventory_page = 0
        start = store.inventory_page * per_page
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
                "action": [SetVariable("_return_to_inventory", True), SetVariable("phone_transition", "to_mini"), Function(queue_inspect_item, item), Return()],
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
            
            frame:
                background "#1a1a25"
                xsize 320
                yfill True
                padding (14, 14)
                vbox:
                    spacing 10
                    text "Equipped" size 18 color "#ffd700"
                    $ body_slots = slot_registry.get_slots_for_body(pc.body_type)
                    $ equipped_any = False
                    for slot_id in body_slots:
                        $ item = pc.equipped_slots.get(slot_id)
                        if item:
                            $ equipped_any = True
                            $ slot_def = slot_registry.slots.get(slot_id, {})
                            hbox:
                                spacing 8
                                text slot_def.get("name", slot_id) size 14 color "#aaa"
                                text item.name size 14 color "#fff" xalign 1.0
                    if not equipped_any:
                        text "Nothing equipped" size 14 color "#666"
            
            vbox:
                spacing 12
                xfill True
                yfill True
                $ inv_weight = pc.get_total_weight()
                $ weight_max = pc.max_weight
                $ slots_used = pc.get_used_slots()
                $ slots_max = pc.max_slots
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

screen stats_content():
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
                    text "[pc.name]" size 30 xalign 0.5 color "#ffd700"
            frame:
                background "#222"
                padding (20, 20)
                xsize 300
                vbox:
                    spacing 5
                    text "Gold: [pc.gold]" size 22 color "#ffd700"
                    null height 10
                    $ outfit_name = getattr(pc, "current_outfit", "Default")
                    text "Outfit: [outfit_name.capitalize()]" size 20 color "#ffffff"
                    for part, item in pc.equipped_items.items():
                        text "[part.capitalize()]: [item.name]" size 16 color "#cccccc"
        frame:
            background "#222"
            padding (30, 30)
            xsize 500
            vbox:
                spacing 15
                text "Attributes" size 28 color "#ffd700"
                $ stats = pc.stats
                python:
                    # Filter out HP stats and anything else starting with underscore
                    display_stats = sorted([s for s in stats.keys() if s not in ('hp', 'max_hp') and not s.startswith('_')])
                
                if not display_stats:
                    text "No special attributes" size 18 italic True color "#666"
                else:
                    for s_key in display_stats:
                        $ sname = get_stat_display_name(s_key)
                        $ sicon = get_stat_icon(s_key)
                        $ total = pc.get_stat_total(s_key)
                        $ mod = pc.get_stat_mod(s_key)
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
                if pc.active_perks:
                    for p in pc.active_perks:
                        $ perk = perk_manager.get(p["id"])
                        text "[perk.name]" size 16 color "#ccc"
                else:
                    text "None" size 16 color "#666"
                
                text "Status Effects" size 22 color "#ffd700"
                if pc.active_statuses:
                    for s in pc.active_statuses:
                        $ st = status_manager.get(s["id"])
                        text "[st.name]" size 16 color "#ccc"
                else:
                    text "None" size 16 color "#666"

screen journal_content():
    vbox:
        spacing 10
        xfill True
        yfill True
        # Sub-tabs
        hbox:
            spacing 10
            xalign 0.5
            textbutton "Notes":
                action SetVariable("journal_tab", "notes")
                style "tab_button"
                text_style "tab_button_text"
                selected (journal_tab == "notes")
            textbutton "People":
                action SetVariable("journal_tab", "people")
                style "tab_button"
                text_style "tab_button_text"
                selected (journal_tab == "people")
        
        null height 10

        if journal_tab == "notes":
            use notes_sub_content
        elif journal_tab == "people":
            use people_sub_content
screen notes_sub_content():
    hbox:
        spacing 20
        xfill True
        yfill True
        # Note List
        frame:
            background "#222"
            xsize 520
            yfill True
            viewport:
                scrollbars "vertical"
                mousewheel True
                vbox:
                    spacing 5
                    for note in wiki_manager.get_unlocked_notes():
                        textbutton "[note.name]":
                            action SetVariable("selected_note", note)
                            xfill True
                            background ("#333" if globals().get("selected_note") == note else "#111")
                            text_style "inventory_item_text"

        # Note Details
        frame:
            background "#222"
            xfill True
            yfill True
            padding (20, 20)
            
            if globals().get("selected_note"):
                $ n = selected_note
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    vbox:
                        spacing 10
                        text "[n.name]" size 30 color "#ffd700"
                        text "[n.content]" size 22 color "#fff"
            else:
                text "Select a note to read." align (0.5, 0.5) color "#666666"

screen people_sub_content():
    hbox:
        spacing 20
        xfill True
        yfill True
        # People List
        frame:
            background "#222"
            xsize 520
            yfill True
            viewport:
                scrollbars "vertical"
                mousewheel True
                vbox:
                    spacing 5
                    for name, desc in wiki_manager.met_list:
                        textbutton "[name]":
                            action SetVariable("selected_person", name)
                            xfill True
                            background ("#333" if globals().get("selected_person") == name else "#111")
                            text_style "inventory_item_text"

        # People Details
        frame:
            background "#222"
            xfill True
            yfill True
            padding (20, 20)
            
            if globals().get("selected_person"):
                $ pname = selected_person
                $ desc = wiki_manager.entries.get(pname, "")
                vbox:
                    spacing 10
                    text "[pname]" size 30 color "#ffd700"
                    text "[desc]" size 22 color "#fff"
            else:
                text "Select a person to view details." align (0.5, 0.5) color "#666666"

screen crafting_content():
    hbox:
        spacing 20
        # Recipe List
        frame:
            background "#222"
            xsize 400
            ysize 600
            viewport:
                scrollbars "vertical"
                mousewheel True
                vbox:
                    spacing 5
                    for recipe in crafting_manager.get_all():
                        textbutton "[recipe.name]":
                            action SetVariable("selected_recipe", recipe)
                            xfill True
                            background ("#333" if globals().get("selected_recipe") == recipe else "#111")
                            text_style "inventory_item_text"

        # Recipe Details
        frame:
            background "#222"
            xsize 620
            ysize 600
            padding (20, 20)
            
            if globals().get("selected_recipe"):
                $ rec = selected_recipe
                vbox:
                    spacing 15
                    text "[rec.name]" size 30 color "#ffd700"
                    
                    text "Requires:" size 24 color "#ffffff"
                    for i_id, count in rec.inputs.items():
                        $ itm = item_manager.get(i_id)
                        $ itm_name = itm.name if itm else i_id
                        # Check count in inventory
                        $ have = pc.get_item_count(item_id=i_id)
                        
                        hbox:
                            text "• [itm_name] x[count]" size 20 color ("#50fa7b" if have >= count else "#ff5555")
                            text " (Have [have])" size 18 color "#888"
                            
                    null height 20
                    
                    textbutton "CRAFT":
                        action [Function(crafting_manager.craft, rec, pc), Function(renpy.restart_interaction)]
                        background "#444" padding (30, 15)
                        text_style "tab_button_text"

            else:
                text "Select a recipe to view details." align (0.5, 0.5) color "#666666"

style tab_button:
    background "#333"
    hover_background "#555"
    selected_background "#ffd700"
    padding (12, 8)
    xsize 160

style tab_button_text:
    size 20
    color "#ffffff"
    selected_color "#000000"

screen inventory_screen():
    on "show" action [SetVariable("phone_current_app", "inventory"), SetVariable("phone_transition", "to_landscape")]
    if phone_state == "mini" and phone_transition is None:
        timer 0.01 action Return()
    use phone_router

style inventory_item_text:
    size 20
    color "#ffffff"

style quest_list_text:
    size 18
    color "#eee"
    insensitive_color "#666"
    selected_color "#ffd700"

# --- TRANSFORMATIONS ---
transform glide_up:
    on show:
        alpha 0.0 yoffset 300 zoom 0.8
        parallel:
            easein 0.6 alpha 1.0
        parallel:
            easein 0.7 yoffset 0
        parallel:
            easein 0.8 zoom 1.0
    on hide:
        parallel:
            easeout 0.4 alpha 0.0
        parallel:
            easeout 0.5 yoffset 100

transform char_menu_fade:
    on show:
        alpha 0.0
        easein 0.2 alpha 1.0
    on hide:
        easeout 0.2 alpha 0.0

transform char_buttons_rise:
    on show:
        alpha 0.0 yoffset 80
        easeout 0.25 alpha 1.0 yoffset 0
    on hide:
        easein 0.15 alpha 0.0 yoffset 40

transform char_panel_fade:
    on show:
        alpha 0.0
        easein 0.2 alpha 1.0
    on hide:
        easeout 0.2 alpha 0.0

# --- CHARACTER INTERACTION SCREEN ---
default char_interaction_state = "menu"
default char_interaction_pending_label = None

init python:
    def char_interaction_set_state(state):
        store.char_interaction_state = state
        try:
            renpy.restart_interaction()
        except Exception:
            pass

    def char_interaction_queue_label(label_name):
        if not label_name:
            return
        try:
            set_tooltip(None, True)
        except Exception:
            pass
        store.char_interaction_pending_label = label_name
        try:
            renpy.hide_screen("char_interaction_menu")
            renpy.restart_interaction()
        except Exception:
            pass

screen char_interaction_menu(char, show_preview=True, show_backdrop=True):
    modal True
    zorder 150
    tag menu
    
    # Everything wrapped in a fixed block
    fixed at char_menu_fade:
        # Background dismissal
        $ _bg = "#00000099" if show_backdrop else "#00000055"
        $ _dismiss_state = "menu" if char_interaction_state in ("talk", "give") else "exit"
        button:
            action Function(char_interaction_set_state, _dismiss_state)
            background Solid(_bg)
            at phone_visual_hover
        
        # Names (Bottom)
        text "[pc.name!u]":
            align (0.08, 0.92)
            size 36
            color "#e6edf5"
            outlines text_outline_fx("#e6edf5")
        text "[char.name!u]":
            align (0.92, 0.92)
            size 36
            color "#e6edf5"
            outlines text_outline_fx("#e6edf5")
        
        # Attributes (Right - Upper)
        frame:
            align (0.78, 0.35)
            background None
            padding (20, 20)
            xsize 520
            vbox:
                spacing 12
                if any(stat not in ['hp', 'max_hp'] and not stat.startswith('_') for stat in char.stats.keys()):
                    vbox:
                        spacing 8
                        label "ATTRIBUTES" text_color "#ffd700" text_size 26
                        python:
                            # Filter and sort
                            char_display_stats = sorted([s for s in char.stats.keys() if s not in ('hp', 'max_hp') and not s.startswith('_')])
                        
                        for s_key in char_display_stats:
                            $ sname = get_stat_display_name(s_key)
                            $ sicon = get_stat_icon(s_key)
                            $ sval = char.stats.get(s_key)
                            text "[sicon] [sname]: [sval]" size 24 color "#f8f8f2"


        # MAIN CONTENT: Full-Screen Sprite Presence (Absolute Bottom)
        if show_preview:
            fixed:
                xfill True
                yfill True
                
                if char.base_image:
                    add char.base_image:
                        fit "contain"
                        align (0.6, 1.0)
                        xzoom -1
                        at glide_up
                else:
                    add Solid("#1a1a2a"):
                        align (0.5, 0.5)
                        xsize 400
                        ysize 650
                        at glide_up

        if char_interaction_state == "talk":
            frame at char_panel_fade:
                align (0.5, 0.55)
                background None
                padding (40, 30)
                xsize 1000
                vbox:
                    spacing 20
                    $ options = dialogue_manager.get_for_char(char)
                    python:
                        option_rows = []
                        for opt in options:
                            avail, reason = opt.availability_status(char)
                            option_rows.append((opt, avail, reason))

                    if not option_rows:
                        text "You have nothing special to discuss." italic True color "#666" xalign 0.5
                    else:
                        viewport:
                            scrollbars "vertical"
                            mousewheel True
                            draggable True
                            ymaximum 400
                            vbox:
                                spacing 10
                                for opt, is_avail, reason in option_rows:
                                    $ is_seen = opt.id in pc.dialogue_history
                                    $ tag_prefix = "".join([f"[{t}] " for t in opt.tags])
                                    
                                    button:
                                        action (
                                            [
                                                Function(pc.dialogue_history.add, opt.id),
                                                Function(char_interaction_queue_label, opt.label),
                                                Function(char_interaction_set_state, "menu")
                                            ] if is_avail else NullAction()
                                        )
                                        hovered [SetVariable("hovered_dialogue_option", opt), SetVariable("hovered_dialogue_reason", (None if is_avail else reason))]
                                        unhovered [SetVariable("hovered_dialogue_option", None), SetVariable("hovered_dialogue_reason", None)]
                                        sensitive is_avail
                                        
                                        xfill True
                                        padding (20, 15)
                                        background ("#252535" if is_avail and not is_seen else "#151520")
                                        hover_background ("#353545" if is_avail else "#2a2a2a")
                                        
                                        at phone_visual_hover
                                        
                                        hbox:
                                            spacing 15
                                            text "[opt.emoji]" size 24 yalign 0.5
                                            text "[tag_prefix][opt.short_text]" size 22 color ("#fff" if is_avail and (not is_seen or not opt.memory) else "#777") yalign 0.5

        if char_interaction_state == "give":
            frame at char_panel_fade:
                align (0.5, 0.55)
                background "#1a2e1a"
                padding (20, 20)
                xsize 900
                ysize 620
                vbox:
                    spacing 12
                    if pc.items:
                        python:
                            give_columns = 4
                            give_rows = 3
                            grid_spacing = 8
                            cell_size = int(min((900 - 40 - (give_columns - 1) * grid_spacing) / give_columns, (560 - 40 - (give_rows - 1) * grid_spacing) / give_rows))
                            grid_entries = []
                            for entry in build_inventory_entries(pc):
                                item = entry["item"]
                                qty = entry["qty"]
                                label = get_give_label(char, item)
                                givable = bool(label)
                                action = (
                                    [Function(char_interaction_queue_label, label),
                                    Function(char_interaction_set_state, "menu")]
                                    if givable else NullAction()
                                )
                                grid_entries.append({
                                    "item": item,
                                    "qty": qty,
                                    "icon": get_item_icon(item),
                                    "tooltip": item_tooltip_text(item, qty),
                                    "action": action,
                                    "sensitive": givable,
                                    "givable": givable,
                                })
                            grid_entries.sort(key=lambda e: (0 if e.get("givable") else 1, e["item"].name.lower()))
                        use inventory_grid(grid_entries, columns=give_columns, cell_size=cell_size, total_slots=(give_columns * give_rows), selected_item=None, xspacing=grid_spacing, yspacing=grid_spacing)
                    else:
                        text "No items in inventory" size 20 color "#666666" xalign 0.5 yalign 0.5
        
        # Actions Layer
        vbox at char_buttons_rise:
            align (0.5, 0.94)
            
            hbox:
                spacing 50
                xalign 0.5
                
                textbutton "🗣️ TALK":
                    action Function(char_interaction_set_state, ("menu" if char_interaction_state == "talk" else "talk"))
                    padding (50, 25)
                    background Frame("#2c3e50", 4, 4)
                    hover_background Frame("#34495e", 4, 4)
                    text_size 40
                    text_bold True
                    at phone_visual_hover
                
                textbutton "🎁 GIVE":
                    action Function(char_interaction_set_state, ("menu" if char_interaction_state == "give" else "give"))
                    padding (50, 25)
                    background Frame("#8e44ad", 4, 4)
                    hover_background Frame("#9b59b6", 4, 4)
                    text_size 40
                    text_bold True
                    at phone_visual_hover

            null height 18

            textbutton "🚪 LEAVE":
                action [Function(char_interaction_set_state, "exit"), Jump("char_interaction_end")]
                padding (30, 14)
                background Frame("#3b3b3b", 4, 4)
                hover_background Frame("#4a4a4a", 4, 4)
                text_size 26
                text_bold True
                xalign 0.5
                at phone_visual_hover
        
# --- CONTAINER TRANSFER SCREEN ---
init python:
    def transfer_item(item, source_inv, target_inv):
        reason = "loot" if target_inv == pc else "deposit"
        if source_inv.transfer_to(item, target_inv, count=1, reason=reason):
            renpy.restart_interaction()

    def transfer_all(source_inv, target_inv):
        if not source_inv.items:
            return
        for itm in list(source_inv.items):
            qty = max(1, int(getattr(itm, "quantity", 1)))
            reason = "loot" if target_inv == pc else "deposit"
            source_inv.transfer_to(itm, target_inv, count=qty, reason=reason)
        renpy.restart_interaction()

    def transfer_by_tags(source_inv, target_inv, tags):
        if not source_inv.items:
            return
        tag_set = set(tags or [])
        moved = False
        for itm in list(source_inv.items):
            it_tags = getattr(itm, 'tags', set())
            if it_tags & tag_set:
                qty = max(1, int(getattr(itm, "quantity", 1)))
                reason = "loot" if target_inv == pc else "deposit"
                source_inv.transfer_to(itm, target_inv, count=qty, reason=reason)
                moved = True
        if moved:
            renpy.restart_interaction()

screen container_transfer_screen(container_inv):
    modal True
    zorder 200
    tag menu
    
    # Backdrop
    add "#0c0c0cdd"
    
    # Context Reset
    on "show" action SetVariable("selected_inventory_item", None)

    vbox:
        align (0.5, 0.4)
        spacing 30
        
        hbox:
            spacing 80
            xalign 0.5
            
            # Left Column: Player Inventory
            use inventory_column("YOUR INVENTORY", pc, container_inv, bulk_label="Deposit All", bulk_action=Function(transfer_all, pc, container_inv))
            
            # Right Column: Container Inventory
            use inventory_column(container_inv.name.upper(), container_inv, pc, bulk_label="Take All", bulk_action=Function(transfer_all, container_inv, pc), quick_label="Quick Loot", quick_action=Function(transfer_by_tags, container_inv, pc, quick_loot_tags))

        # Bottom Close Button
        textbutton "FINISH & CLOSE":
            action Hide("container_transfer_screen")
            xalign 0.5
            padding (40, 20)
            background Frame("#2c3e50", 4, 4)
            hover_background Frame("#34495e", 4, 4)
            text_size 30
            text_bold True
            at phone_visual_hover

screen inventory_column(title, source_inv, target_inv, bulk_label=None, bulk_action=None, quick_label=None, quick_action=None):
    vbox:
        spacing 15
        xsize 500
        
        label title text_size 28 text_color "#ffd700" xalign 0.5
        
        if bulk_label and bulk_action:
            hbox:
                spacing 10
                xalign 0.5
                textbutton "[bulk_label]":
                    action bulk_action
                    text_size 16
                    background Frame("#2c3e50", 4, 4)
                    hover_background Frame("#34495e", 4, 4)
                if quick_label and quick_action:
                    textbutton "[quick_label]":
                        action quick_action
                        text_size 16
                        background Frame("#2c3e50", 4, 4)
                        hover_background Frame("#34495e", 4, 4)
        
        frame:
            background "#1a1a1acc"
            padding (10, 10)
            xfill True
            ysize 650
            
            viewport:
                scrollbars "vertical"
                mousewheel True
                draggable True
                
                vbox:
                    spacing 8
                    xfill True
                    
                    python:
                        # Group items for cleaner display
                        grouped = {}
                        for itm in source_inv.items:
                            item_id = item_manager.get_id_of(itm)
                            key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
                            if key not in grouped:
                                label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
                                grouped[key] = {"item": itm, "qty": 0, "label": label}
                            grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
                    
                    if not source_inv.items:
                        text "Empty" italic True color "#666" align (0.5, 0.2)
                    
                    for key, entry in grouped.items():
                        $ first_item = entry["item"]
                        $ count = entry["qty"]
                        
                        button:
                            action Function(transfer_item, first_item, source_inv, target_inv)
                            xfill True
                            padding (15, 12)
                            background Frame("#222", 4, 4)
                            hover_background Frame("#333", 4, 4)
                            
                            hbox:
                                spacing 10
                                text "[entry['label']]" size 22 color "#eee"
                                if count > 1:
                                    text "x[count]" size 18 color "#ffd700" yalign 0.5
                                
                                # Visual indicator of action
                                text ("➡" if source_inv == pc else "⬅") size 22 color "#ffd700" xalign 1.0

style back_button_text:
    size 25
    xalign 0.5

screen char_give_screen(char):
    modal True
    add Solid("#000000aa")
    
    frame:
        align (0.5, 0.5)
        background "#1a1a1a"
        padding (30, 30)
        xsize 600
        ysize 600
        
        vbox:
            spacing 15
            text "Give item to [char.name]" size 24 xalign 0.5
            
            viewport:
                scrollbars "vertical"
                mousewheel True
                vbox:
                    spacing 5
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
                        textbutton "[entry['label']] (x[count])":
                            action [Function(pc.transfer_to, item, char, 1, "gift", True), Notify(f"Gave {item.name} to {char.name}"), Hide("char_give_screen")]
                            xfill True
                            background "#222"
            
            textbutton "Cancel":
                xalign 0.5
                action Hide("char_give_screen")
                background "#444" padding (10, 5)

style interact_button:
    background "#333"
    hover_background "#555"
    padding (30, 20)
    xsize 200

style interact_button_text:
    size 24
    xalign 0.5

screen shop_screen(shop):
    tag menu
    add "#0c0c0c"
    vbox:
        align (0.5, 0.5)
        spacing 20
        xsize 1100
        ysize 850
        hbox:
            xfill True
            text "[shop.name]" size 36 color "#ffffff"
            text "Your Gold: [pc.gold]" size 24 color "#ffd700" xalign 1.0 yalign 0.5
        hbox:
            spacing 20
            vbox:
                spacing 10
                text "Shop Stock" size 20 xalign 0.5
                frame:
                    background "#1a1a1a"
                    xsize 530
                    ysize 600
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            spacing 5
                            python:
                                shop_grouped = {}
                                for itm in shop.items:
                                    item_id = item_manager.get_id_of(itm)
                                    key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
                                    if key not in shop_grouped:
                                        label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
                                        shop_grouped[key] = {"item": itm, "qty": 0, "label": label}
                                    shop_grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
                            for key, entry in shop_grouped.items():
                                $ item = entry["item"]
                                $ count = entry["qty"]
                                $ price = shop.get_buy_price(item)
                                hbox:
                                    xfill True
                                    textbutton "[entry['label']] (x[count])":
                                        action SetVariable("selected_shop_item", item)
                                        background ("#333" if globals().get("selected_shop_item") == item else "#222")
                                    text "[price]G" color "#ffd700" yalign 0.5 xalign 1.0
                                    if pc.gold >= price:
                                        textbutton "Buy":
                                            action [Function(shop.transfer_to, item, pc, 1, "purchase", True), SetField(pc, "gold", pc.gold - price), Notify(f"Bought {item.name}")]
                                            xalign 1.0
                                    else:
                                        text "Poor" size 14 color "#666" yalign 0.5 xalign 1.0
            vbox:
                spacing 10
                text "Your Pack" size 20 xalign 0.5
                frame:
                    background "#1a1a1a"
                    xsize 530
                    ysize 600
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            spacing 5
                            python:
                                inv_grouped = {}
                                for itm in pc.items:
                                    item_id = item_manager.get_id_of(itm)
                                    key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
                                    if key not in inv_grouped:
                                        label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
                                        inv_grouped[key] = {"item": itm, "qty": 0, "label": label}
                                    inv_grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
                            for key, entry in inv_grouped.items():
                                $ item = entry["item"]
                                $ count = entry["qty"]
                                $ price = shop.get_sell_price(item)
                                hbox:
                                    xfill True
                                    textbutton "[entry['label']] (x[count])":
                                        action SetVariable("selected_shop_item", item)
                                        background ("#333" if globals().get("selected_shop_item") == item else "#222")
                                    text "[price]G" color "#ffd700" yalign 0.5 xalign 1.0
                                    textbutton "Sell":
                                        action [Function(pc.transfer_to, item, shop, 1, "sell", True), SetField(pc, "gold", pc.gold + price), Notify(f"Sold {item.name}")]
                                        xalign 1.0
        textbutton "Close Shop":
            align (0.5, 1.0)
            action Return()
            background "#444"
            padding (20, 10)
            text_style "back_button_text"

screen container_screen(container):
    tag menu
    add "#0c0c0c"
    vbox:
        align (0.5, 0.5)
        spacing 20
        xsize 1100
        ysize 850
        text "[container.name]" xalign 0.5 size 36 color "#ffffff"
        hbox:
            spacing 20
            xalign 0.5
            textbutton "Take All":
                action Function(transfer_all, container, pc)
                background "#333"
                padding (10, 6)
            textbutton "Quick Loot":
                action Function(transfer_by_tags, container, pc, quick_loot_tags)
                background "#333"
                padding (10, 6)
            textbutton "Deposit All":
                action Function(transfer_all, pc, container)
                background "#333"
                padding (10, 6)
        hbox:
            spacing 20
            vbox:
                spacing 10
                text "Inside" size 20 xalign 0.5
                frame:
                    background "#1a1a1a"
                    xsize 530
                    ysize 600
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            spacing 5
                            python:
                                cont_grouped = {}
                                for itm in container.items:
                                    item_id = item_manager.get_id_of(itm)
                                    key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
                                    if key not in cont_grouped:
                                        label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
                                        cont_grouped[key] = {"item": itm, "qty": 0, "label": label}
                                    cont_grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
                            for key, entry in cont_grouped.items():
                                $ item = entry["item"]
                                $ count = entry["qty"]
                                hbox:
                                    xfill True
                                    textbutton "[entry['label']] (x[count])":
                                        action SetVariable("selected_cont_item", item)
                                        background ("#333" if globals().get("selected_cont_item") == item else "#222")
                                    textbutton "Take":
                                        action [Function(container.transfer_to, item, pc, 1, "loot", False), Notify(f"Took {item.name}")]
                                        xalign 1.0
            vbox:
                spacing 10
                text "Your Items" size 20 xalign 0.5
                frame:
                    background "#1a1a1a"
                    xsize 530
                    ysize 600
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            spacing 5
                            python:
                                inv_grouped = {}
                                for itm in pc.items:
                                    item_id = item_manager.get_id_of(itm)
                                    key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
                                    if key not in inv_grouped:
                                        label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
                                        inv_grouped[key] = {"item": itm, "qty": 0, "label": label}
                                    inv_grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
                            for key, entry in inv_grouped.items():
                                $ item = entry["item"]
                                $ count = entry["qty"]
                                hbox:
                                    xfill True
                                    textbutton "[entry['label']] (x[count])":
                                        action SetVariable("selected_cont_item", item)
                                        background ("#333" if globals().get("selected_cont_item") == item else "#222")
                                    textbutton "Deposit":
                                        action [Function(pc.transfer_to, item, container, 1, "deposit", False), Notify(f"Stored {item.name}")]
                                        xalign 1.0
        textbutton "Close":
            align (0.5, 1.0)
            action Return()
            background "#444"
            padding (20, 10)
            text_style "back_button_text"

screen character_sheet():
    on "show" action SetVariable("meta_menu_tab", "stats")
    use meta_menu
