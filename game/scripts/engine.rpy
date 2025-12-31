# Data system migrated to compile_data.py

init -10 python:
    import json
    import random
    import copy

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
        def __init__(self, name, description, weight=0, value=0, tags=None, equip_slots=None, outfit_part=None):
            TaggedObject.__init__(self, tags)
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

    class EventManager:
        def dispatch(self, etype, **kwargs): quest_manager.handle_event(etype, **kwargs)

    event_manager = EventManager()

    class TimeManager(object):
        def __init__(self, hour=8, minute=0):
            self.hour, self.minute = hour, minute
        @property
        def time_string(self): return "{:02d}:{:02d}".format(self.hour, self.minute)
        def advance(self, mins):
            self.minute += mins
            while self.minute >= 60:
                self.minute -= 60
                self.hour = (self.hour + 1) % 24

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
                try:
                    if not eval(self.trigger_data["cond"], {}, {"player": pc, "rpg_world": rpg_world, "kwargs": kwargs}): return False
                except: return False
            self.current_value = int(kwargs.get("total", self.current_value + 1))
            if self.current_value >= int(self.trigger_data.get("total", self.required_value)):
                self.state = "complete"
                return True
            return False

    class DialogueOption(object):
        def __init__(self, id, chars, short_text, long_text, emoji, label, cond=None, tags=None, memory=False):
            self.id = id
            self.chars = set(chars or [])
            self.short_text = short_text
            self.long_text = long_text
            self.emoji = emoji
            self.label = label
            self.cond = cond
            self.tags = tags or []
            self.memory = memory
        
        def is_available(self, char):
            if self.chars and char.id not in self.chars and "*" not in self.chars:
                return False
            if self.cond and str(self.cond).strip() and str(self.cond) != "True":
                try:
                    return eval(str(self.cond), {}, {"pc": pc, "char": char, "rpg_world": rpg_world, "quest_manager": quest_manager})
                except:
                    return False
            return True

    class DialogueManager:
        def __init__(self):
            self.options = {}
        def register(self, opt):
            self.options[opt.id] = opt
        def get_available(self, char):
            opts = [opt for opt in self.options.values() if opt.is_available(char)]
            return sorted(opts, key=lambda x: x.id)

    dialogue_manager = DialogueManager()

    class Archetype(object):
        def __init__(self, id, name, description, location_id, intro_label, stats=None, factions=None, items=None):
            self.id = id
            self.name = name
            self.description = description
            self.location_id = location_id
            self.intro_label = intro_label
            self.stats = stats or {}
            self.factions = factions or []
            self.items = items or []

    class ArchetypeManager:
        def __init__(self):
            self.archetypes = {}
        def register(self, arch):
            self.archetypes[arch.id] = arch
        def get_all(self):
            return sorted(self.archetypes.values(), key=lambda x: x.name)
        def get(self, arch_id):
            return self.archetypes.get(arch_id)

    archetype_manager = ArchetypeManager()

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
                try: return eval(t["cond"], {}, {"player": pc, "rpg_world": rpg_world, "kwargs": kwargs})
                except: return False
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
        def __init__(self, id, name, description="", label=None, x=0, y=0, tags=None, **kwargs):
            SpatialObject.__init__(self, x, y)
            TaggedObject.__init__(self, tags)
            self.id, self.name, self.description, self.label = id, name, description, label
        def interact(self):
            if self.label: renpy.jump(self.label)
            else: renpy.say(None, f"You see {self.name}. {self.description}")

    class Inventory(Entity):
        def __init__(self, id, name, blocked_tags=None, allowed_tags=None, **kwargs):
            super(Inventory, self).__init__(id, name, **kwargs)
            self.items, self.gold = [], 0
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
        def __init__(self, id, name, stats=None, location_id=None, factions=None, body_type="humanoid", **kwargs):
            super(RPGCharacter, self).__init__(id, name, **kwargs)
            self.stats = stats if isinstance(stats, StatBlock) else StatBlock(stats) if stats else StatBlock()
            self.factions = set(factions or [])
            self.body_type = body_type
            self.equipped_slots = {}  # slot_id -> Item
            self.location_id = location_id
            self.pchar = Character(name)
            self.gold = 100
            self.dialogue_history = set()
            # Legacy compatibility
            self.equipped_items = self.equipped_slots
        
        def __call__(self, what, *args, **kwargs):
            return self.pchar(what, *args, **kwargs)
        
        def interact(self):
            renpy.show_screen("char_interact_screen", char=self)
        
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
        
        def apply_archetype(self, archetype):
            """Initialize character stats, location, and items from an archetype"""
            # Set Stats
            for stat_name, value in archetype.stats.items():
                self.stats.set(stat_name, value)
            
            # Set Location
            self.location_id = archetype.location_id
            
            # Join Factions
            for faction_id in archetype.factions:
                self.join_faction(faction_id)
            
            # Add Items
            for item_id in archetype.items:
                item = item_manager.get(item_id)
                if item:
                    self.add_item(item, force=True)
            
            renpy.store.td_manager.setup(rpg_world.current_location)
        
        def get_equipped_in_slot(self, slot_id):
            return self.equipped_slots.get(slot_id)

    class Location(SpatialObject, TaggedObject):
        def __init__(self, id, name, description, map_image=None, obstacles=None, entities=None, x=0, y=0, tags=None,
                parent_id=None, ltype="world", map_x=0, map_y=0, zoom_range=(0.0, 99.0), floor_idx=0):
            SpatialObject.__init__(self, x, y)
            TaggedObject.__init__(self, tags)
            self.id, self.name, self.description = id, name, description
            self.map_image = map_image
            self.obstacles = obstacles or set()
            self.entities = entities or []
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
            return [c for c in rpg_world.characters.values() if c.location_id == self.id and c.name != pc.name]
        
        def get_entities_with_tag(self, tag):
            return [e for e in self.entities if hasattr(e, 'tags') and tag in e.get('tags', [])]
        
        @property
        def children(self):
            # Return immediate children based on parent_id
            return [l for l in rpg_world.locations.values() if l.parent_id == self.id]

    class MapManager:
        def __init__(self):
            self.zoom = 1.0
            self.cam_x = 0
            self.cam_y = 0
            self.search_query = ""
            self.selected_structure = None
        
        def set_zoom(self, z):
            self.zoom = max(0.5, min(z, 5.0))
            
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
            if loc.ltype == 'structure':
                self.selected_structure = loc
            else:
                self.selected_structure = None
            
            # Optional: Center camera?
            # For now just select logic
        
        def input_search(self):
            renpy.call_in_new_context("map_search_input_label")

    map_manager = MapManager()

    class GameWorld:
        def __init__(self): self.locations, self.characters, self.current_location_id = {}, {}, None
        @property
        def actor(self): return pc
        @property
        def current_location(self): return self.locations.get(self.current_location_id)
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
                self.locations[lid].visited = True
                event_manager.dispatch("LOCATION_VISITED", location=lid)
                return True
            return False

    rpg_world = GameWorld()
    pc = RPGCharacter("player", "Player")
    rpg_world.add_character(pc)
    class AchievementManager:
        def unlock(self, ach_id):
            if ach_id not in persistent.achievements:
                persistent.achievements.add(ach_id)
                renpy.notify(f"Achievement Unlocked: {ach_id}")

    ach_mgr = AchievementManager() # Internal name
    achievements = ach_mgr # Global alias for Markdown/Labels

    class WikiManager:
        def __init__(self): self.entries = {}
        def register(self, n, d): self.entries[n] = d
        def unlock(self, n, d=None):
            if n not in persistent.met_characters:
                persistent.met_characters.add(n)
                if d: self.register(n, d)
                renpy.notify(f"Wiki Unlock: {n}")
        @property
        def met_list(self): return [(n, self.entries.get(n, "No data.")) for n in sorted(persistent.met_characters)]

    wiki_manager = WikiManager()

    def instantiate_all():
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
            item_manager.register(oid, Item(
                p['name'], 
                p['description'], 
                p.get('weight', 0), 
                p.get('value', 0),
                tags=p.get('tags', []),
                equip_slots=p.get('equip_slots', []),
                outfit_part=p.get('outfit_part')
            ))
        
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
                p.get('map_image'), obstacles, p.get('entities'),
                tags=p.get('tags', []),
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
                x=p.get('x', 0),
                y=p.get('y', 0),
                label=p.get('label'),
                factions=p.get('factions', []),
                body_type=p.get('body_type', 'humanoid'),
                tags=p.get('tags', [])
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
                memory=(str(p.get('memory', 'False')).lower() == 'true')
            ))

        # Archetypes
        for oid, p in data.get("archetypes", {}).items():
            archetype_manager.register(Archetype(
                oid,
                name=p.get('name', oid),
                description=p.get('description', ''),
                location_id=p.get('location'),
                intro_label=p.get('intro_label'),
                stats=p.get('stats', {}),
                factions=p.get('factions', []),
                items=p.get('items', [])
            ))

        # Quests
        for oid, p in data.get("quests", {}).items():
            quest_manager.add_quest(Quest(oid, p['name'], p['description']))

    instantiate_all()

default persistent.achievements = set()
default persistent.met_characters = set()
