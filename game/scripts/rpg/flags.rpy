default flag_manager = FlagManager()

init 10 python:
    class FlagManager:
        def __init__(self):
            self.flags = {}
    
    def reload_flag_manager(data):
        flag_manager.flags = data.get("flags", {})

        for flag_id, value in data.get("flags", {}).items():
            if not isinstance(value, bool):
                with open("debug_load.txt", "a") as df:
                    df.write("Flag Load Warning ({}): Expected boolean value, got {}. Defaulting to False.\n".format(flag_id, type(value).__name__))
                flag_manager.flags[flag_id] = False
    
    def flag_get(name, default=False):
        return flag_manager.flags.get(name, default)
    
    def flag_set(name, value=True):
        flag_manager.flags[name] = value
        return value

    def flag_clear(name):
        if name in flag_manager.flags:
            del flag_manager.flags[name]
    
    def flag_toggle(name):
        flag_manager.flags[name] = not flag_manager.flags.get(name, False)
        return flag_manager.flags[name]