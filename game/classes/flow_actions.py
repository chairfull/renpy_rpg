import renpy
from . import engine
"""Functions called by flow script"""

def PLAYER(being):
    engine.set_player(being)

def ZONE(zone):
    engine.player.zone = zone

def NOTIFY(msg, *args, **kwargs):
    renpy.notify(msg, *args, **kwargs)

def AWARD(award):
    award.unlock()

def FLAG(flag, value=True):
    """Set a flag to True or any given value"""
    flag.change(value)

def FLAG_RESET(flag):
    flag.reset()

def FLAG_TOGGLE(flag):
    flag.toggle()

def GAIN(item, count=None, who=None, _from=None, steal=False):
    """Gain an item from an inventory. Optionally remove it some someone else"""
    count = count or 1
    who = who or engine.player()
    who and who.gain_item(item, count, owner=_from, steal=steal)
    _from and _from.lose_item(item, count)

def LOSE(item, count=None, who=None, _from=None, steal=False):
    """Remove an item from an inventory. Optionally add it some someone else"""
    who = who or engine.player()
    GAIN(item, count=count, who=_from, _from=who, steal=steal)

def LORE(lore):
    """Unlocks lore for the codex"""
    lore.unlock()

def FOLLOWER(who, follow=None):
    """Start following the player or follow"""
    who.follow = follow or engine.player()

def UNFOLLOWER(who):
    """Stops a being from following"""
    who.follow = None

def BOND(who, type, amount=1, _with=None):
    pass # TODO

def SHOW(what, *args, **kwargs):
    pass

def HIDE(what, *args, **kwargs):
    pass

def QUEST_TICK(quest, amount=1):
    """Tick a quest. This may set it to passed if ticks == max_ticks."""
    quest.tick(amount)

def QUEST_SHOW(quest):
    """Show a quest in the quest log. (Otherwise it stays hidden.)"""
    quest.show()

def QUEST_COMPLETE(quest, fail=False):
    """Mark a quest as passed. If it's visible it will create a notification."""
    if not fail:
        quest.set_passed()
    else:
        quest.set_failed()

def MET(who):
    """Marks a character as met, creating a notification."""
    who.mark_met()

def PERK(perk, *args):
    engine.player.set_trait(perk, *args)

def STAT(stat, remove=False, *args):
    pass

def get_flow_actions():
    """Returned values are tuple of (func, doc string, properties)"""
    import sys
    import inspect
    module = sys.modules[__name__]
    actions = {
        name: (func, inspect.getdoc(func), inspect.signature(func))
        for name, func in inspect.getmembers(module, inspect.isfunction)
        if name.isupper()
    }
    return actions