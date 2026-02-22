import renpy

class MetaMenuTab:
    def __init__(self, id, emoji, name, **kwargs):
        self.id = id
        self.emoji = emoji
        self.name = name
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])
    
    def get_screen(self):
        return renpy.display.screen.screens.get(f"meta_menu_{self.id}_screen")

class MetaMenu:
    def __init__(self):
        self.tabs = {}
        self.selected = None
        self.minimised = True

    def add_tab(self, mm_id, emoji, name, **kwargs):
        self.tabs[mm_id] = MetaMenuTab(mm_id, emoji, name, **kwargs)
    
    def open(self, to = None):
        self.selected = to
        self.minimised = False