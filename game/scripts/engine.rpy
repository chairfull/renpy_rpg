

default persistent.known_character_locations = {}
default persistent.unlocked_scenes = set()
default allow_unvisited_travel = False
default pending_inspect_item_id = None
default _return_to_inventory = False
default inspect_force = False
default inspect_resolved_label = None
default inspect_resolved_item = None

default event_manager = EventManager()

init -10 python:
    import json
    import random
    import copy
    import ast
    import math

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

    def cond_jump(expr, label_true, label_false=None):
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

    TAG_TAXONOMY = {
        "type": {"weapon", "armor", "consumable", "tool", "material", "quest", "key", "currency", "container"},
        "consumable": {"food", "drink", "medical", "buff", "ammo"},
        "rarity": {"common", "uncommon", "rare", "epic", "legendary"},
        "damage": {"melee", "ranged", "magic", "thrown"},
        "utility": {"light", "lockpick", "repair", "crafting"},
    }
    TAG_ALIASES = {
        "quest_item": "quest",
        "credits": "currency",
        "coin": "currency",
        "coins": "currency",
        "health": "medical",
        "med": "medical",
        "meds": "medical",
        "ammo_pack": "ammo",
        "mats": "material",
    }

    def _canonical_tag(tag):
        if tag is None:
            return None
        t = str(tag).strip().lower().replace(" ", "_")
        return TAG_ALIASES.get(t, t)

    def _normalize_tags(tags):
        if not tags:
            return set()
        return set(_canonical_tag(t) for t in tags if str(t).strip())

    class TaggedObject(object):
        """Mixin for objects with tags for filtering"""
        def __init__(self, tags=None, **kwargs):
            self.tags = _normalize_tags(tags)
        
        def has_tag(self, tag):
            return _canonical_tag(tag) in self.tags
        
        def has_any_tag(self, tags):
            return bool(self.tags & _normalize_tags(tags))
        
        def has_all_tags(self, tags):
            return _normalize_tags(tags) <= self.tags
        
        def add_tag(self, tag):
            self.tags.add(_canonical_tag(tag))
        
        def remove_tag(self, tag):
            self.tags.discard(_canonical_tag(tag))

    class EventManager:
        def __init__(self):
            self.listeners = {}

        def subscribe(self, etype, fn):
            self.listeners.setdefault(etype, set()).add(fn)

        def unsubscribe(self, etype, fn):
            if etype in self.listeners and fn in self.listeners[etype]:
                self.listeners[etype].remove(fn)

        def dispatch(self, etype, **kwargs):
            quest_manager.handle_event(etype, **kwargs)
            if "ach_mgr" in globals() and ach_mgr is not None:
                ach_mgr.handle_event(etype, **kwargs)
            for fn in list(self.listeners.get(etype, [])):
                try:
                    fn(etype, **kwargs)
                except Exception:
                    pass

    def reload_event_manager():
        event_manager.listeners = {}

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
    
    class MapManager:
        def __init__(self):
            self.zoom = 1.0
            self.target_zoom = 1.0  # For smooth zoom animation
            self.cam_x = 0
            self.cam_y = 0
            self.search_query = ""
            self.selected_structure = None
            self.selected_location = None  # For location info popup
            self.hover_location = None
            self.hover_tooltip = None
        
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
            for loc in world.locations.values():
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
            if not allow_unvisited_travel and not loc.visited and loc.id != world.current_location_id:
                renpy.notify("You haven't discovered this location yet.")
                return False
            # Advance time based on map distance
            curr = world.current_location
            if curr and loc.id != curr.id:
                dx = float(loc.map_x - curr.map_x)
                dy = float(loc.map_y - curr.map_y)
                dist = (dx * dx + dy * dy) ** 0.5
                travel_mins = max(5, int(dist / 100.0 * 10))
                time_manager.advance(travel_mins)
                renpy.notify(f"Traveled to {loc.name} (+{travel_mins}m)")
            if world.move_to(loc.id):
                self.selected_location = None
                # Hide map and show the new location
                renpy.hide_screen("map_browser")
                if renpy.has_label("_post_travel_setup"):
                    renpy.call("_post_travel_setup")
                return True
            return False
        
        def center_on_player(self, adj_x, adj_y, view_w, view_h, pad):
            """Center the map view on the player's current location"""
            if not world.current_location_id:
                return
                
            loc = world.locations.get(world.current_location_id)
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
    
    def reload_world_data():
        try:
            # Use a more robust path check for renpy.file
            json_path = "generated/generated_json.json"
            if not renpy.loadable(json_path):
                # Fallback check
                json_path = game_dir + "/generated/generated_json.json"

            with renpy.file(json_path) as f:
                content = f.read().decode('utf-8')
                data = json.loads(content)
        except Exception as e:
            with open("debug_load.txt", "a") as df:
                df.write("JSON Load Error: {}\n".format(str(e)))
            return
        
        reload_event_manager()
        reload_quest_manager(data)
        reload_equipment_manager(data)
        reload_item_manager(data)
        reload_location_manager(data)
        reload_character_manager(data)
        reload_dialogue_manager(data)
        reload_craft_manager(data)
        reload_note_manager(data)
        reload_achievement_manager(data)
        reload_faction_manager(data)
        reload_stat_manager(data)
        reload_perk_manager(data)

    reload_world_data()


