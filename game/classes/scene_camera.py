import renpy.config as config
from .vector3 import Vector3
from .util import lerp, clamp
from .engine import player

class SceneCamera:
    def __init__(self, position=Vector3(), zoom=1.0):
        self.position = position
        self.screen_size = Vector3(config.screen_width, 0, config.screen_height)
        self.screen_center = self.screen_size / 2.0
        self.zoom = zoom
        self.target_zoom = zoom
        self._snapped = False # Camera snap flag - skip lerp on first frame after setup
    
    def update(self, dt):
        target_cam = player.position - self.screen_center
        
        # Skip lerp if camera was just snapped (first frame after setup)
        if self._snapped:
            self.position = target_cam
            self._snapped = False
        else:
            lerp_speed = dt * 5.0
            self.position = self.position.lerp(target_cam, lerp_speed)
    
        if abs(self.zoom - self.target_zoom) < 0.001:
            return None # Already at target, no update needed
        else:
            # Get current center point in world coords BEFORE zoom changes
            old_zoom = self.zoom
            center_world = (self.position + self.screen_center) / old_zoom
            
            # Lerp zoom (fast but smooth), snap when very close
            if abs(self.zoom - self.target_zoom) < 0.01:
                self.zoom = self.target_zoom
            else:
                self.zoom = lerp(self.zoom, self.target_zoom, 0.2)
            
            # Calculate new scroll position to maintain center (always, including final frame)
            self.position = center_world * self.zoom - self.screen_center

    def set_zoom(self, z):
        self.target_zoom = clamp(z, 0.5, 5.0)

    def snap_to(self, target):
        self.position = target.position - self.screen_center
    
    def world_to_screen(self, vec):
        return (vec.x - self.x, vec.z - self.z)
    
    def screen_to_world(self, vec):
        rel = (vec - self.screen_center) / self.zoom
        return rel + self.screen_center + self.position

    def in_view(self, position, size):
        return True
        return -size.x < position.x < self.screen_size.x and -size.z < position.z < self.screen_size.z