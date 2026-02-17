# Developer Mode Screens
default dev_tab = "items"
default dev_reload_message = ""

init python:
    import subprocess, sys, os
    def _dev_reload_content():
        global dev_reload_message
        base_dir = os.path.dirname(config.gamedir)
        compile_path = os.path.join(base_dir, "game", "python", "compile_data.py")
        try:
            res = subprocess.run([sys.executable, compile_path], cwd=base_dir, capture_output=True, text=True)
            if res.returncode != 0:
                dev_reload_message = f"Compile failed: {res.stderr.strip() or res.stdout.strip()}"
                return dev_reload_message
        except Exception as e:
            dev_reload_message = f"Compile error: {e}"
            return dev_reload_message
        try:
            load_world()
            dev_reload_message = "Content reloaded."
        except Exception as e:
            dev_reload_message = f"Reload error: {e}"
        return dev_reload_message

screen dev_mode_screen():
    tag menu
    modal True
    zorder 200
    
    # Dark high-contrast theme
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
            textbutton "Locations" action SetVariable("dev_tab", "locations") selected (dev_tab == "locations") text_style "dev_tab_text"
            textbutton "Quests" action SetVariable("dev_tab", "quests") selected (dev_tab == "quests") text_style "dev_tab_text"
            textbutton "Characters" action SetVariable("dev_tab", "chars") selected (dev_tab == "chars") text_style "dev_tab_text"
        
        # Content Area
        frame:
            background "#0a0a1a"
            xfill True
            ysize 600
            padding (20, 20)
            
            if dev_tab == "items":
                use dev_items_view()
            elif dev_tab == "locations":
                use dev_locations_view()
            elif dev_tab == "quests":
                use dev_quests_view()
            elif dev_tab == "chars":
                use dev_chars_view()
        
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
            # Get all items from registry
            for item_id in sorted(item_manager.registry.keys()):
                $ item_base = item_manager.registry[item_id]
                hbox:
                    xfill True
                    vbox:
                        text "[item_base.name] ([item_id])" size 20 color "#eee"
                        text "[item_base.desc]" size 14 color "#999"
                    
                    textbutton "ADD TO INVENTORY":
                        align (1.0, 0.5)
                        action Function(character.add_item, item_manager.get(item_id))
                        text_size 16

screen dev_locations_view():
    viewport:
        mousewheel True
        draggable True
        scrollbars "vertical"
        vbox:
            spacing 10
            for loc_id in sorted(world.locations.keys()):
                $ loc = world.locations[loc_id]
                hbox:
                    xfill True
                    vbox:
                        text "[loc.name] ([loc_id])" size 20 color "#eee"
                        if world.current_location_id == loc_id:
                            text "CURRENTLY HERE" color "#44ff44" size 14
                    
                    textbutton "TELEPORT":
                        align (1.0, 0.5)
                        action [Function(world.move_to, loc_id), Return()]
                        text_size 16

screen dev_quests_view():
    viewport:
        mousewheel True
        draggable True
        scrollbars "vertical"
        vbox:
            spacing 20
            for q_id, q_data in all_quests.items():
                frame:
                    background "#151525"
                    xfill True
                    padding (15, 15)
                    vbox:
                        spacing 5
                        hbox:
                            xfill True
                            text "[q_data.name] ([q_id]) - State: [q_data.state]" size 20 color "#ffd700"
                            textbutton "COMPLETE QUEST":
                                align (1.0, 0.5)
                                action Function(q_complete, q_id)
                                text_size 14
                        
                        for tick_id, tick_data in q_data.ticks.items():
                            hbox:
                                xfill True
                                spacing 20
                                text "  - [tick_data.name]: [tick_data.state] ([tick_data.value]/[tick_data.max_value])" size 16 color ("#ffffff" if tick_data.state == "active" else "#888")
                                if t.state != "complete":
                                    textbutton "FORCE":
                                        yalign 0.5
                                        action Function(q_force_tick, q_id, i)
                                        text_size 12

screen dev_chars_view():
    viewport:
        mousewheel True
        draggable True
        scrollbars "vertical"
        vbox:
            spacing 10
            for c_name in sorted(world.characters.keys()):
                $ c = world.characters[c_name]
                if c.name != "Player":
                    hbox:
                        xfill True
                        vbox:
                            text "[c.name]" size 20 color "#eee"
                            text "Location: [c.location_id]" size 14 color "#999"
                        
                        textbutton "INTERACT":
                            align (1.0, 0.5)
                            action [Function(c.interact), Return()]
                            text_size 16

style dev_tab_text:
    size 22
    color "#888"
    selected_color "#ff3333"
    hover_color "#ffffff"
