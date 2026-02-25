import renpy
from . import engine
from .has_zone import HasZone
from .has_flags import HasFlags
from .has_traits import HasTraits
from .has_items import HasItems
from .has_path import HasPath
from .has_rich_text import HasRichText
from .stat import Stat
from .perk import Perk
from .clan import Clan

class Being(HasZone, HasTraits, HasFlags, HasItems, HasPath, HasRichText):
    def __init__(self, _id, name, desc, **kwargs):
        HasZone.__init__(self, zone=kwargs.get("zone"))
        HasTraits.__init__(self, traits=kwargs.get("traits"))
        HasFlags.__init__(self, flags=kwargs.get("flags"))
        HasItems.__init__(self, items=kwargs.get("items"))
        HasPath.__init__(self)
        HasRichText.__init__(self)
        self.id = _id
        self.name = name
        self.desc = desc
        self.following = None
        self._cached_stats = {}
        self.pchar = renpy.store.Character(name)
        self.dialogue_history = set()
        self.fixture = None
        engine.all_beings[_id] = self

    def get_rich_string(self, **kwargs):
        if self.id in engine.all_lore:
            return "{a:lore=" + self.id + "}{}" + "{/a}"
        return super().get_rich_string(**kwargs)

    def cache_stats(self):
        stats = {}
        for stat in self.get_traits(Stat):
            stats[stat.id] = stat.default
        for perk in self.get_traits(Perk):
            perk.mutate_stats(self, stats)
        for clan in self.get_traits(Clan):
            clan.mutate_stats(self, stats)
        for equip in self.get_equipped():
            equip.mutate_stats(self, stats)
        self._cached_stats = stats

    @property
    def male(self): return bool(self.has_trait(renpy.store.male))

    @property
    def female(self): return bool(self.has_trait(renpy.store.female))

    def set_zone(self, zone):
        """Change current location.
            Should trigger the topdown scenee.
        """
        last_zone = self.zone
        if super().set_zone(zone):
            engine.ZONE_EXITED.emit(zone=last_zone, being=self)
            engine.ZONE_ENTERED.emit(zone=self.zone, being=self)

    def update(self, dt):
        HasPath.update_path_following(self, dt)
        # if self.moving and self.path:
        #     target = self.path[0]
        #     dif = target - character
        #     length = dif.length()
        #     norm = dif.normal()
        #     # dist = math.hypot(dx, dy)
            
        #     if length < self.speed * dt:
        #         character.reset(target)
        #         self.path.pop(0)
        #         if not self.path:
        #             self.moving = False
        #             self.check_interaction()
        #             self.check_pending_exit()
        #     else:
        #         self.move(norm * self.speed * dt)
        #         angle = math.degrees(math.atan2(norm.z, norm.x))
        #         self.target_rotation = angle + 90 + 180
    
    def __call__(self, what, *args, **kwargs):
        return self.pchar(what, *args, **kwargs)
    
    def interact(self, form="talk"):
        engine.queue(self, form)
    
    def mark_as_met(self):
        lore = engine.all_lore.get(self.id)
        lore and lore.unlock()
    
    def add_perk(self, perk):
        pass
    
    def remove_perk(self, perk):
        pass

    @property
    def fixated(self):
        return self.fixture != None

