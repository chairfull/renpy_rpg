init python:
    def _equip_item_quick(itm):
        """Equip the item to the first compatible slot, using the safe equip pipeline."""
        slots_for_body = slot_registry.get_slots_for_body(pc.body_type)
        valid_slots = [s for s in getattr(itm, "equip_slots", []) if s in slots_for_body]
        if not valid_slots:
            renpy.notify("No valid slot for this item")
            return
        ok, msg = pc.equip(itm, valid_slots[0])
        renpy.notify(msg)
        renpy.restart_interaction()

    def build_inventory_entries(inv):
        grouped = {}
        for item in inv.items:
            item_id = item_manager.get_id_of(item)
            key = (item_id, getattr(item, "owner_id", None), bool(getattr(item, "stolen", False)))
            if key not in grouped:
                label = item.name + (" [stolen]" if getattr(item, "stolen", False) else "")
                grouped[key] = {"item": item, "qty": 0, "label": label}
            grouped[key]["qty"] += max(1, int(getattr(item, "quantity", 1)))
        return list(grouped.values())

    def item_tooltip_text(item, qty=1):
        if not item:
            return ""
        lines = [f"{{b}}{item.name}{{/b}}"]
        if getattr(item, "description", ""):
            lines.append(f"{{i}}{item.description}{{/i}}")
        if qty is not None:
            lines.append(f"Qty: {{color=#ffd700}}{qty}{{/color}}")
        wt = getattr(item, "weight", None)
        if wt is not None:
            try:
                total = float(wt) * (qty or 1)
                if (qty or 1) > 1:
                    lines.append(f"Weight: {{color=#ffd700}}{wt}{{/color}} (Total {{color=#ffd700}}{total:.1f}{{/color}})")
                else:
                    lines.append(f"Weight: {{color=#ffd700}}{wt}{{/color}}")
            except Exception:
                lines.append(f"Weight: {{color=#ffd700}}{wt}{{/color}}")
        val = getattr(item, "value", None)
        if val is not None:
            lines.append(f"Value: {{color=#ffd700}}{val}{{/color}}")
        owner_id = getattr(item, "owner_id", None)
        if owner_id and owner_id != pc.id:
            lines.append(f"Owner: {owner_id}")
        if getattr(item, "stolen", False):
            lines.append("Stolen")
        return "\n".join([l for l in lines if l])
