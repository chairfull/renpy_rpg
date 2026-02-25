from .engine import ZONE_ENTERED, ZONE_EXITED

class HasZone:
    """Mixin for objects that have a location in the game world"""
    def __init__(self, zone=None):
        self._zone = zone
    
    @property
    def zone(self):
        return self.get_zone_path()[-1]
    
    @zone.setter
    def zone(self, next):
        if self._zone == next:
            return
        if self._zone is not None:
            ZONE_EXITED.emit(zone=self._zone, what=self)
        self._zone = next
        if self._zone is not None:
            ZONE_ENTERED.emit(zone=self._zone, what=self)
    
    def get_zone_path(self):
        path = []
        if hasattr(self, "id"):
            parts = self.id.split("__")
        z = self.zone
        while z:
            path.append(z)
            z = z.zone if hasattr(z, "zone") else None
        return z