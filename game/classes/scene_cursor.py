import renpy
from .vector3 import Vector3

class SceneCursor:
    def __init__(self):
        self._position = Vector3()
        
    def _update_transform(self, tr, st, at):
        mx, my = renpy.exports.get_mouse_pos()
        self._position.move_towards(Vector3(mx, 0, my), 0.3)
        tr.pos = self._position.xz_int
        return 0.0