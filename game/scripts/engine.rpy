# Data system migrated to compile_data.py

init -10 python:
    import json
    import random
    import copy

    class Item:
        def __init__(self, name, description, weight=0, value=0, outfit_part=None):
            self.name, self.description, self.weight, self.value, self.outfit_part = name, description, weight, value, outfit_part

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

    class Entity(object):
        def __init__(self, name, description="", label=None, x=0, y=0, **kwargs):
            self.name, self.description, self.label, self.x, self.y = name, description, label, x, y
        def interact(self):
            if self.label: renpy.jump(self.label)
            else: renpy.say(None, f"You see {self.name}. {self.description}")

    class Inventory(Entity):
        def __init__(self, name, **kwargs):
            super(Inventory, self).__init__(name, **kwargs)
            self.items, self.gold = [], 0
        def add_item(self, i):
            self.items.append(i)
            event_manager.dispatch("ITEM_GAINED", item=i.name, total=len([x for x in self.items if x.name == i.name]))
        def remove_item(self, i):
            if i in self.items:
                self.items.remove(i)
                return True
            return False
        def transfer_to(self, i, target):
            if self.remove_item(i):
                target.add_item(i)
                return True
            return False

    class Container(Inventory):
        def __init__(self, name, id=None, **kwargs):
            super(Container, self).__init__(name, **kwargs)
            self.id = id
        def interact(self): renpy.show_screen("container_screen", container=self)

    class Shop(Inventory):
        def __init__(self, name, buy_mult=1.2, sell_mult=0.6, **kwargs):
            super(Shop, self).__init__(name, **kwargs)
            self.buy_mult, self.sell_mult = buy_mult, sell_mult
        def get_buy_price(self, i): return int(i.value * self.buy_mult)
        def get_sell_price(self, i): return int(i.value * self.sell_mult)
        def interact(self): renpy.show_screen("shop_screen", shop=self)

    class RPGStats:
        def __init__(self, s=10, d=10, i=10, c=10):
            self.strength, self.dexterity, self.intelligence, self.charisma = s, d, i, c
            self.hp = self.max_hp = 100

    class RPGCharacter(Inventory):
        def __init__(self, name, stats=None, location_id=None, **kwargs):
            super(RPGCharacter, self).__init__(name, **kwargs)
            self.stats, self.equipped_items, self.location_id, self.pchar, self.gold = stats or RPGStats(), {}, location_id, Character(name), 100
        def __call__(self, what, *args, **kwargs): return self.pchar(what, *args, **kwargs)
        def interact(self): renpy.show_screen("char_interact_screen", char=self)
        def mark_as_met(self): wiki_manager.unlock(self.name, self.description)

    class Location:
        def __init__(self, id, name, description, map_image=None, obstacles=None, entities=None):
            self.id, self.name, self.description = id, name, description
            self.map_image = map_image
            self.obstacles = obstacles or set()
            self.entities = entities or []
            self.visited = False
        @property
        def characters(self): return [c for c in rpg_world.characters.values() if c.location_id == self.id and c.name != pc.name]

    class GameWorld:
        def __init__(self): self.locations, self.characters, self.current_location_id = {}, {}, None
        @property
        def actor(self): return pc
        @property
        def current_location(self): return self.locations.get(self.current_location_id)
        def add_location(self, l):
            self.locations[l.id] = l
            if not self.current_location_id: self.current_location_id = l.id
        def add_character(self, c): self.characters[c.name] = c
        def move_to(self, lid):
            if lid in self.locations:
                self.current_location_id = lid
                self.locations[lid].visited = True
                event_manager.dispatch("LOCATION_VISITED", location=lid)
                return True
            return False

    rpg_world = GameWorld()
    pc = RPGCharacter("Player")
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

        # Items
        for oid, p in data.get("items", {}).items():
            item_manager.register(oid, Item(p['name'], p['description'], p['weight'], p['value'], p['outfit_part']))
        
        # Locations
        for oid, p in data.get("locations", {}).items():
            obstacles = set(tuple(obs) for obs in p.get("obstacles", []))
            loc = Location(oid, p['name'], p['description'], p.get('map_image'), obstacles, p.get('entities'))
            rpg_world.add_location(loc)
            
        # Characters
        for oid, p in data.get("characters", {}).items():
            rpg_world.add_character(RPGCharacter(p['name'], description=p.get('description', ''), location_id=p.get('location'), x=p.get('x', 0), y=p.get('y', 0)))
                
        # Quests
        for oid, p in data.get("quests", {}).items():
            quest_manager.add_quest(Quest(oid, p['name'], p['description']))

    instantiate_all()

default persistent.achievements = set()
default persistent.met_characters = set()
