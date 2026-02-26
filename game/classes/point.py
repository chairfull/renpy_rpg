import math
from .util import clamp, lerp

class Point:
    def __init__(self, x=0.0, y=None, z=None):
        if isinstance(x, tuple):
            if len(x) == 2:
                x, z = x
                y = 0.0
            elif len(x) == 3:
                x, y, z = x
        if y is None: y = x
        if z is None: z = x
        self.reset(x, y, z)
    
    def set_debug(self, color="#ff0000", width=1):
        self.debug_color = color
        self.debug_width = width
        return self
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar):
        return Point(self.x / scalar, self.y / scalar, self.z / scalar)

    def __floordiv__(self, scalar):
        return Point(self.x // scalar, self.y // scalar, self.z // scalar)

    def __getattr__(self, name):
        if name == "xz":
            return (self.x, self.z)
        # Renpy screens often won't render stuff at float positions.
        elif name == "xz_int":
            return (int(self.x), int(self.z))
        elif name == "neg_xz_int":
            return (int(-self.x), int(-self.z))
        raise AttributeError(f"'Point' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name == "xz":
            if isinstance(value, Point):
                self.__dict__["x"], self.__dict__["z"] = value.x, value.z
            elif isinstance(value, (list, tuple)):
                if len(value) == 2:
                    self.__dict__["x"], self.__dict__["z"] = float(value[0]), float(value[1])
                elif len(value) == 3:
                    self.__dict__["x"], self.__dict__["z"] = float(value[0]), float(value[2])
        else:
            super().__setattr__(name, value)
    
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def _xyz(self, x=0.0, y=0.0, z=0.0):
        if isinstance(x, (list, tuple)):
            if len(x) == 3:
                x, y, z = x
            elif len(x) == 2:
                x, z = x
            else:
                raise ValueError("Expected a list or tuple of 2-3 elements")
        elif isinstance(x, Point):
            x, y, z = x.x, x.y, x.z
        return float(x), float(y), float(z)

    def reset(self, x=0.0, y=0.0, z=0.0): 
        self.x, self.y, self.z = self._xyz(x, y, z)

    def move(self, x=0.0, y=0.0, z=0.0):
        x, y, z = self._xyz(x, y, z)
        self.x += x
        self.y += y
        self.z += z

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalized(self):
        l = self.length()
        if l == 0:
            return Point(0.0, 0.0, 0.0)
        return Point(self.x / l, self.y / l, self.z / l)
        
    def lerp(self, other, t):
        return Point(
            lerp(self.x, other.x, t),
            lerp(self.y, other.y, t),
            lerp(self.z, other.z, t)
        )
    
    def move_towards(self, other, t):
        self.reset(*self.lerp(other, t))
    
    @classmethod
    def lengthdir_xz(clss, length, angle):
        return Point(math.cos(angle) * length, 0.0, math.sin(angle) * length)