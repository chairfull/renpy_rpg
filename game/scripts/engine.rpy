default persistent.met_characters = set()
default persistent.unlocked_notes = set()
default world_flags = {}
default encounter_history = set()
default scavenge_history = {}
default allow_unvisited_travel = False

init -10 python:
    # Initialize Persistent Data Defaults (Legacy safety)
    if persistent.met_characters is None:
        persistent.met_characters = set()
    if persistent.unlocked_notes is None:
        persistent.unlocked_notes = set()

    import json
    import random
    import copy
    import ast

    SAFE_FUNC_NAMES = {"len", "int", "float", "str", "max", "min"}

    def _ast_safe(node):
        """Whitelist a small subset of Python expressions for data-driven conditions."""
        allowed = (
            ast.Expression, ast.BoolOp, ast.UnaryOp, ast.BinOp, ast.Compare,
            ast.Name, ast.Load, ast.Attribute, ast.Constant,
            ast.And, ast.Or, ast.Not, ast.Eq, ast.NotEq, ast.Lt, ast.LtE,
            ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.Is, ast.IsNot,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.USub
        )
        if isinstance(node, ast.Call):
            # Allow basic builtins and kwargs.get only
            func = node.func
            if isinstance(func, ast.Name) and func.id in SAFE_FUNC_NAMES:
                pass
            elif isinstance(func, ast.Attribute) and func.attr == "get" and isinstance(func.value, ast.Name) and func.value.id == "kwargs":
                pass
            else:
                return False
            return all(_ast_safe(arg) for arg in node.args) and all(_ast_safe(kw.value) for kw in node.keywords)
        if not isinstance(node, allowed):
            return False
        for child in ast.iter_child_nodes(node):
            if not _ast_safe(child):
                return False
        return True

    def safe_eval_bool(expr, env):
        """Evaluate small boolean expressions safely; returns False on error."""
        try:
            tree = ast.parse(str(expr), mode="eval")
        except Exception:
            return False
        if not _ast_safe(tree):
            return False
        try:
            builtins_obj = __builtins__
            safe_funcs = {}
            for n in SAFE_FUNC_NAMES:
                fn = getattr(builtins_obj, n, None) if hasattr(builtins_obj, n) else builtins_obj.get(n) if isinstance(builtins_obj, dict) else None
                if fn:
                    safe_funcs[n] = fn
            return bool(eval(compile(tree, "<cond>", "eval"), {"__builtins__": {}, **safe_funcs}, env))
        except Exception:
            return False

    def flag_get(name, default=False):
        return world_flags.get(name, default)

    def flag_set(name, value=True):
        world_flags[name] = value
        return value

    def flag_clear(name):
        if name in world_flags:
            del world_flags[name]

    def flag_toggle(name):
        world_flags[name] = not world_flags.get(name, False)
        return world_flags[name]

    def find_item_by_tag(tag):
        for it in pc.items:
            if tag in getattr(it, "tags", set()):
                return it
        return None

    def consume_item_by_tag(tag):
        it = find_item_by_tag(tag)
        if it:
            pc.remove_item(it)
            return it
        return None

    class Bond(object):
        def __init__(self, id, a_id, b_id, tags=None, stats=None):
            self.id = id
            self.a_id = a_id
            self.b_id = b_id
            self.tags = set(tags or [])
            self.stats = stats or {}
        
        def other(self, cid):
            return self.b_id if cid == self.a_id else self.a_id
        
        def get_stat(self, name, default=0):
            try:
                return int(self.stats.get(name, default))
            except Exception:
                return default
        
        def set_stat(self, name, value):
            self.stats[name] = int(value)
        
        def add_stat(self, name, delta):
            self.set_stat(name, self.get_stat(name, 0) + int(delta))
        
        def has_tag(self, tag):
            return tag in self.tags
        
        def add_tag(self, tag):
            self.tags.add(tag)
        
        def remove_tag(self, tag):
            self.tags.discard(tag)

    class BondManager:
        def __init__(self):
            self.bonds = {}
        
        def _key(self, a, b):
            return tuple(sorted([a, b]))
        
        def register(self, bond):
            self.bonds[self._key(bond.a_id, bond.b_id)] = bond
        
        def get_between(self, a, b):
            if not a or not b or a == b:
                return None
            return self.bonds.get(self._key(a, b))
        
        def ensure(self, a, b):
            if not a or not b or a == b:
                return None
            key = self._key(a, b)
            if key not in self.bonds:
                bid = f"{key[0]}__{key[1]}"
                self.bonds[key] = Bond(bid, key[0], key[1])
            return self.bonds[key]
        
        def get_for(self, cid):
            res = []
            for bond in self.bonds.values():
                if bond.a_id == cid or bond.b_id == cid:
                    res.append(bond)
            return res

    bond_manager = BondManager()

    def bond_get_stat(a_id, b_id, stat, default=0):
        b = bond_manager.get_between(a_id, b_id)
        return b.get_stat(stat, default) if b else default

    def bond_stat(other_id, stat, default=0):
        return bond_get_stat(pc.id, other_id, stat, default)

    def bond_set_stat(a_id, b_id, stat, value):
        b = bond_manager.ensure(a_id, b_id)
        if not b:
            return False
        b.set_stat(stat, value)
        return True

    def bond_add_stat(a_id, b_id, stat, delta):
        b = bond_manager.ensure(a_id, b_id)
        if not b:
            return False
        b.add_stat(stat, delta)
        return True

    def bond_has_tag(a_id, b_id, tag):
        b = bond_manager.get_between(a_id, b_id)
        return b.has_tag(tag) if b else False

    def bond_add_tag(a_id, b_id, tag):
        b = bond_manager.ensure(a_id, b_id)
        if not b:
            return False
        b.add_tag(tag)
        return True

    def bond_remove_tag(a_id, b_id, tag):
        b = bond_manager.get_between(a_id, b_id)
        if not b:
            return False
        b.remove_tag(tag)
        return True

    def bond_tags(a_id, b_id):
        b = bond_manager.get_between(a_id, b_id)
        return list(b.tags) if b else []

    def bond_level_from_value(val):
        if val <= -50: return "Hostile"
        if val <= -20: return "Cold"
        if val < 20: return "Neutral"
        if val < 50: return "Warm"
        return "Allied"

    def bond_level(a_id, b_id, stat):
        return bond_level_from_value(bond_get_stat(a_id, b_id, stat, 0))

    def give_item(item_id, count=1):
        count = max(1, int(count))
        for _ in range(count):
            it = item_manager.get(item_id)
            if it:
                pc.add_item(it)
        return True

    def take_item(item_id, count=1):
        count = max(1, int(count))
        removed = 0
        for it in list(pc.items):
            if item_manager.get_id_of(it) == item_id:
                pc.remove_item(it)
                removed += 1
                if removed >= count:
                    break
        return removed

    def add_gold(amount):
        pc.gold = max(0, int(pc.gold + amount))
        return pc.gold

    def cond_jump(expr, label_true, label_false=None):
        ok = safe_eval_bool(expr, {"pc": pc, "rpg_world": rpg_world, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level})
        if ok and label_true and renpy.has_label(label_true):
            renpy.jump(label_true)
        elif (not ok) and label_false and renpy.has_label(label_false):
            renpy.jump(label_false)
        return ok

    def perk_add(perk_id, duration_minutes=None):
        p = perk_manager.get(perk_id)
        if not p:
            renpy.notify("Unknown perk")
            return False
        duration = duration_minutes if duration_minutes is not None else p.duration_minutes
        ok, msg = pc.add_perk(perk_id, duration)
        renpy.notify(msg)
        return ok

    def perk_remove(perk_id):
        ok = pc.remove_perk(perk_id)
        if ok:
            renpy.notify("Perk removed")
        return ok

    def status_add(status_id, duration_minutes=None):
        s = status_manager.get(status_id)
        if not s:
            renpy.notify("Unknown status")
            return False
        duration = duration_minutes if duration_minutes is not None else s.duration_minutes
        ok, msg = pc.add_status(status_id, duration)
        renpy.notify(msg)
        return ok

    def status_remove(status_id):
        ok = pc.remove_status(status_id)
        if ok:
            renpy.notify("Status removed")
        return ok

    class Perk(object):
        def __init__(self, id, name, description="", mods=None, tags=None, duration_minutes=None):
            self.id = id
            self.name = name
            self.description = description
            self.mods = mods or {}
            self.tags = set(tags or [])
            self.duration_minutes = duration_minutes

    class StatusEffect(object):
        def __init__(self, id, name, description="", mods=None, tags=None, duration_minutes=None):
            self.id = id
            self.name = name
            self.description = description
            self.mods = mods or {}
            self.tags = set(tags or [])
            self.duration_minutes = duration_minutes

    class PerkManager:
        def __init__(self): self.registry = {}
        def register(self, p): self.registry[p.id] = p
        def get(self, pid): return self.registry.get(pid)
        def get_all(self): return sorted(self.registry.values(), key=lambda x: x.name)

    class StatusManager:
        def __init__(self): self.registry = {}
        def register(self, s): self.registry[s.id] = s
        def get(self, sid): return self.registry.get(sid)
        def get_all(self): return sorted(self.registry.values(), key=lambda x: x.name)

    perk_manager = PerkManager()
    status_manager = StatusManager()

    # --- BASE MIXINS (must be defined first) ---
    class SpatialObject(object):
        """Mixin for objects with position data"""
        def __init__(self, x=0, y=0, **kwargs):
            self.x, self.y = x, y
        
        def distance_to(self, other):
            return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        
        def move_to(self, x, y):
            self.x, self.y = x, y

    class TaggedObject(object):
        """Mixin for objects with tags for filtering"""
        def __init__(self, tags=None, **kwargs):
            self.tags = set(tags or [])
        
        def has_tag(self, tag):
            return tag in self.tags
        
        def has_any_tag(self, tags):
            return bool(self.tags & set(tags))
        
        def has_all_tags(self, tags):
            return set(tags) <= self.tags
        
        def add_tag(self, tag):
            self.tags.add(tag)
        
        def remove_tag(self, tag):
            self.tags.discard(tag)

    # --- ITEM SYSTEM ---
    class Item(TaggedObject):
        def __init__(self, name="Unknown", description="", weight=0, value=0, tags=None, factions=None, equip_slots=None, outfit_part=None, id=None, **kwargs):
            TaggedObject.__init__(self, tags)
            self.id = id
            self.factions = set(factions or [])
            self.name, self.description, self.weight, self.value = name, description, weight, value
            self.equip_slots = equip_slots or []
            # Legacy compatibility - map outfit_part to equip_slots if provided
            if outfit_part and not equip_slots:
                self.equip_slots = [outfit_part]
            self.outfit_part = outfit_part

    class ItemManager:
        def __init__(self): self.registry = {}
        def register(self, sid, obj): self.registry[sid.lower()] = obj
        def get(self, sid):
            base = self.registry.get(sid.lower())
            return copy.copy(base) if base else None
        def get_id_of(self, obj):
            if not obj: return "unknown"
            for k, v in self.registry.items():
                if v.name == obj.name: return k
            return "unknown"

    item_manager = ItemManager()

    class Recipe(object):
        def __init__(self, id, name, inputs, output, req_skill=None, tags=None):
            self.id = id
            self.name = name
            self.inputs = inputs # {item_id: count}
            self.output = output # {item_id: count}
            self.req_skill = req_skill # {skill_name: level}
            self.tags = set(tags or [])

    class CraftingManager:
        def __init__(self):
            self.recipes = {}
        
        def register(self, recipe):
            self.recipes[recipe.id] = recipe
            
        def get_all(self):
            return sorted(self.recipes.values(), key=lambda x: x.name)

        def can_craft(self, recipe, inventory):
            for item_id, count in recipe.inputs.items():
                current_count = 0
                for itm in inventory.items:
                    # Helper to match ID
                    if item_manager.get_id_of(itm) == item_id:
                        current_count += 1
                
                if current_count < count:
                    return False, f"Missing {item_id}"
            
            if recipe.req_skill:
                for skill, level in recipe.req_skill.items():
                    if pc.stats.get(skill) < level:
                        return False, f"Need {skill} {level}"
            
            return True, "OK"

        def craft(self, recipe, inventory):
            can, msg = self.can_craft(recipe, inventory)
            if not can:
                renpy.notify(msg)
                return False
            
            # Consume inputs
            for item_id, count in recipe.inputs.items():
                items_to_remove = []
                found = 0
                for itm in inventory.items:
                    if item_manager.get_id_of(itm) == item_id:
                        items_to_remove.append(itm)
                        found += 1
                        if found >= count:
                            break
                for itm in items_to_remove:
                    inventory.remove_item(itm)
            
            # Grant outputs
            for item_id, count in recipe.output.items():
                for _ in range(count):
                    new_item = item_manager.get(item_id)
                    inventory.add_item(new_item, force=True)
            
            renpy.notify(f"Crafted {recipe.name}")
            event_manager.dispatch("ITEM_CRAFTED", item=recipe.output, recipe=recipe.id)
            return True

    crafting_manager = CraftingManager()

    class EventManager:
        def dispatch(self, etype, **kwargs): 
            quest_manager.handle_event(etype, **kwargs)
            ach_mgr.handle_event(etype, **kwargs)

    event_manager = EventManager()

    class TimeManager(object):
        def __init__(self, hour=8, minute=0, day=1):
            self.hour, self.minute = hour, minute
            self.day = day
        
        @property
        def time_string(self): return "{:02d}:{:02d} (Day {})".format(self.hour, self.minute, self.day)
        
        @property
        def time_of_day(self):
            if 5 <= self.hour < 12: return "Morning"
            elif 12 <= self.hour < 17: return "Afternoon"
            elif 17 <= self.hour < 21: return "Evening"
            else: return "Night"
        
        @property
        def total_minutes(self):
            return self.day * 1440 + self.hour * 60 + self.minute

        def advance(self, mins):
            self.minute += mins
            while self.minute >= 60:
                self.minute -= 60
                self.hour += 1
            while self.hour >= 24:
                self.hour -= 24
                self.day += 1
            
            # notify world of time change
            rpg_world.update_schedules()
            # tick timed effects
            try:
                pc.tick_effects()
            except Exception:
                pass

    time_manager = TimeManager()

    class QuestTick:
        def __init__(self, id, name):
            self.id, self.name = id, name
            self.state, self.flow_label, self.trigger_data = "hidden", None, {}
            self.current_value, self.required_value = 0, 1
        def check_trigger(self, etype, **kwargs):
            if self.state not in ["shown", "active"] or self.trigger_data.get("event") != etype: return False
            for k, v in self.trigger_data.items():
                if k not in ["event", "cond", "total"] and str(kwargs.get(k)) != str(v): return False
            if self.trigger_data.get("cond"):
                if not safe_eval_bool(self.trigger_data["cond"], {"player": pc, "rpg_world": rpg_world, "kwargs": kwargs, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level}): 
                    return False
            self.current_value = int(kwargs.get("total", self.current_value + 1))
            if self.current_value >= int(self.trigger_data.get("total", self.required_value)):
                self.state = "complete"
                return True
            return False

    class DialogueOption(object):
        def __init__(self, id, chars, short_text, long_text, emoji, label, cond=None, tags=None, memory=False, reason=None):
            self.id = id
            self.chars = set(chars or [])
            self.short_text = short_text
            self.long_text = long_text
            self.emoji = emoji
            self.label = label
            self.cond = cond
            self.tags = tags or []
            self.memory = memory
            self.reason = reason
        
        def is_available(self, char):
            if self.chars and char.id not in self.chars and "*" not in self.chars:
                return False
            if self.cond and str(self.cond).strip() and str(self.cond) != "True":
                return safe_eval_bool(self.cond, {"pc": pc, "char": char, "rpg_world": rpg_world, "quest_manager": quest_manager, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level})
            return True

        def availability_status(self, char):
            if self.chars and char.id not in self.chars and "*" not in self.chars:
                return False, "Not for this character."
            if self.cond and str(self.cond).strip() and str(self.cond) != "True":
                ok = safe_eval_bool(self.cond, {"pc": pc, "char": char, "rpg_world": rpg_world, "quest_manager": quest_manager, "flags": world_flags, "flag_get": flag_get})
                if not ok:
                    return False, self.reason or "Locked."
            return True, "Available."

    class DialogueManager:
        def __init__(self):
            self.options = {}
        def register(self, opt):
            self.options[opt.id] = opt
        def get_for_char(self, char):
            opts = [opt for opt in self.options.values() if (not opt.chars or char.id in opt.chars or "*" in opt.chars)]
            return sorted(opts, key=lambda x: x.id)
        def get_available(self, char):
            opts = [opt for opt in self.options.values() if opt.is_available(char)]
            return sorted(opts, key=lambda x: x.id)

    dialogue_manager = DialogueManager()

    class StoryOrigin(object):
        def __init__(self, id, name, description, pc_id, intro_label, image=None):
            self.id = id
            self.name = name
            self.description = description
            self.pc_id = pc_id
            self.intro_label = intro_label
            self.image = image

    class StoryOriginManager:
        def __init__(self):
            self.origins = {}
        def register(self, origin):
            self.origins[origin.id] = origin
        def get_all(self):
            return sorted(self.origins.values(), key=lambda x: x.name)
        def get(self, origin_id):
            return self.origins.get(origin_id)

    story_origin_manager = StoryOriginManager()

    class Quest:
        def __init__(self, id, name, description=""):
            self.id, self.name, self.description, self.state, self.ticks = id, name, description, "unknown", []
        def add_tick(self, t): self.ticks.append(t)
        def start(self):
            if self.state in ["unknown", "known"]:
                self.state = "active"
                if self.ticks: self.ticks[0].state = "active"
                renpy.notify(f"Quest Started: {self.name}")
                if renpy.has_label(f"QUEST__{self.id}__started"): renpy.call(f"QUEST__{self.id}__started")
        def complete(self):
            self.state = "passed"
            renpy.notify(f"Quest Completed: {self.name}")
            if renpy.has_label(f"QUEST__{self.id}__passed"): renpy.call(f"QUEST__{self.id}__passed")

    class QuestManager:
        def __init__(self): self.quests, self.start_triggers = {}, {}
        def add_quest(self, q): self.quests[q.id] = q
        def start_quest(self, qid):
            q = self.quests.get(qid)
            if q: q.start()
        def complete_quest(self, qid):
            q = self.quests.get(qid)
            if q: q.complete()
        def update_goal(self, qid, gid, status="active"):
            target_quests = [self.quests[qid]] if qid and qid in self.quests else self.quests.values()
            
            for q in target_quests:
                for t in q.ticks:
                    if t.id == gid:
                        t.state = status
                        if status == "complete":
                            t.current_value = t.required_value
                # Check for quest completion if manual update
                if status == "complete":
                    all_c = True
                    for t in q.ticks:
                        if t.state != "complete":
                            all_c = False
                            break
                    if all_c: q.complete()
        def register_start_trigger(self, qid, data): self.start_triggers[qid] = data
        def handle_event(self, etype, **kwargs):
            for qid, trigger in self.start_triggers.items():
                q = self.quests.get(qid)
                if q and q.state == "unknown" and self._match(trigger, etype, **kwargs): q.start()
            for q in self.quests.values():
                if q.state == "active":
                    any_done = False
                    for t in q.ticks:
                        if t.check_trigger(etype, **kwargs):
                            any_done = True
                            if t.flow_label and renpy.has_label(t.flow_label): renpy.call(t.flow_label)
                    if any_done:
                        all_c = True
                        for t in q.ticks:
                            if t.state != "complete":
                                all_c = False
                                if t.state in ["hidden", "shown"]: t.state = "active"
                                break
                        if all_c: q.complete()
        def _match(self, t, etype, **kwargs):
            if t.get("event") != etype: return False
            for k, v in t.items():
                if k not in ["event", "cond"] and str(kwargs.get(k)) != str(v): return False
            if t.get("cond"):
                return safe_eval_bool(t["cond"], {"player": pc, "rpg_world": rpg_world, "kwargs": kwargs, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level})
            return True

    quest_manager = QuestManager()

    # --- DEBUG HELPERS ---
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

    # --- CORE ENTITY ---
    class Entity(SpatialObject, TaggedObject):
        def __init__(self, id, name, description="", label=None, x=0, y=0, tags=None, factions=None, sprite=None, **kwargs):
            SpatialObject.__init__(self, x, y)
            TaggedObject.__init__(self, tags)
            self.factions = set(factions or [])
            self.id, self.name, self.description, self.label = id, name, description, label
            self.sprite = sprite
        def interact(self):
            if self.label: renpy.jump(self.label)
            else: renpy.say(None, f"You see {self.name}. {self.description}")

    class Inventory(Entity):
        def __init__(self, id, name, items=None, blocked_tags=None, allowed_tags=None, **kwargs):
            super(Inventory, self).__init__(id, name, **kwargs)
            self.items, self.gold = [], 0
            if items:
                for item_id in items:
                    it = item_manager.get(item_id)
                    if it: self.items.append(it)
            self.blocked_tags = set(blocked_tags or [])
            self.allowed_tags = set(allowed_tags or [])  # empty = allow all
        
        def can_accept_item(self, item):
            """Check if item can be added based on tag restrictions"""
            item_tags = getattr(item, 'tags', set())
            if self.blocked_tags and item_tags & self.blocked_tags:
                return False
            if self.allowed_tags and not (item_tags & self.allowed_tags):
                return False
            return True
        
        def add_item(self, i, force=False):
            if not force and not self.can_accept_item(i):
                return False
            self.items.append(i)
            event_manager.dispatch("ITEM_GAINED", item=i.name, total=len([x for x in self.items if x.name == i.name]))
            return True
        
        def remove_item(self, i):
            if i in self.items:
                self.items.remove(i)
                return True
            return False
        
        def transfer_to(self, i, target):
            if not target.can_accept_item(i):
                return False
            if self.remove_item(i):
                target.add_item(i, force=True)
                return True
            return False
        
        def get_items_with_tag(self, tag):
            return [i for i in self.items if hasattr(i, 'tags') and tag in i.tags]
        
        def get_items_without_tag(self, tag):
            return [i for i in self.items if not hasattr(i, 'tags') or tag not in i.tags]

    class Container(Inventory):
        def __init__(self, id, name, **kwargs):
            super(Container, self).__init__(id, name, **kwargs)
        def interact(self): renpy.show_screen("container_screen", container=self)

    class Shop(Inventory):
        def __init__(self, id, name, buy_mult=1.2, sell_mult=0.6, **kwargs):
            super(Shop, self).__init__(id, name, **kwargs)
            self.buy_mult, self.sell_mult = buy_mult, sell_mult
        def get_buy_price(self, i): return int(i.value * self.buy_mult)
        def get_sell_price(self, i): return int(i.value * self.sell_mult)
        def interact(self): renpy.show_screen("shop_screen", shop=self)

    # --- STAT SYSTEM ---
    class StatBlock:
        """Flexible stat container that loads stats from data"""
        def __init__(self, stats_dict=None):
            self._stats = stats_dict or {}
            # Provide defaults for required stats
            self._stats.setdefault('hp', 100)
            self._stats.setdefault('max_hp', 100)
        
        def __getattr__(self, name):
            if name.startswith('_'):
                raise AttributeError(name)
            return self._stats.get(name, 0)
        
        def __setattr__(self, name, value):
            if name.startswith('_'):
                super().__setattr__(name, value)
            else:
                self._stats[name] = value
        
        def get(self, name, default=0):
            return self._stats.get(name, default)
        
        def set(self, name, value):
            self._stats[name] = value
        
        def keys(self):
            return self._stats.keys()
        
        def items(self):
            return self._stats.items()

    # Legacy alias for backward compatibility
    class RPGStats(StatBlock):
        def __init__(self, s=10, d=10, i=10, c=10):
            super().__init__({
                'strength': s, 'dexterity': d, 'intelligence': i, 'charisma': c,
                'hp': 100, 'max_hp': 100
            })

    # --- SLOT SYSTEM ---
    class SlotRegistry:
        """Manages equipment slot definitions and body types"""
        def __init__(self):
            self.slots = {}  # slot_id -> {"name": str, "unequips": set}
            self.body_types = {}  # body_type_id -> [slot_ids]
        
        def register_slot(self, slot_id, name, unequips=None):
            self.slots[slot_id] = {"name": name, "unequips": set(unequips or [])}
        
        def register_body_type(self, type_id, name, slots):
            self.body_types[type_id] = {"name": name, "slots": slots}
        
        def get_slots_for_body(self, body_type):
            bt = self.body_types.get(body_type, {})
            return bt.get("slots", [])
        
        def get_conflicting_slots(self, slot_id):
            """Get slots that would be unequipped when equipping to slot_id"""
            conflicts = set()
            slot_def = self.slots.get(slot_id, {})
            # Direct unequips from this slot
            conflicts.update(slot_def.get("unequips", []))
            # Reverse: slots that list this slot in their unequips
            for other_id, other_def in self.slots.items():
                if slot_id in other_def.get("unequips", []):
                    conflicts.add(other_id)
            return conflicts

    slot_registry = SlotRegistry()

    # --- CHARACTER ---
    class RPGCharacter(Inventory):
        def __init__(self, id, name, stats=None, location_id=None, factions=None, body_type="humanoid", base_image=None, td_sprite=None, affinity=0, schedule=None, companion_mods=None, is_companion=False, **kwargs):
            super(RPGCharacter, self).__init__(id, name, **kwargs)
            self.stats = stats if isinstance(stats, StatBlock) else StatBlock(stats) if stats else StatBlock()
            self.factions = set(factions or [])
            self.affinity = affinity  # -100 to 100
            self.schedule = schedule or {}  # "HH:MM": "loc_id"
            self.body_type = body_type
            self.base_image = base_image
            self.companion_mods = companion_mods or {}
            self.is_companion = is_companion
            self.following = False
            
            # Determine TD Sprite
            if td_sprite:
                self.td_sprite = td_sprite
            else:
                # Default to gender-based sprite if base_image hints at it
                if base_image and "female" in base_image.lower():
                    self.td_sprite = "images/topdown/chars/female_base.png"
                else:
                    self.td_sprite = "images/topdown/chars/male_base.png"
            self.equipped_slots = {}  # slot_id -> Item
            self.location_id = location_id
            self.pchar = Character(name)
            self.gold = 100
            self.dialogue_history = set()
            # Legacy compatibility
            self.equipped_items = self.equipped_slots
            self.active_perks = []
            self.active_statuses = []
        
        def change_affinity(self, amount):
            self.affinity = max(-100, min(100, self.affinity + amount))
            status = "Neutral"
            if self.affinity >= 50: status = "Friendly"
            elif self.affinity <= -50: status = "Hostile"
            renpy.notify(f"{self.name} is now {status} ({self.affinity})")

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
            # Show the character hub menu via the flow queue for context safety
            renpy.store._interact_target_char = self
            import store
            store.flow_queue.queue_label("_char_interaction_wrapper")
        
        def mark_as_met(self):
            wiki_manager.unlock(self.name, self.description)
        
        def is_member_of(self, faction_id):
            return faction_id in self.factions
        
        def join_faction(self, faction_id):
            self.factions.add(faction_id)
        
        def leave_faction(self, faction_id):
            self.factions.discard(faction_id)
        
        def can_equip_to_slot(self, item, slot_id):
            """Check if item can be equipped to slot"""
            valid_slots = slot_registry.get_slots_for_body(self.body_type)
            if slot_id not in valid_slots:
                return False, "Invalid slot for this body type"
            item_slots = getattr(item, 'equip_slots', [])
            if item_slots and slot_id not in item_slots:
                return False, "Item cannot be equipped to this slot"
            return True, "OK"
        
        def equip(self, item, slot_id):
            """Equip item to slot, handling conflicts"""
            can, msg = self.can_equip_to_slot(item, slot_id)
            if not can:
                return False, msg
            
            # Unequip conflicting slots
            conflicts = slot_registry.get_conflicting_slots(slot_id)
            for conflict_slot in conflicts:
                if conflict_slot in self.equipped_slots:
                    self.unequip(conflict_slot)
            
            # Unequip current item in target slot
            if slot_id in self.equipped_slots:
                self.unequip(slot_id)
            
            # Equip
            self.equipped_slots[slot_id] = item
            if item in self.items:
                self.items.remove(item)
            return True, "Equipped"
        
        def unequip(self, slot_id):
            """Unequip item from slot back to inventory"""
            if slot_id not in self.equipped_slots:
                return False
            item = self.equipped_slots.pop(slot_id)
            self.items.append(item)
            return True
        
        def apply_story_origin(self, origin):
            """Deprecated: logic moved to intro flow"""
            pass
        
        def get_equipped_in_slot(self, slot_id):
            return self.equipped_slots.get(slot_id)
        
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
        
        def add_status(self, status_id, duration_minutes=None):
            s = status_manager.get(status_id)
            if not s:
                return False, "Unknown status"
            expires = None
            if duration_minutes:
                expires = time_manager.total_minutes + int(duration_minutes)
            for e in self.active_statuses:
                if e["id"] == status_id:
                    e["expires_at"] = expires
                    return True, "Status refreshed"
            self.active_statuses.append({"id": status_id, "expires_at": expires})
            return True, "Status added"
        
        def remove_status(self, status_id):
            before = len(self.active_statuses)
            self.active_statuses[:] = [e for e in self.active_statuses if e["id"] != status_id]
            return len(self.active_statuses) != before
        
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

    class Lock(object):
        def __init__(self, ltype="physical", difficulty=1, keys=None, locked=True):
            self.type = ltype
            self.difficulty = difficulty
            self.keys = set(keys or [])
            self.locked = locked
        
        def unlock(self, key_id):
            if key_id in self.keys:
                self.locked = False
                return True
            return False
            
        def pick(self, skill_level=0):
            # Simple check for now (placeholder for minigame)
            # Roll or stat check
            if skill_level + renpy.random.randint(1, 20) >= self.difficulty + 10:
                self.locked = False
                return True
            return False
            
        def lock(self):
            self.locked = True

    class Location(SpatialObject, TaggedObject):
        def __init__(self, id, name, description, map_image=None, obstacles=None, entities=None, encounters=None, scavenge=None, x=0, y=0, tags=None, factions=None,
                parent_id=None, ltype="world", map_x=0, map_y=0, zoom_range=(0.0, 99.0), floor_idx=0):
            SpatialObject.__init__(self, x, y)
            TaggedObject.__init__(self, tags)
            self.factions = set(factions or [])
            self.id, self.name, self.description = id, name, description
            self.map_image = map_image
            self.obstacles = obstacles or set()
            self.entities = entities or []
            self.encounters = encounters or []
            self.scavenge = scavenge or []
            self.visited = False
            
            # Map Hierarchy Fields
            self.parent_id = parent_id
            self.ltype = ltype # world, country, city, structure, floor
            self.map_x = map_x
            self.map_y = map_y
            self.min_zoom, self.max_zoom = zoom_range
            self.floor_idx = floor_idx
        
        @property
        def characters(self):
            return [c for c in rpg_world.characters.values() if getattr(c, 'location_id', None) == self.id and c.id != pc.id]
        
        def get_entities_with_tag(self, tag):
            return [e for e in self.entities if hasattr(e, 'tags') and tag in e.get('tags', [])]
        
        @property
        def children(self):
            # Return immediate children based on parent_id
            return [l for l in rpg_world.locations.values() if l.parent_id == self.id]

    class MapManager:
        def __init__(self):
            self.zoom = 1.0
            self.target_zoom = 1.0  # For smooth zoom animation
            self.cam_x = 0
            self.cam_y = 0
            self.search_query = ""
            self.selected_structure = None
            self.selected_location = None  # For location info popup
        
        def set_zoom(self, z):
            """Set target zoom for smooth animation"""
            self.target_zoom = max(0.5, min(z, 5.0))
        
        def update_zoom(self, adj_x, adj_y, view_w, view_h):
            """Lerp zoom toward target while maintaining center point"""
            if abs(self.zoom - self.target_zoom) < 0.001:
                return None  # Already at target, no update needed
            
            # Get current center point in world coords BEFORE zoom changes
            old_zoom = self.zoom
            center_world_x = (adj_x.value + view_w / 2) / old_zoom
            center_world_y = (adj_y.value + view_h / 2) / old_zoom
            
            # Lerp zoom (fast but smooth), snap when very close
            if abs(self.zoom - self.target_zoom) < 0.01:
                self.zoom = self.target_zoom
            else:
                lerp_factor = 0.2
                self.zoom = self.zoom + (self.target_zoom - self.zoom) * lerp_factor
            
            # Calculate new scroll position to maintain center (always, including final frame)
            new_adj_x = center_world_x * self.zoom - view_w / 2
            new_adj_y = center_world_y * self.zoom - view_h / 2
            
            return (new_adj_x, new_adj_y)
            
        def get_visible_markers(self):
            # Return list of locations relevant to current zoom
            visible = []
            for loc in rpg_world.locations.values():
                # Search Filter
                if self.search_query and self.search_query.lower() not in loc.name.lower():
                    continue
                
                # Zoom Filter (if not searching)
                if not self.search_query:
                    if loc.min_zoom > self.zoom or loc.max_zoom < self.zoom:
                        continue
                    
                    # Hierarchy Filter: If structure is selected, only show its floors (if zoomed appropriately?)
                    # Simplified: Just show everything in range.
                    # Or: If zoomed in high (structure level), show floors?
                    pass

                visible.append(loc)
            return visible
            
        def search(self, query):
            self.search_query = query.strip()

        def select_location(self, loc):
            """Select a location - opens info popup"""
            self.selected_location = loc
            if loc.ltype == 'structure':
                self.selected_structure = loc
            else:
                self.selected_structure = None
        
        def close_location_popup(self):
            """Close the location info popup"""
            self.selected_location = None
        
        def travel_to_location(self, loc):
            """Travel to the selected location"""
            if not loc:
                return False
            if not allow_unvisited_travel and not loc.visited and loc.id != rpg_world.current_location_id:
                renpy.notify("You haven't discovered this location yet.")
                return False
            # Advance time based on map distance
            curr = rpg_world.current_location
            if curr and loc.id != curr.id:
                dx = float(loc.map_x - curr.map_x)
                dy = float(loc.map_y - curr.map_y)
                dist = (dx * dx + dy * dy) ** 0.5
                travel_mins = max(5, int(dist / 100.0 * 10))
                time_manager.advance(travel_mins)
                renpy.notify(f"Traveled to {loc.name} (+{travel_mins}m)")
            if rpg_world.move_to(loc.id):
                self.selected_location = None
                # Hide map and show the new location
                renpy.hide_screen("map_browser")
                if renpy.has_label("_post_travel_setup"):
                    renpy.call("_post_travel_setup")
                return True
            return False
        
        def center_on_player(self, adj_x, adj_y, view_w, view_h, pad):
            """Center the map view on the player's current location"""
            if not rpg_world.current_location_id:
                return
                
            loc = rpg_world.locations.get(rpg_world.current_location_id)
            if not loc:
                return
                
            # Calculate center position in map coords (including padding)
            center_x = (loc.map_x + pad) * self.zoom
            center_y = (loc.map_y + pad) * self.zoom
            
            # Update adjustments to center the view
            adj_x.value = center_x - view_w / 2
            adj_y.value = center_y - view_h / 2
            
        def input_search(self):
            renpy.call_in_new_context("map_search_input_label")

    map_manager = MapManager()

    class GameWorld:
        def __init__(self): self.locations, self.characters, self.shops, self.current_location_id = {}, {}, {}, None
        @property
        def actor(self): return pc
        @property
        def current_location(self): return self.locations.get(self.current_location_id)
        
        def update_schedules(self):
            for c in self.characters.values():
                if c.id != "player":
                    if not getattr(c, "following", False):
                        c.check_schedule()
            party_manager.sync_followers()

        def add_location(self, l):
            self.locations[l.id] = l
            if not self.current_location_id: self.current_location_id = l.id
        def add_character(self, c):
            self.characters[c.id] = c
            # Inject directly into Ren'Py store to ensure accessibility across contexts
            renpy.store.__dict__[c.id] = c
        def move_to(self, lid):
            if lid in self.locations:
                self.current_location_id = lid
                was_visited = self.locations[lid].visited
                self.locations[lid].visited = True
                if not was_visited:
                    renpy.notify(f"Discovered {self.locations[lid].name}")
                    event_manager.dispatch("LOCATION_DISCOVERED", location=lid)
                    flag_set(f"discover_{lid}", True)
                event_manager.dispatch("LOCATION_VISITED", location=lid)
                self._maybe_trigger_encounter(self.locations[lid])
                party_manager.sync_followers()
                return True
            return False

        def _maybe_trigger_encounter(self, location):
            if not location or not location.encounters:
                return
            candidates = []
            for enc in location.encounters:
                if not isinstance(enc, dict):
                    continue
                label = enc.get("label")
                if not label or not renpy.has_label(label):
                    continue
                enc_id = enc.get("id", label)
                if enc.get("once") and enc_id in encounter_history:
                    continue
                cond = enc.get("cond")
            if cond and not safe_eval_bool(cond, {"pc": pc, "rpg_world": rpg_world, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level}):
                continue
                try:
                    chance = float(enc.get("chance", 1.0))
                except Exception:
                    chance = 1.0
                if chance > 1.0:
                    chance = chance / 100.0
                if renpy.random.random() <= chance:
                    candidates.append((enc_id, label, enc.get("once")))
            if not candidates:
                return
            enc_id, label, once = renpy.random.choice(candidates)
            if once:
                encounter_history.add(enc_id)
            try:
                import store
                if hasattr(store, "flow_queue"):
                    store.flow_queue.queue_label(label)
                    return
            except Exception:
                pass
            renpy.call_in_new_context(label)

    rpg_world = GameWorld()
    pc = RPGCharacter("player", "Player", base_image="characters/male_fit.png")
    rpg_world.add_character(pc)

    class PartyManager:
        def __init__(self):
            self.followers = []
            self.max_followers = 2
        
        def add_follower(self, char_id):
            c = rpg_world.characters.get(char_id)
            if not c:
                return False, "Unknown follower"
            if c.id in self.followers:
                return False, "Already following"
            if len(self.followers) >= self.max_followers:
                return False, "Party full"
            c.following = True
            c.location_id = pc.location_id
            self.followers.append(c.id)
            renpy.notify(f"{c.name} is now following you.")
            return True, "Follower added"
        
        def remove_follower(self, char_id):
            if char_id not in self.followers:
                return False, "Not following"
            c = rpg_world.characters.get(char_id)
            if c:
                c.following = False
            self.followers.remove(char_id)
            return True, "Follower removed"
        
        def get_followers(self):
            return [rpg_world.characters[cid] for cid in self.followers if cid in rpg_world.characters]
        
        def get_stat_bonus(self, stat_name):
            bonus = 0
            for c in self.get_followers():
                bonus += int(c.companion_mods.get(stat_name, 0))
            return bonus
        
        def sync_followers(self):
            for c in self.get_followers():
                c.location_id = pc.location_id

    party_manager = PartyManager()

    def companion_add(char_id):
        ok, msg = party_manager.add_follower(char_id)
        renpy.notify(msg)
        return ok

    def companion_remove(char_id):
        ok, msg = party_manager.remove_follower(char_id)
        if ok:
            renpy.notify(msg)
        return ok
    
    # --- ACHIEVEMENT SYSTEM ---
    class Achievement(object):
        """Represents an unlockable achievement with rarity tiers and event triggers."""
        RARITY_COLORS = {
            "common": "#9d9d9d",      # Gray
            "uncommon": "#1eff00",    # Green
            "rare": "#0070dd",        # Blue
            "epic": "#a335ee",        # Purple
            "legendary": "#ff8000",   # Orange
        }
        RARITY_POINTS = {
            "common": 5,
            "uncommon": 10,
            "rare": 25,
            "epic": 50,
            "legendary": 100,
        }
        
        def __init__(self, id, name, description, icon="🏆", rarity="common", tags=None, trigger=None, ticks_required=1):
            self.id = id
            self.name = name
            self.description = description
            self.icon = icon
            self.rarity = rarity.lower() if rarity else "common"
            self.tags = set(tags or [])
            self.trigger = trigger or {}  # {event: "EVENT_NAME", key: value, cond: "..."}
            self.ticks_required = max(1, int(ticks_required))
        
        @property
        def color(self):
            return self.RARITY_COLORS.get(self.rarity, "#9d9d9d")
        
        @property
        def points(self):
            return self.RARITY_POINTS.get(self.rarity, 5)
        
        def check_trigger(self, etype, **kwargs):
            """Check if an event matches this achievement's trigger."""
            if not self.trigger or self.trigger.get("event") != etype:
                return False
            # Check all key-value pairs in trigger (except reserved keys)
            for k, v in self.trigger.items():
                if k not in ["event", "cond"] and str(kwargs.get(k)) != str(v):
                    return False
            # Check condition if present
            if self.trigger.get("cond"):
                if not safe_eval_bool(self.trigger["cond"], {"player": pc, "rpg_world": rpg_world, "kwargs": kwargs, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level}):
                    return False
            return True
    
    # Persistent progress for multi-tick achievements
    default persistent.achievement_progress = {}
    
    class AchievementManager:
        """Manages achievement definitions, tracking, and event-based unlocks."""
        def __init__(self):
            self.registry = {}  # id -> Achievement
        
        def register(self, achievement):
            """Register an achievement definition."""
            self.registry[achievement.id] = achievement
        
        def get(self, ach_id):
            """Get achievement by ID."""
            return self.registry.get(ach_id)
        
        def get_progress(self, ach_id):
            """Get current tick progress for an achievement."""
            if persistent.achievement_progress is None:
                persistent.achievement_progress = {}
            return persistent.achievement_progress.get(ach_id, 0)
        
        def add_tick(self, ach_id, count=1):
            """Add ticks to an achievement's progress. Auto-unlocks when complete."""
            if persistent.achievement_progress is None:
                persistent.achievement_progress = {}
            
            ach = self.registry.get(ach_id)
            if not ach or self.is_unlocked(ach_id):
                return False
            
            current = persistent.achievement_progress.get(ach_id, 0)
            new_progress = current + count
            persistent.achievement_progress[ach_id] = new_progress
            
            if new_progress >= ach.ticks_required:
                self.unlock(ach_id)
                return True
            return False
        
        def handle_event(self, etype, **kwargs):
            """Check all achievements for matching triggers."""
            for ach in self.registry.values():
                if not self.is_unlocked(ach.id) and ach.check_trigger(etype, **kwargs):
                    self.add_tick(ach.id)
        
        def unlock(self, ach_id):
            """Unlock an achievement for the player."""
            if persistent.achievements is None:
                persistent.achievements = set()
            
            if ach_id in self.registry and ach_id not in persistent.achievements:
                persistent.achievements.add(ach_id)
                ach = self.registry[ach_id]
                renpy.show_screen("achievement_toast", ach=ach)
                renpy.restart_interaction()
                return True
            return False
        
        def is_unlocked(self, ach_id):
            """Check if achievement is unlocked."""
            if persistent.achievements is None:
                return False
            return ach_id in persistent.achievements
        
        def get_all(self):
            """Get all registered achievements."""
            return sorted(self.registry.values(), key=lambda x: (x.rarity != "legendary", x.rarity != "epic", x.name))
        
        def get_unlocked(self):
            """Get all unlocked achievements."""
            if persistent.achievements is None:
                return []
            return [self.registry[aid] for aid in persistent.achievements if aid in self.registry]
        
        def get_locked(self):
            """Get all locked achievements."""
            if persistent.achievements is None:
                return list(self.registry.values())
            return [a for a in self.registry.values() if a.id not in persistent.achievements]
        
        @property
        def total_points(self):
            """Calculate total achievement points."""
            return sum(a.points for a in self.get_unlocked())
        
        @property
        def progress_text(self):
            """Get progress as text (e.g., '3/10')."""
            unlocked = len(self.get_unlocked())
            total = len(self.registry)
            return f"{unlocked}/{total}"

    ach_mgr = AchievementManager()
    achievements = ach_mgr  # Global alias

    def contested_check(stat_name, difficulty=10, target=None, success_label=None, fail_label=None):
        """
        Roll 1d20 + stat modifier against a difficulty or opposing stat (if target provided).
        If success_label/fail_label are provided and exist, jump accordingly; otherwise returns bool.
        """
        roll = renpy.random.randint(1, 20)
        actor_stat = pc.get_stat_total(stat_name)
        target_dc = difficulty
        if target and hasattr(target, "stats"):
            target_dc = target.get_stat_total(stat_name) if hasattr(target, "get_stat_total") else getattr(target.stats, stat_name, difficulty)
        total = roll + (actor_stat - 10) // 2
        passed = total >= target_dc
        renpy.notify(f"Check {stat_name}: {total} vs {target_dc} ({'pass' if passed else 'fail'})")
        if success_label and passed and renpy.has_label(success_label):
            renpy.jump(success_label)
        elif fail_label and not passed and renpy.has_label(fail_label):
            renpy.jump(fail_label)
        return passed

    def rest(hours=1, require_safe=True, allow_camp=True, camp_ambush_chance=0.2):
        loc = rpg_world.current_location
        used_camp = False
        if require_safe and loc and "safe" not in loc.tags:
            if allow_camp:
                kit = consume_item_by_tag("camp")
                if kit:
                    used_camp = True
                    renpy.notify("You set up a small camp.")
                    event_manager.dispatch("CAMP_USED", location=loc.id if loc else None)
                else:
                    renpy.notify("This doesn't feel safe enough to rest.")
                    return False
            else:
                renpy.notify("This doesn't feel safe enough to rest.")
                return False
        time_manager.advance(int(hours * 60))
        heal = int(hours * 10)
        pc.stats.hp = min(pc.stats.max_hp, pc.stats.hp + heal)
        renpy.notify(f"Rested {hours}h. HP +{heal}.")
        if loc:
            event_manager.dispatch("RESTED", hours=hours, location=loc.id, used_camp=used_camp)
        if used_camp and renpy.random.random() < camp_ambush_chance:
            label = "SCENE__camp_ambush__flow"
            try:
                import store
                if renpy.has_label(label) and hasattr(store, "flow_queue"):
                    store.flow_queue.queue_label(label)
                elif renpy.has_label(label):
                    renpy.call_in_new_context(label)
                else:
                    event_manager.dispatch("CAMP_AMBUSH", location=loc.id if loc else None)
            except Exception:
                event_manager.dispatch("CAMP_AMBUSH", location=loc.id if loc else None)
        return True

    def scavenge_location(loc=None):
        if not loc:
            loc = rpg_world.current_location
        if not loc:
            renpy.notify("There's nowhere to search.")
            return False
        if not getattr(loc, "scavenge", None):
            renpy.notify("You don't find anything useful here.")
            return False
        key = f"{loc.id}:{time_manager.day}"
        if scavenge_history.get(key):
            renpy.notify("You've already searched here today.")
            return False
        results = []
        for entry in loc.scavenge:
            if not isinstance(entry, dict):
                continue
            cond = entry.get("cond")
            if cond and not safe_eval_bool(cond, {"pc": pc, "rpg_world": rpg_world, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level}):
                continue
            try:
                chance = float(entry.get("chance", 1.0))
            except Exception:
                chance = 1.0
            if chance > 1.0:
                chance = chance / 100.0
            if renpy.random.random() > chance:
                continue
            item_id = entry.get("item")
            if not item_id:
                continue
            if "min" in entry or "max" in entry:
                lo = int(entry.get("min", 1))
                hi = int(entry.get("max", lo))
                count = renpy.random.randint(lo, hi)
            else:
                count = int(entry.get("count", 1))
            count = max(1, count)
            for _ in range(count):
                it = item_manager.get(item_id)
                if it:
                    pc.add_item(it)
            results.append(f"{item_id} x{count}")
        scavenge_history[key] = True
        if results:
            renpy.notify("Found: " + ", ".join(results))
            event_manager.dispatch("SCAVENGED", location=loc.id, items=results)
            return True
        renpy.notify("You come up empty-handed.")
        return False

    class Note(object):
        def __init__(self, id, name, content, tags=None):
            self.id = id
            self.name = name
            self.content = content
            self.tags = set(tags or [])

    class JournalManager:
        def __init__(self):
            self.entries = {} # People: name -> description
            self.notes = {}   # Notes: id -> Note object
        
        # --- People Logic (Legacy Wiki) ---
        def register(self, n, d): 
            self.entries[n] = d
            
        def unlock(self, n, d=None):
            if n not in persistent.met_characters:
                persistent.met_characters.add(n)
                if d: self.register(n, d)
                renpy.notify(f"New Person Met: {n}")
                event_manager.dispatch("CHAR_MET", char=n)
        
        @property
        def met_list(self): 
            return [(n, self.entries.get(n, "No data.")) for n in sorted(persistent.met_characters)]

        # --- Note Logic ---
        def register_note(self, note):
            self.notes[note.id] = note
            
        def unlock_note(self, note_id):
            if note_id in self.notes:
                if persistent.unlocked_notes is None:
                    persistent.unlocked_notes = set()
                
                if note_id not in persistent.unlocked_notes:
                    persistent.unlocked_notes.add(note_id)
                    renpy.notify(f"Note Found: {self.notes[note_id].name}")
                    event_manager.dispatch("NOTE_UNLOCKED", note=note_id)
        
        def get_unlocked_notes(self):
            if persistent.unlocked_notes is None:
                return []
            return [self.notes[nid] for nid in persistent.unlocked_notes if nid in self.notes]

    wiki_manager = JournalManager()
    journal_manager = wiki_manager # Alias

    def from_dict(cls, data, id=None, **defaults):
        """
        Convert a YAML dict to class constructor kwargs.
        Merges defaults with data (data takes precedence).
        Optionally injects 'id' if provided.
        """
        params = dict(defaults)
        params.update(data)
        if id is not None:
            params['id'] = id
        return cls(**params)

    def reset_game_data():
        """Clear runtime registries before reloading generated data."""
        item_manager.registry.clear()
        slot_registry.slots.clear()
        slot_registry.body_types.clear()
        crafting_manager.recipes.clear()
        dialogue_manager.options.clear()
        story_origin_manager.origins.clear()
        quest_manager.quests.clear()
        quest_manager.start_triggers.clear()
        ach_mgr.registry.clear()
        perk_manager.registry.clear()
        status_manager.registry.clear()
        bond_manager.bonds.clear()
        wiki_manager.entries.clear()
        wiki_manager.notes.clear()
        rpg_world.locations.clear()
        rpg_world.shops.clear()
        rpg_world.characters.clear()
        rpg_world.current_location_id = None
        # Re-register the player to keep references stable across reloads
        rpg_world.add_character(pc)
    
    def instantiate_all():
        reset_game_data()
        try:
            with renpy.file(".generated/generated_json.json") as f:
                data = json.load(f)
        except Exception as e:
            # If JSON is missing, we can't load metadata objects
            return

        # Slots (must be loaded before body types and characters)
        for oid, p in data.get("slots", {}).items():
            slot_registry.register_slot(oid, p.get('name', oid), p.get('unequips', []))
        
        # Body Types (must be loaded before characters)
        for oid, p in data.get("body_types", {}).items():
            slot_registry.register_body_type(oid, p.get('name', oid), p.get('slots', []))

        # Items (now with tags and equip_slots)
        for oid, p in data.get("items", {}).items():
            item_manager.register(oid, from_dict(Item, p, id=oid))


        
        # Locations
        for oid, p in data.get("locations", {}).items():
            obstacles = set(tuple(obs) for obs in p.get("obstacles", [])) if isinstance(p.get("obstacles"), list) else set()
            
            # Parse zoom range
            z_raw = p.get('zoom_range', [])
            if z_raw and len(z_raw) >= 2:
                try: z_range = (float(z_raw[0]), float(z_raw[1]))
                except: z_range = (0.0, 99.0)
            else:
                z_range = (0.0, 99.0)

            loc = Location(
                oid, p['name'], p['description'], 
                p.get('map_image'), obstacles, p.get('entities'), p.get('encounters'), p.get('scavenge'),
                tags=p.get('tags', []),
                factions=p.get('factions', []),
                parent_id=p.get('parent'),
                ltype=p.get('map_type', 'world'),
                map_x=int(p.get('map_x', 0)),
                map_y=int(p.get('map_y', 0)),
                zoom_range=z_range,
                floor_idx=int(p.get('floor_idx', 0))
            )
            rpg_world.add_location(loc)
            
        # Characters (now with factions, body_type, stats, and tags)
        for oid, p in data.get("characters", {}).items():
            stats_data = p.get('stats', {})
            stats = StatBlock(stats_data) if stats_data else None
            char = RPGCharacter(
                oid, p['name'],
                stats=stats,
                description=p.get('description', ''),
                location_id=p.get('location'),
                base_image=p.get('base_image'),
                td_sprite=p.get('td_sprite'),
                x=p.get('x', 0),
                y=p.get('y', 0),
                label=p.get('label'),
                factions=p.get('factions', []),
                body_type=p.get('body_type', 'humanoid'),
                items=p.get('items', []),
                tags=p.get('tags', []),
                affinity=int(p.get('affinity', 0)),
                schedule=p.get('schedule', {}),
                companion_mods=p.get('companion_mods', {}),
                is_companion=bool(p.get('companion_mods'))
            )
            rpg_world.add_character(char)
                
        # Dialogue Options
        for oid, p in data.get("dialogue", {}).items():
            dialogue_manager.register(DialogueOption(
                oid,
                chars=p.get('chars', []),
                short_text=p.get('short', '...'),
                long_text=p.get('long', '...'),
                emoji=p.get('emoji', '💬'),
                label=p.get('label'),
                cond=p.get('cond'),
                tags=p.get('tags', []),
                memory=(str(p.get('memory', 'False')).lower() == 'true'),
                reason=p.get('reason')
            ))

        # Story Origins
        for oid, p in data.get("story_origins", {}).items():
            story_origin_manager.register(StoryOrigin(
                oid,
                name=p.get('name', oid),
                description=p.get('description', ''),
                pc_id=p.get('pc_id'),
                intro_label=p.get('intro_label'),
                image=p.get('image')
            ))

        # Shops
        for oid, p in data.get("shops", {}).items():
            # Shops are inventories with multipliers
            shop = Shop(
                oid,
                p.get('name', oid),
                buy_mult=p.get('buy_mult', 1.2),
                sell_mult=p.get('sell_mult', 0.6),
                items=p.get('items', [])
            )
            # Register in world shops
            # They are globals, but separated from characters to avoid map-spawn issues
            rpg_world.shops[oid] = shop
            renpy.store.__dict__[oid] = shop

        # Recipes
        for oid, p in data.get("recipes", {}).items():
            crafting_manager.register(Recipe(
                oid,
                p.get('name', oid),
                p.get('inputs', {}),
                p.get('output', {}),
                req_skill=p.get('req_skill'),
                tags=p.get('tags', [])
            ))

        # Notes
        for oid, p in data.get("notes", {}).items():
            wiki_manager.register_note(Note(
                oid,
                p.get('name', oid),
                p.get('body', ''),
                tags=p.get('tags', [])
            ))

        # Quests
        for oid, p in data.get("quests", {}).items():
            q = Quest(oid, p['name'], p.get('description', ''))
            for t_idx, tp in enumerate(p.get('ticks', [])):
                tick = QuestTick(tp['id'], tp['name'])
                tick.trigger_data = tp.get('trigger', {})
                tick.flow_label = tp.get('label')
                # Optional: if it's the first tick and quest is autostart, it might be active
                # But we handle state changes via commands/triggers
                q.add_tick(tick)
            quest_manager.add_quest(q)

        # Achievements
        for oid, p in data.get("achievements", {}).items():
            ach_mgr.register(Achievement(
                oid,
                p.get('name', oid),
                p.get('description', ''),
                icon=p.get('icon', '🏆'),
                rarity=p.get('rarity', 'common'),
                tags=p.get('tags', []),
                trigger=p.get('trigger', {}),
                ticks_required=p.get('ticks', 1)
            ))
        
        # Perks
        for oid, p in data.get("perks", {}).items():
            duration = p.get("duration")
            try:
                duration = int(duration) if duration is not None else None
            except Exception:
                duration = None
            perk_manager.register(Perk(
                oid,
                p.get('name', oid),
                p.get('description', ''),
                mods=p.get('mods', {}),
                tags=p.get('tags', []),
                duration_minutes=duration
            ))
        
        # Status Effects
        for oid, p in data.get("status_effects", {}).items():
            duration = p.get("duration")
            try:
                duration = int(duration) if duration is not None else None
            except Exception:
                duration = None
            status_manager.register(StatusEffect(
                oid,
                p.get('name', oid),
                p.get('description', ''),
                mods=p.get('mods', {}),
                tags=p.get('tags', []),
                duration_minutes=duration
            ))
        
        # Bonds
        for oid, p in data.get("bonds", {}).items():
            a = p.get("a")
            b = p.get("b")
            if a and b:
                bond_manager.register(Bond(
                    oid,
                    a,
                    b,
                    tags=p.get("tags", []),
                    stats=p.get("stats", {})
                ))

    instantiate_all()

default persistent.achievements = set()
default persistent.met_characters = set()
