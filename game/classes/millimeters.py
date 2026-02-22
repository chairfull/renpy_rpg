from .base_unit import BaseUnit

class Millimeters(BaseUnit):
    BASE_UNIT = "mm"
    BASE_HUMANISE = ("km", "m", "mm")
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
