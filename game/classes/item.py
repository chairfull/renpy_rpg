import renpy
from . import engine
from .has_tags import HasTags
from .milligrams import Milligrams

class Item(HasTags):
    """Base item definition class."""
    def __init__(self, _id, name="", desc="", weight=0, cost=0, tags=None, equip_slots=None, stack_size=1_000, **kwargs):
        HasTags.__init__(self, tags)
        self.id = _id
        self.name = name
        self.desc = desc
        self.weight = Milligrams(weight)
        self.cost = cost
        self.stack_size = max(1, int(stack_size or 1))
        self.equip_slots = equip_slots or []
        self.icon_override = None
        engine.all_items[_id] = self
    
    @property
    def stackable(self):
        return self.stack_size > 1

    @property
    def tooltip(self):
        return self.get_tooltip()

    def get_tooltip(self, qty=1, owner=None, stolen=False):
        """Tooltip"""
        # Name.
        lines = [f"{{b}}{self.name}{{/b}}"]
        # Description.
        if self.desc:
            lines.append(f"{{i}}{self.desc}{{/i}}")
        # Quantity.
        if qty is not None:
            lines.append(f"Qty: {{color=#ffd700}}{qty}{{/color}}")
        # Weight.
        if (qty or 1) > 1:
            total = self.mass * (qty or 1)
            lines.append(f"Weight: {{color=#ffd700}}{self.mass}{{/color}} (Total {{color=#ffd700}}{total:.1f}{{/color}})")
        else:
            lines.append(f"Weight: {{color=#ffd700}}{self.mass}{{/color}}")
        # Cost.
        if (qty or 1) > 1:
            total = self.cost * (qty or 1)
            lines.append(f"Value: {{color=#ffd700}}{self.cost}{{/color}} (Total ${{colr=#ffd700}}{total:.1f}{{/color}})")
        else:
            lines.append(f"Value: {{color=#ffd700}}{self.cost}{{/color}}")
        # Owner.
        if owner and owner != engine.player:
            lines.append(f"Owner: {owner.name}")
        # Stolen.
        if stolen:
            lines.append("{color=red}Stolen{/color}")
        return "\n".join(lines)

    @property
    def icon(self):
        """Return an item icon path, falling back to a generic icon."""
        if self.icon:
            return self.icon
        for ext in ("png", "webp", "jpg", "jpeg"):
            candidate = f"images/items/{self.id}.{ext}"
            if renpy.loadable(candidate):
                return candidate
        return "images/items/unknown.webp"