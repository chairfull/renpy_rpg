import renpy
from .. import engine
from ..scene_child import SceneChild

class TravelNode(SceneChild):
    """Clicking brings up menu for traveling to a different scene"""
    def __init__(self, position, zone):
        SceneChild.__init__(self, position)
        self.zone = zone
    
    def action(self):
        return renpy.Function(engine.player.set_zone, self.zone)