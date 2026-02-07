default meta_menu_tab = "inventory"
default selected_inventory_item = None
default selected_quest = None
default selected_recipe = None
default journal_tab = "quests"
default selected_note = None
default selected_person = None
default quick_loot_tags = ["consumable", "food", "medical", "ammo", "currency", "component", "material"]
default quest_filter = "active"

init python:
    def _equip_item_quick(itm):
        """Equip the item to the first compatible slot, using the safe equip pipeline."""
        slots_for_body = slot_registry.get_slots_for_body(pc.body_type)
        valid_slots = [s for s in getattr(itm, "equip_slots", []) if s in slots_for_body]
        if not valid_slots:
            renpy.notify("No valid slot for this item")
            return
        ok, msg = pc.equip(itm, valid_slots[0])
        renpy.notify(msg)
        renpy.restart_interaction()

screen meta_menu():
    tag menu
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
            
            textbutton "Stats":
                action SetVariable("meta_menu_tab", "stats")
                style "tab_button"
                text_style "tab_button_text"
                selected (meta_menu_tab == "stats")
            
            textbutton "Crafting":
                action SetVariable("meta_menu_tab", "crafting")
                style "tab_button"
                text_style "tab_button_text"
                selected (meta_menu_tab == "crafting")
            
            textbutton "Journal":
                action SetVariable("meta_menu_tab", "journal")
                style "tab_button"
                text_style "tab_button_text"
                selected (meta_menu_tab == "journal")
            
            textbutton "🏆":
                action SetVariable("meta_menu_tab", "achievements")
                style "tab_button"
                text_style "tab_button_text"
                selected (meta_menu_tab == "achievements")

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
        align (0.5, 0.25)
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

screen inventory_content():
    hbox:
        spacing 20
        # Item List
        frame:
            background "#222"
            xsize 400
            ysize 600
            vbox:
                spacing 6
                xfill True
                $ inv_weight = pc.get_total_weight()
                $ weight_max = pc.max_weight
                $ slots_used = pc.get_used_slots()
                $ slots_max = pc.max_slots
                if weight_max is not None:
                    text "Weight: [inv_weight:.1f] / [weight_max:.1f]" size 16 color "#999" xalign 0.5
                if slots_max is not None:
                    text "Slots: [slots_used] / [slots_max]" size 16 color "#999" xalign 0.5
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    vbox:
                        spacing 5
                        python:
                            grouped_items = {}
                            for item in pc.items:
                                item_id = item_manager.get_id_of(item)
                                key = (item_id, getattr(item, "owner_id", None), bool(getattr(item, "stolen", False)))
                                if key not in grouped_items:
                                    label = item.name + (" [stolen]" if getattr(item, "stolen", False) else "")
                                    grouped_items[key] = {"item": item, "qty": 0, "label": label}
                                grouped_items[key]["qty"] += max(1, int(getattr(item, "quantity", 1)))
                        
                        for key, entry in grouped_items.items():
                            $ first_item = entry["item"]
                            $ count = entry["qty"]
                            textbutton "[entry['label']] (x[count])":
                                action SetVariable("selected_inventory_item", first_item)
                                xfill True
                                background ("#333" if globals().get("selected_inventory_item") == first_item else "#111")
                                text_style "inventory_item_text"

        # Item Details
        frame:
            background "#222"
            xsize 620
            ysize 600
            padding (20, 20)
            
            if globals().get("selected_inventory_item"):
                $ itm = selected_inventory_item
                $ i_id = item_manager.get_id_of(itm)
                vbox:
                    spacing 15
                    text "[itm.name]" size 30 color "#ffd700"
                    text "[itm.description]" size 20
                    
                    null height 10
                    $ qty = pc.get_item_count(item_id=i_id)
                    text "Quantity: [qty]" size 18 color "#cccccc"
                    text "Weight: [itm.weight] kg (Total [itm.weight * qty:.1f] kg)" size 18 color "#cccccc"
                    text "Value: [itm.value] gold" size 18 color "#cccccc"
                    if getattr(itm, "stackable", False):
                        text "Stack Size: [itm.stack_size]" size 16 color "#888"
                    if getattr(itm, "owner_id", None):
                        text "Owner: [itm.owner_id]" size 16 color "#888"
                    if getattr(itm, "stolen", False):
                        text "Stolen" size 16 color "#ff7777"
                    
                    if itm.equip_slots:
                        $ slots_for_body = slot_registry.get_slots_for_body(pc.body_type)
                        vbox:
                            spacing 4
                            text "Slots: [', '.join(itm.equip_slots)]" size 16 color "#aaa"
                            for s in itm.equip_slots:
                                $ cur = pc.equipped_slots.get(s)
                                text ("Currently in [s]: [cur.name]" if cur else f"Currently in {s}: (empty)") size 14 color "#888"
                    
                    hbox:
                        spacing 10
                        textbutton "Inspect":
                            action Function(inspect_item, itm)
                            background "#555" padding (15, 10)
                        
                        if itm.equip_slots:
                            textbutton "Equip":
                                action Function(_equip_item_quick, itm)
                                background "#444" padding (15, 10)
            else:
                text "Select an item to see details." align (0.5, 0.5) color "#666666"

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
                $ stat_list = [("Strength", "strength", "💪"), ("Dexterity", "dexterity", "🏹"), ("Intelligence", "intelligence", "🧠"), ("Charisma", "charisma", "✨")]
                for sname, sval, sicon in stat_list:
                    $ total = pc.get_stat_total(sval)
                    $ mod = pc.get_stat_mod(sval)
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
        # Sub-tabs
        hbox:
            spacing 10
            xalign 0.5
            textbutton "Quests":
                action SetVariable("journal_tab", "quests")
                style "tab_button"
                text_style "tab_button_text"
                selected (journal_tab == "quests")
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

        if journal_tab == "quests":
             use quest_sub_content
        elif journal_tab == "notes":
             use notes_sub_content
        elif journal_tab == "people":
             use people_sub_content

