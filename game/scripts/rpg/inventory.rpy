default quick_loot_tags = ["consumable", "food", "medical", "ammo", "currency", "component", "material"]

init -1400 python:
    onstart(add_meta_menu_tab, "inventory", "🎒", "Inventory",
        selected_item=None,
        selected_page=0)
    
    class Inventory(Entity):
        def __init__(self, id, name, items=None, blocked_tags=None, allowed_tags=None, max_weight=None, max_slots=None, owner_id=None, **kwargs):
            super(Inventory, self).__init__(id, name, **kwargs)
            self.items, self.gold = [], 0
            self.blocked_tags = _normalize_tags(blocked_tags)
            self.allowed_tags = _normalize_tags(allowed_tags)  # empty = allow all
            self.max_weight = float(max_weight) if max_weight is not None else None
            self.max_slots = int(max_slots) if max_slots is not None else None
            self.owner_id = owner_id
            self._encumbrance_state = "none"
            if items:
                for item_id in items:
                    it = item_manager.get(item_id)
                    if it:
                        self.add_item(it, count=None, force=True, reason="seed")

        def _item_id(self, item):
            return item_manager.get_id_of(item)

        def _stackable(self, item):
            return bool(getattr(item, "stackable", False) or getattr(item, "stack_size", 1) > 1)

        def _stack_size(self, item):
            try:
                return max(1, int(getattr(item, "stack_size", 1)))
            except Exception:
                return 1

        def _item_qty(self, item, count):
            if count is None:
                return max(1, int(getattr(item, "quantity", 1)))
            return max(1, int(count))

        def _same_ownership(self, a, b):
            return getattr(a, "owner_id", None) == getattr(b, "owner_id", None) and bool(getattr(a, "stolen", False)) == bool(getattr(b, "stolen", False))

        def get_total_weight(self):
            return sum(getattr(i, "weight", 0) * max(1, int(getattr(i, "quantity", 1))) for i in self.items)

        def get_used_slots(self):
            return len(self.items)

        def get_item_count(self, item_id=None, name=None):
            total = 0
            for itm in self.items:
                if item_id and self._item_id(itm) != item_id:
                    continue
                if name and itm.name != name:
                    continue
                total += max(1, int(getattr(itm, "quantity", 1)))
            return total

        def _estimate_new_stack_slots(self, item, qty):
            if not self._stackable(item):
                return qty
            stack_size = self._stack_size(item)
            item_id = self._item_id(item)
            free = 0
            for stack in self.items:
                if self._item_id(stack) != item_id or not self._stackable(stack):
                    continue
                if not self._same_ownership(stack, item):
                    continue
                free += max(0, stack_size - max(1, int(getattr(stack, "quantity", 1))))
            remaining = max(0, qty - free)
            if remaining <= 0:
                return 0
            return int(math.ceil(float(remaining) / float(stack_size)))

        def _can_accept_capacity(self, item, qty):
            if self.max_weight is not None:
                if self.get_total_weight() + (getattr(item, "weight", 0) * qty) > self.max_weight:
                    return False, "overweight"
            if self.max_slots is not None:
                new_slots = self._estimate_new_stack_slots(item, qty)
                if self.get_used_slots() + new_slots > self.max_slots:
                    return False, "full"
            return True, "ok"

        def _tags_allow(self, item):
            item_tags = getattr(item, "tags", set())
            if self.blocked_tags and item_tags & self.blocked_tags:
                return False
            if self.allowed_tags and not (item_tags & self.allowed_tags):
                return False
            return True

        def can_accept_item(self, item, qty=1):
            """Check if item can be added based on tag restrictions and capacity."""
            if not self._tags_allow(item):
                return False
            ok, _reason = self._can_accept_capacity(item, qty)
            return ok

        def _update_encumbrance(self):
            if self.max_weight is None or self.max_weight <= 0:
                return
            ratio = self.get_total_weight() / float(self.max_weight)
            if ratio < 0.7:
                state = "light"
            elif ratio < 0.9:
                state = "medium"
            elif ratio <= 1.0:
                state = "heavy"
            else:
                state = "over"
            if state != self._encumbrance_state:
                prev = self._encumbrance_state
                self._encumbrance_state = state
                signal("ENCUMBRANCE_CHANGED", inventory=self.id, state=state, previous=prev, ratio=ratio)

        def get_encumbrance_ratio(self):
            if self.max_weight is None or self.max_weight <= 0:
                return 0.0
            return self.get_total_weight() / float(self.max_weight)

        def get_encumbrance_state(self):
            return self._encumbrance_state

        def _post_inventory_change(self, item, delta, added, reason=None):
            item_id = self._item_id(item)
            total = self.get_item_count(item_id=item_id)
            payload = {
                "item": item.name,
                "item_id": item_id,
                "quantity": int(delta),
                "total": total,
                "inventory": self.id,
                "reason": reason or "unspecified",
                "owner_id": getattr(item, "owner_id", None),
                "stolen": bool(getattr(item, "stolen", False)),
            }
            if added:
                ITEM_GAINED.emit(**payload)
            else:
                ITEM_REMOVED.emit(**payload)
            INVENTORY_CHANGED.emit(inventory=self, item=item, delta=int(delta), total=total)
            self._update_encumbrance()

        def add_item(self, i, count=None, force=False, reason=None):
            if not i:
                return False
            qty = self._item_qty(i, count)
            if getattr(i, "owner_id", None) is None and self.owner_id is not None:
                i.owner_id = self.owner_id
                i.stolen = False
            if not force:
                if not self._tags_allow(i):
                    signal("INVENTORY_BLOCKED", inventory=self.id, item_id=self._item_id(i), quantity=qty, reason="tags")
                    return False
                ok, cap_reason = self._can_accept_capacity(i, qty)
                if not ok:
                    signal("INVENTORY_BLOCKED", inventory=self.id, item_id=self._item_id(i), quantity=qty, reason=cap_reason)
                    return False

            item_id = self._item_id(i)
            use_original = i not in self.items
            if self._stackable(i):
                stack_size = self._stack_size(i)
                remaining = qty
                for stack in self.items:
                    if self._item_id(stack) != item_id or not self._stackable(stack):
                        continue
                    if not self._same_ownership(stack, i):
                        continue
                    free = stack_size - max(1, int(getattr(stack, "quantity", 1)))
                    if free <= 0:
                        continue
                    add = min(remaining, free)
                    stack.quantity += add
                    remaining -= add
                    if remaining <= 0:
                        break
                while remaining > 0:
                    add = min(remaining, stack_size)
                    if use_original:
                        new_item = i
                        use_original = False
                    else:
                        new_item = copy.copy(i)
                    new_item.quantity = add
                    self.items.append(new_item)
                    remaining -= add
            else:
                for _ in range(qty):
                    if use_original:
                        new_item = i
                        use_original = False
                    else:
                        new_item = copy.copy(i)
                    new_item.quantity = 1
                    self.items.append(new_item)

            self._post_inventory_change(i, qty, added=True, reason=reason)
            return True

        def remove_item(self, i, count=1, reason=None):
            if i not in self.items:
                return None
            qty = max(1, int(getattr(i, "quantity", 1)))
            take = max(1, int(count))
            take = min(take, qty)
            if self._stackable(i) and qty > take:
                i.quantity = qty - take
                removed = copy.copy(i)
                removed.quantity = take
                self._post_inventory_change(i, take, added=False, reason=reason)
                return removed
            self.items.remove(i)
            self._post_inventory_change(i, qty, added=False, reason=reason)
            return i

        def remove_items_by_id(self, item_id, count=1, reason=None):
            remaining = max(1, int(count))
            removed = 0
            for itm in list(self.items):
                if self._item_id(itm) != item_id:
                    continue
                qty = max(1, int(getattr(itm, "quantity", 1)))
                if qty <= remaining:
                    self.items.remove(itm)
                    self._post_inventory_change(itm, qty, added=False, reason=reason)
                    removed += qty
                    remaining -= qty
                else:
                    itm.quantity = qty - remaining
                    self._post_inventory_change(itm, remaining, added=False, reason=reason)
                    removed += remaining
                    remaining = 0
                if remaining <= 0:
                    break
            return removed

        def transfer_to(self, i, target, count=1, reason="transfer", assign_owner=False):
            probe = i
            if assign_owner:
                probe = copy.copy(i)
                probe.owner_id = target.owner_id
                probe.stolen = False
            if not target.can_accept_item(probe, count):
                return False
            removed = self.remove_item(i, count=count, reason="transfer_out")
            if not removed:
                return False
            if assign_owner:
                removed.owner_id = target.owner_id
                removed.stolen = False
            else:
                if getattr(removed, "owner_id", None) and target.owner_id != removed.owner_id:
                    if not getattr(removed, "stolen", False):
                        removed.stolen = True
                        signal("ITEM_STOLEN", item_id=self._item_id(removed), owner=removed.owner_id, source=self.id, target=target.id, reason=reason)
                elif getattr(removed, "owner_id", None) and target.owner_id == removed.owner_id:
                    removed.stolen = False
            signal("ITEM_OWNERSHIP_CHANGED", item_id=self._item_id(removed), owner=removed.owner_id, stolen=bool(getattr(removed, "stolen", False)))
            if not target.add_item(removed, count=None, reason=reason):
                self.add_item(removed, count=None, force=True, reason="transfer_rollback")
                return False
            signal("ITEM_TRANSFERRED", source=self.id, target=target.id, item_id=self._item_id(removed), quantity=max(1, int(getattr(removed, "quantity", 1))))
            return True

        def get_items_with_tag(self, tag):
            t = _canonical_tag(tag)
            return [i for i in self.items if hasattr(i, 'tags') and t in i.tags]

        def get_items_without_tag(self, tag):
            t = _canonical_tag(tag)
            return [i for i in self.items if not hasattr(i, 'tags') or t not in i.tags]

    class InventoryManager:
        def __init__(self): self.inventories = {}

    def _resolve_inventory(ref):
        if ref in (None, "", "none"): return None
        if isinstance(ref, Inventory): return ref
        if isinstance(ref, RPGCharacter): return ref
        key = str(ref).lower()
        if key == "player":
            return character
        if key == "char":
            return getattr(store, "_interact_target_char", None)
        if key in world.characters:
            return world.characters.get(key)
        if key in world.shops:
            return world.shops.get(key)
        return None

    def give_item_between(item_id, source_id=None, target_id=None, count=1, assign_owner=True):
        """Transfer an item between inventories (used by GIVE flows)."""
        count = max(1, int(count))
        src = _resolve_inventory(source_id)
        tgt = _resolve_inventory(target_id)
        if not src or not tgt:
            return False
        it = item_manager.get(item_id)
        if not it:
            return False
        return src.transfer_to(it, tgt, count=count, reason="gift", assign_owner=assign_owner)

    def get_give_label(char, item_or_id):
        item = item_or_id
        if isinstance(item_or_id, str):
            item = item_manager.get(item_or_id)
        if not item or not char:
            return None
        item_id = item_manager.get_id_of(item)
        give_map = getattr(char, "give_flows", {}) or {}
        return give_map.get(item_id)

    def is_givable(char, item_or_id):
        return bool(get_give_label(char, item_or_id))

    def _equip_item_quick(itm):
        """Equip the item to the first compatible slot, using the safe equip pipeline."""
        slots_for_body = slot_registry.get_slots_for_body(character.body_type)
        valid_slots = [s for s in getattr(itm, "equip_slots", []) if s in slots_for_body]
        if not valid_slots:
            renpy.notify("No valid slot for this item")
            return
        ok, msg = character.equip(itm, valid_slots[0])
        renpy.notify(msg)
        renpy.restart_interaction()

    def _unequip_and_refresh(slot_id):
        try:
            character.unequip(slot_id)
        except Exception:
            pass
        try:
            renpy.restart_interaction()
        except Exception:
            pass

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
        if getattr(item, "desc", ""):
            lines.append(f"{{i}}{item.desc}{{/i}}")
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
        if owner_id and owner_id != character.id:
            lines.append(f"Owner: {owner_id}")
        if getattr(item, "stolen", False):
            lines.append("Stolen")
        return "\n".join([l for l in lines if l])
    
    def transfer_item(item, source_inv, target_inv):
        reason = "loot" if target_inv == character else "deposit"
        if source_inv.transfer_to(item, target_inv, count=1, reason=reason):
            renpy.restart_interaction()

    def transfer_all(source_inv, target_inv):
        if not source_inv.items:
            return
        for itm in list(source_inv.items):
            qty = max(1, int(getattr(itm, "quantity", 1)))
            reason = "loot" if target_inv == character else "deposit"
            source_inv.transfer_to(itm, target_inv, count=qty, reason=reason)
        renpy.restart_interaction()

    def transfer_by_tags(source_inv, target_inv, tags):
        if not source_inv.items:
            return
        tag_set = set(tags or [])
        moved = False
        for itm in list(source_inv.items):
            it_tags = getattr(itm, 'tags', set())
            if it_tags & tag_set:
                qty = max(1, int(getattr(itm, "quantity", 1)))
                reason = "loot" if target_inv == character else "deposit"
                source_inv.transfer_to(itm, target_inv, count=qty, reason=reason)
                moved = True
        if moved:
            renpy.restart_interaction()

