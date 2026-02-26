from .engine import all_beings, all_zones, all_lore
from .vector3 import Vector3
from .has_flags import HasFlags
from .has_zone import HasZone
from .has_tags import HasTags

class Zone(HasFlags, HasZone, HasTags):
    """Main location class."""

    OVERWORLD = "overworld"
    WORLD = "world"
    COUNTRY = "country"
    CITY = "city"
    STRUCTURE = "structure"
    ROOM = "room"
    FLOOR = "floor"

    def __init__(self, _id, name, desc=None, obstacles=None, entities=None, zone=None, position=Vector3(0,0,0), tags=None,
            parent_id=None, subtype="world", flags={}, floor=0):
        HasFlags.__init__(self, flags)
        HasZone.__init__(self, zone)
        HasTags.__init__(self, tags)
        self.id = _id
        self.name = name
        self.desc = desc
        self.subtype = subtype
        self.position = position
        self.obstacles = obstacles or set()
        self.entities = entities or {}
        self.floor = floor
        self.visited = False
    
    def mark_visited(self):
        if self.visited:
            return
        self.visited = True
        lore = all_lore.get(self.id)
        lore and lore.unlock()
    
    def get_path(self, start=Vector3(), end=Vector3()):
        """Find a path between points."""
        # TODO: AStart pathfinding.
        return [start, end]

    @property
    def beings(self):
        """Characters inside this zone"""
        return [x for x in all_beings.values() if x.location == self]
    
    @property
    def child_zones(self):
        """Return child zones"""
        return [x for x in all_zones.values() if x.zone == self]

    def get_entities(self, tag):
        return [x for x in self.entities if x.has_tag(tag)]