init python:
    def select_quest_origin(origin):
        global quest_origin
        quest_origin = origin.id
        origin.start()
        renpy.hide_screen("quest_origin_select_screen")
        # renpy.jump("world_loop_start")

screen quest_origin_select_screen():
    modal True
    zorder 150
    
    python:
        from classes import Quest
    
    button:
        action NullAction()
        background Solid("#000000cc")
    
    vbox:
        align (0.5, 0.5)
        spacing 100
        
        text "CHOOSE STORY [len(Quest.get_quests())]" size 32 color "#ffd700" xalign 0.5
        
        hbox:
            spacing 40
            xalign 0.5
            
            for origin in Quest.get_origins():
                button:
                    background Frame("#1b1b2f", 8, 8)
                    xsize 420
                    ysize 720
                    padding (0, 0)
                    at button_hover_effect
                    action [Function(select_quest_origin, origin), Return()]
                    
                    fixed:
                        if origin.image:
                            add origin.image:
                                fit "contain"
                                align (0.5, 1.0)
                        
                        frame:
                            align (0.5, 1.0)
                            # background Frame(Solid("#00000088"), 4, 4)
                            padding (20, 15)
                            xsize 380
                            
                            vbox:
                                spacing 10
                                text "[origin.desc]" size 22 color "#ffffff" xalign 0.5 text_align 0.5 outlines [(1, "#000", 0, 0)]

                        frame:
                            background None
                            padding (20, 30)
                            xfill True
                            text "[origin.name!u]" size 40 color "#ffd700" xalign 0.5 outlines [(3, "#000", 0, 0)]

# Compact Quest Panel - shows active quest and next goal/progress
screen quest_hud():
    # overlay, small z-order so it sits above map but below full-screen UI
    zorder 80
    $ active = active_quest
    if active and active.state == 'active':
        $ next_tick = quest_next_tick(active)
        frame:
            xalign 0.5
            yalign 0.06
            background Frame(Solid("#0f141bcc"), 10, 10)
            padding (12, 8)
            xmaximum 760
            hbox:
                spacing 16
                vbox:
                    spacing 4
                    text active.name size 18 color "#ffd700" slow_cps None
                    if next_tick:
                        text next_tick.name size 14 color "#c9d3dd" slow_cps None
                        if getattr(next_tick, 'required_value', None) and getattr(next_tick, 'current_value', None) is not None:
                            $ cur = float(next_tick.current_value or 0.0)
                            $ req = float(next_tick.required_value or 1.0)
                            bar value (cur/ max(1.0, req)) xmaximum 220 yminimum 8
                            text "[int(cur)]/[int(req)]" size 12 color "#c9d3dd"
                hbox:
                    spacing 8
                    textbutton "Details":
                        action Function(renpy.show_screen, "quests_screen")
                        xminimum 80
                    textbutton "Set Active":
                        action Function(quest_manager.set_active_quest, active.id)
                        xminimum 80