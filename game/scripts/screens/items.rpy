
transform item_popup_bounce:
    on show:
        yalign 1.5
        pause 0.1
        easein_back 0.6 yalign 0.25
    on hide:
        easeout_back 0.6 yalign 1.5

label show_item(item):
    show screen item_inspect_screen(item)
    return

label hide_item:
    hide screen item_inspect_screen
    return

screen item_inspect_screen(item):
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

# label inspect_item_pending:
#     $ store.inspect_force = True
#     $ iid = store.pending_inspect_item_id
#     $ store.pending_inspect_item_id = None
#     if not iid:
#         $ store.inspect_force = False
#         return

#     # Resolve the label
#     $ inspect_item(iid)
#     $ resolved_label = store.inspect_resolved_label
#     $ resolved_item = store.inspect_resolved_item
#     $ store.inspect_force = False

#     if resolved_label:
#         call expression resolved_label
#     elif resolved_item and resolved_item.desc:
#         $ item_show_image(resolved_item)
#         "[resolved_item.desc]"
#         $ item_hide_image()

#     $ item_hide_image()

#     if store._return_to_inventory:
#         $ store._return_to_inventory = False
#         call screen inventory_screen
#     return


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
                            outlines text_outline("#ffffff")
                    
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


