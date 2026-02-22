class HasZone:
    """Mixin for objects that have a location in the game world"""
    def __init__(self, zone=None):
        self._zone = zone
    
    @property
    def zone(self):
        return self.get_zone_path()[-1]
    
    def get_zone_path(self):
        path = []
        if hasattr(self, "id"):
            parts = self.id.split("__")
        z = self.zone
        while z:
            path.append(z)
            z = z.zone if hasattr(z, "zone") else None
        return z