import renpy
from renpy.color import Color
from .util import clamp
from .point import Point

class SceneLight:
    def __init__(self, color="#fff", radius=256.0, energy=0.9, image="light.svg"):
        self.position = Point()
        self._color = Color(color)
        self._radius = radius
        self._energy = clamp(energy, 0.0, 1.0)
        self._image = f"../game/images/lighting/{image}"

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, v):
        self._color = Color(v)
        self._invalidate()

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, v):
        self._radius = v
        self._invalidate()

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, v):
        self._energy = clamp(v, 0.0, 1.0)
        self._invalidate()

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, v):
        self._image = f"../game/images/lighting/{v}"
        self._invalidate()

    def _invalidate(self):
        """Bust the layer's cache by clearing the key it checks against."""
        self._light_surf_key = None