init -1000 python:
    GAME_STARTED = create_signal(origin=StoryOrigin)
    GAME_FINISHED = create_signal() # Never called.
    # Fixtures
    FIXATED = create_signal(character=Character, fixture=Fixture)
    UNFIXATED = create_signal(character=Character, fixture=Fixture)
    # Locations
    LOCATION_ENTERED = create_signal(character=Character, location=Location)
    LOCATION_EXITED = create_signal(character=Character, location=Location)
    # Items
    ITEM_GAINED  = create_signal(item=Item, inventory=Inventory, amount=int)
    ITEM_LOST = create_signal(item=Item, inventory=Inventory, amount=int)
    ITEM_CRAFTED = create_signal(item=Item, craft=Craft)
    # Quest
    ACTIVE_QUEST_CHANGED = create_signal(quest=Quest) # Emitted when the active quest changes, with the new active quest (or None if no active quest)
    QUEST_STARTED = create_signal(quest=Quest)
    QUEST_TICK_SHOWN = create_signal(quest=Quest, tick=QuestTick) # Emitted when a tick moves from hidden to shown. Only emitted once per tick.
    QUEST_TICK_PROGRESSED = create_signal(quest=Quest, tick=QuestTick)
    QUEST_TICK_COMPLETED = create_signal(quest=Quest, tick=QuestTick)
    QUEST_TICK_FAILED = create_signal(quest=Quest, tick=QuestTick)
    QUEST_TICK_PASSED = create_signal(quest=Quest, tick=QuestTick)
    QUEST_COMPLETED = create_signal(quest=Quest)
    QUEST_FAILED = create_signal(quest=Quest)
    QUEST_PASSED = create_signal(quest=Quest)

init -2000 python:
    import inspect

    class Signal:
        def __init__(self, name, **required):
            self.name = name
            self.required = required
            self.listeners = set()
        
        def connect(self, fn):
            self.listeners.add(fn)
        
        def disconnect(self, fn):
            self.listeners.discard(fn)

        def emit(self, **state):
            payload = {}
            for k, typ in self.required.items():
                if k not in state:
                    raise ValueError(f"Missing required field {k}")
                elif not isinstance(state[k], typ):
                    raise TypeError(f"{k} must be {typ}, got {type(state[k])}")
                else:
                    payload[k] = state[k]
            
            for fn in list(self.listeners):
                try:
                    fn(**payload)
                except Exception as e:
                    renpy.log(f"Event error ({self.name}): {e}")
    
    def create_signal(**required):
        frame = inspect.currentframe().f_back
        name = [k for k, v in frame.f_locals.items() if v is None][0]  
        return Signal(name, **required)

