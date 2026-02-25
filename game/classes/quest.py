import renpy
from . import engine
from .has_tags import HasTags
from .quest_tick import QuestTick

class Quest(HasTags, QuestTick):
    def __init__(self, _id, name, desc="", tags=[], trigger=None):
        HasTags.__init__(self, tags)
        QuestTick.__init__(self, _id, name, desc, trigger)
        engine.all_quests[_id] = self
    
    @property
    def is_origin(self):
        return self.has_tag("origin")

    @property
    def image(self):
        return ""

    @classmethod
    def get_quests(clss, tag=None):
        return [x for x in engine.all_quests.values() if tag is None or tag in x.tags]

    @classmethod
    def get_origins(clss):
        return clss.get_quests("origin")