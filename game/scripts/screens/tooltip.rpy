init python:
    class _TooltipState:
        def __init__(self):
            self.alpha    = 0.0
            self.text     = ""
            self.position = (0.0, 0.0)

        def update(self, tf, st, at):
            tx, ty  = self.position
            talpha  = self.alpha
            ttext   = self.text

            mx, my = renpy.get_mouse_pos()
            tx = lerp(tx, mx, 0.25)
            ty = lerp(ty, my, 0.25)
            cw, ch = tf.child_size
            sw, sh = config.screen_width, config.screen_height
            px, py = 16, 16 # Padding from screen edges

            tt = GetTooltip()
            if tt:
                if ttext != tt:
                    ttext = tt
                    tx, ty = mx, my # Jump to mouse immediately on tooltip change
                talpha = lerp(talpha, 1.0, 0.25)
            else:
                talpha = lerp(talpha, 0.0, 0.25)
            
            tx = clamp(tx, px, sw - cw - px)
            ty = clamp(ty, py, sh - ch - py)
            tf.pos = (int(tx), int(ty))
            tf.alpha = talpha
            tf.subpixel = True

            # Remember for next tick
            self.position = (tx, ty)
            self.alpha    = talpha
            self.text     = ttext
            return 0
    
    _tt = _TooltipState()

screen tooltip_screen:
    frame at Transform(function=_tt.update):
        offset (16, 16)
        vbox:
            if _tt.text:
                text "[_tt.text!ti]":
                    align (0.5, 0.5)
                    size 16
                    color "#fff"
                    # outlines text_outlines()
