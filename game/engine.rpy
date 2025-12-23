python early:
    import os
    import re
    import hashlib

    class MarkdownParser:
        @staticmethod
        def parse(filepath):
            try:
                with renpy.file(filepath) as f:
                    content = f.read().decode("utf-8")
            except:
                return None, None
            
            # Looser frontmatter regex
            fm_match = re.search(r'---\s*\r?\n(.*?)\r?\n---\s*\r?\n', content, re.DOTALL)
            if not fm_match: return None, None
            
            fm_text = fm_match.group(1)
            body_text = content[fm_match.end():].strip()
            
            props = {}
            for line in fm_text.split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    props[k.strip()] = v.strip()
            return props, body_text

        @staticmethod
        def load_all():
            output_dir = os.path.join(renpy.config.gamedir, "generated")
            output_file = os.path.join(output_dir, "generated_labels.rpy")
            if not os.path.exists(output_dir): os.makedirs(output_dir)
            
            script_parts = ["# AUTOMATICALLY GENERATED LABELS - DO NOT EDIT\n"]
            files_to_process = []

            # Try renpy.list_files first
            try:
                all_files = renpy.list_files()
                for f in all_files:
                    if f.startswith("data/") and f.endswith(".md"):
                        files_to_process.append(f)
            except: pass

            # Fallback for early pass if list_files is empty
            if not files_to_process:
                data_path = os.path.join(renpy.config.gamedir, "data")
                if os.path.exists(data_path):
                    for root, dirs, files in os.walk(data_path):
                        for f in files:
                            if f.endswith(".md"):
                                rel_path = os.path.relpath(os.path.join(root, f), renpy.config.gamedir)
                                files_to_process.append(rel_path)

            world = globals().get('rpg_world')
            wiki = globals().get('wiki_manager')
            scenes = globals().get('scene_manager')
            quests = globals().get('quest_manager')
            
            for f in files_to_process:
                props, body = MarkdownParser.parse(f)
                if not props: continue
                
                obj_id = props.get('id', props.get('name', 'unknown')).lower()
                obj_type = props.get('type', 'location')
                prefix = "CHAR" if obj_type == "character" else "SCENE" if obj_type == "scene" else "LOC"
                if obj_type == "quest": prefix = "QUEST"

                # 1. Script Generation (Flow blocks)
                detected_label = None
                # Heading regex: look for # or ## followed by title, then capture until next heading or end
                sections = re.finditer(r'^#+\s*(.*?)\r?\n(.*?)(?=^#+|\Z)', body, re.DOTALL | re.MULTILINE)
                
                for section in sections:
                    heading_text = section.group(1).strip()
                    heading_slug = heading_text.lower().replace(' ', '_')
                    section_body = section.group(2)
                    
                    flow_match = re.search(r'```flow\s*\r?\n(.*?)\r?\n```', section_body, re.DOTALL)
                    if flow_match:
                        flow_content = flow_match.group(1)
                        label_name = f"{prefix}__{obj_id}__{heading_slug}"
                        # if obj_type == "scene" and heading_slug == "start": label_name = f"SCENE__{obj_id}__start"
                        if not detected_label: detected_label = label_name
                        
                        script_parts.append(f"label {label_name}:\n")
                        lines = [l.strip() for l in flow_content.split('\n') if l.strip()]
                        
                        chars_to_fetch = set()
                        for line in lines:
                            if ':' in line and not line.startswith('$'):
                                chars_to_fetch.add(line.split(':', 1)[0].strip().lower())
                        
                        for cid in chars_to_fetch:
                            script_parts.append(f'    $ {cid} = rpg_world.characters.get("{cid.capitalize()}")\n')
                        
                        for line in lines:
                            if line.startswith('$'):
                                script_parts.append(f'    {line}\n')
                            elif ':' in line:
                                char_id, text = line.split(':', 1)
                                text = text.strip().replace('"', '\\"')
                                script_parts.append(f'    {char_id.strip().lower()} "{text}"\n')
                            else:
                                text = line.strip().replace('"', '\\"')
                                script_parts.append(f'    "{text}"\n')
                        
                        if obj_type == 'scene':
                            script_parts.append(f"    $ scene_manager.unlock('{obj_id}')\n")
                        script_parts.append("    jump world_loop\n\n")

                # 2. Object Instantiation (only if world exists, i.e., in init phase)
                if world:
                    if obj_type == 'location':
                        loc = Location(id=obj_id, name=props.get('name', obj_id), description=props.get('description', ''))
                        world.add_location(loc)
                    elif obj_type == 'character':
                        char = RPGCharacter(name=props.get('name'), description=props.get('description', ''), label=props.get('label', detected_label), location_id=props.get('location', None))
                        if wiki: wiki.register(char.name, char.description)
                        world.add_character(char)
                    elif obj_type == 'scene':
                        scene = Scene(id=obj_id, name=props.get('name', obj_id), start_label=f"scene_{obj_id}_start", end_label=f"scene_{obj_id}_end")
                        if scenes: scenes.add_scene(scene)
                    elif obj_type == 'quest' and quests:
                        quest = Quest(id=obj_id, name=props.get('name', obj_id), description=props.get('description', ''))
                        
                        # Use the already parsed sections to build quest ticks
                        sections_for_ticks = re.finditer(r'^##\s*(.*?)\r?\n(.*?)(?=^#+|\Z)', body, re.DOTALL | re.MULTILINE)
                        for gsec in sections_for_ticks:
                            goal_name = gsec.group(1).strip()
                            goal_body = gsec.group(2)
                            
                            tick = QuestTick(id=goal_name.lower().replace(' ', '_'), name=goal_name)
                            trigger_match = re.search(r'```trigger\s*\r?\n(.*?)\r?\n```', goal_body, re.DOTALL)
                            if trigger_match:
                                t_lines = trigger_match.group(1).split('\n')
                                for tl in t_lines:
                                    if ':' in tl:
                                        tk, tv = tl.split(':', 1)
                                        tick.trigger_data[tk.strip().lower()] = tv.strip()
                            
                            if re.search(r'```flow', goal_body):
                                tick.flow_label = f"QUEST_{obj_id}__{goal_name.lower().replace(' ', '_')}"
                            quest.add_tick(tick)
                        
                        # Handle quest-level triggers
                        start_trigger_match = re.search(r'^#\s*Started\n.*?```trigger\s*\r?\n(.*?)\r?\n```', body, re.DOTALL | re.MULTILINE)
                        if start_trigger_match:
                            t_lines = start_trigger_match.group(1).split('\n')
                            q_trigger = {}
                            for tl in t_lines:
                                if ':' in tl:
                                    tk, tv = tl.split(':', 1)
                                    q_trigger[tk.strip().lower()] = tv.strip()
                            quests.register_start_trigger(obj_id, q_trigger)
                        quests.add_quest(quest)

            # Write scripts file with change detection
            new_content = "".join(script_parts)
            old_content = ""
            if os.path.exists(output_file):
                with open(output_file, "r", encoding="utf-8") as f:
                    old_content = f.read()
            
            if new_content != old_content:
                with open(output_file, "w", encoding="utf-8") as out:
                    out.write(new_content)
                
                try:
                    config.developer = True
                    renpy.reload_script(output_file)
                except:
                    pass

    MarkdownParser.load_all()

