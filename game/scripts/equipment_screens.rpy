# Equipment management screen
screen equipment_content():
    $ body_slots = slot_registry.get_slots_for_body(pc.body_type)
    $ entries = build_inventory_entries(pc)
    # Filter equipable items and attach equip actions
    $ equip_entries = [e for e in entries if getattr(e.get('item'), 'equip_slots', None)]
    $ equip_entries = _make_equip_entry_actions(equip_entries) if callable(globals().get('_make_equip_entry_actions')) else equip_entries

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
                        $ item = pc.equipped_slots.get(slot_id)
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
                    $ inv_weight = pc.get_total_weight()
                    $ weight_max = pc.max_weight
                    if weight_max is not None:
                        text "Weight: [inv_weight:.1f] / [weight_max:.1f]" size 16 color "#999"

                # Show inventory grid on the right; include empty cells so it remains visible when no equipable items exist.
                $ inv_total = pc.max_slots if getattr(pc, 'max_slots', None) is not None else max(12, len(equip_entries))
                use inventory_grid(equip_entries, columns=4, cell_size=120, total_slots=inv_total, selected_item=selected_inventory_item, show_qty=False)
                text "Click an item to equip it to the first compatible slot." size 14 color "#aaa"


init -100 python:
    # Prepare equip entries with actions for the equipment screen.
    def _make_equip_entry_actions(entries):
        out = []
        for e in entries:
            itm = e.get('item')
            e['action'] = Function(_equip_item_quick, itm)
            out.append(e)
        return out
