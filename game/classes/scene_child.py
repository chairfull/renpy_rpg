import renpy
from .vector3 import Vector3

class SceneChild:
    """Object that can draw to screen."""
    def __init__(self, position=Vector3(), tooltip=None, transform=None, image=None, **kwargs):
        self.position = position
        self.size = (120, 120)
        self.tooltip = tooltip
        self.image = image
        self.transform = transform or renpy.store.Transform(anchor=(0.5, 0.5), size=self.size, subpixel=True, **kwargs)
    
    def _ready(self):
        """Called when screen starts."""
        pass
    
    def _hovered(self):
        """"""
        return renpy.store.NullAction()

    def _unhovered(self):
        """"""
        return renpy.store.NullAction()

    def _clicked(self, alt=False):
        """Called when clicked on."""
        return renpy.store.NullAction()
    
    def _process(self, dt):
        """Called every update tick."""
        pass
    
    @property
    def image(self):
        return self.image
    
    @property
    def transform(self):
        return self.transform