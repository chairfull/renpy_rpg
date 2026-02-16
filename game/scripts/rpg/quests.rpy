default quest_manager = QuestManager()

init 10 python:
    onstart(add_meta_menu_tab, "quests", "📋", "Quests",
        selected_quest=None,
        filter="active")
    
    class QuestTick:
        def __init__(self, id, name):
            self.id, self.name = id, name
            self.state, self.flow_label, self.trigger_data, self.guidance = "hidden", None, {}, {}

            self.current_value, self.required_value = 0, 1

        def check_trigger(self, etype, **kwargs):
            if self.state not in ["shown", "active"]: 
                return False
            # event compare (case-insensitive)
            if str(self.trigger_data.get("event")).upper() != str(etype).upper():
                return False
            for k, v in self.trigger_data.items():
                if k in ["event", "cond", "total"]: 
                    continue
                actual = kwargs.get(k)
                if isinstance(v, list):
                    if actual not in v:
                        return False
                else:
                    try:
                        if isinstance(actual, (int, float)) and str(v).replace('.', '', 1).isdigit():
                            if float(actual) != float(v):
                                return False
                        else:
                            if str(actual) != str(v):
                                return False
                    except Exception:
                        if str(actual) != str(v):
                            return False
            if self.trigger_data.get("cond"):
                try:
                    if not safe_eval_bool(self.trigger_data["cond"], {"player": character, "world": world, "kwargs": kwargs, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation}): 
                        return False
                except Exception as e:
                    renpy.log(f"Error evaluating tick cond for {self.id}: {e}")
                    return False
            self.current_value = int(kwargs.get("total", self.current_value + 1))
            try:
                required = int(self.trigger_data.get("total", self.required_value))
            except Exception:
                required = self.required_value
            if self.current_value >= required:
                self.state = "complete"
                return True
            return False
    
    class Quest:
        def __init__(self, id, name, description="", category="side", giver=None, location=None, tags=None, prereqs=None, rewards=None, start_trigger=None, origin=False, character=None, image=None, outcomes=None):
            self.id = id
            self.name = name
            self.description = description
            self.category = category or "side"
            self.giver = giver
            self.location = location
            self.tags = set(tags or [])
            self.prereqs = prereqs or {}
            self.rewards = rewards or {}
            self.outcomes = outcomes or []
            self.start_trigger = start_trigger or {}
            self.origin = bool(origin)
            self.character = character
            self.image = image
            self.state = "unknown"
            self.ticks = []
            self.rewards_applied = False
        def add_tick(self, t): self.ticks.append(t)
        def can_start(self):
            # Quest prereqs: quests passed + flags set + optional condition.
            req = self.prereqs or {}
            for qid in req.get("quests", []) or []:
                q = quest_manager.quests.get(qid)
                if not q or q.state != "passed":
                    return False
            for flag in req.get("flags", []) or []:
                if not flag_get(flag, False):
                    return False
            for flag in req.get("not_flags", []) or []:
                if flag_get(flag, False):
                    return False
            cond = req.get("cond")
            if cond and str(cond).strip():
                if not safe_eval_bool(cond, {"character": character, "world": world, "flags": world_flags, "flag_get": flag_get, "quest_manager": quest_manager, "faction_get": faction_manager.get_reputation}):
                    return False
            return True
        def start(self):
            if self.state in ["unknown", "known"]:
                if not self.can_start():
                    renpy.notify(f"Quest Locked: {self.name}")
                    signal("QUEST_START_BLOCKED", quest=self.id)
                    return False
                self.state = "active"
                if self.ticks:
                    self.ticks[0].state = "active"
                renpy.notify(f"Quest Started: {self.name}")
                signal("QUEST_STARTED", quest=self.id)
                if renpy.has_label(f"QUEST__{self.id}__started"): renpy.call(f"QUEST__{self.id}__started")
                return True
            return False
        def _apply_rewards(self, rewards):
            if self.rewards_applied:
                return
            rewards = rewards or {}
            gold = int(rewards.get("gold", 0) or 0)
            if gold:
                add_gold(gold)
            for item_id, count in (rewards.get("items", {}) or {}).items():
                give_item(item_id, count)
            for flag in rewards.get("flags", []) or []:
                flag_set(flag, True)
            # Reputation changes: allow 'reputation' or 'reputations' mapping
            rep_map = rewards.get('reputation') or rewards.get('reputations') or {}
            if isinstance(rep_map, dict):
                for fid, delta in rep_map.items():
                    try:
                        faction_manager.modify_reputation(str(fid), int(delta))
                    except Exception:
                        try:
                            faction_manager.modify_reputation(str(fid), float(delta))
                        except Exception:
                            renpy.log(f"Invalid reputation delta for faction {fid}: {delta}")
            # Faction membership changes
            for fid in rewards.get('factions_add', []) or []:
                try:
                    character.join_faction(fid)
                except Exception:
                    renpy.log(f"Failed to add character to faction {fid}")
            for fid in rewards.get('factions_remove', []) or []:
                try:
                    character.leave_faction(fid)
                except Exception:
                    renpy.log(f"Failed to remove character from faction {fid}")
            self.rewards_applied = True

        def _choose_outcome(self, outcome_id=None):
            """Evaluate outcomes (list of dicts) and return the first matching outcome dict.
            Each outcome may contain a 'cond' expression evaluated with safe_eval_bool.
            If none match, return None."""
            try:
                for o in (self.outcomes or []):
                    if not isinstance(o, dict):
                        continue
                    # If outcome_id specified, match by id immediately
                    if outcome_id and (str(o.get('id')) == str(outcome_id) or str(o.get('name')) == str(outcome_id)):
                        return o
                    cond = o.get('cond')
                    if not cond or str(cond).strip() == '':
                        # No condition -> default outcome (lowest priority)
                        default = o
                        continue
                    try:
                        ok = safe_eval_bool(cond, {"character": character, "world": world, "flags": world_flags, "flag_get": flag_get, "quest_manager": quest_manager, "faction_get": faction_manager.get_reputation})
                    except Exception as e:
                        renpy.log(f"Error evaluating outcome cond for quest {self.id}: {e}")
                        ok = False
                    if ok:
                        return o
                # If none matched, return default if present
                if 'default' in locals() and default:
                    return default
            except Exception as e:
                renpy.log(f"Error choosing outcome for quest {self.id}: {e}")
            return None
        def complete(self, outcome_id=None):
            self.state = "passed"
            # If outcomes are defined, evaluate and apply the matching outcome's rewards/flags
            outcome = None
            if self.outcomes:
                outcome = self._choose_outcome(outcome_id=outcome_id)
            if outcome and isinstance(outcome, dict):
                rewards = outcome.get('rewards', {}) or {}
                self._apply_rewards(rewards)
                # Apply any additional flags from outcome
                for flag in outcome.get('flags', []) or []:
                    flag_set(flag, True)
                # Apply faction membership changes if present at outcome level
                for fid in outcome.get('factions_add', []) or []:
                    try:
                        character.join_faction(fid)
                    except Exception:
                        renpy.log(f"Failed to add character to faction {fid} via outcome")
                for fid in outcome.get('factions_remove', []) or []:
                    try:
                        character.leave_faction(fid)
                    except Exception:
                        renpy.log(f"Failed to remove character from faction {fid} via outcome")
                renpy.log(f"Quest {self.id} completed with outcome: {outcome.get('id') or outcome.get('name')}")
            else:
                # Fallback to default rewards defined on the quest
                self._apply_rewards(self.rewards)

            renpy.notify(f"Quest Completed: {self.name}")
            signal("QUEST_COMPLETED", quest=self.id)
            if renpy.has_label(f"QUEST__{self.id}__passed"): renpy.call(f"QUEST__{self.id}__passed")
            if quest_manager.active_quest_id == self.id:
                quest_manager.set_active_quest(None)
        def fail(self):
            self.state = "failed"
            renpy.notify(f"Quest Failed: {self.name}")
            signal("QUEST_FAILED", quest=self.id)
            if renpy.has_label(f"QUEST__{self.id}__failed"): renpy.call(f"QUEST__{self.id}__failed")
            if quest_manager.active_quest_id == self.id:
                quest_manager.set_active_quest(None)

    class QuestManager:
        def __init__(self):
            self.quests, self.origins, self.start_triggers = {}, {}, {}
            self.active_quest_id = None
            self.trigger_index = {}
        def get_origins(self):
            origins = [q for q in self.quests.values() if getattr(q, "origin", False)]
            return sorted(origins, key=lambda x: x.name)
        def start_quest(self, qid):
            q = self.quests.get(qid)
            if q and q.start():
                if not self.active_quest_id:
                    self.set_active_quest(q.id)
                return True
            return False
        def set_active_quest(self, qid):
            prev = self.active_quest_id
            if not qid or qid not in self.quests:
                self.active_quest_id = None
            else:
                self.active_quest_id = qid
            if prev != self.active_quest_id:
                signal("QUEST_ACTIVE_CHANGED", quest=self.active_quest_id, previous=prev)
            return self.active_quest_id
        def get_active_quest(self):
            if self.active_quest_id and self.active_quest_id in self.quests:
                return self.quests[self.active_quest_id]
            return None
        def get_current_guidance(self):
            q = self.get_active_quest()
            if not q or q.state != "active": return None
            for t in q.ticks:
                if t.state == "active":
                    return t.guidance
            return None

        def complete_quest(self, qid):
            q = self.quests.get(qid)
            if q: q.complete()
        def fail_quest(self, qid):
            q = self.quests.get(qid)
            if q: q.fail()
        def update_goal(self, qid, gid, status="active"):
            target_quests = [self.quests[qid]] if qid and qid in self.quests else self.quests.values()
            
            for q in target_quests:
                for t in q.ticks:
                    if t.id == gid:
                        t.state = status
                        if status == "complete":
                            t.current_value = t.required_value
                            signal("QUEST_TICK_COMPLETED", quest=q.id, tick=t.id)
                # Check for quest completion if manual update
                if status == "complete":
                    all_c = True
                    for t in q.ticks:
                        if t.state != "complete":
                            all_c = False
                            break
                    if all_c: q.complete()
                signal("QUEST_UPDATED", quest=q.id)
        def handle_event(self, etype, **kwargs):
            # Start triggers (unchanged)
            for qid, trigger in self.start_triggers.items():
                q = self.quests.get(qid)
                if q and q.state == "unknown" and self._match(trigger, etype, **kwargs): q.start()

            # Fast-path: use precompiled trigger index when available
            processed = set()
            ev_key = str(etype).upper()
            entries = self.trigger_index.get(ev_key, []) if getattr(self, 'trigger_index', None) else []
            if entries:
                for ent in entries:
                    qid = ent.get('quest')
                    tick_id = ent.get('tick')
                    q = self.quests.get(qid)
                    if not q or q.state != 'active':
                        continue
                    for t in q.ticks:
                        if t.id != tick_id:
                            continue
                        # check trigger with tick's stored trigger data
                        try:
                            if t.check_trigger(etype, **kwargs):
                                processed.add((q.id, t.id))
                                signal("QUEST_TICK_COMPLETED", quest=q.id, tick=t.id)
                                if t.flow_label:
                                    if renpy.has_label(t.flow_label):
                                        renpy.call(t.flow_label)
                                    else:
                                        renpy.log(f"Missing flow label for quest {q.id} tick {t.id}: {t.flow_label}")
                        except Exception as e:
                            renpy.log(f"Error checking trigger for {q.id}.{t.id}: {e}")

            # Fallback scan for any other active quests/ticks not covered by index
            for q in self.quests.values():
                if q.state == "active":
                    any_done = False
                    for t in q.ticks:
                        if (q.id, t.id) in processed:
                            continue
                        if t.check_trigger(etype, **kwargs):
                            any_done = True
                            signal("QUEST_TICK_COMPLETED", quest=q.id, tick=t.id)
                            if t.flow_label and renpy.has_label(t.flow_label):
                                renpy.call(t.flow_label)
                            elif t.flow_label:
                                renpy.log(f"Missing flow label for quest {q.id} tick {t.id}: {t.flow_label}")
                    if any_done:
                        all_c = True
                        for t in q.ticks:
                            if t.state != "complete":
                                all_c = False
                                if t.state in ["hidden", "shown"]: t.state = "active"
                                break
                        if all_c: q.complete()
                        signal("QUEST_UPDATED", quest=q.id)
        def _match(self, t, etype, **kwargs):
            if str(t.get("event")).upper() != str(etype).upper(): return False
            for k, v in t.items():
                if k in ["event", "cond"]: continue
                actual = kwargs.get(k)
                # Support list membership
                if isinstance(v, list):
                    if actual not in v:
                        return False
                else:
                    try:
                        # numeric compare when possible
                        if isinstance(actual, (int, float)) and str(v).replace('.', '', 1).isdigit():
                            if float(actual) != float(v):
                                return False
                        else:
                            if str(actual) != str(v):
                                return False
                    except Exception:
                        if str(actual) != str(v):
                            return False
            if t.get("cond"):
                try:
                    return safe_eval_bool(t["cond"], {"character": character, "world": world, "kwargs": kwargs, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation})
                except Exception as e:
                    renpy.log(f"Error evaluating start trigger cond for {t}: {e}")
                    return False
            return True

    class StoryOrigin:
        def __init__(self, id, name, description, character, intro_label, image=None):
            self.id = id
            self.name = name
            self.description = description
            self.character = character
            self.intro_label = intro_label
            self.image = image

    def reload_quest_manager(data):
        quest_manager.trigger_index = data.get("quest_trigger_index", {}) # Clear old index to avoid stale data

        quest_manager.origins = {}
        for origin_id, p in data.get("story_origins", {}).items():
            quest_manager.origins[origin_id] = StoryOrigin(
                origin_id,
                name=p.get('name', origin_id),
                description=p.get('description', ''),
                character=(p.get('character')),
                intro_label=p.get('intro_label'),
                image=p.get('image')
            )
        
        quest_manager.quests = {}
        for quest_id, p in data.get("quests", {}).items():
            try:
                q = Quest(
                    quest_id,
                    p.get('name', quest_id),
                    p.get('description', ''),
                    category=p.get('category', 'side'),
                    giver=p.get('giver'),
                    location=p.get('location'),
                    tags=p.get('tags', []),
                    prereqs=p.get('prereqs', {}),
                    rewards=p.get('rewards', {}),
                    start_trigger=p.get('start_trigger', {}),
                    outcomes=p.get('outcomes', []),
                    origin=p.get('origin', False),
                    character=p.get('character'),
                    image=p.get('image')
                )
                for t_idx, tp in enumerate(p.get('ticks', [])):
                    tick = QuestTick(tp['id'], tp['name'])
                    tick.trigger_data = tp.get('trigger', {})
                    tick.guidance = tp.get('guidance', {})
                    try:
                        tick.required_value = int(tick.trigger_data.get("total", 1) or 1)
                    except Exception:
                        tick.required_value = 1
                    tick.flow_label = tp.get('label')
                    q.add_tick(tick)
                # Attach compiled choices (if any)
                try:
                    q.choices = p.get('choices', []) or []
                except Exception:
                    q.choices = []
                quest_manager.quests[quest_id] = q
                if q.start_trigger:
                    quest_manager.start_triggers[quest_id] = q.start_trigger
                # (no-op)
            except Exception as e:
                with open("debug_load.txt", "a") as df:
                    df.write("Quest Load Error ({}): {}\n".format(quest_id, str(e)))

    def _finish_origin_selection(origin):
        # Set global player from the origin's character ID
        if origin.character:
            char = world.characters.get(origin.character)
            if char:
                renpy.store.character = char
                # Ensure starting location is set from character
                if renpy.store.character.location_id:
                    world.move_to(renpy.store.character.location_id)
        # Core origin bootstrapping lives here.
        flag_set("origin", origin.id)
        signal("GAME_STARTED", origin=origin.id)

        renpy.hide_screen("story_select_screen")
        # Auto-start quest if ID matches origin
        if origin.id in quest_manager.quests:
            quest_manager.start_quest(origin.id)
        else:
            renpy.notify("Origin quest not found; starting world loop.")
        
        renpy.transition(fade)
        renpy.jump("world_loop")


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

    def quest_get_choices_for_menu(menu_id, char=None):
        """Return list of available quest-provided choices for a given menu target (char id or menu id).
        Each entry: {quest, id, text, label}.
        """
        res = []
        try:
            for q in quest_manager.quests.values():
                if q.state != 'active':
                    continue
                for choice in getattr(q, 'choices', []) or []:
                    # Menu matching: None means global; allow list or single
                    menu = choice.get('menu')
                    if menu:
                        if isinstance(menu, list):
                            if str(menu_id) not in [str(m) for m in menu]:
                                continue
                        else:
                            if str(menu) != str(menu_id) and not (hasattr(char, 'id') and str(menu) == str(getattr(char, 'id'))):
                                continue
                    # Evaluate condition
                    cond = choice.get('cond', True)
                    ok = safe_eval_bool(cond, {"character": character, "world": world, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation, "char": (getattr(char, 'id', None))})
                    if ok:
                        res.append({"quest": q.id, "id": choice.get('id'), "text": choice.get('text'), "label": choice.get('label')})
        except Exception as e:
            renpy.log(f"Error while gathering quest choices for menu {menu_id}: {e}")
        return res

    def _on_quest_tick(etype, **kwargs):
        try:
            qid = kwargs.get('quest')
            tick_id = kwargs.get('tick')
            q = quest_manager.quests.get(qid)
            t = None
            if q:
                for tt in q.ticks:
                    if tt.id == tick_id:
                        t = tt
                        break
            if q and t:
                renpy.notify(f"Goal updated: {q.name} — {t.name}")
            elif q:
                renpy.notify(f"Goal updated: {q.name}")
            else:
                renpy.notify(f"Goal updated")
        except Exception:
            pass

    onstart(listen, "QUEST_TICK_COMPLETED", _on_quest_tick)

    # Debug helpers.
    def q_force_tick(qid, tick_idx):
        q = quest_manager.quests.get(qid)
        if q and tick_idx < len(q.ticks):
            t = q.ticks[tick_idx]
            t.state = "complete"
            t.current_value = t.required_value
            # Check for next tick or quest completion
            all_c = True
            for i, tick in enumerate(q.ticks):
                if tick.state != "complete":
                    all_c = False
                    if tick.state in ["hidden", "shown"]:
                        tick.state = "active"
                    break
            if all_c:
                q.complete()
            renpy.notify(f"Forced tick: {t.name}")

    def q_complete(qid):
        q = quest_manager.quests.get(qid)
        if q:
            for t in q.ticks:
                t.state = "complete"
                t.current_value = t.required_value
            q.complete()
            renpy.notify(f"Forced quest complete: {q.name}")

