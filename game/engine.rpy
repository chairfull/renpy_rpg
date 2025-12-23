init python:
    import random

default persistent.achievements = set()
default persistent.unlocked_scenes = set()

init -100 python:
    class Entity:
        def __init__(self, name, description="", label=None):
            self.name = name
            self.description = description
            self.label = label # Label to jump to when interacting

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
            self.outfit_part = outfit_part # e.g., "top", "bottom", "accessory"

    class RPGCharacter(Inventory):
        def __init__(self, name, stats=None, description="", label=None):
            super(RPGCharacter, self).__init__(name, description, label)
            self.stats = stats or RPGStats()
            self.outfits = {"default": "base_outfit"}
            self.current_outfit = "default"
            self.equipped_items = {} # part -> item
            self.pcharacter = renpy.Character(name)

        def __call__(self, what, *args, **kwargs):
            return self.pcharacter(what, *args, **kwargs)

        def equip(self, item):
            if item.outfit_part:
                self.equipped_items[item.outfit_part] = item

        def unequip(self, part):
            if part in self.equipped_items:
                del self.equipped_items[part]

    class Location:
        def __init__(self, id, name, description, entities=None, background=None):
            self.id = id
            self.name = name
            self.description = description
            self.entities = entities or []
            self.background = background
            self.connections = {} # Destination ID -> Connection Description

        def add_connection(self, dest_id, description):
            self.connections[dest_id] = description

        def add_entity(self, entity):
            self.entities.append(entity)

    class GameWorld:
        def __init__(self):
            self.locations = {}
            self.current_location_id = None

        def add_location(self, location):
            self.locations[location.id] = location
            if not self.current_location_id:
                self.current_location_id = location.id

        @property
        def current_location(self):
            return self.locations.get(self.current_location_id)

        def move_to(self, location_id):
            if location_id in self.locations:
                self.current_location_id = location_id
                # Track achievement for visiting location
                achievements.unlock(f"visit_{location_id}")
                return True
            return False

    # --- Achievement System ---
    class AchievementManager:
        def __init__(self):
            if persistent.achievements is None:
                persistent.achievements = set()

        def unlock(self, achievement_id):
            if achievement_id not in persistent.achievements:
                persistent.achievements.add(achievement_id)
                renpy.notify(f"Achievement Unlocked: {achievement_id}")

        def is_unlocked(self, achievement_id):
            return achievement_id in persistent.achievements

    # --- Scene System ---
    class Scene:
        def __init__(self, id, name, start_label, end_label):
            self.id = id
            self.name = name
            self.start_label = start_label
            self.end_label = end_label

    class SceneManager:
        def __init__(self):
            if persistent.unlocked_scenes is None:
                persistent.unlocked_scenes = set()
            self.scenes = {}

        def add_scene(self, scene):
            self.scenes[scene.id] = scene

        def unlock(self, scene_id):
            if scene_id not in persistent.unlocked_scenes:
                persistent.unlocked_scenes.add(scene_id)
                renpy.notify(f"Scene Unlocked: {self.scenes[scene_id].name}")

        def play(self, scene_id):
            if scene_id in self.scenes:
                renpy.jump(self.scenes[scene_id].start_label)

    # Persistent initialization logic
    if persistent.achievements is None:
        persistent.achievements = set()
    if persistent.unlocked_scenes is None:
        persistent.unlocked_scenes = set()

    # Singletons
    rpg_world = GameWorld()
    achievements = AchievementManager()
    scene_manager = SceneManager()
    pc = RPGCharacter("Player")
