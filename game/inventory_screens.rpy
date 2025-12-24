screen inventory_screen():
    tag menu
    add "#0f0f0f"
    
    vbox:
        align (0.5, 0.5)
        spacing 20
        xsize 1000
        ysize 800
        
        hbox:
            align (0.5, 0.0)
            xfill True
            label "Inventory" text_size 40 text_color "#ffffff"
            text "Gold: [pc.gold]" size 24 color "#ffd700" xalign 1.0 yalign 0.5
        
        hbox:
            spacing 20
            
            # Item List
            frame:
                background "#1a1a1a"
                xsize 400
                ysize 600
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    vbox:
                        spacing 5
                        python:
                            grouped_items = {}
                            for item in pc.items:
                                if item.name not in grouped_items:
                                    grouped_items[item.name] = []
                                grouped_items[item.name].append(item)
                        
                        for name, item_list in grouped_items.items():
                            $ first_item = item_list[0]
                            textbutton "[name] (x[len(item_list)])":
                                action SetVariable("selected_inventory_item", first_item)
                                xfill True
                                text_color "#ffffff"
                                background ("#333" if globals().get("selected_inventory_item") == first_item else "#222")
                                text_size 20

            # Item Details
            frame:
                background "#1a1a1a"
                xsize 580
                ysize 600
                padding (20, 20)
                
                if globals().get("selected_inventory_item"):
                    $ itm = selected_inventory_item
                    $ i_id = item_manager.get_id_of(itm)
                    vbox:
                        spacing 15
                        text "[itm.name]" size 30 color "#ffd700"
                        text "[itm.description]" size 20
                        
                        null height 10
                        text "Weight: [itm.weight] kg" size 18 color "#cccccc"
                        text "Value: [itm.value] gold" size 18 color "#cccccc"
                        
                        hbox:
                            spacing 10
                            if renpy.has_label(f"ITEM__{i_id}__inspect"):
                                textbutton "Inspect":
                                    action [Hide("inventory_screen"), Call(f"ITEM__{i_id}__inspect"), Show("inventory_screen")]
                                    background "#555" padding (15, 10)
                            
                            if itm.outfit_part:
                                textbutton "Equip":
                                    action [Function(pc.equipped_items.update, {itm.outfit_part: itm}), Notify(f"Equipped {itm.name}")]
                                    background "#444" padding (15, 10)
                else:
                    text "Select an item to see details." align (0.5, 0.5) color "#666666"

        textbutton "Back":
            align (0.5, 1.0)
            action Return()
            text_size 25
            background "#444"
            padding (20, 10)

# --- CHARACTER INTERACTION SCREEN ---
screen char_interact_screen(char):
    tag menu
    add "#0c0c0c"
    
    vbox:
        align (0.5, 0.5)
        spacing 30
        xsize 800
        
        frame:
            background "#1a1a1a"
            padding (40, 40)
            xfill True
            vbox:
                spacing 10
                text "[char.name]" size 40 color "#ffd700" xalign 0.5
                text "[char.description]" size 20 italic True xalign 0.5 color "#cccccc"
                
                null height 20
                hbox:
                    xalign 0.5
                    spacing 40
                    $ stats = char.stats
                    vbox:
                        label "Stats" text_color "#ffffff"
                        text "Relation: Friendly" size 18 color "#00ff00"
                        text "Status: Relaxed" size 18 color "#ffffff"
                    vbox:
                        label "Attributes" text_color "#ffffff"
                        text "Knowledge: [stats.intelligence]" size 18 color "#ffffff"
                        text "Presence: [stats.charisma]" size 18 color "#ffffff"

        hbox:
            spacing 20
            xalign 0.5
            
            # Talk Button
            if char.label and renpy.has_label(char.label):
                textbutton "Talk":
                    action [Hide("char_interact_screen"), Jump(char.label)]
                    style "interact_button"
            
            # Give Button
            textbutton "Give":
                action Show("char_give_screen", char=char)
                style "interact_button"
            
            # Outfit Button (Placeholder)
            textbutton "Outfit":
                action Notify("Outfit system coming soon!")
                style "interact_button"

        textbutton "Back":
            xalign 0.5
            action Return()
            text_size 25
            background "#444"
            padding (20, 10)

screen char_give_screen(char):
    modal True
    add Solid("#000000aa")
    
    frame:
        align (0.5, 0.5)
        background "#1a1a1a"
        padding (30, 30)
        xsize 600
        ysize 600
        
        vbox:
            spacing 15
            label "Give item to [char.name]" text_size 24 xalign 0.5
            
            viewport:
                scrollbars "vertical"
                mousewheel True
                vbox:
                    spacing 5
                    for item in pc.items:
                        textbutton "[item.name]":
                            action [Function(pc.transfer_to, item, char), Notify(f"Gave {item.name} to {char.name}"), Hide("char_give_screen")]
                            xfill True
                            background "#222"
            
            textbutton "Cancel":
                xalign 0.5
                action Hide("char_give_screen")
                background "#444" padding (10, 5)

style interact_button:
    background "#333"
    hover_background "#555"
    padding (30, 20)
    xsize 200
    # text_size 24
    # text_xalign 0.5

