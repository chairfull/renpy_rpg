default persistent.met_characters = set()
default character = None # Main player character.
default char_interaction_state = "menu"
default char_interaction_pending_label = None

init -90 python:
    # TODO: Combine these two screens.
    onstart(add_meta_menu_tab, "characters", "📞", "Characters",
        selected_character=None)

    class RPGCharacter(Equipment, Entity, PathFollower):
        def __init__(self, id, name, stats=None, location_id=None, factions=None, body_type="humanoid", base_image=None, td_sprite=None, affinity=0, schedule=None, companion_mods=None, is_companion=False, owner_id=None, gender=None, age=None, height=None, weight=None, hair_color=None, eye_color=None, hair_style=None, face_shape=None, breast_size=None, dick_size=None, foot_size=None, skin_tone=None, build=None, distinctive_feature=None, equipment=None, **kwargs):
            super(RPGCharacter, self).__init__(**kwargs)
            if self.max_weight is None:
                base_weight = 50
                self.max_weight = base_weight + (self.stats.get("strength", 0) * 5)
            if self.max_slots is None:
                base_slots = 24
                self.max_slots = base_slots + max(0, int(self.stats.get("strength", 0) // 2))
            self._update_encumbrance()
            self.factions = set(factions or [])
            self.schedule = schedule or {}  # "HH:MM": "loc_id"
            self.base_image = base_image
            self.following = None
            self.give_flows = {}
            
            # Determine TD Sprite
            if td_sprite:
                self.td_sprite = td_sprite
            else:
                # Default to gender-based sprite if base_image hints at it
                if base_image and "female" in base_image.lower():
                    self.td_sprite = "images/topdown/chars/female_base.png"
                else:
                    self.td_sprite = "images/topdown/chars/male_base.png"
            
            self.location_id = location_id
            self.pchar = Character(name)
            self.dialogue_history = set()
            self.perks = {}
            self.stats = {}
            self.fixated_to = None
            # Appearance metadata
            self.gender = gender
            self.age = age
            self.height = height
            self.weight = weight
            self.height_in = self._parse_height_to_inches(height)
            self.weight_lbs = self._parse_weight_to_lbs(weight)
            self.hair_color = hair_color
            self.hair_style = hair_style
            self.eye_color = eye_color
            self.face_shape = face_shape
            self.breast_size = breast_size
            self.dick_size = dick_size
            self.foot_size = foot_size
            self.skin_tone = skin_tone
            self.build = build
            self.distinctive_feature = distinctive_feature

        def update(self, dt):
            PathFollower.update_path_following(self, dt)
            # if self.moving and self.path:
            #     target = self.path[0]
            #     dif = target - character
            #     length = dif.length()
            #     norm = dif.normal()
            #     # dist = math.hypot(dx, dy)
                
            #     if length < self.speed * dt:
            #         character.reset(target)
            #         self.path.pop(0)
            #         if not self.path:
            #             self.moving = False
            #             self.check_interaction()
            #             self.check_pending_exit()
            #     else:
            #         self.move(norm * self.speed * dt)
            #         angle = math.degrees(math.atan2(norm.z, norm.x))
            #         self.target_rotation = angle + 90 + 180

        def _parse_height_to_inches(self, value):
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return float(value)
            s = str(value).strip().lower()
            if not s:
                return None
            # 5'10" or 5 ft 10 in
            if "'" in s or "ft" in s:
                ft = 0.0
                inch = 0.0
                # normalize separators
                s = s.replace("feet", "ft").replace("foot", "ft").replace("inches", "in").replace("inch", "in").replace("\"", "in")
                parts = s.replace("ft", " ft ").replace("in", " in ").replace("'", " ft ").split()
                for i in range(len(parts)):
                    token = parts[i]
                    if token.replace(".", "", 1).isdigit():
                        num = float(token)
                        unit = parts[i + 1] if i + 1 < len(parts) else ""
                        if unit == "ft":
                            ft = num
                        elif unit == "in":
                            inch = num
                return ft * 12.0 + inch
            if "cm" in s:
                try:
                    num = float(s.replace("cm", "").strip())
                    return num / 2.54
                except Exception:
                    return None
            if "m" in s:
                try:
                    num = float(s.replace("m", "").strip())
                    return (num * 100.0) / 2.54
                except Exception:
                    return None
            if "in" in s:
                try:
                    return float(s.replace("in", "").strip())
                except Exception:
                    return None
            try:
                return float(s)
            except Exception:
                return None

        def _parse_weight_to_lbs(self, value):
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return float(value)
            s = str(value).strip().lower()
            if not s:
                return None
            if "kg" in s:
                try:
                    num = float(s.replace("kg", "").strip())
                    return num * 2.20462
                except Exception:
                    return None
            if "g" in s and "kg" not in s:
                try:
                    num = float(s.replace("g", "").strip())
                    return num * 0.00220462
                except Exception:
                    return None
            if "lb" in s or "lbs" in s:
                try:
                    return float(s.replace("lbs", "").replace("lb", "").strip())
                except Exception:
                    return None
            try:
                return float(s)
            except Exception:
                return None

        def is_player(self):
            return self == character

        def apply_equipment(self, equipment):
            """Seed and equip a character from a slot -> item_id map."""
            if not equipment:
                return
            if not isinstance(equipment, dict):
                return
            for slot_id, item_id in equipment.items():
                if not item_id:
                    continue
                target_id = str(item_id).lower()
                itm = None
                for owned in self.items:
                    if self._item_id(owned) == target_id and owned not in self.equipped_slots.values():
                        itm = owned
                        break
                if itm is None:
                    itm = item_manager.get(item_id)
                    if not itm:
                        continue
                    if getattr(itm, "owner_id", None) is None:
                        itm.owner_id = self.id
                    # Seed into inventory so equip removes it cleanly
                    self.add_item(itm, count=1, force=True, reason="equip_seed")
                    if itm not in self.items:
                        for owned in self.items:
                            if self._item_id(owned) == target_id and owned not in self.equipped_slots.values():
                                itm = owned
                                break
                ok, _msg = self.equip(itm, slot_id)
                if not ok:
                    # Fall back to inventory if equip fails (invalid slot or tag mismatch)
                    if itm not in self.items:
                        self.add_item(itm, count=1, force=True, reason="equip_seed")

        def check_schedule(self):
            """Move character if current time matches a schedule entry"""
            tm = time_manager
            current_time_str = "{:02d}:00".format(tm.hour) # Simple hourly check for now
            
            # Find best match (exact or previous hour?)
            # For now, let's just check if we are AT or PAST a schedule point that puts us somewhere new
            # Better: iterate schedule, find latest time <= current time
            target_loc = None
            latest_time = -1
            
            current_mins = tm.hour * 60 + tm.minute
            
            for time_str, loc_id in self.schedule.items():
                try:
                    h, m = map(int, time_str.split(':'))
                    mins = h * 60 + m
                    if mins <= current_mins and mins > latest_time:
                        latest_time = mins
                        target_loc = loc_id
                except: continue
                
            if target_loc and target_loc != self.location_id:
                self.location_id = target_loc
                # If player is in same location, maybe show notification?
                # renpy.notify(f"{self.name} moved to {target_loc}")
        
        def next_schedule_entry(self):
            """Return (time_str, loc_id) for the next scheduled move after current time."""
            if not self.schedule:
                return None, None
            tm = time_manager
            now = tm.hour * 60 + tm.minute
            future = []
            for time_str, loc_id in self.schedule.items():
                try:
                    h, m = map(int, time_str.split(':'))
                    mins = h*60 + m
                    if mins >= now:
                        future.append((mins, time_str, loc_id))
                except:
                    continue
            if not future:
                return None, None
            future.sort(key=lambda x: x[0])
            return future[0][1], future[0][2]
        
        def __call__(self, what, *args, **kwargs):
            return self.pchar(what, *args, **kwargs)
        
        def interact(self):
            import store
            renpy.store._interact_target_char = self
            queue("label", "_char_interaction_wrapper")
        
        def mark_as_met(self):
            journal_manager.unlock(self.name, self.desc)
        
        def in_faction(self, faction_id):
            return faction_id in self.factions
        
        def tick_effects(self):
            now = time_manager.total_minutes
            for arr, manager, label in [
                (self.active_perks, perk_manager, "Perk"),
                (self.active_statuses, status_manager, "Status")
            ]:
                expired = []
                for e in arr:
                    if e.get("expires_at") is not None and now >= e["expires_at"]:
                        expired.append(e["id"])
                if expired:
                    arr[:] = [e for e in arr if e["id"] not in expired]
                    for eid in expired:
                        obj = manager.get(eid)
                        if obj:
                            renpy.notify(f"{label} expired: {obj.name}")
        
        def add_perk(self, perk_id, duration_minutes=None):
            p = perk_manager.get(perk_id)
            if not p:
                return False, "Unknown perk"
            expires = None
            if duration_minutes:
                expires = time_manager.total_minutes + int(duration_minutes)
            for e in self.active_perks:
                if e["id"] == perk_id:
                    e["expires_at"] = expires
                    return True, "Perk refreshed"
            self.active_perks.append({"id": perk_id, "expires_at": expires})
            return True, "Perk added"
        
        def remove_perk(self, perk_id):
            before = len(self.active_perks)
            self.active_perks[:] = [e for e in self.active_perks if e["id"] != perk_id]
            return len(self.active_perks) != before

        def is_fixated(self, fixture_id=None):
            if not self.fixated_to:
                return False
            if fixture_id is None:
                return True
            return self.fixated_to == fixture_id

        def fixate(self, fixture):
            return fixture_manager.fixate_char(self, fixture)

        def unfixate(self):
            return fixture_manager.unfixate_char(self)
        
        def get_stat_total(self, name):
            base = self.stats.get(name, 0)
            mod = 0
            for e in self.active_perks:
                p = perk_manager.get(e["id"])
                if p:
                    mod += int(p.mods.get(name, 0))
            for e in self.active_statuses:
                s = status_manager.get(e["id"])
                if s:
                    mod += int(s.mods.get(name, 0))
            try:
                mod += party_manager.get_stat_bonus(name)
            except Exception:
                pass
            return base + mod
        
        def get_stat_mod(self, name):
            return self.get_stat_total(name) - self.stats.get(name, 0)
    
    class RelationType:
        def __init__(self):
            self.value = 0

    class RelationSet:
        def __init__(self):
            self.types = {}


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
        store.char_interaction_pending_label = label_name
        try:
            renpy.hide_screen("char_interaction_menu")
            renpy.restart_interaction()
        except Exception:
            pass


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
                                    $ is_seen = opt.id in character.dialogue_history
                                    $ tag_prefix = "".join([f"[{t}] " for t in opt.tags])
                                    
                                    button:
                                        action (
                                            [
                                                Function(character.dialogue_history.add, opt.id),
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
                    if character.items:
                        python:
                            give_columns = 4
                            give_rows = 3
                            grid_spacing = 8
                            cell_size = int(min((900 - 40 - (give_columns - 1) * grid_spacing) / give_columns, (560 - 40 - (give_rows - 1) * grid_spacing) / give_rows))
                            grid_entries = []
                            for entry in build_inventory_entries(character):
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

screen characters_screen(meta_menu):
    if selected_character:
        use character_detail_screen
    else:
        use character_list_screen

screen character_list_screen():
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

screen character_detail_screen():
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

screen followers_screen():
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
