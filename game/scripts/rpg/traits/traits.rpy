init -3000 python:
    class Trait(Taggable):
        def __init__(self, _id, state_key=None, tags=[])
            Taggable.__init__(self, tags)
            self.id = _id
            self.name = name
            self.desc = desc

        def get_traits(self):
            return [x for x in all_traits if x.has_tag(self.id)]
        
        def to_value(self, *args, **kwargs):
            return (args, kwargs)
    
    class HasTraits:
        def __init__():
            self.traits = {}
        
        def has_trait(self, trait):
            return trait in self.traits
        
        def add_trait(self, trait, *args, **kwargs):
            if self.has_trait(key):
                return
            self.traits[trait.id] = trait.to_value(*args, **kwargs)
        
        def get_trait(self, trait, **kwargs):
            return self.traits.get(trait.id)
        
        def get_traits(self, tag_or_class):
            if isinstance(tag, str):
                return {k: v for k, v in self.traits.items() if v.has_tag(tag_or_class)}
            elif isinstance(tag, Trait):
                return {k: v for k, v in self.traits.items() if isinstance(v, tag_or_class)}
            return []