from .base_unit import BaseUnit

class Milliseconds(BaseUnit):
    BASE_UNIT = "ms"
    BASE_HUMANISE = ("years", "days", "hours", "minutes", "seconds", "ms")
    CONVERSIONS = {
        "ms": 1,
        "s": 1_000,
        "sec": 1_000,
        "secs": 1_000,
        "second": 1_000,
        "seconds": 1_000,
        "m": 60_000,
        "min": 60_000,
        "mins": 60_000,
        "minute": 60_000,
        "minutes": 60_000,
        "h": 3_600_000,
        "hr": 3_600_000,
        "hrs": 3_600_000,
        "hour": 3_600_000,
        "hours": 3_600_000,
        "d": 86_400_000,
        "day": 86_400_000,
        "days": 86_400_000,
        "w": 604_800_000,
        "week": 604_800_000,
        "weeks": 604_800_000,
    }