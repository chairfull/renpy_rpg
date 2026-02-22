screen dev_mode_screen():
    default tab = "items"
    default reload_message = ""
    tag menu
    modal True
    zorder 200
    
    add Solid("#050510")
    
    vbox:
        spacing 20
        xsize 1000
        align (0.5, 0.5)
        
        hbox:
            spacing 40
            xalign 0.5
            text "DEVELOPER CONSOLE" size 48 color "#ff3333" bold True
        
        # Tabs
        hbox:
            spacing 10
            xalign 0.5
            textbutton "Items" action SetVariable("dev_tab", "items") selected (dev_tab == "items") text_style "dev_tab_text"
            textbutton "Locations" action SetVariable("dev_tab", "zones") selected (dev_tab == "zones") text_style "dev_tab_text"
            textbutton "Quests" action SetVariable("dev_tab", "quests") selected (dev_tab == "quests") text_style "dev_tab_text"
            textbutton "Characters" action SetVariable("dev_tab", "beings") selected (dev_tab == "beings") text_style "dev_tab_text"
        
        # Content Area
        frame:
            background "#0a0a1a"
            xfill True
            ysize 600
            padding (20, 20)
            
            if dev_tab == "items":
                use dev_items_view()
            elif dev_tab == "zones":
                use dev_zones_view()
            elif dev_tab == "quests":
                use dev_quests_view()
            elif dev_tab == "beings":
                use dev_beings_view()
        
        hbox:
            spacing 20
            xalign 0.5
            textbutton "RELOAD CONTENT":
                action [Function(_dev_reload_content), Notify(dev_reload_message or "Reload requested")]
                text_size 18
                text_color "#ffcc66"
            textbutton "TOGGLE FREE TRAVEL":
                action ToggleVariable("allow_unvisited_travel")
                text_size 14
                text_color "#66ccff"
            textbutton "TOGGLE QUICK TRAVEL":
                action ToggleVariable("quick_travel_on_click")
                text_size 14
                text_color "#66ccff"
            if dev_reload_message:
                text "[dev_reload_message]" size 14 color "#aaa"

        textbutton "EXIT CONSOLE":
            xalign 0.5
            action Hide("dev_mode_screen")
            text_size 24
            text_color "#ff6666"

screen dev_items_view():
    viewport:
        mousewheel True
        draggable True
        scrollbars "vertical"
        vbox:
            spacing 10
            for item in all_items.values():
                hbox:
                    xfill True
                    vbox:
                        text "[item.name] ([item.id])" size 20 color "#eee"
                        text "[item.desc]" size 14 color "#999"
                    
                    textbutton "ADD TO INVENTORY":
                        align (1.0, 0.5)
                        action Function(player.gain_item, item)
                        text_size 16

screen dev_zones_view():
    viewport:
        mousewheel True
        draggable True
        scrollbars "vertical"
        vbox:
            spacing 10
            for zone in all_zones.values():
                hbox:
                    xfill True
                    vbox:
                        text "[zone.name] ([zone.id])" size 20 color "#eee"
                        if player.zone == zone:
                            text "CURRENTLY HERE" color "#44ff44" size 14
                    
                    textbutton "TELEPORT":
                        align (1.0, 0.5)
                        action [Function(set_zone, zone), Return()]
                        text_size 16

screen dev_quests_view():
    viewport:
        mousewheel True
        draggable True
        scrollbars "vertical"
        vbox:
            spacing 20
            for quest in all_quests.values():
                frame:
                    background "#151525"
                    xfill True
                    padding (15, 15)
                    vbox:
                        spacing 5
                        hbox:
                            xfill True
                            text "[quest.name] ([quest.id]) - State: [quest.state]" size 20 color "#ffd700"
                            textbutton "COMPLETE QUEST":
                                align (1.0, 0.5)
                                action Function(complete_quest, quest)
                                text_size 14
                        
                        for tick_id, tick_data in quest.ticks.items():
                            hbox:
                                xfill True
                                spacing 20
                                text "  - [tick_data.name]: [tick_data.state] ([tick_data.value]/[tick_data.max_value])" size 16 color ("#ffffff" if tick_data.state == "active" else "#888")
                                if t.state != "complete":
                                    textbutton "FORCE":
                                        yalign 0.5
                                        action Function(q_force_tick, q_id, i)
                                        text_size 12

screen dev_beings_view():
    viewport:
        mousewheel True
        draggable True
        scrollbars "vertical"
        vbox:
            spacing 10
            for being in all_beings.values():
                if being == player:
                    continue
                hbox:
                    xfill True
                    vbox:
                        $ loc_name = being.zone.name or "NONE"
                        text "[being.name]" size 20 color "#eee"
                        text "Location: [loc_name]" size 14 color "#999"
                    
                    textbutton "INTERACT":
                        align (1.0, 0.5)
                        action [Function(being.interact), Return()]
                        text_size 16

style dev_tab_text:
    size 22
    color "#888"
    selected_color "#ff3333"
    hover_color "#ffffff"
