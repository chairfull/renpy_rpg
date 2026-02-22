from .trait import Trait

class Stat(Trait):
    def __init__(self, _id, name=None, desc=None, default=0, *args, **kwargs):
        Trait.__init__(self, _id, name, desc, *args, **kwargs)
        self.default = default