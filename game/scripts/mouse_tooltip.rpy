init python:
    # Helper to constrain tooltip to screen bounds
    def clamp_val(val, minv, maxv):
        return max(min(val, maxv), minv)

    # State for the tooltip fade
    tooltip_alpha = 0.0
    last_tt = ""

    def update_mouse_pos(tf, st, at):
        mx, my = renpy.get_mouse_pos()
        tf.pos = (mx + 30, my + 30)
        return 0

    def tooltip_alpha_manager(tf, st, at):
        global tooltip_alpha, last_tt
        tt = GetTooltip()
        
        # Target alpha
        target_a = 1.0 if tt else 0.0
        
        # Smooth lerp for alpha
        # 0.1s fade (10.0 multiplier)
        if tooltip_alpha < target_a:
            tooltip_alpha = min(target_a, tooltip_alpha + 10.0 * 0.016)
        elif tooltip_alpha > target_a:
            tooltip_alpha = max(target_a, tooltip_alpha - 10.0 * 0.016)
            
        # Keep the text while fading out
        if tt:
            last_tt = tt
            
        tf.alpha = tooltip_alpha
        # Return 0 to keep updating as fast as possible
        return 0

transform mouse_pos:
    function update_mouse_pos

transform tooltip_master_fade:
    function tooltip_alpha_manager

screen mouse_tooltip():
    zorder 101
    
    $ tt = GetTooltip()
    # We always render the frame, but control visibility via the transform
    # This prevents 'showif' from instantly destroying the child
    fixed at mouse_pos, tooltip_master_fade:
        # Only show the box if alpha > 0
        if tooltip_alpha > 0.01:
            frame:
                background Solid("#000a")
                padding (12, 8)
                xsize 200
                
                text "[last_tt]":
                    size 20
                    color "#fff"
                    outlines [(1, "#000", 0, 0)]
                    align (0.5, 0.5)
                    text_align 0.5