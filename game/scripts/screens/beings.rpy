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
            at button_hover_effect
        
        # Names (Bottom)
        text "[character.name!u]":
            align (0.08, 0.92)
            size 36
            color "#e6edf5"
            outlines text_outline("#e6edf5")
        text "[char.name!u]":
            align (0.92, 0.92)
            size 36
            color "#e6edf5"
            outlines text_outline("#e6edf5")
        
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
                        # Poll quest-provided choices for this character/menu
                        try:
                            qc_list = quest_get_choices_for_menu(char.id, char)
                            class _QuestChoiceWrapper(object):
                                def __init__(self, quest_id, cid, text, label):
                                    self.quest = quest_id
                                    self.id = f"quest__{quest_id}__{cid}"
                                    self.label = label
                                    self.tags = []
                                    self.emoji = "❗"
                                    self.short_text = text
                                    self.memory = False
                                def availability_status(self, target_char):
                                    return True, None
                            for qc in qc_list:
                                qcw = _QuestChoiceWrapper(qc.get('quest'), qc.get('id') or 'choice', qc.get('text') or '...', qc.get('label'))
                                option_rows.append((qcw, True, None))
                        except Exception:
                            pass

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
                                    $ is_seen = opt.id in player.dialogue_history
                                    $ tag_prefix = "".join([f"[{t}] " for t in opt.tags])
                                    
                                    button:
                                        action (
                                            [
                                                Function(player.dialogue_history.add, opt.id),
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
                                        
                                        at button_hover_effect
                                        
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
                    if player.items:
                        python:
                            give_columns = 4
                            give_rows = 3
                            grid_spacing = 8
                            cell_size = int(min((900 - 40 - (give_columns - 1) * grid_spacing) / give_columns, (560 - 40 - (give_rows - 1) * grid_spacing) / give_rows))
                            grid_entries = []
                            for entry in build_inventory_entries(player):
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
                    at button_hover_effect
                
                textbutton "🎁 GIVE":
                    action Function(char_interaction_set_state, ("menu" if char_interaction_state == "give" else "give"))
                    padding (50, 25)
                    background Frame("#8e44ad", 4, 4)
                    hover_background Frame("#9b59b6", 4, 4)
                    text_size 40
                    text_bold True
                    at button_hover_effect

            null height 18

            textbutton "🚪 LEAVE":
                action [Function(char_interaction_set_state, "exit"), Jump("char_interaction_end")]
                padding (30, 14)
                background Frame("#3b3b3b", 4, 4)
                hover_background Frame("#4a4a4a", 4, 4)
                text_size 26
                text_bold True
                xalign 0.5
                at button_hover_effect

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
                        for itm in character.items:
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
                            action [Function(character.transfer_to, item, char, 1, "gift", True), Notify(f"Gave {item.name} to {char.name}"), Hide("char_give_screen")]
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

screen give_item_screen(target_char):
    modal True
    zorder 170
    
    # Background dismissal
    button:
        action Return()
        background Solid("#00000099")
    
    frame:
        align (0.5, 0.5)
        background "#1a2e1a"
        padding (30, 25)
        xsize 600
        ysize 500
        
        vbox:
            spacing 15
            
            text "Give item to [target_char.name]" size 30 color "#aaffaa" bold True xalign 0.5
            
            null height 10
            
            viewport:
                xfill True
                ysize 320
                scrollbars "vertical"
                mousewheel True
                
                vbox:
                    spacing 8
                    
                    if player.items:
                        python:
                            grouped = {}
                            for itm in player.items:
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
                                background "#2a3a2a"
                                hover_background "#3a4a3a"
                                padding (15, 10)
                                action [
                                    Function(player.transfer_to, item, target_char, 1, "gift", True),
                                    Return(),
                                    Notify(f"Gave {item.name} to {target_char.name}")
                                ]
                                
                                hbox:
                                    spacing 20
                                    text "[entry['label']] (x[count])" size 20 color "#ffffff"
                                    text "[item.desc]" size 16 color "#888888" yalign 0.5
                    else:
                        text "No items in inventory" size 20 color "#666666" xalign 0.5 yalign 0.5
            
            null height 10
            
            # Removed Cancel button as background clicking is now the dismissal method.
            null height 10
    
    key "game_menu" action Return()
