from .trait import Trait

class Perk(Trait):
    def __init__(self, *args, **kwargs):
        Trait.__init__(self, *args, **kwargs)