style quest_list_text:
    size 18
    color "#eee"
    insensitive_color "#666"
    selected_color "#ffd700"

screen quests_screen():
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

## Compact Quest Panel - shows active quest and next goal/progress
screen quest_panel():
    # overlay, small z-order so it sits above map but below full-screen UI
    zorder 80
    $ active = quest_manager.get_active_quest()
    if active and active.state == 'active':
        $ next_tick = quest_next_tick(active)
        frame:
            xalign 0.5
            yalign 0.06
            background Frame(Solid("#0f141bcc"), 10, 10)
            padding (12, 8)
            xmaximum 760
            hbox:
                spacing 16
                vbox:
                    spacing 4
                    text active.name size 18 color "#ffd700" slow_cps None
                    if next_tick:
                        text next_tick.name size 14 color "#c9d3dd" slow_cps None
                        if getattr(next_tick, 'required_value', None) and getattr(next_tick, 'current_value', None) is not None:
                            $ cur = float(next_tick.current_value or 0.0)
                            $ req = float(next_tick.required_value or 1.0)
                            bar value (cur/ max(1.0, req)) xmaximum 220 yminimum 8
                            text "[int(cur)]/[int(req)]" size 12 color "#c9d3dd"
                hbox:
                    spacing 8
                    textbutton "Details":
                        action Function(renpy.show_screen, "quests_screen")
                        xminimum 80
                    textbutton "Set Active":
                        action Function(quest_manager.set_active_quest, active.id)
                        xminimum 80

