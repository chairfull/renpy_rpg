init -200 python:
    event_listeners = {}
    
    def signal(etype, **kwargs):
        for fn in list(event_listeners.get(etype, [])):
            try:
                fn(etype, **kwargs)
            except Exception:
                pass
    
    def listen(etype, fn):
        event_listeners.setdefault(etype, set()).add(fn)