screen top_down_map(location):
    # No longer modal as it's the primary screen
    tag world_view
    
    # Update Loop
    timer 0.016 repeat True action Function(td_manager.update, 0.016)
    
    # Camera container - all world elements are offset by camera
    fixed:
        # Background Map (offset by camera)
        $ cam_x = int(td_manager.camera_offset[0])
        $ cam_y = int(td_manager.camera_offset[1])
        
        if location.map_image:
            add location.map_image:
                pos (-cam_x, -cam_y)
        else:
            add Solid("#222"):
                pos (-cam_x, -cam_y)
        
        # Click to Move (convert screen coords to world coords)
        button:
            area (0, 0, 1920, 1080)
            action Function(_td_click_to_move)
            background None
        
        # Unified Entities Rendering
        for entity in td_manager.entities:
            $ ent_screen_pos = td_manager.world_to_screen(entity.x, entity.y)
            
            imagebutton:
                anchor (0.5, 0.5)
                pos (int(ent_screen_pos[0]), int(ent_screen_pos[1]))
                action entity.action
                mouse "gamemenu"
                
                # Sprite Logic
                if entity.sprite_tint:
                    # Tinte sprites (e.g. Exits)
                    idle Transform(entity.sprite, zoom=0.3, matrixcolor=entity.sprite_tint)
                    hover Transform(entity.sprite, zoom=0.35, matrixcolor=entity.sprite_tint)
                else:
                    # Regular sprites (NPCs, Objects)
                    if entity.idle_anim:
                        idle At(Transform(entity.sprite, zoom=0.3), char_idle_anim)
                        hover At(Transform(entity.sprite, zoom=0.33), char_idle_anim) # Slight zoom on hover
                    else:
                        idle Transform(entity.sprite, zoom=0.3)
                        hover Transform(entity.sprite, zoom=0.33)
                
                if entity.tooltip:
                    hovered Notify(entity.tooltip)

        # Player Sprite (with rotation)
        $ player_screen_pos = td_manager.world_to_screen(td_manager.player_pos[0], td_manager.player_pos[1])
        add Transform("images_topdown/chars/theo.png", zoom=0.35, rotate=td_manager.player_rotation, subpixel=True):
            anchor (0.5, 0.5)
            pos (int(player_screen_pos[0]), int(player_screen_pos[1]))
    
    # UI Overlays (fixed position, not affected by camera)
    
    # Location name (top center)
    frame:
        align (0.5, 0.02)
        background "#00000088"
        padding (20, 8)
        text "[location.name]" size 28 color "#ffffff"
    
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

    # Path Debugging (in screen space)
    if td_manager.path:
        for wx, wy in td_manager.path:
            $ path_screen_pos = td_manager.world_to_screen(wx, wy)
            add Solid("#ffff00", xsize=4, ysize=4):
                pos (int(path_screen_pos[0])-2, int(path_screen_pos[1])-2)

    # DEBUG OVERLAY
    frame:
        align (0.95, 0.05)
        background "#000000aa"
        vbox:
            text "DEBUG INFO" size 20 color "#f00"
            text f"Entities: {len(td_manager.entities)}" size 18 color "#fff"

            for i, e in enumerate(td_manager.entities[:5]):
                $ sx, sy = td_manager.world_to_screen(e.x, e.y)
                text f"[{i}] {e.tooltip}: ({e.x},{e.y})" size 16 color "#aaa"
            text f"Player: ({int(td_manager.player_pos[0])}, {int(td_manager.player_pos[1])})" size 16 color "#aaa"
            text f"CamOffset: ({int(td_manager.camera_offset[0])}, {int(td_manager.camera_offset[1])})" size 16 color "#aaa"


# Idle breathing animation for characters (NPCs)
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
        """Handle click-to-move, converting screen coords to world coords"""
        mx, my = renpy.get_mouse_pos()
        wx, wy = td_manager.screen_to_world(mx, my)
        td_manager.set_target(wx, wy)
