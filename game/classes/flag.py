import renpy
from . import engine

class Flag:
    """Basic variable that fires event when changed."""
    def __init__(self, _id, name="", desc="", default=False):
        self.id = _id
        self.name = name
        self.desc = desc
        self.default = default
    
    @property
    def value(self):
        return renpy.store.flag_state.get(self.id, self.default)

    @value.setter
    def value(self, value):
        if self.value == value:
            return
        old_value = self.value
        renpy.store.flag_state[self.id] = value
        engine.FLAG_CHANGED.emit(flag=self, old_value=old_value)

    @property
    def parent(self):
        if "." in self.id:
            return getattr(renpy.store, self.id.split(".", 1)[0])
        return None

    def toggle(self):
        self.value = not self.value
    
    def reset(self):
        if self.id not in renpy.store.flag_state:
            return
        old_value = self.value
        renpy.store.flag_state.discard(self.id)
        engine.FLAG_CHANGED.emit(flag=self, old_value=old_value)