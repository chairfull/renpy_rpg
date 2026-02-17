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

