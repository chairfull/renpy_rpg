import renpy
from . import engine
from .util import clamp
from .trigger import Trigger

class QuestTick:
    def __init__(self, _id, name=None, desc=None, mark=None, max_ticks=1, trigger=None):
        self.id = _id
        self.name = name or _id
        self.desc = desc
        self.trigger = Trigger(**trigger)
        self.mark = set(mark or []) # IDs of zones, characters, or items to highlight as a way of helper player.
        self.max_ticks = max_ticks

    @property
    def hidden(self):
        return self.id in renpy.store.quest_hidden
    
    @hidden.setter
    def hidden(self, value):
        if value:
            renpy.store.quest_hidden.add(self.id)
        else:
            renpy.store.quest_hidden.discard(self.id)

    @property
    def tick(self):
        return self.state if isinstance(self.state, int) else 0
    
    @tick.setter
    def tick(self, new_value):
        if not self.active or self.completed:
            return
        self.tick = new_value
        if self.tick >= self.max_ticks:
            self.complete()
        else:
            engine.QUEST_TICK_CHANGED.emit(quest=self.quest, tick=self)

    @property
    def state(self):
        if self.failed: return "failed"
        if self.completed: return "completed"
        if self.active: return "active"
        return "not_started"
    
    @property
    def completed(self):
        return isinstance(self.state, bool)
    
    def complete(self, passed=True):
        """Forces a quest complete."""
        if passed:
            self.state = True
            renpy.notift(f"Quest Complete: {self.name}")
            engine.QUEST_PASSED.emit(quest=self.quest, tick=self)
        else:
            self.state = False
            renpy.notift(f"Quest Failed: {self.name}")
            engine.QUEST_FAILED.emit(quest=self.quest, tick=self)

    @property
    def quest(self):
        quest_id, tick_id = self.id.split("__", 1)
        return renpy.store.all_quests.get(quest_id)

    @property
    def active(self):
        return self.state is not None
    
    @active.setter
    def active(self, value):
        if value:
            self.state = 0
        else:
           del renpy.store.quest_state[self.id]
    
    @property
    def passed(self):
        return isinstance(self.state, bool) and self.state == True
    
    @property
    def failed(self):
        return isinstance(self.state, bool) and self.state == False
    
    @property
    def state(self):
        return renpy.store.quest_state.get(self.id, None)

    @state.getter
    def state(self, value):
        renpy.store.quest_state[self.id] = value

    def start(self):
        if self.active:
            return
        self.active = True
        engine.QUEST_TICK_STARTED.emit(quest=self.quest, tick=self)
    
    def show(self):
        if not self.active:
            self.start()
        
        if self.hide:
            self.hide = False
            engine.QUEST_TICK_SHOWN.emit(quest=self.quest, tick=self)