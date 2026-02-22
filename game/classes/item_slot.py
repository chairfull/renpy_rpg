class ItemSlot:
    """Item container. Used for inventory, equipment, and item holders."""
    def __init__(self, item, quantity, owner=None, stolen=False):
        self.item = item
        self.quantity = quantity
        self.owner = owner
        self.stolen = stolen