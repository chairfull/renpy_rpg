init -3000 python:
    class Trait(HasTags):
        def __init__(self, _id, name, desc, tags=None, options=None, range=None, **default)
            HasTags.__init__(self, tags)
            self.id = _id
            self.name = name
            self.desc = desc
            self.default = default
            if range is not None:
                self.type = "range"
                self.range = kwargs["range"]
            elif options is not None:
                self.type = "options"
                self.options = kwargs["options"]
            else:
                self.type = None
        
        def mutate(self, original, *keys, **state):
            if self.type == "options":
                if keys and keys[0] in self.options:
                    return keys[0]
                return self.options[0]
            elif self.type == "range":
                mmin, mmax = self.range
                if keys and keys[0] >= mmin and keys[1] <= mmax:
                    return keys[0]
                return self.range[0]
            else:
                original = original or {}
                for key in self.default:
                    if key not in original:
                        original[key] = self.default[key]
                for key in state:
                    if key in self.default:
                        original[key] = state[key]
                for key in keys:
                    if isinstance(key, tuple):
                        k, v = key
                        original[k] = v
                return original
    
    class HasTraits:
        def __init__(self):
            self.traits = {}
        
        def has_trait(self, trait):
            return trait in self.traits

        def get_trait(self, trait, key=None, default=None):
            tr = self.traits.get(trait)
            if not tr:
                return default
            if key is None:
                return tr
            return tr.get(key, default)
        
        def set_trait(self, trait, *keys, **state):
            self.traits[trait] = trait.mutate(self.traits.get(trait), *keys, **state)

        def reset_trait(self, trait, key=None):
            tr = self.traits.get(trait)
            if not tr:
                return False
            if key is None:
                self.traits[trait] = dict(trait.default)
            else:
                if key in trait.default:
                    tr[trait][key] = trait.default[key]
                else:
                    del tr[trait][key]
            return True

        def remove_trait(self, trait):
            if trait in self.traits:
                del self.traits[trait]
                return True
            return False

        def get_traits(self, trait, key=None):
            matches = {k: v for k, v in self.traits.items() if isinstance(v, trait)}
            if key is not None:
                return {k: v.get(key) for k, v in matches.items()}
            return matches