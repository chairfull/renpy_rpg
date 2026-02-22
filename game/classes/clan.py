from . import engine
from .trait import Trait
from .has_traits import HasTraits

class Clan(Trait, HasTraits):
    def __init__(self, _id, name=None, desc=None, allies=None, enemies=None, bonds=None, *args, **kwargs):
        Trait.__init__(self, _id, name, desc, *args, **kwargs)
        HasTraits.__init__(self)
    
    def get_members(self):
        return [x for x in engine.all_beings.values() if x.has_trait(Clan, self.id)]