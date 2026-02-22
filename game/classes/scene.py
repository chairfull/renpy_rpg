import renpy
from .vector3 import Vector3
from .scene_camera import SceneCamera

class Scene:
    """Object that handles updating and rendering children in a screen."""
    def __init__(self):
        self.update_dt =  1.0 / 60.0
        self.show_reachability = False
        self.camera = SceneCamera()
        self.bg = [] # Non-interactive images rendered below objects.
        self.children = [] # Interactive objects that implement a _process().
        self.paused = False
    
    def _ready(self):
        self.camera._ready()
        for child in self.children:
            child._ready()
    
    def _process(self, dt):
        self.camera._process(dt)
        if self.paused:
            return
        for child in self.children:
            child._process(dt)
    
    def _clicked(self, what=None, alternate=False):
        if self.paused:
            return
        if what is not None:
            x, y, z = self.get_mouse()
            renpy.notify(f"Clicked at {x}, {y}, {z}.")
        else:
            what._clicked(alternate)

    def get_mouse(self):
        mx, my = renpy.get_mouse_pos()
        return self.camera.screen_to_world(Vector3(mx, 0, my))