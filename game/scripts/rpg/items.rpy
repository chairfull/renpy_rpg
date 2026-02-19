init -1400 python:
    onstart(add_meta_menu_tab, "inventory", "🎒", "Inventory",
        selected_item=None,
        selected_page=0)
    
    class Item(HasTags):
        """Base item definition class."""
        def __init__(self, _id, name="", desc="", mass=0, cost=0, tags=None, equip_slots=None, stack_size=1_000, **kwargs):
            self.id = _id
            HasTags.__init__(self, tags)
            self.name = name
            self.desc = desc
            self.mass = mass
            self.cost = cost
            self.stack_size = max(1, int(stack_size or 1))
            self.equip_slots = equip_slots or []
        
        @property
        def stackable(self):
            return self.stack_size > 1

    class ItemSlot:
        """Item container. Used for inventory, equipment, and item holders."""
        def __init__(self, item, quantity, owner=None, stolen=False):
            self.item = item
            self.quantity = quantity
            self.owner = None
            self.stolen = stolen
    
    class ItemFilter:
        def __init__(self, _id, slots, allowed_tags=[], blocked_tags=[], allowed_items=[], blocked_items=[]):
            self.id = _id
            self.slots = slots
            self.allowed_tags = allowed_tags
            self.blocked_tags = blocked_tags
            self.allowed_items = allowed_items
            self.blocked_items = blocked_items
        
        def passes(self, item):
            if self.allowed_tags and item.has_any_tag(self.allowed_tags):
                return True
            if self.allowed_items and item in self.allowed_items:
                return True
            if self.blocked_tags and item.has_any_tag(self.blocked_tags):
                return False
            if self.blocked_items and item in self.blocked_items:
                return False
            return True
    
    class HasItems:
        """Mixin for inventories."""
        def __init__(self, _id, name, items=None, item_filters=None, item_columns=1, max_item_slots=1_000_000, max_item_mass=1_000_000, **kwargs):
            self.id = _id
            self.name = name
            self.items = {} # Item slots can either be a string for equipment or an (tuple) for unequipped items.
            self.item_filters = item_filters
            self.item_columns = clamp(item_columns, 1, 100)
            self.item_mass = 0
            self.max_item_slots = clamp(max_item_slots, 1, 1_000_000)
            self.max_item_mass = clamp(max_item_mass, 1, 1_000_000)
        
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
            
            ITEMS_CHANGED.emit(items=self)

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
                unequip_item_slot(to_slot_id)
            for sid in slot_info.get("unequip", []):
                unequip_item_slot(sid)
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

    @flow_action("GAIN_ITEM")
    def gain_item(item, count=None, target=player, source=None, steal=False):
        count = count or 1
        if target:
            target.gain_item(item, count, owner=source, steal=steal)
        if source:
            source.lose_item(item, count)

    @flow_action("LOSE_ITEM")
    def lose_item(selfitem, count=None, source=player, target=None, steal=False):
        gain_item(item, count, target, source, steal)

    def get_item_icon(item_or_id, fallback=None):
        "Return an item icon path, falling back to a generic icon."
        item = item_or_id
        if isinstance(item_or_id, str):
            item = item_manager.get(item_or_id)
        if item is None:
            return None
        icon = getattr(item, "image", None)
        if icon and renpy.loadable(icon):
            return icon
        item_id = item_manager.get_id_of(item)
        for ext in ("png", "webp", "jpg", "jpeg"):
            candidate = f"images/items/{item_id}.{ext}"
            if renpy.loadable(candidate):
                return candidate
        if fallback is None:
            fallback = "images/items/unknown.webp"
        if fallback and renpy.loadable(fallback):
            return fallback
        alt = "images/icons/unknown.webp"
        return alt if renpy.loadable(alt) else None

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

    def _get_item_actions(item):
        actions = []
        for act in getattr(item, "actions", []) or []:
            label = act.get("label") if isinstance(act, dict) else None
            name = act.get("name") if isinstance(act, dict) else None
            if label and renpy.has_label(label):
                actions.append((name or label, label))
        return actions

    def inspect_item(item_or_id):
        """Resolve an inventory item's inspect label and store it for calling."""
        item = item_or_id
        if isinstance(item_or_id, str):
            item = item_manager.get(item_or_id)
        if not item:
            return

        # If we're inside an interaction, queue a safe inspect label and exit.
        if not getattr(store, "inspect_force", False):
            try:
                if renpy.in_interaction():
                    queue_inspect_item(item)
                    return
            except Exception:
                pass

        item_id = item_manager.get_id_of(item)
        sep = "__"

        # Try inspect label first, then flow label as fallback
        inspect_label = sep.join(["ITEM", item_id, "inspect"])
        if not renpy.has_label(inspect_label):
            alt_label = sep.join(["ITEM", item_id, "Inspect"])
            if renpy.has_label(alt_label):
                inspect_label = alt_label
        if not renpy.has_label(inspect_label):
            flow_label = sep.join(["ITEM", item_id, "flow"])
            if renpy.has_label(flow_label):
                inspect_label = flow_label

        # Store results for _inspect_item_pending to use
        if renpy.has_label(inspect_label):
            store.inspect_resolved_label = inspect_label
        else:
            store.inspect_resolved_label = None
        store.inspect_resolved_item = item

    def queue_inspect_item(item_or_id):
        item = item_or_id
        if isinstance(item_or_id, str):
            item = item_manager.get(item_or_id)
        if not item:
            return
        store.pending_inspect_item_id = item_manager.get_id_of(item)
        queue("label", "inspect_item_pending")
    
    ITEM_GAINED  = create_signal(item=Item, items=HasItems, amount=int)
    ITEM_LOST = create_signal(item=Item, items=HasItems, amount=int)
    ITEMS_CHANGED = create_signal(items=HasItems)

transform item_popup_bounce:
    on show:
        yalign 1.5
        pause 0.1
        easein_back 0.6 yalign 0.25
    on hide:
        easeout_back 0.6 yalign 1.5

label show_item(item_id):
    show screen item_inspect_screen(item_id)
    return

label hide_item:
    hide screen item_inspect_screen
    return

screen item_inspect_screen(item_id):
    $ item = item_manager.get(item_id)
    $ icon = get_item_icon(item)
    zorder 200
    frame at item_popup_bounce:
        xalign 0.5
        padding (20, 20)
        vbox:
            spacing 10
            if item.name:
                text "[item.name]" size 22 color "#ffd700" xalign 0.5
            if icon:
                add icon xalign 0.5 yalign 0.5
            else:
                text "No icon available." size 16 color "#999" xalign 0.5

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
                $ inv_weight = player.get_total_weight()
                $ weight_max = player.max_weight
                $ slots_used = player.get_used_slots()
                $ slots_max = player.max_slots
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
                                text ("➡" if source_inv == player else "⬅") size 22 color "#ffd700" xalign 1.0

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
            text "$[player.count_money()]" size 24 color "#ffd700" xalign 1.0 yalign 0.5
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
                                    if player.count_money() >= price:
                                        textbutton "Buy":
                                            action [Function(shop.transfer_to, item, player, 1, "purchase", True), SetField(character, "gold", character.count_money() - price), Notify(f"Bought {item.name}")]
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
                action Function(transfer_all, container, player)
                background "#333"
                padding (10, 6)
            textbutton "Quick Loot":
                action Function(transfer_by_tags, container, player, quick_loot_tags)
                background "#333"
                padding (10, 6)
            textbutton "Deposit All":
                action Function(transfer_all, player, container)
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


