default flag_manager = FlaggedObject()

init 10 python:
    def reload_flag_manager(data):
        flag_manager.flags = {}

        for flag_id, value in data.get("flags", {}).items():
            if not isinstance(value, bool):
                with open("debug_load.txt", "a") as df:
                    df.write("Flag Load Warning ({}): Expected boolean value, got {}. Defaulting to False.\n".format(flag_id, type(value).__name__))
                flag_manager.flags[flag_id] = False