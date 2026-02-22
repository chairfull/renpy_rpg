from .trait import Trait
class Bond(Trait):
    """Relationship base class."""
    def __init__(self, who=None, *args, **kwargs):
        Trait.__init__(self, *args, **kwargs)
        self.who = who
        self.affinity = 0