screen quest_sub_content():
    vbox:
        spacing 10
        hbox:
            spacing 8
            xalign 0.5
            textbutton "Active":
                action SetVariable("quest_filter", "active")
                style "tab_button"
                text_style "tab_button_text"
                selected (quest_filter == "active")
            textbutton "Completed":
                action SetVariable("quest_filter", "passed")
                style "tab_button"
                text_style "tab_button_text"
                selected (quest_filter == "passed")
            textbutton "Failed":
                action SetVariable("quest_filter", "failed")
                style "tab_button"
                text_style "tab_button_text"
                selected (quest_filter == "failed")
            textbutton "All":
                action SetVariable("quest_filter", "all")
                style "tab_button"
                text_style "tab_button_text"
                selected (quest_filter == "all")

        hbox:
            spacing 20
            # Quest List
            frame:
                background "#222"
                xsize 350
                ysize 600
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    vbox:
                        spacing 5
                        python:
                            quests = []
                            for q in quest_manager.quests.values():
                                if q.state == "unknown":
                                    continue
                                if quest_filter == "all" or q.state == quest_filter:
                                    quests.append(q)
                            quests = sorted(quests, key=lambda x: (x.category, x.name))
                        for q in quests:
                             $ cat = (q.category or "side").upper()
                             textbutton "[q.name] ([cat])":
                                 action SetVariable("selected_quest", q)
                                 xfill True
                                 background ("#333" if globals().get("selected_quest") == q else "#111")
                                 text_style "quest_list_text"

            # Quest Details
            frame:
                background "#222"
                xsize 670
                ysize 600
                padding (20, 20)
                if globals().get("selected_quest"):
                    $ q = selected_quest
                    vbox:
                        spacing 8
                        text "[q.name]" size 30 color "#ffd700"
                        text "[q.description]" size 18 italic True
                        text "State: [q.state]" size 16 color "#888"
                        if q.giver:
                            text "Giver: [q.giver]" size 16 color "#888"
                        if q.location:
                            text "Location: [q.location]" size 16 color "#888"
                        null height 6
                        if q.rewards and (q.rewards.get("gold") or q.rewards.get("items") or q.rewards.get("flags")):
                            text "Rewards" size 20 color "#ffffff"
                            if q.rewards.get("gold"):
                                text "• Gold: [q.rewards['gold']]" size 16 color "#ddd"
                            for item_id, count in (q.rewards.get("items", {}) or {}).items():
                                $ itm = item_manager.get(item_id)
                                $ itm_name = itm.name if itm else item_id
                                text "• [itm_name] x[count]" size 16 color "#ddd"
                            for flag in (q.rewards.get("flags", []) or []):
                                text "• Flag: [flag]" size 16 color "#888"
                        null height 6
                        text "Objectives" size 22 color "#ffffff"
                        for tick in q.ticks:
                            if tick.state != "hidden":
                                hbox:
                                    spacing 10
                                    python:
                                        done = (tick.state == "complete")
                                        prog = ""
                                        if tick.required_value and tick.required_value > 1:
                                            prog = " ({}/{})".format(tick.current_value, tick.required_value)
                                    text ("✅" if done else "⭕") size 18
                                    text "[tick.name][prog]" size 18 color ("#888" if done else "#eee")
                else:
                    text "Select a quest to see details." align (0.5, 0.5) color "#666666"

