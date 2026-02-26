import math
import renpy
from renpy.exports import notify
from .point import Point
from .point_list import PointList
from .sphere import Sphere
from .scene import Scene
from .scene_child import SceneChild
from .scene_light import SceneLight
from .assets import find_image

class SceneDebug(Scene):
    def __init__(self):
        super().__init__()
        self.bg.append(SceneChild(image=find_image("tiles/checker"), zoom=0.25))
        self.bg.append(SceneChild(image=find_image("tiles/checker"), zoom=0.25, position=Point(256, 0, 256)))
        self.children.append(SceneChild(image=find_image("topdown/chars/male_base")))
        self.ui.append(SceneChild(image=find_image("gui/landmark")))
        self.landmark = self.ui[-1]
        self.lights.append(SceneLight())
        self.lights.append(SceneLight("#ff0000"))
        self.lights.append(SceneLight("#0000ff"))
        self.debug["point_line"] = PointList((0, 0), (200, 0), (200, 200)).set_debug()
        self.debug["sphere"] = Sphere(Point(), 256.0).set_debug()
        self.anim = 0.0
    
    def _update_transform(self, tr, st, at):
        self.anim += 0.01
        # mx, my = renpy.exports.get_mouse_pos()
        self.lights[-1].position = Point(256, 0, 256) + Point.lengthdir_xz(256, self.anim)
        self.lights[-2].position = Point(256, 0, 256) + Point.lengthdir_xz(256, -self.anim)
        self.lights[-3].position = Point(256, 0, 256) + Point.lengthdir_xz(128, self.anim * .5)
        return super()._update_transform(tr, st, at)

    def _clicked(self, what=None, alternate=False):
        if what is None and not alternate:
            self.camera.target_position = self.get_mouse()
            self.landmark.position = self.get_mouse()
        return super()._clicked(what, alternate)