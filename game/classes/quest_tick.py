import renpy
from . import engine
from .util import clamp
from .trigger import Trigger

class QuestTick:
    def __init__(self, _id, name=None, desc=None, mark=None, max_ticks=1, trigger=None):
        self.id = _id
        self.name = name or _id
        self.desc = desc
        self.trigger = Trigger(**trigger) if trigger else None
        self.mark = set(mark or []) # IDs of zones, characters, or items to highlight as a way of helper player.
        self.max_ticks = max_ticks

    @property
    def tick(self):
        return self.state if isinstance(self.state, int) else 0
    
    @tick.setter
    def tick(self, value):
        if not self.active or self.completed:
            return
        self.tick = value
        if self.tick >= self.max_ticks:
            self.complete()
        else:
            engine.QUEST_CHANGED.emit(quest=self)
    
    @property
    def completed(self):
        return isinstance(self.state, bool)
    
    def start(self):
        if self.has_tag("origin"):
            engine.GAME_STARTED.emit(quest=self)
        else:
            if self.visible:
                renpy.notify(f"Quest Started: {self.name}")
            engine.QUEST_STARTED.emit(quest=self)
        engine.queue(self, "started")

    def complete(self, fail=False):
        """Forces a quest complete."""
        if not fail:
            self.state = True
            if self.visible:
                renpy.notify(f"Quest Completed: {self.name}")
            engine.QUEST_PASSED.emit(quest=self)
            engine.queue(self, "passed")
        else:
            self.state = False
            if self.visible:
                renpy.notify(f"Quest Failed: {self.name}")
            engine.QUEST_FAILED.emit(quest=self)
            engine.queue(self, "failed")
        engine.queue(self, "completed")
        engine.QUEST_COMPLETED.emit(quest=self)

    @property
    def parent(self):
        quest_id, tick_id = self.id.split("__", 1)
        return renpy.store.all_quests.get(quest_id)
    
    @property
    def children(self):
        """Quests that are children of this one."""
        return {k: v for k, v in engine.all_quests.items() if k.startswith(self.id + "__")}

    @property
    def active(self):
        return self.state is not None
    
    @active.setter
    def active(self, value):
        if value:
            self.state = 0
        else:
            renpy.store.quest_state.discard(self.id)
    
    @property
    def passed(self):
        return isinstance(self.state, bool) and self.state == True
    
    @property
    def failed(self):
        return isinstance(self.state, bool) and self.state == False
    
    @property
    def in_progress(self):
        return isinstance(self.state, int)
    
    @property
    def state(self):
        return renpy.store.quest_state.get(self.id, None)

    @state.setter
    def state(self, value):
        renpy.store.quest_state[self.id] = value

    def start(self):
        if self.active:
            return
        self.active = True
        engine.QUEST_STARTED.emit(quest=self)
    
    @property
    def visible(self):
        return self.id in renpy.store.quest_visible
    
    @visible.setter
    def visible(self, value):
        """Shows or hides quest in quest log."""

        if self.visible == value:
            return

        if value:
            renpy.store.quest_visible.add(self.id)
            engine.QUEST_SHOWN.emit(quest=self)
        else:
            renpy.store.quest_visible.discard(self.id)
            engine.QUEST_HIDDEN.emit(quest=self)