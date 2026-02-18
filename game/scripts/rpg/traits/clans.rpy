init python:
    class Clan(Trait, HasTraits):
        def __init__(self, *args, **kwargs):
            Trait.__init__(self, *args, **kwargs)
            HasTraits.__init__(self, *args, **kwargs)
        
        def get_members(self):
            return [x for x in all_characters.values() if x.has_trait(["faction", self.id])]