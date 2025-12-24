screen top_down_map(location):
    # No longer modal as it's the primary screen
    tag world_view
    
    # Background Map
    if location.map_image:
        add location.map_image
    else:
        add Solid("#222")
    
    # Update Loop
    timer 0.016 repeat True action Function(td_manager.update, 0.016)

    # Click to Move
    button:
        area (0, 0, 1920, 1080)
        action Function(td_manager.set_target, renpy.get_mouse_pos()[0], renpy.get_mouse_pos()[1])
        background None

    # Entities/Interactives
    for obj_id, (ox, oy) in td_manager.interactives.items():
        imagebutton:
            idle Solid("#f00", xsize=20, ysize=20) # Placeholder for entity sprite
            pos (ox - 10, oy - 10)
            action Function(td_manager.set_target, ox, oy)
            hovered Notify(f"Interact with {obj_id}")

    # Player Sprite
    add Solid("#00f", xsize=30, ysize=30):
        pos (int(td_manager.player_pos[0]) - 15, int(td_manager.player_pos[1]) - 15)
    
    # UI Overlays
    
    # Bottom Left: Dashboard
    frame:
        align (0.02, 0.98)
        background "#000a"
        padding (10, 10)
        hbox:
            spacing 10
            textbutton "DASHBOARD":
                action ShowMenu("inventory_screen")
                text_size 24
                text_color "#ffd700"
            
            textbutton "DEV CONSOLE":
                action Show("dev_mode_screen")
                text_size 16
                text_color "#ff3333"

    # Right Side: Navigation
    frame:
        align (0.98, 0.5)
        background "#000a"
        padding (15, 15)
        xsize 250
        vbox:
            spacing 10
            text "Navigation" size 24 color "#ffffff" bold True
            null height 10
            
            for dest_id, desc in location.connections.items():
                $ dest_loc = rpg_world.locations.get(dest_id)
                button:
                    action [Function(rpg_world.move_to, dest_id), Function(td_manager.setup, rpg_world.locations[dest_id]), Return()]
                    xfill True
                    background "#1a1a2a"
                    padding (10, 5)
                    hover_background "#33334a"
                    if dest_loc:
                        text "[dest_loc.name]" size 18 color "#eee" xalign 0.5
                    else:
                        text "[desc]" size 18 color "#eee" xalign 0.5

    # Path Debugging
    if td_manager.path:
        for wx, wy in td_manager.path:
            add Solid("#ffff00", xsize=4, ysize=4):
                pos (wx-2, wy-2)
