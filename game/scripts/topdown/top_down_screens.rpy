default td_zoom = 1.0

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

            # 3. Interactive Entities (NPCs, Exits, Objects)
            for entity in td_manager.entities:
                $ sx = int(entity.x - cam_x)
                $ sy = int(entity.y - cam_y)
                
                button:
                    anchor (0.5, 0.5)
                    pos (sx, sy)
                    xsize 120 ysize 120 # Uniform hit area
                    action entity.action
                    tooltip entity.tooltip
                    focus_mask None
                    
                    background None
                    
                    # Visuals
                    fixed at phone_visual_hover:
                        if entity.sprite_tint:
                            # For colored markers (like exits)
                            # NO SCALE CHANGE ON HOVER
                            add Transform(entity.sprite, zoom=0.3, matrixcolor=entity.sprite_tint) align (0.5, 0.5)
                        else:
                            # For characters/objects
                            if entity.idle_anim:
                                # NO SCALE CHANGE ON HOVER
                                add At(Transform(entity.sprite, zoom=0.35), char_idle_anim) align (0.5, 0.5)
                            else:
                                # NO SCALE CHANGE ON HOVER
                                add Transform(entity.sprite, zoom=0.35) align (0.5, 0.5)

            # 4. Player Sprite
            $ psx = int(td_manager.player_pos[0] - cam_x)
            $ psy = int(td_manager.player_pos[1] - cam_y)
            
            button:
                anchor (0.5, 0.5)
                pos (psx, psy)
                xsize 120 ysize 120
                action NullAction()
                tooltip pc.name
                background None
                
                add Transform(pc.td_sprite, zoom=0.35, rotate=td_manager.player_rotation, subpixel=True) align (0.5, 0.5)
    
    # 5. UI Layers (Location Name, Dashboard)
    frame:
        align (0.5, 0.02)
        background "#00000088"
        padding (20, 8)
        text "[location.name]" size 28 color "#ffffff"
    
    frame:
        align (0.02, 0.98)
        background "#000a"
        padding (10, 10)
        hbox:
            spacing 10
            textbutton "📱 PHONE" action Show("phone_router") text_size 24 text_color "#00bfff"
            textbutton "DEV" action Show("dev_mode_screen") text_size 14 text_color "#ff3333"

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
