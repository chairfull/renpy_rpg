define config.layers = [ 'master', 'scene', 'transient', 'screens', 'overlay', 'tooltip' ]    
define narr = Character("Narrator")
#region States
default persistent.lore = set[str]
default persistent.awards = set[str]
default persistent.award_ticks = {}
default persistent.lighting_enabled = True
default quest_state = {}
default quest_origin = None # Primary questline. There may be multiple.
default quest_visible = set[str]
default flag_state = {}
default zone_visited = set[str]
default lock_unlocked = set[str]
#endregion
default player = None # Main character reference.
default loop_queue = [] # Labels and screens queued.
default current_scene = None
define null_scene = None

init python:
    import pygame_sdl2 as pg
    from renpy.uguu import (GL_FUNC_ADD, GL_FUNC_SUBTRACT, GL_ONE, GL_ONE_MINUS_SRC_ALPHA, GL_MIN, GL_MAX, GL_ZERO, GL_ONE_MINUS_DST_COLOR,)
    config.gl_blend_func["screen"]    = (GL_FUNC_ADD,      GL_ONE_MINUS_DST_COLOR, GL_ONE, GL_FUNC_ADD, GL_ONE, GL_ONE)
    config.gl_blend_func["lighten"]   = (GL_MAX,            GL_ONE,                 GL_ONE, GL_FUNC_ADD, GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
    config.gl_blend_func["darken"]    = (GL_MIN,            GL_ONE,                 GL_ONE, GL_FUNC_ADD, GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
    config.gl_blend_func["erase"]     = (GL_FUNC_ADD,       GL_ZERO,                GL_ONE, GL_FUNC_ADD, GL_ZERO, GL_ONE_MINUS_SRC_ALPHA)
    config.gl_blend_func["sub"]       = (GL_FUNC_SUBTRACT,  GL_ONE,                 GL_ONE, GL_FUNC_ADD, GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
    config.gl_blend_func["sub_better"]= (GL_FUNC_SUBTRACT,  GL_ONE,                 GL_ONE, GL_FUNC_SUBTRACT, GL_ONE, GL_ONE)


define POPUP_X = 0
define POPUP_Y = 0
define POPUP_W = 500
define POPUP_H = 300

screen frosted_popup():
    $ mx, my = renpy.get_mouse_pos()
    timer 0.01 action Function(renpy.restart_interaction) repeat True

    add Transform(_popup_bg, crop=(mx, my, POPUP_W, POPUP_H)):
        xpos mx
        ypos my

    add Solid("#FFFFFF28"):
        xpos mx  ypos my
        xsize POPUP_W ysize POPUP_H

    frame:
        pos (mx, my)
        xsize POPUP_W ysize POPUP_H
        background None
        padding (30, 30)
        vbox:
            spacing 10
            text "Popup Title"
            text "Some body content here."

label splashscreen:
    python:
        global current_scene, null_scene
        from classes import Scene, SceneDebug
        current_scene = SceneDebug()
        null_scene = Scene()
        renpy.notify("beep boop splashscreen")
    show screen tooltip_screen onlayer tooltip
    return

label start:
    show expression "../game/images/test.jpg"
    pause 1.0
    $ _popup_bg_data = renpy.screenshot_to_bytes((config.screen_width, config.screen_height))
    $ _popup_bg = im.Blur(im.Data(_popup_bg_data, "screenshot.png"), 4)
    call screen frosted_popup
    # # Story selection (Skipped if a quick-start origin was chosen from the main menu)
    # if not quest_origin:
    #     call screen quest_origin_select_screen
    # jump world_loop_start

label world_loop_start:
    show screen scene_screen onlayer scene
    jump world_loop

label world_loop:
    python:
        renpy.notify("Looped")
        if loop_queue:
            qtype, args, kwargs = loop_queue.pop(0)
            if qtype == "label":
                # TODO: Signal dialogue-start so that scene can react and hide/pause.
                renpy.call(args[0], *args[1:], **kwargs)
                # TODO: Signal dialogue-end so that scene can react and show/unpause.
            elif qtype == "screen":
                renpy.show_screen(args[0], *args[1:], **kwargs)
            else:
                raise ValueError(f"Unknown loop queue type: {qtype}")
    pause 5.0 # pause between loop
    jump world_loop
