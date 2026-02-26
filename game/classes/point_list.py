from .point import Point

class PointList:
    def __init__(self, *points):
        self.points = []
        for p in points:
            if isinstance(p, Point):
                self.points.append(p)
            elif isinstance(p, tuple):
                self.points.append(Point(p))
        self.closed = False
    
    def set_debug(self, color="#ff0000", width=1):
        self.debug_color = color
        self.debug_width = width
        return self
    
    @property
    def is_polygon(self):
        return self.closed
    
    @property
    def is_line(self):
        return len(self) == 2