class HasRichText:
    """
    Mixin for objects with custom Ren'Py rich-text rendering.
    """
    def __init__(self, rich_string=None, rich_tooltip=None):
        if rich_string:
            setattr(self, "rich_string", rich_string)
        if rich_tooltip:
            setattr(self, "rich_tooltip", rich_tooltip)

    def get_rich_string(self, **kwargs) -> str:
        if hasattr(self, "rich_string"):
            return self.rich_string
        raise NotImplementedError(
            f"{type(self).__name__} inherits HasRichStr "
            "but does not implement to_rich_string()"
        )
    
    def get_rich_tooltip(self, **kwargs) -> str:
        if hasattr(self, "rich_tooltip"):
            return self.rich_tooltip
        raise NotImplementedError(
            f"{type(self).__name__} inherits HasTooltip "
            "but does not implement get_tooltip()"
        )