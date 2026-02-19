init -3000 python:
    import json
    import math

    def clamp(val, minv = 0.0, maxv = 1.0):
        return max(minv, min(maxv, val))

    def ease_in_out_sine(val):
        return 0.5 - (math.cos(math.pi * val) * 0.5)

    def lerp(a, b, t):
        return a + (b - a) * t
    
    def bracket_label(text, color="#ff3b3b", bracket_color="#ffffff"):
        """White square brackets w colored text inside."""
        return "{color=%s}[{/color}{color=%s}%s{/color}{color=%s}]{/color}" % (
            bracket_color, color, text, bracket_color
        )

    def parse_height_to_inches(self, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        s = str(value).strip().lower()
        if not s:
            return None
        # 5'10" or 5 ft 10 in
        if "'" in s or "ft" in s:
            ft = 0.0
            inch = 0.0
            # normalize separators
            s = s.replace("feet", "ft").replace("foot", "ft").replace("inches", "in").replace("inch", "in").replace("\"", "in")
            parts = s.replace("ft", " ft ").replace("in", " in ").replace("'", " ft ").split()
            for i in range(len(parts)):
                token = parts[i]
                if token.replace(".", "", 1).isdigit():
                    num = float(token)
                    unit = parts[i + 1] if i + 1 < len(parts) else ""
                    if unit == "ft":
                        ft = num
                    elif unit == "in":
                        inch = num
            return ft * 12.0 + inch
        if "cm" in s:
            try:
                num = float(s.replace("cm", "").strip())
                return num / 2.54
            except Exception:
                return None
        if "m" in s:
            try:
                num = float(s.replace("m", "").strip())
                return (num * 100.0) / 2.54
            except Exception:
                return None
        if "in" in s:
            try:
                return float(s.replace("in", "").strip())
            except Exception:
                return None
        try:
            return float(s)
        except Exception:
            return None

    def parse_weight_to_lbs(self, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        s = str(value).strip().lower()
        if not s:
            return None
        if "kg" in s:
            try:
                num = float(s.replace("kg", "").strip())
                return num * 2.20462
            except Exception:
                return None
        if "g" in s and "kg" not in s:
            try:
                num = float(s.replace("g", "").strip())
                return num * 0.00220462
            except Exception:
                return None
        if "lb" in s or "lbs" in s:
            try:
                return float(s.replace("lbs", "").replace("lb", "").strip())
            except Exception:
                return None
        try:
            return float(s)
        except Exception:
            return None

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