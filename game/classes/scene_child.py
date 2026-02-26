import renpy
from .vector3 import Vector3

class SceneChild:
    """Object that can draw to screen."""
    def __init__(self, position=Vector3(), tooltip=None, image=None,
                 zoom=1.0, flipped=False,
                 matrixcolor=None, **kwargs):
        self._transform = renpy.store.Transform(anchor=(0.5, 0.5), size=(256, 256), zoom=zoom, xzoom=1.0, yzoom=1.0, subpixel=True, **kwargs)
        self._matrixcolor = matrixcolor
        if flipped:
            self.flipped = True
        self.position = position
        self.tooltip = tooltip
        self._image = image
    
    def _update_transform(self, tr, st, at):
        tr.subpixel = True
        tr.zoom = self._transform.zoom
        tr.pos = self._transform.pos
        return 0.0

    @property
    def size(self):
        return self._transform.size
    
    @size.setter
    def size(self, xz):
        self._transform.size = xz

    @property
    def scale(self):
        return self._transform.zoom
    
    @scale.setter
    def scale(self, value):
        self._transform.zoom = value
    
    @property
    def flipped(self):
        return self._transform.xzoom < 0.0
    
    @flipped.setter
    def flipped(self, value):
        self._transform.xzoom = abs(self._transform.xzoom) * (-1 if value else 1)

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
    
    def _apply_camera_transform(self, camera):
        x, _, z = (self.position - camera.position) * camera.zoom + camera.screen_center
        self._transform.pos = (int(x), int(z))
        self._transform.zoom = camera.zoom
    
    def _process(self, dt):
        """Called every update tick."""
        pass
    
    @property
    def image(self):
        return self._image
    
    @property
    def transform(self):
        return self._transform
    
    @property
    def matrixcolor(self):
        return self._matrixcolor