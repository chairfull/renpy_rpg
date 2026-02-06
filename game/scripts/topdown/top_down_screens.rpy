default td_zoom = 1.0
default show_reachability = False

transform td_cinematic_enter:
    subpixel True
    zoom 2.0 alpha 0.0
    align (0.5, 0.5)
    anchor (0.5, 0.5)
    parallel:
        easein 0.5 alpha 1.0
    parallel:
        easein 2.0 zoom 1.0

transform td_interactive_zoom(z):
    subpixel True
    zoom z
    align (0.5, 0.5)
    anchor (0.5, 0.5)

screen top_down_map(location):
    tag world_view
    zorder 10
    
    # Zoom Controls
    key "K_PLUS" action SetVariable("td_zoom", min(2.5, td_zoom + 0.1))
    key "K_EQUALS" action SetVariable("td_zoom", min(2.5, td_zoom + 0.1))
    key "K_MINUS" action SetVariable("td_zoom", max(0.5, td_zoom - 0.1))
    key "mousedown_4" action SetVariable("td_zoom", min(2.5, td_zoom + 0.1))
    key "mousedown_5" action SetVariable("td_zoom", max(0.5, td_zoom - 0.1))
    key "c" action Function(td_manager.snap_camera)
    key "h" action ToggleVariable("show_reachability")
    
    # Update Loop - Paused when phone is open
    timer 0.033 repeat True action [
        If(not renpy.get_screen("phone_router"), [Function(td_manager.update, 0.033), renpy.restart_interaction])
    ]
    
    # Main Map Container with Zoom/Cinematic
    frame:
        background None
        padding (0, 0)
        xfill True
        yfill True
        
        # Apply transforms based on state
        if not intro_cinematic_done:
            at td_cinematic_enter
            timer 2.0 action SetVariable("intro_cinematic_done", True)
        else:
            at td_interactive_zoom(td_zoom)
        
        fixed:
            xsize 1920
            ysize 1080
            
            $ cam_x = int(td_manager.camera_offset[0])
            $ cam_y = int(td_manager.camera_offset[1])
            
            # 1. Background Map
            if location.map_image:
                add location.map_image pos (-cam_x, -cam_y)
            else:
                add Solid("#222") pos (-cam_x, -cam_y)
            
            # 2. Click-to-Move Ground Layer
            button:
                area (0, 0, 1920, 1080)
                action Function(_td_click_to_move)
                background None

            # 3. Interactive Entities (NPCs, Exits, Objects, Player) - Depth Sorted
            for entity in td_manager.get_sorted_entities():
                $ sx = int(entity.x - cam_x)
                $ sy = int(entity.y - cam_y)
                $ reach_color = None
                if show_reachability and not entity.is_player:
                    $ path_ok = bool(td_manager.find_path((int(td_manager.player_pos[0]), int(td_manager.player_pos[1])), (int(entity.x), int(entity.y))))
                    $ reach_color = TintMatrix("#44ff44") if path_ok else TintMatrix("#ff4444")
                
                button:
                    anchor (0.5, 0.5)
                    pos (sx, sy)
                    xsize 120 ysize 120 # Uniform hit area
                    action entity.action
                    tooltip entity.tooltip
                    focus_mask None
                    
                    background None
                    
                    # Visuals - Different rendering for player vs other entities
                    if entity.is_player:
                        add Transform(
                            entity.sprite,
                            zoom=0.35,
                            rotate=entity.rotation,
                            anchor=(0.5, 1.0),
                            align=(0.5, 1.0),
                            transform_anchor=True,
                            subpixel=True
                        )
                    else:
                        fixed at phone_visual_hover:
                            if entity.sprite_tint:
                                # For colored markers (like exits)
                                add Transform(entity.sprite, zoom=0.3, matrixcolor=entity.sprite_tint) align (0.5, 0.5)
                            else:
                                # For characters/objects
                                if entity.idle_anim:
                                    add At(Transform(entity.sprite, zoom=0.35, matrixcolor=reach_color), char_idle_anim) align (0.5, 0.5)
                                else:
                                    add Transform(entity.sprite, zoom=0.35, matrixcolor=reach_color) align (0.5, 0.5)
    
    # 5. UI Layers (Location Name, Dashboard)
    frame:
        align (0.5, 0.02)
        background "#00000088"
        padding (20, 8)
        text "[location.name]" size 28 color "#ffffff"
    
    # Time and schedule quick panel
    frame:
        align (0.18, 0.02)
        background "#00000088"
        padding (12, 10)
        vbox:
            spacing 6
            text "Time: [time_manager.time_string]" size 18 color "#ffd700"
            hbox:
                spacing 6
                textbutton "+15m" action Function(time_manager.advance, 15) text_size 14
                textbutton "+1h" action Function(time_manager.advance, 60) text_size 14
                text "[time_manager.time_of_day]" size 14 color "#ccc"
            text "Here now:" size 14 color "#aaa"
            vbox:
                spacing 2
                for c in location.characters:
                    $ nxt_time, nxt_loc = c.next_schedule_entry()
                    hbox:
                        spacing 6
                        text c.name size 14 color "#fff"
                        if nxt_time and nxt_loc:
                            text f"→ {nxt_loc} @ {nxt_time}" size 12 color "#777"
    
    frame:
        align (0.02, 0.98)
        background "#000a"
        padding (10, 10)
        hbox:
            spacing 10
            textbutton "📱 PHONE" action Show("phone_router") text_size 24 text_color "#00bfff"
            textbutton "DEV" action Show("dev_mode_screen") text_size 14 text_color "#ff3333"
            textbutton "CENTER" action Function(td_manager.snap_camera) text_size 12 text_color "#ccc"

    # 6. Tooltip Layer
    use mouse_tooltip

# Idle breathing animation (Removed zoom pulse as per user request)
transform char_idle_anim:
    subpixel True
    anchor (0.5, 0.5)
    parallel:
        ease 1.5 rotate -1.5
        ease 1.5 rotate 1.5
        repeat

init python:
    def _td_click_to_move():
        zoom = getattr(store, "td_zoom", 1.0)
        mx, my = renpy.get_mouse_pos()
        wx, wy = td_manager.screen_to_world(mx, my, zoom)
        td_manager.set_target(wx, wy)
