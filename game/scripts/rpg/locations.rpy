default location_manager = LocationManager()
default location = None # Current location

init -1500 python:
    class LocationType:
        OVERWORLD = "overworld"
        WORLD = "world"
        COUNTRY = "country"
        CITY = "city"
        STRUCTURE = "structure"
        ROOM = "room"
        FLOOR = "floor"

    onstart(add_meta_menu_tab, "locations", "🗺️", "Locations",
        map_mode=LocationType.OVERWORLD, map_overworld=None, map_location=None, map_area=None)

    class Gate:
        def __init__(self, gtype="physical", difficulty=1, keys=None, locked=True):
            self.type = gtype
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

    class Fixture(Vector3):
        """A place or object a character can fixate to (seat, bed, table, floor spot)."""
        def __init__(self, id, name, fixture_type="seat", tags=None, x=0, y=0, z=0):
            Vector3.__init__(self, x, y, z)
            self.id = id
            self.name = name
            self.fixture_type = fixture_type or "seat"
            self.tags = set(tags or [])
            self.occupant = None

        def is_occupied(self):
            return self.occupant is not None

        def fixate(self, char):
            if self.occupant and self.occupant != char.id:
                return False, "Occupied"
            # Unfixate from previous fixture if needed
            if getattr(char, "fixated_to", None) and getattr(char, "fixated_to") != self.id:
                fixture_manager.unfixate_char(char)
            self.occupant = char.id
            char.fixated_to = self.id
            if self.x is not None and self.y is not None:
                char.x, char.y = self.x, self.y
            signal("CHARACTER_FIXATED", actor=char.id, fixture=self)
            return True, "Fixated"

        def unfixate(self, char=None):
            target_id = self.occupant
            if char is not None and target_id and target_id != char.id:
                return False, "Not occupied by this character"
            self.occupant = None
            if char is not None:
                char.fixated_to = None
            signal("CHARACTER_UNFIXATED", actor=target_id, fixture=self)
            return True, "Unfixated"

    class Location(Vector3, TaggedObject, FlaggedObject):
        def __init__(self, id, name, desc, map_image=None, obstacles=None, entities=None, position=Vector3(0,0,0), tags=None,
                parent_id=None, type="world", map_position=Vector2(), zoom_range=(0.0, 99.0), floor_idx=0):
            Vector3.__init__(self, position.x, position.y, position.z)
            TaggedObject.__init__(self, tags)
            FlaggedObject.__init__(self)
            self.id = id
            self.name = name
            self.desc = desc
            self.type = type # world, country, city, structure, floor
            self.gates = {}
            self.fixtures = {}
            self.flags = {}
            self.obstacles = obstacles or set()
            self.entities = entities or {}
            self.visited = False
            self.parent_id = parent_id
            self.map_image = map_image
            self.map_position = map_position
            self.min_zoom, self.max_zoom = zoom_range
            self.floor_idx = floor_idx
        
        def get_path(self, start, end):
            # Placeholder for pathfinding logic (A* or similar)
            return [start, end]
        
        @property
        def characters(self):
            return [c for c in all_characters() if getattr(c, 'location_id', None) == self.id and c.id != character.id]
        
        def get_tagged(self, tag):
            return [e for e in self.entities if hasattr(e, 'tags') and tag in e.get('tags', [])]
        
        @property
        def children(self):
            # Return immediate children based on parent_id
            return [l for l in all_locations() if l.parent_id == self.id]
    
    class LocationManager:
        def __init__(self):
            self.locations = {}
    
    def get_location(loc_id):
        return location_manager.locations.get(loc_id)

    def all_locations():
        return location_manager.locations.values()

    def reload_location_manager(data):
        location_manager.locations = {}
        for oid, p in data.get("locations", {}).items():
            try:
                location_manager.locations[oid] = from_dict(Location, p, id=oid)
            except Exception as e:
                with open("debug_load.txt", "a") as df:
                    df.write("Location Load Error ({}): {}\n".format(oid, str(e)))

