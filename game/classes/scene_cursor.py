import renpy
from .point import Point

class SceneCursor:
    def __init__(self):
        self._position = Point()
        
    def _update_transform(self, tr, st, at):
        mx, my = renpy.exports.get_mouse_pos()
        self._position.move_towards(Point(mx, 0, my), 0.3)
        tr.pos = self._position.xz_int
        return 0.0