screen story_select_screen():
    modal True
    zorder 150
    # Background dismissal
    button:
        action Return(None)
        background Solid("#000000cc")
    
    vbox:
        align (0.5, 0.5)
        spacing 100
        
        text "CHOOSE YOUR ORIGIN" size 60 color "#ffd700" xalign 0.5
        
        hbox:
            spacing 40
            xalign 0.5
            
            $ origins = quest_manager.get_origins()
            
            for origin in origins:
                button:
                    background Frame("#1b1b2f", 8, 8)
                    xsize 420
                    ysize 720
                    padding (0, 0)
                    at button_hover_effect
                    action Function(_finish_origin_selection, origin)
                    
                    fixed:
                        # 1. Full-size character sprite at absolute bottom
                        if origin.image:
                            add origin.image:
                                fit "contain"
                                align (0.5, 1.0)
                        
                        # 2. Description Overlay at the bottom
                        frame:
                            align (0.5, 0.95) # Anchored towards bottom
                            background Frame(Solid("#00000088"), 4, 4)
                            padding (20, 15)
                            xsize 380
                            
                            vbox:
                                spacing 10
                                text "[origin.description]" size 22 color "#ffffff" xalign 0.5 text_align 0.5 outlines [(1, "#000", 0, 0)]

                        # 3. Title at the Top (Drawn LAST to be on TOP)
                        frame:
                            background None
                            padding (20, 30)
                            xfill True
                            text "[origin.name!u]" size 40 color "#ffd700" xalign 0.5 outlines [(3, "#000", 0, 0)]
                        # Just show description
