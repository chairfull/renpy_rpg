import math
from .point import Point

class Sphere:
    def __init__(self, position=Point(), radius=1.0):
        self.position = position
        self.radius = radius

    def set_debug(self, color="#ff0000", width=1):
        self.debug_color = color
        self.debug_width = width
        return self
    
    def get_circle(self, points):
        for i in range(0, points):
            t = (i / float(points)) * math.tau
            x, y, z = self.position
            x += math.cos(t) * self.radius
            z += math.sin(t) * self.radius
            yield Point(x, y, z)