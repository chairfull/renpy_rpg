import renpy

class HasLock:
    """Base for locks that prevent travel or accessing inventories."""
    def __init__(self, subtype="physical", difficulty=1, keys=None, locked=True):
        self.subtype = subtype
        self.difficulty = difficulty
        self.keys = set(keys or [])
        self.locked = locked
    
    def unlock(self, key_id):
        if key_id in self.keys:
            self.locked = False
            return True
        return False
        
    def pick(self, skill_level=0):
        # Simple check for now (placeholder for minigame)
        # Roll or stat check
        if skill_level + renpy.random.randint(1, 20) >= self.difficulty + 10:
            self.locked = False
            return True
        return False
        
    def lock(self):
        self.locked = True