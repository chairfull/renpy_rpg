from .flag import Flag

class HasFlags:
    """Mixin for objects that can have flags."""
    def __init__(self, flags=None):
        self.flags = {}
        if not flags:
            return
        for flag_id, flag_default in flags.items():
            if hasattr(self, "id"):
                self.flags[flag_id] = Flag(f"{self.id}.{flag_id}", flag_default)
            else:
                self.flags[flag_id] = Flag(flag_id, flag_default)
    
    def get_flag(self, flag_id, default=False):
        flag = self.flags.get(flag_id)
        return flag.value if flag else default

    def set_flag(self, flag_id, value=True):
        flag = self.flags.get(flag_id)
        if flag:
            flag.value = value