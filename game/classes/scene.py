import renpy
from .point import Point
from .scene_camera import SceneCamera
from .scene_cursor import SceneCursor
from itertools import chain

class Scene:
    """Object that handles updating and rendering children in a screen."""
    def __init__(self):
        self.camera = SceneCamera()
        self.cursor = SceneCursor()
        # TODO: change bg, children, lights, ui to all use dict and have ids for easier
        self.bg = {} # Non-interactive images rendered below objects.
        self.children = {} # Interactive objects that implement a _process().
        self.lights = {}
        self.ui = {} # Rendered over everything including the lights.
        self.debug = {}
        self.paused = False
        self.hovering = None
        self.msg = ""
        self.tick = 0
    
    def reset(self):
        self.camera.reset()
        self.cursor.reset()
        self.bg.clear()
        self.children.clear()
        self.lights.clear()
        self.ui.clear()
        self.debug.clear()

    def init_from_zone(self, zone):
        self.reset()

    def _ready(self):
        self.camera._ready()
        for child in self.children.values():
            child._ready()

    def _update_transform(self, tr, st, at):
        self.tick += 1
        # self.msg = f"Tick: {self.tick}"
        # self.msg = f"Camera pos: {self.children[0].transform.pos} zoom: {self.children[0].transform.zoom}"
        
        self.camera._update()
        
        for child in chain(self.bg.values(), self.children.values(), self.ui.values()):
            child._apply_camera_transform(self.camera)
        
        return 0.0
    
    def _hovered(self, what=None):
        if what == self.hovering:
            return
        self.hovering = what

    def _clicked(self, what=None, alternate=False):
        if self.paused:
            return
        if what is None:
            x, y, z = self.get_mouse()
            renpy.exports.notify(f"Clicked at {x}, {y}, {z}.")
        else:
            what._clicked(alternate)

    def get_mouse(self):
        mx, my = renpy.exports.get_mouse_pos()
        return self.camera.to_world(Point(mx, 0, my))