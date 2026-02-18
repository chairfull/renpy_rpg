init -99 python:
    onstart(add_meta_menu_tab, "equipment", "🛡️", "Equipment",
        selected_equipment_slot=None)

    # Mixin for objects that can equip items.
    class HasEquipment(Inventory):
        def __init__(self, *args, **kwargs):
            Inventory.__init__(self, *args, **kwargs)
            self.equip = body_type
            self.equipment = {}
        
        def get_equipped_in_slot(self, slot_id):
            return self.equipment.get(slot_id)

        # Seed and equip a character from a slot -> item_id map.
        def apply_equipment(self, equipment):
            if not equipment:
                return
            if not isinstance(equipment, dict):
                return
            for slot_id, item_id in equipment.items():
                if not item_id:
                    continue
                target_id = str(item_id).lower()
                itm = None
                for owned in self.items:
                    if self._item_id(owned) == target_id and owned not in self.equipped_slots.values():
                        itm = owned
                        break
                if itm is None:
                    itm = item_manager.get(item_id)
                    if not itm:
                        continue
                    if getattr(itm, "owner_id", None) is None:
                        itm.owner_id = self.id
                    # Seed into inventory so equip removes it cleanly
                    self.add_item(itm, count=1, force=True, reason="equip_seed")
                    if itm not in self.items:
                        for owned in self.items:
                            if self._item_id(owned) == target_id and owned not in self.equipped_slots.values():
                                itm = owned
                                break
                ok, _msg = self.equip(itm, slot_id)
                if not ok:
                    # Fall back to inventory if equip fails (invalid slot or tag mismatch)
                    if itm not in self.items:
                        self.add_item(itm, count=1, force=True, reason="equip_seed")
        
        # Check if item can be equipped to slot.
        def can_equip_to_slot(self, item, slot_id):
            valid_slots = slot_registry.get_slots_for_body(self.body_type)
            if slot_id not in valid_slots:
                return False, "Invalid slot for this body type"
            item_slots = getattr(item, 'equipment', [])
            if item_slots and slot_id not in item_slots:
                return False, "Item cannot be equipped to this slot"
            return True, "OK"
        
        # Equip item to slot, handling conflicts.
        def equip(self, item, slot_id):
            can, msg = self.can_equip_to_slot(item, slot_id)
            if not can:
                return False, msg
            
            # Unequip conflicting slots
            conflicts = slot_registry.get_conflicting_slots(slot_id)
            for conflict_slot in conflicts:
                if conflict_slot in self.equipment:
                    self.unequip(conflict_slot)
            
            # Unequip current item in target slot
            if slot_id in self.equipment:
                self.unequip(slot_id)
            
            # Equip
            equipped = item
            if item in self.items:
                removed = self.remove_item(item, count=1, reason="equip")
                if removed:
                    equipped = removed
            self.equipment[slot_id] = equipped
            ITEM_EQUIPPED.emit(character=self, slot=slot_id, item=equipped)
            return True, "Equipped"
        
        # Unequip item from slot back to inventory.
        def unequip(self, slot_id):
            if slot_id not in self.equipment:
                return False
            item = self.equipment.pop(slot_id)
            self.add_item(item, count=None, force=True, reason="unequip")
            ITEM_UNEQUIPPED.emit(character=self, slot=slot_id, item=item)
            return True

    class ItemSlot:
        def __init__(self, id, name, equip_slots=None, unequips=None):
            self.id = id
            self.name = name
            self.equip_slots = equip_slots or []  # List of slot_ids this item can be equipped to
            self.unequips = unequips or []        # List of slot_ids that would be unequipped when equipping to this slot
    
    class ItemSlotSet:
        def __init__(self, id, name, slots):
            self.id = id
            self.name = name
            self.slots = slots

