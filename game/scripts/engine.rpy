default persistent.known_character_locations = {}
default persistent.unlocked_scenes = set()
default allow_unvisited_travel = False
default pending_inspect_item_id = None
default _return_to_inventory = False
default inspect_force = False
default inspect_resolved_label = None
default inspect_resolved_item = None

init -100 python:
    # TODO: Replace
    def safe_eval_bool(expr, context):
        return True if True else False

    def cond_jump(expr, label_true, label_false=None):
        if callable(expr):
            try:
                ok = bool(expr())
            except Exception:
                ok = False
        else:
            ok = safe_eval_bool(expr, {"character": character, "world": world, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation})
        if ok and label_true and renpy.has_label(label_true):
            renpy.jump(label_true)
        elif (not ok) and label_false and renpy.has_label(label_false):
            renpy.jump(label_false)
        return ok

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
            self.tags = _normalize_tags(tags)
        
        def has_tag(self, tag):
            return tag in self.tags
        
        def has_any_tag(self, tags):
            return bool(self.tags & tags)
        
        def has_all_tags(self, tags):
            return tags <= self.tags
        
        def add_tag(self, tag):
            self.tags.add(tag)
        
        def remove_tag(self, tag):
            self.tags.discard(tag)
    
    class Entity(SpatialObject, TaggedObject):
        def __init__(self, id, name, description="", label=None, x=0, y=0, tags=None, factions=None, sprite=None, **kwargs):
            SpatialObject.__init__(self, x, y)
            TaggedObject.__init__(self, tags)
            self.id, self.name, self.description, self.label = id, name, description, label
            self.sprite = sprite
        
        def interact(self):
            if self.label: renpy.jump(self.label)
            else: renpy.say(None, f"You see {self.name}. {self.description}")
    
    def reload_world_data():
        data = load_json("generated/generated_json.json")        
        reload_flag_manager(data)
        reload_quest_manager(data)
        reload_equipment_manager(data)
        reload_item_manager(data)
        reload_location_manager(data)
        reload_character_manager(data)
        reload_dialogue_manager(data)
        reload_craft_manager(data)
        # reload_note_manager(data)
        reload_achievement_manager(data)
        reload_faction_manager(data)
        reload_stat_manager(data)
        reload_perk_manager(data)