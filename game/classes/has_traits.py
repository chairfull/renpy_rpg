
class HasTraits:
    """Mixin for Stats, Perks, Factions, and Relationships"""
    def __init__(self, traits=None):
        self.traits = traits or {}
    
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