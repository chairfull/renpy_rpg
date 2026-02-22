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

def tint(col, factor):
    r, g, b = hex_to_rgb(col)
    return (r * factor, g * factor, b * factor)