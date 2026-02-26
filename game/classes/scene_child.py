import renpy
from .point import Point

class SceneChild:
    """Object that can draw to screen."""
    def __init__(self, position=Point(), tooltip=None, image=None,
                 zoom=1.0, flipped=False,
                 matrixcolor=None, **kwargs):
        self._transform = renpy.store.Transform(anchor=(0.5, 0.5), zoom=zoom, xzoom=1.0, yzoom=1.0, subpixel=True, **kwargs)
        self._matrixcolor = matrixcolor
        if flipped:
            self.flipped = True
        self.position = position
        self._tooltip = tooltip
        self._image = image
        self.screen_anchor = (0.5, 0.5)
        self.screen_zoom = zoom
        self.screen_pos = position.xz
    
    @property
    def tooltip(self):
        return "My tooltip needs implementing."
    
    def _apply_camera_transform(self, camera):
        x, _, z = (self.position - camera.position) * camera.zoom + camera.screen_center
        self.screen_pos = (int(x), int(z))
        self.screen_zoom = camera.zoom

    def _update_transform(self, tr, st, at):
        tr.subpixel = True
        tr.anchor = self.screen_anchor
        tr.zoom = self.screen_zoom
        tr.pos = self.screen_pos
        self._transform = tr
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