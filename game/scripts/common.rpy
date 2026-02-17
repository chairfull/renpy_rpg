init -3000 python:
    import json
    import math

    def clamp(val, minv = 0.0, maxv = 1.0):
        return max(minv, min(maxv, val))

    def ease_in_out_sine(val):
        return 0.5 - (math.cos(math.pi * val) * 0.5)

    def lerp(a, b, t):
        return a + (b - a) * t

    def from_dict(cls, data, id=None, **defaults):
        """
        Convert a YAML dict to class constructor kwargs.
        Merges defaults with data (data takes precedence).
        Optionally injects 'id' if provided.
        """
        params = dict(defaults)
        params.update(data)
        if id is not None:
            params['id'] = id
        return cls(**params)
    
    def bracket_label(text, color="#ff3b3b", bracket_color="#ffffff"):
        return "{color=%s}[{/color}{color=%s}%s{/color}{color=%s}]{/color}" % (
            bracket_color, color, text, bracket_color
        )

    def hex_to_rgb(col):
        c = str(col).lstrip("#")
        if len(c) == 3:
            c = "".join([ch * 2 for ch in c])
        if len(c) != 6:
            return (255, 255, 255)
        return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb, alpha=None):
        r, g, b = rgb
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        if alpha is None:
            return "#%02x%02x%02x" % (r, g, b)
        a = max(0, min(255, int(alpha)))
        return "#%02x%02x%02x%02x" % (r, g, b, a)

    def tint_color(col, factor):
        r, g, b = hex_to_rgb(col)
        return (r * factor, g * factor, b * factor)

    def text_outline_fx(color, outline_factor=0.45, shadow_factor=0.2, shadow_alpha=80):
        outline = rgb_to_hex(tint_color(color, outline_factor))
        shadow = rgb_to_hex(tint_color(color, shadow_factor), shadow_alpha)
        return [(2, outline, 0, 0), (2, shadow, 0, 2)]
    
    class Trigger:
        def __init__(self, event_name, event_state={}, condition=None, flags=None):
            self.event_name = event_name # Event that triggers this tick.
            self.event_state = event_state # State the event should be in.
            self.condition = condition # Condition to be met if not None.
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
            if self.condition:
                if not test_function(self.condition):
                    return False
            return True

    class Vector2:
        def __init__(self, x=0.0, y=0.0):
            self.reset(x, y)
        
        def _xy(self, x=0.0, y=0.0):
            if isinstance(x, (list, tuple)):
                if len(x) == 2:
                    x, y = x
                elif len(x) == 3:
                    x, _, y = x
                else:
                    raise ValueError("Expected a list or tuple of 2-3 elements")
            elif isinstance(x, Vector2):
                x, y = x.x, x.y
            elif isinstance(x, Vector3):
                x, y = x.x, x.z
            return x, y

        def __add__(self, other):
            return Vector2(self.x + other.x, self.y + other.y)

        def __sub__(self, other):
            return Vector2(self.x - other.x, self.y - other.y)

        def __mul__(self, scalar):
            return Vector2(self.x * scalar, self.y * scalar)

        def __truediv__(self, scalar):
            return Vector2(self.x / scalar, self.y / scalar)

        def __floordiv__(self, scalar):
            return Vector2(self.x // scalar, self.y // scalar)

        def length(self):
            return math.sqrt(self.x**2.0 + self.y**2.0)
        
        def reset(self, x=0.0, y=0.0):
            self.x, self.y = self._xy(x, y)
        
        def move(self, x=0.0, y=0.0):
            x, y = self._xy(x, y)
            self.x += x
            self.y += y

        def normalized(self):
            l = self.length()
            if l == 0:
                return Vector2(0.0, 0.0)
            return Vector2(self.x / l, self.y / l)

        def lerp(self, other, t):
            return Vector2(
                lerp(self.x, other.x, t),
                lerp(self.y, other.y, t)
            )

    class Vector3:
        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.reset(x, y, z)
        
        def __add__(self, other):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

        def __sub__(self, other):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

        def __mul__(self, scalar):
            return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

        def __getattr__(self, name):
            if name == "xz":
                return Vector2(self.x, self.z)
            raise AttributeError(f"'Vector3' object has no attribute '{name}'")

        def __setattr__(self, name, value):
            if name == "xz":
                if isinstance(value, Vector2):
                    self.__dict__["x"] = value.x
                    self.__dict__["z"] = value.y
                elif isinstance(value, (list, tuple)) and len(value) == 2:
                    self.__dict__["x"] = value[0]
                    self.__dict__["z"] = value[1]
            else:
                super().__setattr__(name, value)

        def _xyz(self, x=0.0, y=0.0, z=0.0):
            if isinstance(x, (list, tuple)):
                if len(x) == 3:
                    x, y, z = x
                elif len(x) == 2:
                    x, z = x
                    y = 0.0
                else:
                    raise ValueError("Expected a list or tuple of 2-3 elements")
            elif isinstance(x, Vector2):
                x, z = x.x, x.z
            elif isinstance(x, Vector3):
                x, y, z = x.x, x.y, x.z
            return x, y, z
        
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

# This is a placeholder cell screen. Replace with actual content based on cell_data.
screen grid_page_cell(cell_data):
    frame:
        background "#1a1a25"
        xsize 120
        ysize 120
        align (0.5, 0.5)
        if cell_data:
            text "Cell" color "#fff" xalign 0.5 yalign 0.5
        else:
            text "" xalign 0.5 yalign 0.5

# Displays a grid of cells, with pagination if there are more cells than fit on one page.
screen grid_page(wide, high, cells):
    default current_page = 0
    $ cells_per_page = wide * high
    $ total_pages = (len(cells) + cells_per_page - 1) // cells_per_page

    frame:
        # background "#000a"
        padding (20, 20)
        vbox:
            spacing 10
            for y in range(high):
                hbox:
                    spacing 10
                    for x in range(wide):
                        $ cell_index = y * wide + x
                        if cell_index < len(cells):
                            use grid_page_cell(cells[cell_index])
                        else:
                            use grid_page_cell(None)  # Empty cell for padding

            hbox:
                spacing 10
                xalign 0.5
                for page in range(total_pages):
                    # draw page icons
                    if page == current_page:
                        text "●" size 20 color "#ffd700"
                    else:
                        textbutton "○" text_size 20 text_color "#999" action SetScreenVariable("current_page", page)

# Commonly applied to buttons to create a standard effect.
transform button_hover_effect:
    on idle:
        parallel:
            ease 0.5 matrixcolor HueMatrix(0.0)
        parallel:
            ease 0.3 additive 0.0
    on hover:
        parallel:
            ease 0.5 matrixcolor HueMatrix(180.0)
        parallel:
            additive 0.0
            ease 0.15 additive 0.3
            ease 0.4 additive 0.0
            
            block:
                ease 0.25 additive 0.15
                ease 0.55 additive 0.0
                repeat