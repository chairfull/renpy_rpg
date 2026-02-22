from . import engine
from .trigger import Trigger

class Choice:
    """Dialogue choices when talking to characters or interacting w objects."""
    def __init__(self, _id, menu, text, long=None, emoji=None, cond=None, flags=None):
        self.id = _id
        self.menu = menu
        self.text = text
        self.long = long
        self.emoji = emoji
        self.trigger = Trigger(cond=cond, flags=flags)
        engine.CHOICES_REQUESTED.connect(self._choices_requested)
    
    def _choices_requested(self, menu, choices):
        if self.menu != menu:
            return
        if self.cond and not engine.test_condition(self.cond):
            return
        choices.append(self)

def request_choices(menu):
    choices = []
    engine.CHOICES_REQUESTED.emit(menu=menu, choices=choices)
    return choices