from .base_unit import BaseUnit

class Millicents(BaseUnit):
    BASE_UNIT = "mc"
    BASE_HUMANISE = ("dollars", "cents")
    CONVERSIONS = {
        "mc":           1,
        "millicent":    1,
        "millicents":   1,
        "c":            1_000,
        "cent":         1_000,
        "cents":        1_000,
        "$":            100_000,
        "dollar":       100_000,
        "dollars":      100_000,
    }