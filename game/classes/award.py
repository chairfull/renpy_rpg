import renpy
from . import engine
from .has_tags import HasTags
from .trigger import Trigger

class Award(HasTags):
    def __init__(self, _id, name, desc, icon="🏆", tags=None, trigger=None, max_ticks=1, **kwargs):
        HasTags.__init__(tags)
        self.id = _id
        self.name = name
        self.desc = desc
        self.icon = icon
        self.trigger = trigger or Trigger()
        self.max_ticks = max(1, max_ticks)
        engine.all_awards[_id] = self
    
    @property
    def completed(self):
        return self.id in renpy.persistent.awards

    @property
    def ticks(self):
        return renpy.persistent.award_ticks.get(self.id, 0)
    
    @ticks.setter
    def ticks(self, value):
        renpy.persistent.award_ticks[self.id] = value

    @property
    def delta(self):
        return self.ticks / float(self.max_ticks) 

    def tick(self, amount=1):
        self.ticks += 1
        if self.ticks >= self.max_ticks:
            self.ticks = self.max_ticks
            self.unlock()

    def unlock(self):
        if self.completed:
            return
        renpy.persistent.awards.add(self.id)
        engine.AWARD_UNLOCKED.emit(award=self)
    
    @classmethod
    def total_completed(clss):
        return len(renpy.persistent.awards)
    
    @classmethod
    def total_progress(clss):
        ticks = 0
        max_ticks = 0
        for award in engine.all_awards:
            ticks += award.ticks()
            max_ticks += award.max_ticks
        delta = ticks / float(max_ticks)
        return ticks, max_ticks, delta