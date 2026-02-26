from .point import Point

class HasPath(Point):
    def __init__(self, position=Point(), speed=300):
        Point.__init__(self, position)
        self.path = []
        self.speed = speed
        self.moving = False
    
    # def set_path_target(self, target):
    #     start = self.xyz
    #     self.path = location.get_path(start, target)
    #     if not self.path:
    #         renpy.notify("Path blocked")
    #         return
    #     self.moving = True

    def update_path_following(self, dt):
        if not self.path:
            self.moving = False
            return
        target = self.path[0]
        direction = (target - self).normalized()
        distance = (target - self).length()
        step = self.speed * dt
        if step >= distance:
            self.reset(target)
            self.path.pop(0)
            self.moving = bool(self.path)
        else:
            self.move(direction * step)
            self.moving = True