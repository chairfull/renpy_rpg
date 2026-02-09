default tooltip_manual = ""
default tooltip_active = False
default tooltip_alpha = 1.0
default tooltip_last = ""
default tooltip_current = ""
default tooltip_restart_last_t = 0.0
default tooltip_restart_min_dt = 0.08
default tooltip_pos_x = 0.0
default tooltip_pos_y = 0.0
default mouse_raw_x = 0.0
default mouse_raw_y = 0.0
default mouse_smooth_x = 0.0
default mouse_smooth_y = 0.0
default mouse_smooth_inited = False
default mouse_smooth_lerp = 0.35
default tooltip_use_raw_mouse = False
default tooltip_offset_x = 18
default tooltip_offset_y = 18
default tooltip_force_refresh = False
default tooltip_force_last_t = 0.0
default tooltip_force_min_dt = 0.05
default tooltip_hover_last_x = 0.0
default tooltip_hover_last_y = 0.0
default tooltip_hover_last_t = 0.0

init -20 python:
    def set_tooltip(text, refresh=True):
        text = text or ""
        if store.tooltip_manual != text:
            store.tooltip_manual = text
            if refresh:
                try:
                    now = renpy.get_time()
                    last = getattr(store, "tooltip_restart_last_t", 0.0)
                    min_dt = getattr(store, "tooltip_restart_min_dt", 0.08)
                    if now - last >= min_dt:
                        store.tooltip_restart_last_t = now
                        renpy.restart_interaction()
                except Exception:
                    pass
    
    def tooltip_alpha_tick():
        return
    
    def _mouse_smooth_tick():
        try:
            mx, my = renpy.get_mouse_pos()
        except Exception:
            return
        if mx is None or my is None:
            return
        store.mouse_raw_x = mx
        store.mouse_raw_y = my
        if not store.mouse_smooth_inited:
            store.mouse_smooth_x = mx
            store.mouse_smooth_y = my
            store.mouse_smooth_inited = True
        else:
            lerp = getattr(store, "mouse_smooth_lerp", 0.35)
            store.mouse_smooth_x += (mx - store.mouse_smooth_x) * lerp
            store.mouse_smooth_y += (my - store.mouse_smooth_y) * lerp

    def tooltip_hover_tick():
        try:
            mx, my = renpy.get_mouse_pos()
        except Exception:
            return
        if mx is None or my is None:
            return
        if mx == store.tooltip_hover_last_x and my == store.tooltip_hover_last_y:
            return
        store.tooltip_hover_last_x = mx
        store.tooltip_hover_last_y = my
        try:
            now = renpy.get_time()
        except Exception:
            now = 0.0
        if now - store.tooltip_hover_last_t < 0.05:
            return
        store.tooltip_hover_last_t = now
        try:
            renpy.restart_interaction()
        except Exception:
            pass

    def tooltip_force_tick():
        if not store.tooltip_force_refresh:
            return
        try:
            now = renpy.get_time()
        except Exception:
            now = 0.0
        last = getattr(store, "tooltip_force_last_t", 0.0)
        min_dt = getattr(store, "tooltip_force_min_dt", 0.05)
        if now - last < min_dt:
            return
        store.tooltip_force_last_t = now
        try:
            renpy.restart_interaction()
        except Exception:
            pass

init -2 python:
    if "mouse_tracker" not in config.overlay_screens:
        config.overlay_screens.append("mouse_tracker")
    if "mouse_tooltip" not in config.overlay_screens:
        config.overlay_screens.append("mouse_tooltip")

init python:
    # Helper to constrain tooltip to screen bounds
    def clamp_val(val, minv, maxv):
        return max(min(val, maxv), minv)

screen mouse_tracker():
    layer "overlay"
    zorder 100001
    modal False
    timer 0.016 repeat True action Function(_mouse_smooth_tick)
    timer 0.05 repeat True action Function(tooltip_hover_tick)
    python:
        sw = config.screen_width
        sh = config.screen_height
        use_raw = bool(getattr(store, "tooltip_use_raw_mouse", False))
        ox = int(getattr(store, "tooltip_offset_x", 18))
        oy = int(getattr(store, "tooltip_offset_y", 18))
        if use_raw or not store.mouse_smooth_inited:
            _sx = clamp_val(int(mouse_raw_x) + ox, 0, max(0, sw - 28))
            _sy = clamp_val(int(mouse_raw_y) + oy, 0, max(0, sh - 28))
        else:
            _sx = clamp_val(int(mouse_smooth_x) + ox, 0, max(0, sw - 28))
            _sy = clamp_val(int(mouse_smooth_y) + oy, 0, max(0, sh - 28))
        store.tooltip_pos_x = _sx
        store.tooltip_pos_y = _sy
    # Debug cursor boxes (commented out, keep for quick re-enable)
    # frame:
    #     pos (mouse_raw_x, mouse_raw_y)
    #     xsize 20
    #     ysize 20
    #     background Solid("#00e5ff")
    #     at Transform(alpha=0.9)
    # frame:
    #     pos (_sx, _sy)
    #     xsize 28
    #     ysize 28
    #     background Solid("#ff00ff")
    #     at Transform(alpha=0.9)

screen mouse_tooltip():
    layer "overlay"
    zorder 100000
    modal False
    default debug_tt = False
    key "K_F9" action ToggleScreenVariable("debug_tt")
    timer 0.05 repeat True action Function(tooltip_force_tick)
    $ _map_active = renpy.store.__dict__.get("map_ui_active", False)
    $ tt = tooltip_manual or GetTooltip() or (map_manager.hover_tooltip if _map_active else "")
    $ tooltip_current = tt
    $ _pos = renpy.get_mouse_pos()
    $ _mx = _pos[0] if _pos and _pos[0] is not None else mouse_raw_x
    $ _my = _pos[1] if _pos and _pos[1] is not None else mouse_raw_y
    $ _ox = int(getattr(store, "tooltip_offset_x", 18))
    $ _oy = int(getattr(store, "tooltip_offset_y", 18))
    $ _sx = clamp_val(int(_mx) + _ox, 0, max(0, config.screen_width - 28))
    $ _sy = clamp_val(int(_my) + _oy, 0, max(0, config.screen_height - 28))
    if tt:
        frame:
            pos (_sx, _sy)
            background Solid("#000c")
            padding (12, 8)
            text "[tt]":
                size 20
                color "#fff"
                outlines [(1, "#000", 0, 0)]
    
    if debug_tt:
        frame:
            pos (10, 10)
            xsize 20
            ysize 20
            background Solid("#00ff00")
            at Transform(alpha=0.8)
        frame:
            align (0.02, 0.02)
            background Solid("#000a")
            padding (8, 6)
            vbox:
                spacing 4
                text "TT: [tooltip_current!r]" size 14 color "#fff"
                text "LEN: [len(tooltip_current)]" size 14 color "#ffd700"
                text "MANUAL: [tooltip_manual!r]" size 14 color "#9bb2c7"
                text "ACTIVE: [bool(tooltip_current)]" size 14 color "#c9d3dd"
                text "ALPHA: [1.0]" size 14 color "#ffd700"
                text "POS: [tooltip_pos_x:.1f], [tooltip_pos_y:.1f]" size 14 color "#9bb2c7"
                text "RAW: [mouse_raw_x:.1f], [mouse_raw_y:.1f]" size 14 color "#9bb2c7"
                text "SMOOTH: [mouse_smooth_x:.1f], [mouse_smooth_y:.1f]" size 14 color "#9bb2c7"
                text "RES: [config.screen_width]x[config.screen_height]" size 14 color "#888"
