import math
from . import engine
from .util import clamp
from .item_slot import ItemSlot
from .milligrams import Milligrams

class HasItems:
    """Mixin for inventories."""
    def __init__(self, items=None, item_filters=None, item_columns=1, max_slots=1_000_000, max_weight=1_000_000):
        self.items = {} # Item slots can either be a string for equipment or an (tuple) for unequipped items.
        self.item_filters = item_filters
        self.item_columns = clamp(item_columns, 1, 100)
        self.item_weight = Milligrams(0)
        self.max_item_slots = clamp(max_slots, 1, 1_000_000)
        self.max_item_weight = clamp(max_weight, 1, 1_000_000)
    
    def _item_cell_to_index(self, x, y):
        return x * self.item_columns + y
    
    def _item_index_to_cell(self, index):
        return (index % self.item_columns, index // self.item_columns)

    def _get_max_item_space(self, item, count, force):
        space = count or 1
        if force:
            return space
        # TODO
        return space

    def _items_changed(self):
        """Updates mass and emits signals."""
        self.item_mass = 0
        for slot_id, slot in self.items.items():
            self.item_mass += slot.item.mass * slot.quantity
        engine.ITEMS_CHANGED.emit(items=self)

    def _find_empty_item_slot(self, force):
        index = 0
        while index in self.items:
            index += 1
        if index >= self.max_item_slots and not force:
            return None
        return index

    def item_allowed(self, item):
        if self.item_filters:
            for item_filter in self.item_filters:
                if not item_filter.passes(item):
                    return False
        return True

    def count_item(self, item, include_equipped=True, include_unequipped=True):
        total = 0
        for slot_id, slot in self.items.items():
            if slot.item == item:
                if isinstance(slot_id, str) and not include_equipped:
                    continue
                if isinstance(slot_id, int) and not include_unequipped:
                    continue
                total += slot.quantity
        return total

    def has_item(self, item, total=1, include_equipped=True, include_unequipped=True):
        return self.count(item, include_equipped, include_unequipped) >= total

    def get_equipped(self):
        return [k for k, v in self.slots.items() if isinstance(k, str)]
    
    def get_unequipped(self):
        return [k for k, v in self.slots.items() if isinstance(k, int)]
    
    def get_equip_slot_info(self, slot):
        if self.item_filters:
            for item_filter in self.item_filters:
                if slot.id in item_filter.slots:
                    return item_filter.slots[slot.id]
        return None

    def can_equip_slot(self, slot):
        return self.get_equip_slot_info(slot) != None

    def equip_item(self, item, to_slot_id=None, from_slot_id=None, from_items=None):
        to_slot_id = to_slot_id or item.equip_slots[0]
        slot_info = self.get_equip_slot_info(to_slot_id)
        if slot_info == None:
            return False
        if to_slot_id in self.item_slots:
            self.unequip_item_slot(to_slot_id)
        for sid in slot_info.get("unequip", []):
            self.unequip_item_slot(sid)
        if from_slot_id:
            from_items = from_items or self
            self.item_slots[to_slot_id] = from_items.item_slots[from_slot_id]
            del from_items[from_slot_id]
            if from_items != self:
                from_items._items_changed()
        else:
            self.item_slots[to_slot_id] = ItemSlot(item=item)
        self._items_changed()
        return True

    def unequip_item_slot(self, slot_id, to_items=None):
        """Removes item from equipment slot and puts it in the unequipped slots."""
        if not slot_id in self.item_slots:
            return False
        to_items = to_items or self
        slot_index = to_items._find_empty_item_slot(force=True)
        to_items.item_slots[slot_index] = self.item_slots[slot_id]
        if to_items != self:
            to_items._items_changed()
        del self.item_slots[slot_id]
        self._items_changed()
        return True

    def gain_item(self, item, count=None, owner=None, stolen=False, force=False):
        """Add unequipped item to inventory."""
        leftover = self._get_max_item_space(item, count, force)
        if item.stackable:
            for slot_id, slot in self.items.items():
                if isinstance(slot_id, str): continue
                if slot.item != item: continue
                if slot.owner != owner: continue
                if slot.stolen != stolen: continue
                space_left = item.stack_size - slot.quantity
                gain = math.min(leftover, space_left)
                slot.quantity += gain
                leftover -= gain
                if leftover <= 0:
                    break
        if leftover > 0:
            add_slots = math.ceil(leftover / float(item.stack_size))
            for i in range(0, add_slots):
                slot_id = self._find_empty_item_slot(force)
                if slot_id == None:
                    break
                gain = math.min(leftover, item.stack_size)
                self.items[slot_id] = ItemSlot(item, gain, owner=owner, stolen=stolen)
                leftover -= gain
        if leftover >= 0:
            print(f"Couldn't add x{leftover} {item.id}.")
        self._items_changed()

    def lose_item(self, item, count=None):
        leftover = count or 1
        for slot_id, slot in self.items.items():
            if isinstance(slot_id, str): continue
            if slot.item != item: continue
            lose = math.min(leftover, slot.quantity)
            slot.quantity -= lose
            if slot.quantity <= 0:
                del self.items[slot_id]
            leftover -= lose
            if leftover <= 0:
                break
        if leftover >= 0:
            print(f"Couldn't remove x{leftover} {item.id}.")
        self._items_changed()

    def get_weight_ratio(self):
        return self.weight / float(self.max_weight)