import renpy.persistent as persistent
from . import engine
from .has_tags import HasTags

class Lore(HasTags):
    """Persistent encyclopedia entry."""
    def __init__(self, _id, name=None, content=None, tags=None):
        HasTags.__init__(self, tags)
        self.id = _id
        self.name = name or _id
        self.content = content or ""
        engine.all_lore[_id] = self
    
    @property
    def unlocked(self) -> bool:
        return self.id in persistent.lore

    def unlock(self):
        if self.unlocked:
            return
        persistent.lore.add(self.id)
        engine.LORE_UNLOCKED.emit(lore=self)