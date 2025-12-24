init python:
    def update_mouse_pos(tf, st, at):
        mx, my = renpy.get_mouse_pos()
        mx = clamp(mx, 64, 1920)
        my = clamp(my, 0, 1080-128)
        tf.pos = (mx, my)
        return 0

transform mouse_pos:
    function update_mouse_pos
    
screen mouse_tooltip:
    $ tt = GetTooltip()
    if tt:
        frame at mouse_pos:
            offset (0, 64)
            align (0.25, 0.5)
            vbox:
                text "[tt!ti]":
                    align (0.5, 0.5)
                    color "#fff"
                    outlines get_outlines()