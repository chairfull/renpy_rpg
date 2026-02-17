init 10 python:
    class Faction:
        def __init__(self, id, name, desc="", tags=None):
            self.id = id
            self.name = name
            self.desc = desc
            self.tags = set(tags or [])