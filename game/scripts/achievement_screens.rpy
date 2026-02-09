# Achievement System UI Screens

default selected_achievement = None

# Beautiful toast notification for achievement unlock
screen achievement_toast(ach):
    zorder 200
    modal False
    
    timer 4.0 action Hide("achievement_toast")
    
    frame:
        at achievement_pop
        align (0.5, 0.1)
        background Frame("#1a1a2e", 8, 8)
        padding (30, 20)
        
        hbox:
            spacing 20
            align (0.5, 0.5)
            
            # Icon with glow effect
            frame:
                background Frame(ach.color + "40", 4, 4)
                padding (15, 15)
                text "[ach.icon]" size 50
            
            vbox:
                spacing 5
                text "ACHIEVEMENT UNLOCKED!" size 18 color "#ffd700" bold True
                text "[ach.name]" size 28 color ach.color bold True
                text "[ach.description]" size 16 color "#aaaaaa"
                hbox:
                    spacing 10
                    text "[ach.rarity!u]" size 14 color ach.color
                    text "+" size 14 color "#ffd700"
                    text "[ach.points] pts" size 14 color "#ffd700"

transform achievement_pop:
    on show:
        alpha 0.0 yoffset -50
        easein 0.5 alpha 1.0 yoffset 0
    on hide:
        easeout 0.3 alpha 0.0 yoffset -30

# Achievements content screen for the menu
screen achievements_content():
    vbox:
        spacing 10
        xfill True
        yfill True

        # Header with points
        hbox:
            xfill True
            text "🏆 Achievements" size 28 color "#ffd700"
            hbox:
                xalign 1.0
                text "Total Points: " size 20 color "#aaa"
                text "[ach_mgr.total_points]" size 24 color "#ffd700" bold True
                text "  |  " size 20 color "#444"
                text "[ach_mgr.progress_text]" size 20 color "#aaa"

        null height 10

        frame:
            background "#222"
            xfill True
            yfill True
            padding (16, 16)
            $ cols = 3
            $ spacing = 16
            $ grid_w = 1600
            $ cell_w = int((grid_w - (cols - 1) * spacing) / cols)
            $ cell_h = 180
            $ unlocked = ach_mgr.get_unlocked()
            $ locked = ach_mgr.get_locked()
            $ all_ach = unlocked + locked
            viewport:
                scrollbars "vertical"
                mousewheel True
                draggable True
                xfill True
                yfill True
                vpgrid:
                    cols cols
                    xspacing spacing
                    yspacing spacing
                    xfill True
                    for ach in all_ach:
                        $ is_unlocked = ach_mgr.is_unlocked(ach.id)
                        $ hint = getattr(ach, "hint", None)
                        button:
                            action SetVariable("selected_achievement", ach)
                            xsize cell_w
                            ysize cell_h
                            background ("#2a2a2a" if is_unlocked else "#1a1a1a")
                            hover_background "#333333"
                            padding (14, 12)
                            vbox:
                                spacing 6
                                hbox:
                                    spacing 10
                                    text (ach.icon if is_unlocked else "🔒") size 28 color (ach.color if is_unlocked else "#666")
                                    vbox:
                                        spacing 2
                                        if is_unlocked:
                                            text "[ach.name]" size 20 color ach.color
                                            text "[ach.rarity!u] • [ach.points] pts" size 14 color "#aaa"
                                        else:
                                            text "?????" size 20 color "#666"
                                            if hint:
                                                text "[hint]" size 14 color "#777"
                                text ("[ach.description]" if is_unlocked else "") size 16 color "#bbb"
