python early:
    import os
    import re

    try:
        gamedir = renpy.config.gamedir
    except:
        gamedir = os.path.join(os.getcwd(), "game")
        if not os.path.exists(gamedir): gamedir = os.getcwd()

    class MarkdownParser:
        @staticmethod
        def parse(filepath):
            full_path = os.path.join(gamedir, filepath)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except: return None, None
            
            if "---" not in content: return None, None
            parts = content.split("---", 2)
            if len(parts) < 3: return None, None
            
            props = {}
            for line in parts[1].split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    props[k.strip()] = v.strip()
            return props, parts[2].strip()

        @staticmethod
        def load_all():
            output_file = os.path.join(gamedir, "generated", "generated_labels.rpy")
            if not os.path.exists(os.path.dirname(output_file)): os.makedirs(os.path.dirname(output_file))
            
            script_parts = ["# AUTOMATICALLY GENERATED LABELS - DO NOT EDIT\n"]
            data_path = os.path.join(gamedir, "data")
            if not os.path.exists(data_path): return
            
            for root, dirs, files in os.walk(data_path):
                for f in files:
                    if not f.endswith(".md"): continue
                    path = os.path.relpath(os.path.join(root, f), gamedir)
                    props, body = MarkdownParser.parse(path)
                    if not props: continue
                    
                    obj_id = props.get('id', props.get('name', 'unknown')).lower()
                    otype = props.get('type', 'location')
                    prefix = {"character":"CHAR", "scene":"SCENE", "quest":"QUEST", "container":"CONT", "item":"ITEM"}.get(otype, "LOC")
                    
                    sections = re.split(r'(?m)^#+\s*', body)
                    for sec in sections:
                        if not sec.strip(): continue
                        lines = sec.split('\n', 1)
                        heading = lines[0].strip().lower().replace(' ', '_')
                        content = lines[1] if len(lines) > 1 else ""
                        
                        flows = re.findall(r'```flow.*?\s*\n(.*?)\n```', content, re.DOTALL)
                        if not flows:
                            flows = re.findall(r'```flow.*?\n(.*?)\n```', content, re.DOTALL)

                        if flows:
                            for flow_body in flows:
                                label_name = f"{prefix}__{obj_id}__{heading}"
                                script_parts.append(f"label {label_name}:\n")
                                for line in flow_body.split('\n'):
                                    line = line.strip()
                                    if not line: continue
                                    if line.startswith('$'): script_parts.append(f"    {line}\n")
                                    elif ':' in line:
                                        cid, txt = line.split(':', 1)
                                        txt = txt.strip().replace('"', '\\"')
                                        script_parts.append(f"    {cid.strip().lower()} \"{txt}\"\n")
                                    else:
                                        txt = line.strip().replace('"', '\\"')
                                        script_parts.append(f"    \"{txt}\"\n")
                                
                                if prefix == "ITEM": script_parts.append("    return\n\n")
                                else: script_parts.append("    jump world_loop\n\n")

            with open(output_file, "w", encoding="utf-8") as out:
                out.write("".join(script_parts))

    MarkdownParser.load_all()

init -10 python:
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

    class Entity(object):
        def __init__(self, name, description="", label=None):
            self.name, self.description, self.label = name, description, label
        def interact(self):
            if self.label: renpy.jump(self.label)
            else: renpy.say(None, f"You see {self.name}. {self.description}")

    class Inventory(Entity):
        def __init__(self, name, description="", label=None):
            super(Inventory, self).__init__(name, description, label)
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
        def __init__(self, name, description="", id=None):
            super(Container, self).__init__(name, description)
            self.id = id
        def interact(self): renpy.show_screen("container_screen", container=self)

    class Shop(Inventory):
        def __init__(self, name, description="", buy_mult=1.2, sell_mult=0.6):
            super(Shop, self).__init__(name, description)
            self.buy_mult, self.sell_mult = buy_mult, sell_mult
        def get_buy_price(self, i): return int(i.value * self.buy_mult)
        def get_sell_price(self, i): return int(i.value * self.sell_mult)
        def interact(self): renpy.show_screen("shop_screen", shop=self)

    class RPGStats:
        def __init__(self, s=10, d=10, i=10, c=10):
            self.strength, self.dexterity, self.intelligence, self.charisma = s, d, i, c
            self.hp = self.max_hp = 100

    class RPGCharacter(Inventory):
        def __init__(self, name, stats=None, description="", label=None, location_id=None):
            super(RPGCharacter, self).__init__(name, description, label)
            self.stats, self.equipped_items, self.location_id, self.pchar, self.gold = stats or RPGStats(), {}, location_id, Character(name), 100
        def __call__(self, what, *args, **kwargs): return self.pchar(what, *args, **kwargs)
        def interact(self): renpy.show_screen("char_interact_screen", char=self)
        def mark_as_met(self): wiki_manager.unlock(self.name, self.description)

    class Location:
        def __init__(self, id, name, description):
            self.id, self.name, self.description, self.entities, self.connections, self.visited = id, name, description, [], {}, False
        def add_connection(self, dest, desc): self.connections[dest] = desc
        def add_entity(self, e): self.entities.append(e)
        @property
        def characters(self): return [c for c in rpg_world.characters.values() if c.location_id == self.id and c.name != pc.name]

    class GameWorld:
        def __init__(self): self.locations, self.characters, self.current_location_id = {}, {}, None
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
    wiki_manager = WikiManager()

    def instantiate_all():
        data_path = os.path.join(gamedir, "data")
        for root, dirs, files in os.walk(data_path):
            for f in files:
                if not f.endswith(".md"): continue
                props, body = MarkdownParser.parse(os.path.relpath(os.path.join(root, f), gamedir))
                if not props: continue
                oid, otype = props.get('id', props.get('name', 'unknown')).lower(), props.get('type')
                if otype == 'item': item_manager.register(oid, Item(props.get('name', oid), props.get('description', ''), float(props.get('weight', 0)), int(props.get('value', 0)), props.get('outfit_part')))
                elif otype == 'location': rpg_world.add_location(Location(oid, props.get('name', oid), props.get('description', '')))
                elif otype == 'character': rpg_world.add_character(RPGCharacter(props.get('name'), description=props.get('description', ''), location_id=props.get('location')))
                elif otype == 'container':
                    cont = Container(props.get('name', oid), props.get('description', ''), id=oid)
                    for iid in props.get('items', '').split(','):
                        itm = item_manager.get(iid.strip())
                        if itm: cont.add_item(itm)
                    if props.get('location') in rpg_world.locations: rpg_world.locations[props.get('location')].add_entity(cont)
                elif otype == 'quest': quest_manager.add_quest(Quest(oid, props.get('name', oid), props.get('description', '')))

    instantiate_all()

default persistent.achievements = set()
default persistent.met_characters = set()