label inspect_item_pending:
    $ store.inspect_force = True
    $ iid = store.pending_inspect_item_id
    $ store.pending_inspect_item_id = None
    if not iid:
        $ store.inspect_force = False
        return

    # Resolve the label
    $ inspect_item(iid)
    $ resolved_label = store.inspect_resolved_label
    $ resolved_item = store.inspect_resolved_item
    $ store.inspect_force = False

    if resolved_label:
        call expression resolved_label
    elif resolved_item and resolved_item.desc:
        $ item_show_image(resolved_item)
        "[resolved_item.desc]"
        $ item_hide_image()

    $ item_hide_image()

    if store._return_to_inventory:
        $ store._return_to_inventory = False
        call screen inventory_screen
    return


transform inventory_icon_idle:
    anchor (0.5, 0.5)
    linear 0.12 zoom 1.0 rotate 0.0

transform inventory_icon_hover:
    anchor (0.5, 0.5)
    zoom 1.0
    rotate 0.0
    parallel:
        block:
            ease 0.18 zoom 1.06
            ease 0.22 zoom 1.0
            repeat

transform inventory_fade:
    on show:
        alpha 0.0
        easein 0.15 alpha 1.0
    on hide:
        easeout 0.15 alpha 0.0
    parallel:
        block:
            ease 0.25 rotate 6.0
            ease 0.25 rotate -6.0
            repeat