screen equipment_screen():
    $ body_slots = slot_registry.get_slots_for_body(character.body_type)
    $ entries = build_inventory_entries(character)
    # Filter equipable items and attach equip actions
    $ equip_entries = [e for e in entries if getattr(e.get('item'), 'equip_slots', None)]

    frame:
        background "#222"
        xfill True
        yfill True
        padding (20, 20)

        hbox:
            spacing 20
            xfill True
            yfill True

            # Left: Equipped slots (hide slot names unless occupied)
            frame:
                background "#1a1a25"
                xsize 320
                yfill True
                padding (14, 14)
                vbox:
                    spacing 10
                    text "Equipped" size 18 color "#ffd700"
                    $ equipped_any = False
                    for slot_id in body_slots:
                        $ item = character.equipped_slots.get(slot_id)
                        $ slot_def = slot_registry.slots.get(slot_id, {})
                        hbox:
                            spacing 8
                            # Slot visual: small square; show name only when occupied
                            frame:
                                background "#131418"
                                xsize 48
                                ysize 48
                                align (0.0, 0.5)
                                if item:
                                    text "⚔" size 22 xalign 0.5 yalign 0.5
                            if item:
                                $ equipped_any = True
                                textbutton item.name action Function(_unequip_and_refresh, slot_id) xalign 1.0 text_size 14 text_color "#fff"
                            else:
                                text "" size 14 color "#666" xalign 1.0
                    if not equipped_any:
                        text "Nothing equipped" size 14 color "#666"

            # Right: Equipable items grid (reusable inventory grid)
            vbox:
                spacing 12
                xfill True
                yfill True
                hbox:
                    spacing 20
                    xalign 0.5
                    $ inv_weight = character.get_total_weight()
                    $ weight_max = character.max_weight
                    if weight_max is not None:
                        text "Weight: [inv_weight:.1f] / [weight_max:.1f]" size 16 color "#999"

                # Show inventory grid on the right; include empty cells so it remains visible when no equipable items exist.
                $ inv_total = character.max_slots if getattr(character, 'max_slots', None) is not None else max(12, len(equip_entries))
                use inventory_grid(equip_entries, columns=4, cell_size=120, total_slots=inv_total, selected_item=selected_inventory_item, show_qty=False)
                text "Click an item to equip it to the first compatible slot." size 14 color "#aaa"

# screen phone_wardrobe_content():
#     vbox:
#         spacing 10
        
#         # Equipment Slots
#         frame:
#             background "#1a1a25"
#             xfill True
#             padding (12, 12)
            
#             vbox:
#                 spacing 8
#                 text "Equipped" size 16 color "#ffd700"
                
#                 $ body_slots = slot_registry.get_slots_for_body(character.body_type)
#                 for slot_id in body_slots:
#                     $ slot_def = slot_registry.slots.get(slot_id, {})
#                     $ equipped = character.equipped_slots.get(slot_id)
#                     hbox:
#                         xfill True
#                         text slot_def.get("name", slot_id) size 14 color "#888"
#                         if equipped:
#                             textbutton equipped.name:
#                                 action Function(character.unequip, slot_id)
#                                 text_size 14
#                                 text_color "#4af"
#                         else:
#                             text "—" size 14 color "#444" xalign 1.0
        
#         # Inventory
#         frame:
#             background "#1a1a25"
#             xfill True
#             yfill True
#             padding (12, 12)
            
#             vbox:
#                 spacing 5
#                 text "Inventory" size 16 color "#ffd700"
                
#                 viewport:
#                     mousewheel True
#                     scrollbars "vertical"
#                     yfill True
#                     vbox:
#                         spacing 4
#                         python:
#                             grouped = {}
#                             for itm in character.items:
#                                 item_id = item_manager.get_id_of(itm)
#                                 key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
#                                 if key not in grouped:
#                                     label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
#                                     grouped[key] = {"item": itm, "qty": 0, "label": label}
#                                 grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
#                         for key, entry in grouped.items():
#                             $ item = entry["item"]
#                             $ count = entry["qty"]
#                             button:
#                                 xfill True
#                                 background "#252535"
#                                 hover_background "#353545"
#                                 padding (10, 8)
                                
#                                 # Show equip menu if item has slots
#                                 if item.equip_slots:
#                                     action SetVariable("selected_slot", item)
#                                 else:
#                                     action Notify(f"{item.name}: {item.desc}")
                                
#                                 tooltip item_tooltip_text(item, count)
                                
#                                 hbox:
#                                     xfill True
#                                     text "[entry['label']] (x[count])" size 14 color "#fff"
#                                     if item.equip_slots:
#                                         text "⚔" size 14 color "#4af" xalign 1.0

# # Equip slot picker overlay
# screen phone_equip_picker():
#     if selected_equipment_slot:
#         modal True
#         zorder 152
        
#         add Solid("#00000088")
        
#         frame:
#             align (0.5, 0.5)
#             background "#1a1a25"
#             padding (20, 20)
#             xsize 300
            
#             vbox:
#                 spacing 15
#                 text "Equip [selected_equipment_slot.name] to:" size 18 color "#ffd700" xalign 0.5
                
#                 vbox:
#                     spacing 8
#                     for slot_id in selected_equipment_slot.equip_slots:
#                         $ slot_def = slot_registry.slots.get(slot_id, {})
#                         $ can_use = slot_id in slot_registry.get_slots_for_body(character.body_type)
#                         textbutton slot_def.get("name", slot_id):
#                             action [Function(character.equip, selected_equipment_slot, slot_id), SetVariable("selected_equipment_slot", None), Notify("Equipped!")]
#                             sensitive can_use
#                             text_size 16
#                             text_color ("#fff" if can_use else "#444")
#                             xalign 0.5
                
#                 textbutton "Cancel":
#                     action SetVariable("selected_equipment_slot", None)
#                     text_size 14
#                     text_color "#888"
#                     xalign 0.5

