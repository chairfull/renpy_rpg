from .has_tags import HasTags

class Trait(HasTags):
    def __init__(self, _id, name=None, desc=None, tags=None, options=None, range=None, **default):
        HasTags.__init__(self, tags)
        self.id = _id
        self.name = name
        self.desc = desc
        self.default = default
        if range is not None:
            self.type = "range"
            self.range = default["range"]
        elif options is not None:
            self.type = "options"
            self.options = default["options"]
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