screen notes_sub_content():
    hbox:
        spacing 20
        # Note List
        frame:
            background "#222"
            xsize 350
            ysize 600
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
            xsize 670
            ysize 600
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
        # People List
        frame:
            background "#222"
            xsize 350
            ysize 600
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
            xsize 670
            ysize 600
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
    padding (20, 10)
    xsize 200

style tab_button_text:
    size 20
    color "#ffffff"
    selected_color "#000000"

screen inventory_screen():
    use meta_menu

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

# --- CHARACTER INTERACTION SCREEN ---
screen char_interaction_menu(char):
    modal True
    zorder 150
    tag menu
    
    # Everything wrapped in a fixed block
    fixed:
        # Background dismissal
        button:
            action Return(None)
            background Solid("#0c0c0ccc")
            at phone_visual_hover
        
        # Side Panel: Stats and Info (Left Aligned)
        frame:
            align (0.05, 0.5)
            background Frame("#151520cc", 8, 8)
            padding (40, 40)
            xsize 450
            
                vbox:
                    spacing 30
                    
                    # Character Name
                    text "[char.name!u]" size 60 color "#ffd700" outlines [(2, "#000", 0, 0)]
                    
                    vbox:
                        spacing 10
                        text "ORIENTATION" size 24 color "#ffd700"
                        text "[char.description]" size 22 italic True color "#bbbbbb"
                        $ bond = bond_manager.get_between(pc.id, char.id)
                        if bond:
                            text "BOND" size 22 color "#ffd700"
                            if bond.tags:
                                $ tags_str = ", ".join(sorted(list(bond.tags)))
                                text tags_str size 18 color "#aaa"
                            if bond.stats:
                                for sname, sval in bond.stats.items():
                                    text "[sname!c]: [sval] ([bond_level(pc.id, char.id, sname)])" size 18 color "#ccc"
                        else:
                            text "No bond yet." size 18 color "#666"
                
                # Stats and Attributes
                vbox:
                    spacing 25
                    $ stats = char.stats
                    # Social Context
                    vbox:
                        spacing 8
                        label "SOCIAL" text_color "#ffd700" text_size 26
                        if char.affinity >= 50:
                            text "Relation: Friendly ([char.affinity])" size 24 color "#50fa7b"
                        elif char.affinity <= -50:
                            text "Relation: Hostile ([char.affinity])" size 24 color "#ff5555"
                        else:
                            text "Relation: Neutral ([char.affinity])" size 24 color "#ffffff"
                        text "Status: Relaxed" size 24 color "#f8f8f2"
                    
                    # Dynamic Attributes
                    if any(stat not in ['hp', 'max_hp'] for stat in char.stats.keys()):
                        vbox:
                            spacing 8
                            label "ATTRIBUTES" text_color "#ffd700" text_size 26
                            for stat_name, stat_val in char.stats.items():
                                if stat_name not in ['hp', 'max_hp']:
                                    text "[stat_name!c]: [stat_val]" size 24 color "#f8f8f2"

        # MAIN CONTENT: Full-Screen Sprite Presence (Absolute Bottom)
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
        
        # Actions Layer
        vbox:
            align (0.6, 0.95)
            yoffset -100
            xsize 1000
            
            hbox:
                spacing 50
                xalign 0.5
                
                textbutton "🗣️ TALK":
                    action Return("talk")
                    padding (50, 25)
                    background Frame("#2c3e50", 4, 4)
                    hover_background Frame("#34495e", 4, 4)
                    text_size 40
                    text_bold True
                    at phone_visual_hover
                
                textbutton "🎁 GIVE":
                    action Return("give")
                    padding (50, 25)
                    background Frame("#8e44ad", 4, 4)
                    hover_background Frame("#9b59b6", 4, 4)
                    text_size 40
                    text_bold True
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
