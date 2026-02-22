import renpy
from .signal import Signal

_FLOW_ACTIONS = {}
all_awards = {}
all_beings = {}
all_flags = {}
all_items = {}
all_crafts = {}
all_lore = {}
all_zones = {}
all_quests = {}

def get_flag(self, _id):
    return renpy.store.all_flags.get(_id)

def queue(qtype, suffix=None, *args, **kwargs):
    """Queue a label or screen to play after the current ones."""
    if isinstance(qtype, object):
        label = get_object_label_name(qtype, suffix)
        if not renpy.has_label(label):
            raise ValueError(f"Label '{label}' does not exist.")
        renpy.store.loop_queue.append(("label", [label] + args, kwargs))
    else:
        renpy.store.loop_queue.append((qtype, args, kwargs))

def queue_label(label, *args, **kwargs):
    if not renpy.has_label(label):
        raise ValueError(f"Label '{label}' does not exist.")
    queue("label", label, *args, **kwargs)

def queue_screen(screen, *args, **kwargs):
    if not renpy.has_screen(screen):
        raise ValueError(f"Screen '{screen}' does not exist.")
    queue("screen", screen, *args, **kwargs)

def get_object_label_name(obj, suffix=None):
    """Pattern: obj_id.suffix"""
    return f"{obj.id}.{suffix}" if suffix else obj.id

def has_object_label(obj, suffix=None):
    """Check if an internal label exists for an object."""
    label = get_object_label_name(obj, suffix)
    return label in renpy.get_all_labels()

def get_all_object_labels(obj):
    """Find all labels this one contains."""
    head = get_object_label_name(obj) + "."
    return [x for x in renpy.get_all_labels() if x.beginswith(head)]

def test_condition(f_id):
    return bool(getattr(globals(), f"_cond_{f_id}"))

#region Flow actions
def call_flow_action(action_name, *args, **kwargs):
    func = _FLOW_ACTIONS.get(action_name)
    if not func:
        raise Exception(f"Unknown flow action: {action_name}")
    return func(*args, **kwargs)

def flow_action(name):
    """Marks a function for calling from flow script."""
    def decorator(func):
        _FLOW_ACTIONS[name] = func
        return func
    return decorator

@property
def player():
    return renpy.store.player

@flow_action("PLAYER")
@player.setter
def player(being):
    if being == player:
        return False
    from .being import Being
    if not isinstance(being, Being):
        raise Exception(f"Player must be a Being.")
    renpy.store.player = being
    PLAYER_CHANGED.emit(player=being)

@flow_action("ZONE")
def change_zone(zone):
    player.set_zone(zone)

@flow_action("AWARD")
def unlock_award(award):
    award and award.unlock()

@flow_action("FLAG")
def set_flag(flag, value=True):
    flag and flag.change(value)

@flow_action("GAIN")
def gain_item(item, count=None, who=None, _from=None, steal=False):
    count = count or 1
    who = who or player
    who and who.gain_item(item, count, owner=_from, steal=steal)
    _from and _from.lose_item(item, count)

@flow_action("LOSE")
def lose_item(item, count=None, who=None, _from=None, steal=False):
    who = who or player
    gain_item(item, count=count, who=_from, _from=who, steal=steal)

@flow_action("LORE")
def unlock_lore(lore):
    lore and lore.unlock()
#endregion

#region Signals
# Quest/loop related.
GAME_STARTED = Signal(origin="Quest")
GAME_FINISHED = Signal() # Never called.
ACTIVE_QUEST_CHANGED = Signal(quest="Quest") # Emitted when the active quest changes, with the new active quest (or None if no active quest)
QUEST_STARTED = Signal(quest="Quest")
QUEST_TICK_STARTED = Signal(quest="Quest", tick="QuestTick") # Tick activated and is listening for events now.
QUEST_TICK_SHOWN = Signal(quest="Quest", tick="QuestTick") # Tick made visible to player.
QUEST_TICK_CHANGED = Signal(quest="Quest", tick="QuestTick") # Tick state changed.
QUEST_TICK_COMPLETED = Signal(quest="Quest", tick="QuestTick")
QUEST_TICK_FAILED = Signal(quest="Quest", tick="QuestTick")
QUEST_TICK_PASSED = Signal(quest="Quest", tick="QuestTick")
QUEST_COMPLETED = Signal(quest="Quest")
QUEST_FAILED = Signal(quest="Quest")
QUEST_PASSED = Signal(quest="Quest")
# Zone related.
ZONE_ENTERED = Signal(zone="Zone", being="Being")
ZONE_EXITED = Signal(zone="Zone", being="Being")
FIXATED = Signal(being="Being", fixture="HasFixture")
UNFIXATED = Signal(being="Being", fixture="HasFixture")
# Item related.
ITEM_GAINED  = Signal(item="Item", items="HasItems", amount=int)
ITEM_LOST = Signal(item="Item", items="HasItems", amount=int)
ITEMS_CHANGED = Signal(items="HasItems")
ITEM_CRAFTED = Signal(item="Item", craft="Craft")

CHOICES_REQUESTED = Signal(menu=str, choices=list) # Append choices to the choices list.

LORE_UNLOCKED = Signal(lore="Lore")

PLAYER_CHANGED = Signal()

AWARD_UNLOCKED = Signal(award="Award")

FLAG_CHANGED = Signal(flag="Flag")

TIME_CHANGED = Signal()
#endregion