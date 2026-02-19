init -3000 python:
    class HasScreen:
        """Object that can draw to screen."""
        def __init__(self, position=Vector3(), tooltip=None, action=None, transform=None, sprite=None):
            self.position = position
            self.tooltip = tooltip
            self.sprite = sprite
            self.transform = transform
            self.action = action if action is not None else []
            self.rotation = rotation
            self.anchor = (0.5, 0.5)
            self.size = (120, 120)
        
        def update_screen(self, dt):
            pass

        def transform(self):
            return self.transform
        
        def action(self):
            return self.action

    class Trigger:
        def __init__(self, event_name, event_state={}, cond=None, flags=None):
            self.event_name = event_name # Event that triggers this tick.
            self.event_state = event_state # State the event should be in.
            self.cond = cond # Condition to be met if not None.
            self.flags = flags # Optional quick test against flags.
        
        def check(self, event, **kwargs):
            if not self.active:
                return False
            if self.event_name and self.event_name != event.name:
                return False
            if self.event_state:
                for k, v in self.event_state.items():
                    if kwargs.get(k) != v:
                        return False
            if self.flags:
                for flag in self.flags:
                    if not flag_get(flag, False):
                        return False
            if self.cond:
                if not test_condition(self.condition):
                    return False
            return True

    class Vector3:
        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.reset(x, y, z)
        
        def __add__(self, other):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

        def __sub__(self, other):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

        def __mul__(self, scalar):
            return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
        def __truediv__(self, scalar):
            return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

        def __floordiv__(self, scalar):
            return Vector3(self.x // scalar, self.y // scalar, self.z // scalar)

        def __getattr__(self, name):
            if name == "xz":
                return (self.x, self.z)
            elif name == "xz_int":
                return (int(self.x), int(self.z))
            raise AttributeError(f"'Vector3' object has no attribute '{name}'")

        def __setattr__(self, name, value):
            if name == "xz":
                if isinstance(value, Vector3):
                    self.__dict__["x"] = value.x
                    self.__dict__["z"] = value.z
                elif isinstance(value, (list, tuple)):
                    if len(value) == 2:
                        self.__dict__["x"] = value[0]
                        self.__dict__["z"] = value[1]
                    elif len(value) == 3:
                        self.__dict__["x"] = value[0]
                        self.__dict__["z"] = value[2]
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
            elif isinstance(x, Vector3):
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
                return Vector3(0.0, 0.0, 0.0)
            return Vector3(self.x / l, self.y / l, self.z / l)
            
        def lerp(self, other, t):
            return Vector3(
                lerp(self.x, other.x, t),
                lerp(self.y, other.y, t),
                lerp(self.z, other.z, t)
            )
       
        def move_towards(self, other, t):
            self.reset(*self.lerp(other, t))
    
    class Milligrams(int):
        CONVERSIONS = {
            "mg": 1,
            "g": 1_000,
            "kg": 1_000_000,
            "oz": 28_349,
            "lb": 453_592,
            "lbs": 453_592,
            "grain": 65,
            "grains": 65,
        }

        @classmethod
        def parse(cls, value):
            if isinstance(value, str):
                value = value.strip().lower()
                for unit, factor in cls.CONVERSIONS.items():
                    if value.endswith(unit):
                        number = float(value[:-len(unit)].strip())
                        return cls(round(number * factor))
                raise ValueError(f"Unknown unit in: {value!r}")
            return cls(value)

        def __add__(self, other):
            return Milligrams(int(self) + int(Milligrams.parse(other)))

        def __radd__(self, other):
            return Milligrams(int(Milligrams.parse(other)) + int(self))

        def __sub__(self, other):
            return Milligrams(int(self) - int(Milligrams.parse(other)))

        def __repr__(self):
            return f"{int(self)}mg"

        def __getattr__(self, name):
            unit = name.lstrip("_").rstrip("_").replace("_", " ")
            if unit in self.CONVERSIONS:
                return int(self) / float(self.CONVERSIONS[unit])
            raise AttributeError(f"Unknown unit: {name!r}")

    class Millimeters(int):
        CONVERSIONS = {
            "mm": 1,
            "cm": 10,
            "m": 1_000,
            "km": 1_000_000,
            "in": 25.4,
            "inch": 25.4,
            "inches": 25.4,
            "ft": 305,
            "feet": 305,
            "foot": 305,
            "yd": 914,
            "yard": 914,
            "yards": 914,
            "mi": 1_609_344,
            "mile": 1_609_344,
            "miles": 1_609_344,
        }

        @classmethod
        def parse(cls, value):
            if isinstance(value, str):
                value = value.strip().lower()
                for unit, factor in cls.CONVERSIONS.items():
                    if value.endswith(unit):
                        number = float(value[:-len(unit)].strip())
                        return cls(round(number * factor))
                raise ValueError(f"Unknown unit in: {value!r}")
            return cls(value)

        def __add__(self, other):
            return Millimeters(int(self) + int(Millimeters.parse(other)))

        def __radd__(self, other):
            return Millimeters(int(Millimeters.parse(other)) + int(self))

        def __sub__(self, other):
            return Millimeters(int(self) - int(Millimeters.parse(other)))

        def __repr__(self):
            return f"{int(self)}mm"

        def __getattr__(self, name):
            unit = name.lstrip("_").rstrip("_").replace("_", " ")
            if unit in self.CONVERSIONS:
                return int(self) / float(self.CONVERSIONS[unit])
            raise AttributeError(f"Unknown unit: {name!r}")