screen inventory_grid(entries, columns=5, cell_size=110, total_slots=None, selected_item=None, show_qty=True, slot_image="images/gui/inventory_slot.webp", empty_image="images/gui/inventory_slot_empty.webp", icon_scale=0.8, xspacing=8, yspacing=8):
    default hover_idx = None
    $ _entries = entries or []
    $ _total = total_slots if total_slots is not None else len(_entries)
    $ _total = max(_total, len(_entries))
    $ _icon_size = int(cell_size * icon_scale)
    $ _slot_bg = slot_image if renpy.loadable(slot_image) else None
    $ _empty_bg = empty_image if renpy.loadable(empty_image) else None
    $ _grid_w = columns * cell_size + (columns - 1) * xspacing
    $ _grid_h = ((_total + columns - 1) // columns) * cell_size + ((max(1, (_total + columns - 1) // columns) - 1) * yspacing)
    vpgrid:
        cols columns
        xspacing xspacing
        yspacing yspacing
        draggable False
        mousewheel False
        xsize _grid_w
        ysize _grid_h
        xalign 0.5
        yalign 0.5
        for idx in range(_total):
            if idx < len(_entries):
                $ e = _entries[idx]
                $ itm = e.get("item")
                $ qty = e.get("qty", 1)
                $ icon = e.get("icon") or get_item_icon(itm) or "images/items/unknown.webp"
                $ action = e.get("action") or NullAction()
                $ sensitive = e.get("sensitive", True)
                $ tip = e.get("tooltip")
                $ is_selected = (selected_item is not None and itm == selected_item)
                $ _alpha = 0.45 if not sensitive else 1.0
                button:
                    xsize cell_size
                    ysize cell_size
                    background None
                    action action
                    sensitive sensitive
                    tooltip tip
                    hovered [SetScreenVariable("hover_idx", idx)]
                    unhovered [SetScreenVariable("hover_idx", None)]
                    focus_mask None
                    at button_hover_effect
                    
                    if _slot_bg:
                        add _slot_bg xysize (cell_size, cell_size)
                    else:
                        add Solid("#2b2b2b") xysize (cell_size, cell_size)
                    
                    if icon:
                        $ _icon_at = inventory_icon_hover if hover_idx == idx else inventory_icon_idle
                        add icon:
                            xalign 0.5
                            yalign 0.5
                            xysize (_icon_size, _icon_size)
                            fit "contain"
                            alpha _alpha
                            at _icon_at
                    if not sensitive:
                        add Solid("#00000066")
                    
                    if show_qty and qty > 1:
                        text "[qty]":
                            align (0.88, 0.88)
                            size 18
                            color "#ffffff"
                            outlines text_outline_fx("#ffffff")
                    
                    if is_selected:
                        add Solid("#ffffff22")
            else:
                frame:
                    xsize cell_size
                    ysize cell_size
                    background None
                    if _empty_bg:
                        add _empty_bg xysize (cell_size, cell_size)
                    else:
                        add Solid("#1f1f1f") xysize (cell_size, cell_size)

screen inventory_screen(tab):
    $ columns = 4
    $ rows = 3
    $ per_page = columns * rows
    $ grid_spacing = 8
    $ cell_size = int(min((1100 - 40 - (columns - 1) * grid_spacing) / columns, (850 - 200 - (rows - 1) * grid_spacing) / rows))
    python:
        entries = build_inventory_entries(character)
        total_pages = max(1, (len(entries) + per_page - 1) // per_page)
        if tab.selected_page >= total_pages:
            tab.selected_page = total_pages - 1
        if tab.selected_page < 0:
            tab.selected_page = 0
        start = tab.selected_page * per_page
        page_entries = entries[start:start + per_page]
        grid_entries = []
        for entry in page_entries:
            item = entry["item"]
            qty = entry["qty"]
            grid_entries.append({
                "item": item,
                "qty": qty,
                "icon": get_item_icon(item),
                "tooltip": item_tooltip_text(item, qty),
                "action": [SetVariable("_return_to_inventory", True), Function(meta_menu.close), Function(queue_inspect_item, item), Return()],
                "sensitive": True,
            })
    frame at inventory_fade:
        background "#222"
        xfill True
        yfill True
        padding (20, 20)
        hbox:
            spacing 20
            xfill True
            yfill True
            
            # Equipped box removed from main inventory; use Equipment tab instead
            
            vbox:
                spacing 12
                xfill True
                yfill True
                $ inv_weight = character.get_total_weight()
                $ weight_max = character.max_weight
                $ slots_used = character.get_used_slots()
                $ slots_max = character.max_slots
                hbox:
                    spacing 20
                    xalign 0.5
                    if weight_max is not None:
                        text "Weight: [inv_weight:.1f] / [weight_max:.1f]" size 16 color "#999"
                    if slots_max is not None:
                        text "Slots: [slots_used] / [slots_max]" size 16 color "#999"
                use inventory_grid(grid_entries, columns=columns, cell_size=cell_size, total_slots=per_page, selected_item=selected_inventory_item, xspacing=grid_spacing, yspacing=grid_spacing)
                if total_pages > 1:
                    hbox:
                        spacing 20
                        xalign 0.5
                        if inventory_page > 0:
                            textbutton "◀ Prev":
                                action SetVariable("inventory_page", max(0, inventory_page - 1))
                                background "#333" hover_background "#555"
                                padding (20, 8)
                        text "Page [inventory_page + 1] / [total_pages]" size 16 color "#ddd"
                        if inventory_page < (total_pages - 1):
                            textbutton "Next ▶":
                                action SetVariable("inventory_page", min(total_pages - 1, inventory_page + 1))
                                background "#333" hover_background "#555"
                                padding (20, 8)

style tab_button:
    background "#333"
    hover_background "#555"
    selected_background "#ffd700"
    padding (12, 8)
    xsize 160

style tab_button_text:
    size 20
    color "#ffffff"
    selected_color "#000000"

style inventory_item_text:
    size 20
    color "#ffffff"

screen container_transfer_screen(container_inv):
    modal True
    zorder 200
    tag menu
    
    # Backdrop
    add "#0c0c0cdd"
    
    # Context Reset
    on "show" action SetVariable("selected_inventory_item", None)

    vbox:
        align (0.5, 0.4)
        spacing 30
        
        hbox:
            spacing 80
            xalign 0.5
            
            # Left Column: Player Inventory
            use inventory_column("YOUR INVENTORY", character, container_inv, bulk_label="Deposit All", bulk_action=Function(transfer_all, character, container_inv))
            
            # Right Column: Container Inventory
            use inventory_column(container_inv.name.upper(), container_inv, character, bulk_label="Take All", bulk_action=Function(transfer_all, container_inv, character), quick_label="Quick Loot", quick_action=Function(transfer_by_tags, container_inv, character, quick_loot_tags))

        # Bottom Close Button
        textbutton "FINISH & CLOSE":
            action Hide("container_transfer_screen")
            xalign 0.5
            padding (40, 20)
            background Frame("#2c3e50", 4, 4)
            hover_background Frame("#34495e", 4, 4)
            text_size 30
            text_bold True
            at button_hover_effect

screen inventory_column(title, source_inv, target_inv, bulk_label=None, bulk_action=None, quick_label=None, quick_action=None):
    vbox:
        spacing 15
        xsize 500
        
        label title text_size 28 text_color "#ffd700" xalign 0.5
        
        if bulk_label and bulk_action:
            hbox:
                spacing 10
                xalign 0.5
                textbutton "[bulk_label]":
                    action bulk_action
                    text_size 16
                    background Frame("#2c3e50", 4, 4)
                    hover_background Frame("#34495e", 4, 4)
                if quick_label and quick_action:
                    textbutton "[quick_label]":
                        action quick_action
                        text_size 16
                        background Frame("#2c3e50", 4, 4)
                        hover_background Frame("#34495e", 4, 4)
        
        frame:
            background "#1a1a1acc"
            padding (10, 10)
            xfill True
            ysize 650
            
            viewport:
                scrollbars "vertical"
                mousewheel True
                draggable True
                
                vbox:
                    spacing 8
                    xfill True
                    
                    python:
                        # Group items for cleaner display
                        grouped = {}
                        for itm in source_inv.items:
                            item_id = item_manager.get_id_of(itm)
                            key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
                            if key not in grouped:
                                label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
                                grouped[key] = {"item": itm, "qty": 0, "label": label}
                            grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
                    
                    if not source_inv.items:
                        text "Empty" italic True color "#666" align (0.5, 0.2)
                    
                    for key, entry in grouped.items():
                        $ first_item = entry["item"]
                        $ count = entry["qty"]
                        
                        button:
                            action Function(transfer_item, first_item, source_inv, target_inv)
                            xfill True
                            padding (15, 12)
                            background Frame("#222", 4, 4)
                            hover_background Frame("#333", 4, 4)
                            
                            hbox:
                                spacing 10
                                text "[entry['label']]" size 22 color "#eee"
                                if count > 1:
                                    text "x[count]" size 18 color "#ffd700" yalign 0.5
                                
                                # Visual indicator of action
                                text ("➡" if source_inv == character else "⬅") size 22 color "#ffd700" xalign 1.0

style back_button_text:
    size 25
    xalign 0.5

screen shop_screen(shop):
    tag menu
    add "#0c0c0c"
    vbox:
        align (0.5, 0.5)
        spacing 20
        xsize 1100
        ysize 850
        hbox:
            xfill True
            text "[shop.name]" size 36 color "#ffffff"
            text "$[character.count_money()]" size 24 color "#ffd700" xalign 1.0 yalign 0.5
        hbox:
            spacing 20
            vbox:
                spacing 10
                text "Shop Stock" size 20 xalign 0.5
                frame:
                    background "#1a1a1a"
                    xsize 530
                    ysize 600
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            spacing 5
                            python:
                                shop_grouped = {}
                                for itm in shop.items:
                                    item_id = item_manager.get_id_of(itm)
                                    key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
                                    if key not in shop_grouped:
                                        label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
                                        shop_grouped[key] = {"item": itm, "qty": 0, "label": label}
                                    shop_grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
                            for key, entry in shop_grouped.items():
                                $ item = entry["item"]
                                $ count = entry["qty"]
                                $ price = shop.get_buy_price(item)
                                hbox:
                                    xfill True
                                    textbutton "[entry['label']] (x[count])":
                                        action SetVariable("selected_shop_item", item)
                                        background ("#333" if globals().get("selected_shop_item") == item else "#222")
                                    text "[price]G" color "#ffd700" yalign 0.5 xalign 1.0
                                    if character.count_money() >= price:
                                        textbutton "Buy":
                                            action [Function(shop.transfer_to, item, character, 1, "purchase", True), SetField(character, "gold", character.count_money() - price), Notify(f"Bought {item.name}")]
                                            xalign 1.0
                                    else:
                                        text "Poor" size 14 color "#666" yalign 0.5 xalign 1.0
            vbox:
                spacing 10
                text "Your Pack" size 20 xalign 0.5
                frame:
                    background "#1a1a1a"
                    xsize 530
                    ysize 600
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            spacing 5
                            python:
                                inv_grouped = {}
                                for itm in character.items:
                                    item_id = item_manager.get_id_of(itm)
                                    key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
                                    if key not in inv_grouped:
                                        label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
                                        inv_grouped[key] = {"item": itm, "qty": 0, "label": label}
                                    inv_grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
                            for key, entry in inv_grouped.items():
                                $ item = entry["item"]
                                $ count = entry["qty"]
                                $ price = shop.get_sell_price(item)
                                hbox:
                                    xfill True
                                    textbutton "[entry['label']] (x[count])":
                                        action SetVariable("selected_shop_item", item)
                                        background ("#333" if globals().get("selected_shop_item") == item else "#222")
                                    text "[price]G" color "#ffd700" yalign 0.5 xalign 1.0
                                    textbutton "Sell":
                                        action [Function(character.transfer_to, item, shop, 1, "sell", True), SetField(character, "gold", character.count_money() + price), Notify(f"Sold {item.name}")]
                                        xalign 1.0
        textbutton "Close Shop":
            align (0.5, 1.0)
            action Return()
            background "#444"
            padding (20, 10)
            text_style "back_button_text"

screen container_screen(container):
    tag menu
    add "#0c0c0c"
    vbox:
        align (0.5, 0.5)
        spacing 20
        xsize 1100
        ysize 850
        text "[container.name]" xalign 0.5 size 36 color "#ffffff"
        hbox:
            spacing 20
            xalign 0.5
            textbutton "Take All":
                action Function(transfer_all, container, character)
                background "#333"
                padding (10, 6)
            textbutton "Quick Loot":
                action Function(transfer_by_tags, container, character, quick_loot_tags)
                background "#333"
                padding (10, 6)
            textbutton "Deposit All":
                action Function(transfer_all, character, container)
                background "#333"
                padding (10, 6)
        hbox:
            spacing 20
            vbox:
                spacing 10
                text "Inside" size 20 xalign 0.5
                frame:
                    background "#1a1a1a"
                    xsize 530
                    ysize 600
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            spacing 5
                            python:
                                cont_grouped = {}
                                for itm in container.items:
                                    item_id = item_manager.get_id_of(itm)
                                    key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
                                    if key not in cont_grouped:
                                        label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
                                        cont_grouped[key] = {"item": itm, "qty": 0, "label": label}
                                    cont_grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
                            for key, entry in cont_grouped.items():
                                $ item = entry["item"]
                                $ count = entry["qty"]
                                hbox:
                                    xfill True
                                    textbutton "[entry['label']] (x[count])":
                                        action SetVariable("selected_cont_item", item)
                                        background ("#333" if globals().get("selected_cont_item") == item else "#222")
                                    textbutton "Take":
                                        action [Function(container.transfer_to, item, character, 1, "loot", False), Notify(f"Took {item.name}")]
                                        xalign 1.0
            vbox:
                spacing 10
                text "Your Items" size 20 xalign 0.5
                frame:
                    background "#1a1a1a"
                    xsize 530
                    ysize 600
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            spacing 5
                            python:
                                inv_grouped = {}
                                for itm in character.items:
                                    item_id = item_manager.get_id_of(itm)
                                    key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
                                    if key not in inv_grouped:
                                        label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
                                        inv_grouped[key] = {"item": itm, "qty": 0, "label": label}
                                    inv_grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
                            for key, entry in inv_grouped.items():
                                $ item = entry["item"]
                                $ count = entry["qty"]
                                hbox:
                                    xfill True
                                    textbutton "[entry['label']] (x[count])":
                                        action SetVariable("selected_cont_item", item)
                                        background ("#333" if globals().get("selected_cont_item") == item else "#222")
                                    textbutton "Deposit":
                                        action [Function(character.transfer_to, item, container, 1, "deposit", False), Notify(f"Stored {item.name}")]
                                        xalign 1.0
        textbutton "Close":
            align (0.5, 1.0)
            action Return()
            background "#444"
            padding (20, 10)
            text_style "back_button_text"


