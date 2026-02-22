class ItemFilter:
    """Used by HasItems to block certain items from the inventory."""
    def __init__(self, _id, slots, allowed_tags=[], blocked_tags=[], allowed_items=[], blocked_items=[]):
        self.id = _id
        self.slots = slots
        self.allowed_tags = allowed_tags
        self.blocked_tags = blocked_tags
        self.allowed_items = allowed_items
        self.blocked_items = blocked_items
    
    def passes(self, item):
        if self.allowed_tags and item.has_any_tag(self.allowed_tags):
            return True
        if self.allowed_items and item in self.allowed_items:
            return True
        if self.blocked_tags and item.has_any_tag(self.blocked_tags):
            return False
        if self.blocked_items and item in self.blocked_items:
            return False
        return True