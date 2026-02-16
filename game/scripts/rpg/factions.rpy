default faction_manager = FactionManager()

init -10 python:
    class Faction:
        def __init__(self, id, name, description="", tags=None):
            self.id = id
            self.name = name
            self.description = description
            self.tags = set(tags or [])

    class FactionManager:
        def __init__(self):
            self.factions = {}
    
    def reload_faction_manager(data):
        faction_manager.factions = {}
        for fac_id, fdata in data.get('factions', {}).items():
            try:
                faction_manager.factions[fac_id] = from_dict(Faction, fdata, id=fac_id)
            except Exception as e:
                with open("debug_load.txt", "a") as df:
                    df.write("Faction Load Error ({}): {}\n".format(fac_id, str(e)))