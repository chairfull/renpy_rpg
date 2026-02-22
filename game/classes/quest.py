import renpy
from . import engine
from .has_tags import HasTags
from .trigger import Trigger

class Quest(HasTags):
    def __init__(self, _id, name, desc="", tags=[], trigger=None):
        HasTags.__init__(self, tags)
        self.id = _id
        self.name = name
        self.desc = desc
        self.trigger = trigger or Trigger()
        self.ticks = set()
    
    @property
    def is_origin(self):
        return self.has_tag("origin")

    @classmethod
    def get_origins(clss):
        return [x for x in engine.all_quests if "origin" in x.tags]

    def start(self):
        if self.has_tag("origin"):
            engine.GAME_STARTED.emit(origin=self)
        else:
            renpy.notify(f"Quest Started: {self.name}")
            engine.QUEST_STARTED.emit(quest=self)
        engine.queue(self, "started")
        return True

    def complete(self, outcome_id=None):
        self.state = "passed"
        renpy.notify(f"Quest Completed: {self.name}")
        engine.QUEST_COMPLETED.emit(quest=self)
        engine.queue(self, "passed")

    def fail(self):
        self.state = "failed"
        renpy.notify(f"Quest Failed: {self.name}")
        engine.QUEST_FAILED.emit(quest=self)
        engine.queue(self, "failed")