from .scene import Scene

class SceneDemo(Scene):
    def __init__(self):
        super().__init__()
    
    def _process(self, dt):
        return super()._process(dt)

    def _clicked(self, what=None, alternate=False):
        if what is None and not alternate:
            self.camera.target = self.get_mouse()

        return super()._clicked(what, alternate)