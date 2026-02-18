init -10 python:
    class Flag:
        def __init__(self, fid, default=False):
            self.id = fid
            self.value = default
        
        def change(self, new_value):
            if self.value == new_value:
                return
            old_value = self.value
            self.value = new_value
            FLAG_CHANGED.emit(flag=self, old_value=old_value, new_value=new_value)

        @property
        def parent(self):
            if "." in self.id:
                return getattr(renpy.store, self.id.split(".", 1)[0])
            return None

        def toggle(self):
            set(not self.value)
    
    # Mixin for objects that can have flags.
    # IDs should include a path to the object, so for Zone: zone_id.flag_id
    class Flaggable:
        def __init__(self, flags={}):
            self.flags = {}
            for flag_id, flag_default = flags.items():
                self.add_flag(flag_id, flag_default)

        def add_flag(self, flag_id, default=False):
            if hasattr(self, "id"):
                self.flags[flag_id] = Flag(f"{self.id}.{flag_id}", default)
            else:
                self.flags[flag_id] = Flag(flag_id, default)
        
        def get_flag(self, flag_id, default=False):
            return self.flags.get(flag_id, default)

        def set_flag(self, flag_id, value=True):
            flag = self.flags.get(flag_id)
            if flag:
                flag.change(value)
    
    @flow_function("SET")
    @flow_funcion("FLAG_SET")
    def set_flag(flag, value=True):
        getattr(renpy.store, flag).change(value)
    
    @flow_function("GET")
    @flow_function("FLAG_GET")
    def get_flag(flag, default=False):
        return gettattr(renpy.store, flag).value