init -10 python:
    import random

    class EventManager(object):
        def __init__(self):
            self.listeners = []

        def dispatch(self, event_type, **kwargs):
            quest_manager.handle_event(event_type, **kwargs)

    class QuestTick(object):
        def __init__(self, id, name):
            self.id = id
            self.name = name
            self.state = "hidden" # hidden, shown, active, complete
            self.flow_label = None
            self.trigger_data = {}
            self.current_value = 0
            self.required_value = 1

        def check_trigger(self, event_type, **kwargs):
            if self.state not in ["shown", "active"]: return False
            if self.trigger_data.get("event") != event_type: return False
            for k, v in self.trigger_data.items():
                if k in ["event", "cond", "total"]: continue
                if str(kwargs.get(k)) != str(v): return False
            cond = self.trigger_data.get("cond")
            if cond:
                context = {"player": pc, "rpg_world": rpg_world, "kwargs": kwargs}
                try:
                    if not eval(cond, {}, context): return False
                except: return False
            self.current_value = int(kwargs.get("total", self.current_value + 1))
            req = int(self.trigger_data.get("total", self.required_value))
            if self.current_value >= req:
                self.state = "complete"
                return True
            return False

    class Quest(object):
        def __init__(self, id, name, description=""):
            self.id = id
            self.name = name
            self.description = description
            self.state = "unknown" # unknown, known, active, passed, failed
            self.ticks = []

        def add_tick(self, tick):
            self.ticks.append(tick)

        def start(self):
            if self.state == "unknown" or self.state == "known":
                self.state = "active"
                if len(self.ticks) > 0: self.ticks[0].state = "active"
                renpy.notify(f"Quest Started: {self.name}")
                label = f"quest_{self.id}_started"
                if renpy.has_label(label): renpy.call(label)

        def complete(self):
            self.state = "passed"
            renpy.notify(f"Quest Completed: {self.name}")
            label = f"quest_{self.id}_passed"
            if renpy.has_label(label): renpy.call(label)

        def fail(self):
            self.state = "failed"
            renpy.notify(f"Quest Failed: {self.name}")
            label = f"quest_{self.id}_failed"
            if renpy.has_label(label): renpy.call(label)

    class QuestManager(object):
        def __init__(self):
            self.quests = {}
            self.start_triggers = {}

        def add_quest(self, quest):
            self.quests[quest.id] = quest

        def register_start_trigger(self, quest_id, trigger_data):
            self.start_triggers[quest_id] = trigger_data

        def handle_event(self, event_type, **kwargs):
            for qid, trigger in self.start_triggers.items():
                quest = self.quests.get(qid)
                if quest and quest.state == "unknown":
                    if self._match_trigger(trigger, event_type, **kwargs):
                        quest.start()
            for quest in self.quests.values():
                if quest.state == "active":
                    any_complete = False
                    for tick in quest.ticks:
                        if tick.check_trigger(event_type, **kwargs):
                            any_complete = True
                            if tick.flow_label and renpy.has_label(tick.flow_label):
                                renpy.call(tick.flow_label)
                    if any_complete:
                        all_done = True
                        for tick in quest.ticks:
                            if tick.state != "complete":
                                all_done = False
                                if tick.state == "hidden" or tick.state == "shown":
                                    tick.state = "active"
                                break
                        if all_done:
                            quest.complete()

        def _match_trigger(self, trigger, event_type, **kwargs):
            if trigger.get("event") != event_type: return False
            for k, v in trigger.items():
                if k in ["event", "cond"]: continue
                if str(kwargs.get(k)) != str(v): return False
            cond = trigger.get("cond")
            if cond:
                context = {"player": pc, "rpg_world": rpg_world, "kwargs": kwargs}
                try:
                    if not eval(cond, {}, context): return False
                except: return False
            return True

    class Entity(object):
        def __init__(self, name, description="", label=None):
            self.name = name
            self.description = description
            self.label = label 

        def interact(self):
            if self.label:
                renpy.jump(self.label)
            else:
                renpy.say(None, f"You see {self.name}. {self.description}")

    class Inventory(Entity):
        def __init__(self, name, description="", label=None):
            super(Inventory, self).__init__(name, description, label)
            self.items = []

        def add_item(self, item):
            self.items.append(item)
            event_manager.dispatch("ITEM_GAINED", item=item.name, total=len([i for i in self.items if i.name == item.name]))

        def remove_item(self, item):
            if item in self.items:
                self.items.remove(item)

    class RPGStats:
        def __init__(self, strength=10, dexterity=10, intelligence=10, charisma=10):
            self.strength = strength
            self.dexterity = dexterity
            self.intelligence = intelligence
            self.charisma = charisma
            self.hp = 100
            self.max_hp = 100

    class Item:
        def __init__(self, name, description, weight=0, value=0, outfit_part=None):
            self.name = name
            self.description = description
            self.weight = weight
            self.value = value
            self.outfit_part = outfit_part

    class RPGCharacter(Inventory):
        def __init__(self, name, stats=None, description="", label=None, location_id=None):
            super(RPGCharacter, self).__init__(name, description, label)
            self.stats = stats or RPGStats()
            self.outfits = {"default": "base_outfit"}
            self.current_outfit = "default"
            self.equipped_items = {}
            self.location_id = location_id
            self.pcharacter = Character(name)

        def __call__(self, what, *args, **kwargs):
            return self.pcharacter(what, *args, **kwargs)

        def mark_as_met(self):
            wiki_manager.unlock(self.name, self.description)

    class Location:
        def __init__(self, id, name, description, entities=None, background=None):
            self.id = id
            self.name = name
            self.description = description
            self.entities = entities or []
            self.background = background
            self.connections = {}
            self.visited = False

        def add_connection(self, dest_id, description):
            self.connections[dest_id] = description

        def add_entity(self, entity):
            self.entities.append(entity)

        @property
        def characters(self):
            return [c for c in rpg_world.characters.values() if rpg_world is not None and c.location_id == self.id and c.name != rpg_world.active_actor_name]

    class GameWorld:
        def __init__(self):
            self.locations = {}
            self.characters = {}
            self.current_location_id = None
            self.active_actor_name = "Player"

        def add_location(self, location):
            self.locations[location.id] = location
            if not self.current_location_id:
                self.current_location_id = location.id
                location.visited = True

        def add_character(self, character):
            self.characters[character.name] = character

        @property
        def actor(self):
            return self.characters.get(self.active_actor_name)

        @property
        def current_location(self):
            return self.locations.get(self.current_location_id)

        def move_to(self, location_id):
            if location_id in self.locations:
                self.current_location_id = location_id
                self.locations[location_id].visited = True
                achievements.unlock(f"visit_{location_id}")
                event_manager.dispatch("LOCATION_VISITED", location=location_id)
                return True
            return False

    class AchievementManager:
        def unlock(self, achievement_id):
            if achievement_id not in persistent.achievements:
                persistent.achievements.add(achievement_id)
                renpy.notify(f"Achievement Unlocked: {achievement_id}")

    class Scene:
        def __init__(self, id, name, start_label, end_label):
            self.id = id
            self.name = name
            self.start_label = start_label
            self.end_label = end_label

    class SceneManager:
        def __init__(self):
            self.scenes = {}

        def add_scene(self, scene):
            self.scenes[scene.id] = scene

        def unlock(self, scene_id):
            if scene_id not in persistent.unlocked_scenes:
                persistent.unlocked_scenes.add(scene_id)
                if scene_id in self.scenes:
                    renpy.notify(f"Scene Unlocked: {self.scenes[scene_id].name}")

        def play(self, scene_id):
            if scene_id in self.scenes:
                renpy.hide_screen("navigation_screen")
                renpy.hide_screen("gallery_screen")
                renpy.jump(self.scenes[scene_id].start_label)

    class WikiManager:
        def __init__(self):
            self.entries = {}

        def register(self, name, description):
            self.entries[name] = description

        def unlock(self, name, description=None):
            if name not in persistent.met_characters:
                persistent.met_characters.add(name)
                if description:
                    self.register(name, description)
                renpy.notify(f"New Wiki Entry: {name}")

        @property
        def met_list(self):
            met = []
            for name in sorted(persistent.met_characters):
                desc = self.entries.get(name, "No data available.")
                met.append((name, desc))
            return met

    class TimeManager:
        def __init__(self, day=1, hour=8, minute=0):
            self.day = day
            self.hour = hour
            self.minute = minute

        def advance(self, minutes=0):
            self.minute += minutes
            while self.minute >= 60:
                self.minute -= 60
                self.hour += 1
            while self.hour >= 24:
                self.hour -= 24
                self.day += 1

        @property
        def time_string(self):
            period = "AM" if self.hour < 12 else "PM"
            display_hour = self.hour % 12
            if display_hour == 0: display_hour = 12
            return f"Day {self.day} - {display_hour:02d}:{self.minute:02d} {period}"

    event_manager = EventManager()
    quest_manager = QuestManager()
    rpg_world = GameWorld()
    achievements = AchievementManager()
    scene_manager = SceneManager()
    wiki_manager = WikiManager()
    time_manager = TimeManager()
    pc = RPGCharacter("Player")
    rpg_world.add_character(pc)
    
    MarkdownParser.load_all()

default persistent.achievements = set()
default persistent.unlocked_scenes = set()
default persistent.met_characters = set()
