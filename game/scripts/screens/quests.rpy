init -1000 python:
    def _finish_origin_selection(origin):
        GAME_STARTED.emit(origin=origin)

        renpy.hide_screen("story_select_screen")
        # Auto-start quest if ID matches origin
        if origin.id in quest_manager.quests:
            quest_manager.start_quest(origin.id)
        else:
            renpy.notify("Origin quest not found; starting world loop.")
        
        renpy.transition(fade)
        renpy.jump("world_loop")

## Compact Quest Panel - shows active quest and next goal/progress
screen quest_panel():
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

screen story_select_screen():
    modal True
    zorder 150
    # Background dismissal
    button:
        action Return(None)
        background Solid("#000000cc")
    
    vbox:
        align (0.5, 0.5)
        spacing 100
        
        text "CHOOSE YOUR ORIGIN" size 60 color "#ffd700" xalign 0.5
        
        hbox:
            spacing 40
            xalign 0.5
            
            $ origins = quest_manager.get_origins()
            
            for origin in origins:
                button:
                    background Frame("#1b1b2f", 8, 8)
                    xsize 420
                    ysize 720
                    padding (0, 0)
                    at button_hover_effect
                    action Function(_finish_origin_selection, origin)
                    
                    fixed:
                        # 1. Full-size character sprite at absolute bottom
                        if origin.image:
                            add origin.image:
                                fit "contain"
                                align (0.5, 1.0)
                        
                        # 2. Description Overlay at the bottom
                        frame:
                            align (0.5, 0.95) # Anchored towards bottom
                            background Frame(Solid("#00000088"), 4, 4)
                            padding (20, 15)
                            xsize 380
                            
                            vbox:
                                spacing 10
                                text "[origin.desc]" size 22 color "#ffffff" xalign 0.5 text_align 0.5 outlines [(1, "#000", 0, 0)]

                        # 3. Title at the Top (Drawn LAST to be on TOP)
                        frame:
                            background None
                            padding (20, 30)
                            xfill True
                            text "[origin.name!u]" size 40 color "#ffd700" xalign 0.5 outlines [(3, "#000", 0, 0)]
                        # Just show description
