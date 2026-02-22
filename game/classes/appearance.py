from .trait import Trait

class Appearance(Trait):
    """For adding descriptive detail to beings and other objects."""
    def __init__(self, *args, **kwargs):
        Trait.__init__(self, *args, **kwargs)