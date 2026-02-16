init python:
    tooltip_alpha = 1.0
    tooltip_current = ""
    tooltip_pos = (0.0, 0.0)
    mouse_pos = (0.0, 0.0)

    def _update_mouse_pos(tf, st, at):
        global tooltip_current, tooltip_alpha, tooltip_pos, mouse_pos
        mx, my = renpy.get_mouse_pos()
        mouse_pos = (mx, my)

        tx, ty = tooltip_pos
        tx = lerp(tx, mx, 0.5)
        ty = lerp(ty, my, 0.5)
        cw, ch = tf.child_size
        sw, sh = config.screen_width, config.screen_height
        px, py = 16, 16 # Padding from screen edges

        tt = GetTooltip()
        if tt:
            if tooltip_current != tt:
                tooltip_current = tt
                tx, ty = mx, my # Jump to mouse immediately on tooltip change
            tooltip_alpha = lerp(tooltip_alpha, 1.0, 0.5)
        else:
            tooltip_alpha = lerp(tooltip_alpha, 0.0, 0.5)
            if tooltip_alpha < 0.01:
                tooltip_current = ""
        
        tx = clamp(tx, px, sw - cw - px)
        ty = clamp(ty, py, sh - ch - py)

        tooltip_pos = (tx, ty) # Remember for next tick

        tf.subpixel = True
        tf.pos = (int(tx), int(ty))
        tf.alpha = tooltip_alpha
        return 0

transform _tooltip_follow_mouse:
    function _update_mouse_pos

screen mouse_tooltip:
    timer 0.1 repeat True action Function(renpy.restart_interaction)
    
    frame at _tooltip_follow_mouse:
        offset (32, 32)
        vbox:
            text "[tooltip_current!ti]":
                align (0.5, 0.5)
                size 16
                color "#fff"
                    # outlines get_outlines()
