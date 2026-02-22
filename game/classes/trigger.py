from . import engine

class Trigger:
    def __init__(self, event=None, state=None, cond=None, flags=None):
        self.event = event # Event that triggers this tick.
        self.state = state # State the event should be in.
        self.cond = cond # Condition to be met if not None.
        self.flags = flags # Optional quick test against flags.
    
    def check(self, event, **kwargs):
        if self.event:
            if self.event and self.event != event.id:
                return False
            if self.event_state:
                for k, v in self.event_state.items():
                    if kwargs.get(k) != v:
                        return False
        
        if self.flags:
            for flag_id, flag_val in self.flags.items():
                if engine.get_flag(flag_id) != flag_val:
                    return False
        
        if self.cond:
            if not engine.test_condition(self.condition):
                return False
        
        return True