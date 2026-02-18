init python:
    class Bond(Trait):
        def __init__(self, *args, **kwargs):
            Trait.__init__(self, *args, **kwargs)