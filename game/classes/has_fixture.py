import Point

class HasFixture:
    """Place a Being can fixate to (seat, bed, table, floor spot)."""
    def __init__(self, _id, name, subtype="seat", position=Point()):
        self.id = _id
        self.name = name
        self.position = position
        self.subtype = subtype
        self.occupant = None

    @property
    def occupied(self):
        return self.occupant is not None

    def fixate(self, being):
        if self.occupied:
            return False
        self.occupant = being
        being.fixture = self
        being.position = self.position
        FIXATED.emit(fixture=self, being=being)
        return True

    def unfixate(self, being=None):
        if not self.occupied:
            return False
        if being != self.occupant:
            return
        being = self.occupant
        being.fixture = None
        self.occupant = None
        UNFIXATE.emit(fixture=self, being=being)
        return True