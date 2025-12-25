screen top_down_map(location):
    tag world_view
    zorder 10
    
    # Update Loop - Stable 30fps for smooth movement and tooltips
    timer 0.033 repeat True action [Function(td_manager.update, 0.033), renpy.restart_interaction]
    
    fixed:
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
                fixed:
                    if entity.sprite_tint:
                        # For colored markers (like exits)
                        add Transform(entity.sprite, zoom=0.3, matrixcolor=entity.sprite_tint) align (0.5, 0.5)
                        if GetTooltip() == entity.tooltip:
                            add Transform(entity.sprite, zoom=0.35, matrixcolor=entity.sprite_tint) align (0.5, 0.5)
                    else:
                        # For characters/objects
                        if entity.idle_anim:
                            add At(Transform(entity.sprite, zoom=0.35), char_idle_anim) align (0.5, 0.5)
                            if GetTooltip() == entity.tooltip:
                                add At(Transform(entity.sprite, zoom=0.38), char_idle_anim) align (0.5, 0.5)
                        else:
                            add Transform(entity.sprite, zoom=0.35) align (0.5, 0.5)
                            if GetTooltip() == entity.tooltip:
                                add Transform(entity.sprite, zoom=0.38) align (0.5, 0.5)

        # 4. Player Sprite
        $ psx = int(td_manager.player_pos[0] - cam_x)
        $ psy = int(td_manager.player_pos[1] - cam_y)
        add Transform("images_topdown/chars/theo.png", zoom=0.35, rotate=td_manager.player_rotation, subpixel=True):
            anchor (0.5, 0.5)
            pos (psx, psy)
    
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
            textbutton "DASHBOARD" action ShowMenu("inventory_screen") text_size 24 text_color "#ffd700"
            textbutton "DEV CONSOLE" action Show("dev_mode_screen") text_size 16 text_color "#ff3333"

    # 6. Tooltip Layer
    use mouse_tooltip

# Idle breathing animation
transform char_idle_anim:
    subpixel True
    anchor (0.5, 0.5)
    parallel:
        ease 1.5 rotate -1.5
        ease 1.5 rotate 1.5
        repeat
    parallel:
        ease 2.0 zoom 1.02
        ease 2.0 zoom 0.98
        repeat

init python:
    def _td_click_to_move():
        mx, my = renpy.get_mouse_pos()
        wx, wy = td_manager.screen_to_world(mx, my)
        td_manager.set_target(wx, wy)
