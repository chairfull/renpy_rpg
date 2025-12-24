init python:
    # Helper to constrain tooltip to screen bounds
    def clamp_val(val, minv, maxv):
        return max(min(val, maxv), minv)

    def update_mouse_pos(tf, st, at):
        mx, my = renpy.get_mouse_pos()
        # Constrain to screen options, assuming 1920x1080 default
        mx = clamp_val(mx, 0, 1920) 
        my = clamp_val(my, 0, 1080)
        
        # Offset slightly so it doesn't obstruct cursor interaction
        tf.pos = (mx + 20, my + 20)
        
        # Aggressively restart interaction to keep tooltip movement smooth
        # during heavy top-down processing
        renpy.restart_interaction()
        return 0

transform mouse_pos:
    function update_mouse_pos

transform tooltip_fade:
    alpha 0.0 zoom 0.95
    on show:
        easein 0.15 alpha 1.0 zoom 1.0
    on hide:
        easeout 0.15 alpha 0.0 zoom 0.95
    
screen mouse_tooltip:
    $ tt = GetTooltip()
    if tt:
        frame at mouse_pos, tooltip_fade:
            # PURE VISUAL: Do not intercept mouse events
            mouse_transparent True
            unfocusable True
            
            padding (10, 5)
            background "#000000aa" # Semi-transparent black
            
            # Simple text rendering
            text "[tt!t]": # !t for Title Case if desired, or just [tt]
                size 18
                color "#fff"
                outlines [(1, "#000", 0, 0)]
                align (0.5, 0.5)