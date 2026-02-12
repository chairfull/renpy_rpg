init python:
    import math

    def clamp(val, minv = 0.0, maxv = 1.0):
        return max(minv, min(maxv, val))

    def ease_in_out_sine(val):
        return 0.5 - (math.cos(math.pi * val) * 0.5)

    def lerp(a, b, t):
        return a + (b - a) * t