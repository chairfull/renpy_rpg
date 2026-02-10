default td_zoom = 1.0
default show_reachability = False
default td_update_dt = 1.0 / 60.0

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
    if location is None:
        text "Loading..." align (0.5, 0.5)
    zorder 10
    on "show" action [Function(td_manager.setup, location), SetVariable("tooltip_restart_min_dt", 0.02), SetVariable("tooltip_use_raw_mouse", True), SetVariable("tooltip_offset_x", 0), SetVariable("tooltip_offset_y", 0), SetVariable("tooltip_force_refresh", True)]
    on "hide" action [SetVariable("tooltip_restart_min_dt", 0.08), SetVariable("tooltip_use_raw_mouse", False), SetVariable("tooltip_offset_x", 18), SetVariable("tooltip_offset_y", 18), SetVariable("tooltip_force_refresh", False)]
    
    # Zoom Controls
    key "K_PLUS" action If(phone_state == "mini", SetVariable("td_zoom", min(2.5, td_zoom + 0.1)), NullAction())
    key "K_EQUALS" action If(phone_state == "mini", SetVariable("td_zoom", min(2.5, td_zoom + 0.1)), NullAction())
    key "K_MINUS" action If(phone_state == "mini", SetVariable("td_zoom", max(0.5, td_zoom - 0.1)), NullAction())
    key "mousedown_4" action If(phone_state == "mini", SetVariable("td_zoom", min(2.5, td_zoom + 0.1)), NullAction())
    key "mousedown_5" action If(phone_state == "mini", SetVariable("td_zoom", max(0.5, td_zoom - 0.1)), NullAction())
    key "c" action Function(td_manager.snap_camera)
    key "h" action ToggleVariable("show_reachability")
    
    # Update Loop - Paused when phone is open
    timer td_update_dt repeat True action [
        If(map_ui_active or phone_state != "mini",
            Function(_td_noop),
            [Function(td_manager.update, td_update_dt), Function(_td_update_hover_tooltip)]
        )
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
                
                $ h_anchor = getattr(entity, "hit_anchor", (0.5, 0.5))
                $ h_size = getattr(entity, "hit_size", (120, 120))
                button:
                    anchor h_anchor
                    pos (sx, sy)
                    xsize h_size[0]
                    ysize h_size[1]
                    action Function(_td_click_entity, entity)
                    tooltip entity.tooltip
                    hovered Function(set_tooltip, entity.tooltip)
                    unhovered Function(set_tooltip, None)
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
                                    
                                    # Quest Highlight
                                    $ guidance = quest_manager.get_current_guidance()
                                    if guidance and entity.id in guidance.get('objects', []):
                                        add "images/ui/quest_marker.png" at quest_pulse yoffset -100 align (0.5, 0.5)

    
    # 5. UI Layers (Location Name, Dashboard)
    frame:
        align (0.5, 0.02)
        background "#00000088"
        padding (20, 8)
        textbutton "[location.name]":
            action [SetVariable("phone_current_app", "map"), SetVariable("phone_transition", "to_landscape")]
            text_size 28
            text_color "#ffffff"
            text_hover_color "#ffd700"
            background None
            hover_background None
    
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
            textbutton "DEV" action Show("dev_mode_screen") text_size 14 text_color "#ff3333"
            textbutton "CENTER" action Function(td_manager.snap_camera) text_size 12 text_color "#ccc"
            textbutton "SEARCH" action Function(scavenge_location, location) text_size 12 text_color "#ccc"

    # 6. Phone UI
    use phone_router

# Idle breathing animation (Removed zoom pulse as per user request)
transform char_idle_anim:
    subpixel True
    anchor (0.5, 0.5)
    parallel:
        ease 1.5 rotate -1.5
        ease 1.5 rotate 1.5
        repeat

init python:
    import math
    def _td_noop():
        return None
    def _td_update_hover_tooltip():
        if phone_state != "mini":
            set_tooltip(None)
            return
        try:
            mx, my = renpy.get_mouse_pos()
        except Exception:
            set_tooltip(None)
            return
        zoom = getattr(store, "td_zoom", 1.0)
        wx, wy = td_manager.screen_to_world(mx, my, zoom)
        nearest = None
        nearest_dist = None
        for ent in td_manager.entities:
            dx = ent.x - wx
            dy = ent.y - wy
            h_anchor = getattr(ent, "hit_anchor", (0.5, 0.5))
            h_size = getattr(ent, "hit_size", (120, 120))
            cx = ent.x + (0.5 - h_anchor[0]) * h_size[0]
            cy = ent.y + (0.5 - h_anchor[1]) * h_size[1]
            dist = math.hypot(wx - cx, wy - cy)
            radius = max(h_size[0], h_size[1]) * 0.5
            if dist <= radius and (nearest_dist is None or dist < nearest_dist):
                nearest = ent
                nearest_dist = dist
        if nearest and nearest.tooltip:
            set_tooltip(nearest.tooltip)
        else:
            set_tooltip(None)

    def _td_click_to_move():
        zoom = getattr(store, "td_zoom", 1.0)
        mx, my = renpy.get_mouse_pos()
        wx, wy = td_manager.screen_to_world(mx, my, zoom)
        # If click is near an interactable, auto-approach and interact.
        nearest = None
        nearest_dist = 1e9
        for ent in td_manager.entities:
            if ent.is_player:
                continue
            dx = ent.x - wx
            dy = ent.y - wy
            dist = math.hypot(dx, dy)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = ent
        if nearest and nearest_dist <= 120:
            _td_click_entity(nearest)
        else:
            td_manager.set_target(wx, wy)
