## Compact Quest Panel - shows active quest and next goal/progress
screen quest_panel():
    # overlay, small z-order so it sits above map but below full-screen UI
    zorder 80
    $ active = quest_manager.get_active_quest()
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
                        action Function(renpy.show_screen, "phone_tasks_fullscreen")
                        xminimum 80
                    textbutton "Set Active":
                        action Function(quest_manager.set_active_quest, active.id)
                        xminimum 80
