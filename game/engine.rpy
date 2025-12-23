python early:
    import os
    import re

    class MarkdownParser:
        @staticmethod
        def parse(filepath):
            with renpy.file(filepath) as f:
                content = f.read().decode("utf-8")
            
            fm_match = re.search(r'---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
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
        def generate_scripts():
            # Output path must use physical disk path
            output_dir = os.path.join(renpy.config.gamedir, "generated")
            output_file = os.path.join(output_dir, "generated_labels.rpy")
            if not os.path.exists(output_dir): os.makedirs(output_dir)
            
            final_content = ["# AUTOMATICALLY GENERATED LABELS - DO NOT EDIT\n"]
            
            for f in renpy.list_files():
                if f.startswith("data/") and f.endswith(".md"):
                    props, body = MarkdownParser.parse(f)
                    if not props: continue
                    
                    obj_id = props.get('id', props.get('name', 'unknown')).lower()
                    obj_type = props.get('type', 'location')
                    prefix = "char_" if obj_type == "character" else "scene_" if obj_type == "scene" else "loc_"

                    sections = re.finditer(r'^#+\s*(.*?)\n.*?```flow\s*\n(.*?)\n```', body, re.DOTALL | re.MULTILINE)
                    for section in sections:
                        heading = section.group(1).strip().lower().replace(' ', '_')
                        flow_body = section.group(2)
                        
                        label_name = f"scene_{obj_id}_start" if obj_type == "scene" else f"{prefix}{obj_id}_{heading}"
                        final_content.append(f"label {label_name}:\n")
                        
                        # Process flow lines
                        lines = [l.strip() for l in flow_body.split('\n') if l.strip()]
                        chars_to_fetch = set()
                        for line in lines:
                            if ':' in line and not line.startswith('$'):
                                chars_to_fetch.add(line.split(':', 1)[0].strip().lower())
                        
                        for cid in chars_to_fetch:
                            final_content.append(f'    $ {cid} = rpg_world.characters.get("{cid.capitalize()}")\n')
                        
                        for line in lines:
                            if line.startswith('$'):
                                final_content.append(f'    {line}\n')
                            elif ':' in line:
                                char_id, text = line.split(':', 1)
                                char_id = char_id.strip().lower()
                                text = text.strip().replace('"', '\\"')
                                final_content.append(f'    {char_id} "{text}"\n')
                            else:
                                text = line.replace('"', '\\"')
                                final_content.append(f'    "{text}"\n')
                        
                        if obj_type == 'scene':
                            final_content.append(f"    $ scene_manager.unlock('{obj_id}')\n")
                        final_content.append("    jump world_loop\n\n")

            with open(output_file, "w", encoding="utf-8") as out:
                out.write("".join(final_content))

    MarkdownParser.generate_scripts()

init -10 python:
    import random

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
            return [c for c in rpg_world.characters.values() if c.location_id == self.id and c.name != rpg_world.active_actor_name]

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

    # Consolidated Loader
    def load_all():
        for f in renpy.list_files():
            if f.startswith("data/") and f.endswith(".md"):
                props, body = MarkdownParser.parse(f)
                if not props: continue
                
                obj_type = props.get('type', 'location')
                obj_id = props.get('id', props.get('name', 'unknown')).lower()
                
                # Use same label logic
                detected_label = None
                flow_headings = re.findall(r'^#+\s*(.*?)\n.*?```flow', body, re.DOTALL | re.MULTILINE)
                if flow_headings:
                    best_heading = flow_headings[0].strip().lower().replace(' ', '_')
                    prefix = "char_" if obj_type == "character" else "scene_" if obj_type == "scene" else "loc_"
                    detected_label = f"scene_{obj_id}_start" if obj_type == "scene" else f"{prefix}{obj_id}_{best_heading}"

                if obj_type == 'location':
                    loc = Location(id=obj_id, name=props.get('name', obj_id), description=props.get('description', ''))
                    rpg_world.add_location(loc)
                elif obj_type == 'character':
                    char = RPGCharacter(name=props.get('name'), description=props.get('description', ''), label=props.get('label', detected_label), location_id=props.get('location', None))
                    wiki_manager.register(char.name, char.description)
                    rpg_world.add_character(char)
                elif obj_type == 'scene':
                    scene = Scene(id=obj_id, name=props.get('name', obj_id), start_label=f"scene_{obj_id}_start", end_label=f"scene_{obj_id}_end")
                    scene_manager.add_scene(scene)

    rpg_world = GameWorld()
    achievements = AchievementManager()
    scene_manager = SceneManager()
    wiki_manager = WikiManager()
    time_manager = TimeManager()
    pc = RPGCharacter("Player")
    rpg_world.add_character(pc)
    load_all()

default persistent.achievements = set()
default persistent.unlocked_scenes = set()
default persistent.met_characters = set()