# Existing screens below...
screen shop_screen(shop):
    # ... (same as before)
    tag menu
    add "#0c0c0c"
    vbox:
        align (0.5, 0.5)
        spacing 20
        xsize 1100
        ysize 850
        hbox:
            xfill True
            label "[shop.name]" text_size 36 text_color "#ffffff"
            text "Your Gold: [pc.gold]" size 24 color "#ffd700" xalign 1.0 yalign 0.5
        hbox:
            spacing 20
            vbox:
                spacing 10
                label "Shop Stock" text_size 20 xalign 0.5
                frame:
                    background "#1a1a1a"
                    xsize 530
                    ysize 600
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            spacing 5
                            for item in shop.items:
                                $ price = shop.get_buy_price(item)
                                hbox:
                                    xfill True
                                    textbutton "[item.name]":
                                        action SetVariable("selected_shop_item", item)
                                        background ("#333" if globals().get("selected_shop_item") == item else "#222")
                                    text "[price]G" color "#ffd700" yalign 0.5 xalign 1.0
                                    if pc.gold >= price:
                                        textbutton "Buy":
                                            action [Function(shop.transfer_to, item, pc), SetField(pc, "gold", pc.gold - price), Notify(f"Bought {item.name}")]
                                            xalign 1.0
                                    else:
                                        text "Poor" size 14 color "#666" yalign 0.5 xalign 1.0
            vbox:
                spacing 10
                label "Your Pack" text_size 20 xalign 0.5
                frame:
                    background "#1a1a1a"
                    xsize 530
                    ysize 600
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            spacing 5
                            for item in pc.items:
                                $ price = shop.get_sell_price(item)
                                hbox:
                                    xfill True
                                    textbutton "[item.name]":
                                        action SetVariable("selected_shop_item", item)
                                        background ("#333" if globals().get("selected_shop_item") == item else "#222")
                                    text "[price]G" color "#ffd700" yalign 0.5 xalign 1.0
                                    textbutton "Sell":
                                        action [Function(pc.transfer_to, item, shop), SetField(pc, "gold", pc.gold + price), Notify(f"Sold {item.name}")]
                                        xalign 1.0
        textbutton "Close Shop":
            align (0.5, 1.0)
            action Return()
            text_size 25
            background "#444"
            padding (20, 10)

screen container_screen(container):
    tag menu
    add "#0c0c0c"
    vbox:
        align (0.5, 0.5)
        spacing 20
        xsize 1100
        ysize 850
        label "[container.name]" xalign 0.5 text_size 36 text_color "#ffffff"
        hbox:
            spacing 20
            vbox:
                spacing 10
                label "Inside" text_size 20 xalign 0.5
                frame:
                    background "#1a1a1a"
                    xsize 530
                    ysize 600
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            spacing 5
                            for item in container.items:
                                hbox:
                                    xfill True
                                    textbutton "[item.name]":
                                        action SetVariable("selected_cont_item", item)
                                        background ("#333" if globals().get("selected_cont_item") == item else "#222")
                                    textbutton "Take":
                                        action [Function(container.transfer_to, item, pc), Notify(f"Took {item.name}")]
                                        xalign 1.0
            vbox:
                spacing 10
                label "Your Items" text_size 20 xalign 0.5
                frame:
                    background "#1a1a1a"
                    xsize 530
                    ysize 600
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            spacing 5
                            for item in pc.items:
                                hbox:
                                    xfill True
                                    textbutton "[item.name]":
                                        action SetVariable("selected_cont_item", item)
                                        background ("#333" if globals().get("selected_cont_item") == item else "#222")
                                    textbutton "Deposit":
                                        action [Function(pc.transfer_to, item, container), Notify(f"Stored {item.name}")]
                                        xalign 1.0
        textbutton "Close":
            align (0.5, 1.0)
            action Return()
            text_size 25
            background "#444"
            padding (20, 10)

screen character_sheet():
    tag menu
    add "#0f0f0f"
    vbox:
        align (0.5, 0.5)
        spacing 20
        xsize 1000
        ysize 800
        label "Character Profile" xalign 0.5 text_size 40 text_color "#ffffff"
        hbox:
            spacing 40
            xalign 0.5
            vbox:
                spacing 20
                frame:
                    background "#1a1a1a"
                    padding (20, 20)
                    xsize 300
                    ysize 400
                    vbox:
                        align (0.5, 0.5)
                        text "👤" size 150 xalign 0.5
                        text "[pc.name]" size 30 xalign 0.5 color "#ffd700"
                frame:
                    background "#1a1a1a"
                    padding (20, 20)
                    xsize 300
                    vbox:
                        spacing 5
                        text "Gold: [pc.gold]" size 22 color "#ffd700"
                        null height 10
                        text "Outfit: [pc.current_outfit.capitalize()]" size 20 color "#ffffff"
                        for part, item in pc.equipped_items.items():
                            text "[part.capitalize()]: [item.name]" size 16 color "#cccccc"
            frame:
                background "#1a1a1a"
                padding (30, 30)
                xsize 500
                vbox:
                    spacing 15
                    text "Attributes" size 28 color "#ffd700"
                    $ stats = pc.stats
                    $ stat_list = [("Strength", stats.strength, "💪"), ("Dexterity", stats.dexterity, "🏹"), ("Intelligence", stats.intelligence, "🧠"), ("Charisma", stats.charisma, "✨")]
                    for sname, sval, sicon in stat_list:
                        hbox:
                            xfill True
                            text "[sicon] [sname]" size 22 color "#ffffff"
                            text "[sval]" size 22 color "#00bfff" xalign 1.0
                    null height 20
                    text "Vitals" size 28 color "#ffd700"
                    vbox:
                        spacing 5
                        text "HP: [stats.hp] / [stats.max_hp]" size 18 color "#ffffff"
                        bar value stats.hp range stats.max_hp:
                            xsize 440
                            ysize 20
                            left_bar Solid("#ff4444")
                            right_bar Solid("#333")
        textbutton "Back":
            align (0.5, 1.0)
            action Return()
            text_size 25
            background "#444"
            padding (20, 10)