screen locations_screen(mmtab=None):
    frame:
        background "#0f141b"
        xfill True
        yfill True
        padding (16, 16)

        vbox:
            spacing 12

            # Top mode buttons
            hbox:
                spacing 10
                xalign 0.5
                button:
                    action SetVariable("mmtab.map_mode", "overworld")
                    background ("#2a2a3a" if mmtab.map_mode == "overworld" else "#1a1a25")
                    hover_background "#2f3442"
                    padding (12, 8)
                    vbox:
                        spacing 2
                        text "OVERWORLD" size 18 color "#fff"
                        $ _ov = get_location(mmtab.map_overworld) if mmtab.map_overworld else None
                        text ((_ov.name if _ov else "—")) size 12 color "#aaa"
                button:
                    action SetVariable("mmtab.map_mode", "location")
                    background ("#2a2a3a" if mmtab.map_mode == "location" else "#1a1a25")
                    hover_background "#2f3442"
                    padding (12, 8)
                    vbox:
                        spacing 2
                        text "LOCATION" size 18 color "#fff"
                        $ _loc = get_location(mmtab.map_location) if mmtab.map_location else None
                        text ((_loc.name if _loc else "—")) size 12 color "#aaa"
                button:
                    action SetVariable("mmtab.map_mode", "areas")
                    background ("#2a2a3a" if mmtab.map_mode == "areas" else "#1a1a25")
                    hover_background "#2f3442"
                    padding (12, 8)
                    vbox:
                        spacing 2
                        text "AREAS" size 18 color "#fff"
                        $ _ar = get_location(mmtab.map_area) if mmtab.map_area else None
                        text ((_ar.name if _ar else "—")) size 12 color "#aaa"

            # Grid
            frame:
                background "#111722"
                xfill True
                yfill True
                padding (12, 12)
                viewport:
                    mousewheel True
                    scrollbars "vertical"
                    draggable True
                    vpgrid:
                        cols 3
                        xspacing 10
                        yspacing 10
                        xfill True
                        python:
                            locs = list(all_locations())
                            mode = mmtab.map_mode
                            if mode == "overworld":
                                locs = []
                            elif mode == "location":
                                locs = [l for l in locs if l.ltype not in ("room", "floor") and not l.parent_id]
                            else:
                                # areas: rooms under selected location (any depth)
                                if mmtab.map_location:
                                    locs = [l for l in locs if l.ltype == "room" and _loc_is_descendant(l, mmtab.map_location)]
                                else:
                                    locs = []
                            locs = sorted(locs, key=lambda l: (l.name or ""))
                        for loc in locs:
                            $ can_travel = allow_unvisited_travel or loc.visited or (location == loc)
                            $ display_name = loc.name or loc.id
                            button:
                                xfill True
                                ysize 110
                                background ("#1f2a38" if can_travel else "#151a22")
                                hover_background "#2a3646"
                                padding (10, 8)
                                action [
                                    If(mmtab.map_mode == "overworld", SetVariable("mmtab.map_overworld", loc.id), NullAction()),
                                    If(mmtab.map_mode == "location", SetVariable("mmtab.map_location", loc.id), NullAction()),
                                    If(mmtab.map_mode == "areas", SetVariable("mmtab.map_area", loc.id), NullAction()),
                                    If(mmtab.map_mode == "areas", Function(map_manager.select_location, loc), NullAction())
                                ]
                                vbox:
                                    spacing 4
                                    text "[display_name]" size 16 color ("#fff" if can_travel else "#666")
                                    text "[loc.ltype!u]" size 12 color "#888"

    if map_manager.selected_location:
        use location_info_popup(map_manager.selected_location)

# Location Info Popup Screen
screen location_info_popup(loc):
    # Click outside to close - full screen button behind the popup
    button:
        xfill True
        yfill True
        action Function(map_manager.close_location_popup)
        background "#00000066"
    
    # Popup Frame
    frame:
        align (0.5, 0.5)
        xsize 500
        background "#1a1a2e"
        padding (30, 30)
        
        vbox:
            spacing 15
            
            # Header
            hbox:
                xfill True
                text "[loc.name]" size 28 color "#ffd700" bold True
                textbutton "✕":
                    align (1.0, 0.0)
                    action Function(map_manager.close_location_popup)
                    text_size 24
                    text_color "#888"
                    text_hover_color "#fff"
            
            # Type Badge
            frame:
                background "#333"
                padding (10, 5)
                text "[loc.ltype!u]" size 14 color "#aaa"
            
            null height 5
            
            # Description
            text "[loc.desc]" size 18 color "#ccc" text_align 0.0
            
            null height 15
            
            $ can_travel = allow_unvisited_travel or loc.visited or (world.current_location_id == loc.id)
            if not can_travel:
                text "Undiscovered" size 16 color "#ff6666"

            # Travel Button
            textbutton "🚶 TRAVEL HERE":
                xfill True
                action Function(map_manager.travel_to_location, loc)
                sensitive can_travel
                background ("#2d5a27" if can_travel else "#222")
                hover_background ("#3d7a37" if can_travel else "#333")
                padding (20, 15)
                text_size 22
                text_color ("#fff" if can_travel else "#666")
                text_xalign 0.5
