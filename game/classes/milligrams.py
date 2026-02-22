from .base_unit import BaseUnit

class Milligrams(BaseUnit):
    BASE_UNIT = "mg"
    BASE_HUMANISE = ("kg", "g", "mg")
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