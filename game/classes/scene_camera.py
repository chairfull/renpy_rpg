import renpy.config as config
from .util import lerp, clamp
from .point import Point
from .scene_child import SceneChild

class SceneCamera(SceneChild):
    def __init__(self, position=Point()):
        SceneChild.__init__(self, position=position)
        self.follow_target = True
        self.follow_speed = 0.25
        self.screen_size = Point(config.screen_width, 0, config.screen_height)
        self.screen_center = self.screen_size / 2.0
        self.position += self.screen_size
        self.target_position = self.position
        self.zoom = 1.0
        self.target_zoom = 1.0

    def _ready(self):
        pass

    def _update(self):
        if self.follow_target:
            self.position.move_towards(self.target_position, self.follow_speed)
        
        if abs(self.zoom - self.target_zoom) < 0.001:
            self.zoom = self.target_zoom
        else:
            self.zoom = lerp(self.zoom, self.target_zoom, 0.2)

    def _zoom(self, amount):
        self.set_zoom(self.target_zoom + amount)
    
    def set_zoom(self, z):
        self.target_zoom = clamp(z, 0.5, 5.0)

    def snap_to(self, target):
        self.position = target.position - self.screen_center
    
    def to_screen(self, point):
        """World position to screen position"""
        return (point - self.position) * self.zoom + self.screen_center
    
    def to_world(self, vec):
        """Screen position to world position"""
        rel = (vec - self.screen_center) / self.zoom
        return rel + self.position

    def inside(self, position, size):
        """Is screen position inside camera viewport"""
        return True
        return -size.x < position.x < self.screen_size.x and -size.z < position.z < self.screen_size.z