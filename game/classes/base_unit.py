class BaseUnit(int):
    """Base class for unit measurement types backed by a smallest integer unit.
        See:
            - Milliseconds for time
            - Millimeters for length
            - Milligrams for weight
            - Millicents for money"""
    CONVERSIONS = {}
    BASE_UNIT = ""  # e.g. "mg", "mm", "ms"
    BASE_HUMANISE = ()

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
        return type(self)(int(self) + int(type(self).parse(other)))

    def __radd__(self, other):
        return type(self)(int(type(self).parse(other)) + int(self))

    def __sub__(self, other):
        return type(self)(int(self) - int(type(self).parse(other)))

    def __mul__(self, factor: float):
        return type(self)(round(int(self) * factor))

    def __rmul__(self, factor: float):
        return type(self)(round(factor * int(self)))

    def __truediv__(self, factor: float):
        return type(self)(round(int(self) / factor))

    def __floordiv__(self, other):
        # dividing by same unit type gives a plain ratio, not a new unit
        # e.g. Milliseconds("10 seconds") // Milliseconds("1 second") → 10
        if isinstance(other, type(self)):
            return int(self) // int(other)
        return type(self)(int(self) // int(other))

    def __mod__(self, other):
        return type(self)(int(self) % int(type(self).parse(other)))

    def __abs__(self):
        return type(self)(abs(int(self)))

    def __neg__(self):
        return type(self)(-int(self))

    def __repr__(self):
        return f"{int(self)}{self.BASE_UNIT}"

    def __getattr__(self, name):
        unit = name.lstrip("_").rstrip("_").replace("_", " ")
        if unit in self.CONVERSIONS:
            return int(self) / float(self.CONVERSIONS[unit])
        raise AttributeError(f"Unknown unit: {name!r}")
    
    def clamp(self, min_val, max_val):
        return type(self)(max(int(type(self).parse(min_val)), min(int(self), int(type(self).parse(max_val)))))

    def lerp(self, other, t: float):
        """Linear interpolation between self and other.
        t=0 returns self, t=1 returns other.
        e.g. Milliseconds("1 hour").lerp("2 hours", 0.5) → 5400000ms (1.5 hours)
        """
        a, b = int(self), int(type(self).parse(other))
        return type(self)(round(a + (b - a) * t))

    def to_nearest(self, *units):
        """Returns largest value unit."""
        units = units or self.BASE_HUMANISE
        for unit in units:
            value = int(self) / float(self.CONVERSIONS[unit])
            if value >= 1:
                return value, unit
        # fallback to the smallest unit if nothing is >= 1
        unit = units[-1]
        return int(self) / float(self.CONVERSIONS[unit]), unit

    def components(self, *units) -> dict[str, int]:
        """Break value into whole parts per unit, largest first.
        e.g. 5400000ms.components("hours", "minutes", "seconds")
            → {"hours": 1, "minutes": 30, "seconds": 0}
        """
        units = units or self.BASE_HUMANISE
        remaining = int(self)
        result = {}
        for unit in units:
            factor = int(self.CONVERSIONS[unit])
            result[unit] = remaining // factor
            remaining %= factor
        return result

    def breakdown(self, *units) -> str:
        """Human readable full breakdown, skipping zero-value units.
        e.g. "1 hour, 30 minutes"
        """
        units = units or self.BASE_HUMANISE
        parts = self.components(*units)
        return ", ".join(
            f"{v} {u}" for u, v in parts.items() if v > 0
        ) or f"0 {units[-1]}"
    
    def humanise(self, *units, commas=True):
        """Returns a nice string as largest value unit."""
        units = units or self.BASE_HUMANISE
        value, unit = self.to_nearest(*units)
        rounded = round(value, 2)
        if commas:
            # :, adds comma separators, :g strips trailing zeros
            # but we need both, so format with comma then strip trailing decimal zeros
            formatted = f"{rounded:,.2f}".rstrip("0").rstrip(".")
        else:
            formatted = f"{rounded:g}"
        return f"{formatted} {unit}"