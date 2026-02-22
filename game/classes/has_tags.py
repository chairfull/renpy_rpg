class HasTags:
    """Mixin for objects with tags for filtering."""
    def __init__(self, tags=None, **kwargs):
        self.tags = tags
    
    def has_tag(self, tag):
        return tag in self.tags

    def has_any_tag(self, tags):
        return bool(self.tags & tags)
    
    def has_all_tags(self, tags):
        return tags <= self.tags
    
    def add_tag(self, tag):
        self.tags.add(tag)
    
    def remove_tag(self, tag):
        self.tags.discard(tag)