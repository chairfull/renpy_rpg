screen inventory_screen():
    tag menu
    add "#0f0f0f"
    
    vbox:
        align (0.5, 0.5)
        spacing 20
        xsize 1000
        ysize 800
        
        label "Inventory" xalign 0.5 text_size 40 text_color "#ffffff"
        
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
                        # Group items by name
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
                    vbox:
                        spacing 15
                        text "[itm.name]" size 30 color "#ffd700"
                        text "[itm.description]" size 20# wrap_around True
                        
                        null height 10
                        text "Weight: [itm.weight] kg" size 18 color "#cccccc"
                        text "Value: [itm.value] gold" size 18 color "#cccccc"
                        
                        if itm.outfit_part:
                            null height 20
                            textbutton "Equip":
                                action [Function(pc.equipped_items.update, {itm.outfit_part: itm}), Notify(f"Equipped {itm.name}")]
                                background "#444" 
                                padding (10, 5)
                                text_size 18
                else:
                    text "Select an item to see details." align (0.5, 0.5) color "#666666"

        textbutton "Back":
            align (0.5, 1.0)
            action Return()
            text_size 25
            background "#444"
            padding (20, 10)

default selected_inventory_item = None

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
            
            # Stats and Avatar Placeholder
            vbox:
                spacing 20
                frame:
                    background "#1a1a1a"
                    padding (20, 20)
                    xsize 300
                    ysize 400
                    # Avatar placeholder
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
                        text "Outfit: [pc.current_outfit.capitalize()]" size 20 color "#ffffff"
                        for part, item in pc.equipped_items.items():
                            text "[part.capitalize()]: [item.name]" size 16 color "#cccccc"

            # Detailed Stats
            frame:
                background "#1a1a1a"
                padding (30, 30)
                xsize 500
                vbox:
                    spacing 15
                    text "Attributes" size 28 color "#ffd700"
                    
                    $ stats = pc.stats
                    $ stat_list = [
                        ("Strength", stats.strength, "💪"),
                        ("Dexterity", stats.dexterity, "🏹"),
                        ("Intelligence", stats.intelligence, "🧠"),
                        ("Charisma", stats.charisma, "✨")
                    ]
                    
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
