init 10 python:
    class Flag:
        def __init__(self):
            self.value = None
        
        def change(self, new_value):
            if self.value == new_value:
                return
            old_value = self.value
            self.value = new_value
            FLAG_CHANGED.emit(flag=self, old_value=old_value, new_value=new_value)