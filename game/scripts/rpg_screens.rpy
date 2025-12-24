

transform notify_appear:
    on show:
        alpha 0.0 yoffset -20
        linear .25 alpha 1.0 yoffset 0
    on hide:
        linear .5 alpha 0.0 yoffset -20

screen notify(message):
    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        background "#2a2a2a"
        padding (20, 10)
        xalign 0.5
        ypos 50
        
        text "[message!t]":
            color "#ffd700"
            size 20

    timer 3.2 action Hide('notify')



style notify_frame is empty
style notify_text is empty
