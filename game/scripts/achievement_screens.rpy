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
                text "[ach.name]" size 28 color "[ach.color]" bold True
                text "[ach.description]" size 16 color "#aaaaaa"
                hbox:
                    spacing 10
                    text "[ach.rarity!u]" size 14 color "[ach.color]"
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
        
        hbox:
            spacing 20
            
            # Achievement List
            frame:
                background "#222"
                xsize 400
                ysize 550
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    vbox:
                        spacing 5
                        # Unlocked achievements first
                        for ach in ach_mgr.get_unlocked():
                            button:
                                action SetVariable("selected_achievement", ach)
                                xfill True
                                background ("#333" if globals().get("selected_achievement") == ach else "#222")
                                hover_background "#444"
                                padding (10, 8)
                                hbox:
                                    spacing 10
                                    text "[ach.icon]" size 22
                                    text "[ach.name]" size 18 color "[ach.color]"
                                    text "✓" size 18 color "#50fa7b" xalign 1.0
                        
                        # Separator if there are both unlocked and locked
                        if ach_mgr.get_unlocked() and ach_mgr.get_locked():
                            null height 10
                            text "— LOCKED —" xalign 0.5 size 14 color "#666"
                            null height 10
                        
                        # Locked achievements
                        for ach in ach_mgr.get_locked():
                            button:
                                action SetVariable("selected_achievement", ach)
                                xfill True
                                background ("#333" if globals().get("selected_achievement") == ach else "#1a1a1a")
                                hover_background "#333"
                                padding (10, 8)
                                hbox:
                                    spacing 10
                                    text "🔒" size 22 color "#666"
                                    text "[ach.name]" size 18 color "#666"
            
            # Achievement Details
            frame:
                background "#222"
                xsize 620
                ysize 550
                padding (25, 25)
                
                if globals().get("selected_achievement"):
                    $ a = selected_achievement
                    $ unlocked = ach_mgr.is_unlocked(a.id)
                    
                    vbox:
                        spacing 15
                        
                        # Header with icon and status
                        hbox:
                            spacing 20
                            frame:
                                background Frame(a.color + "30" if unlocked else "#33333330", 8, 8)
                                padding (20, 20)
                                text "[a.icon]" size 60
                            
                            vbox:
                                spacing 5
                                text "[a.name]" size 32 color (a.color if unlocked else "#666666")
                                hbox:
                                    spacing 10
                                    text "[a.rarity!u]" size 18 color (a.color if unlocked else "#555")
                                    text "•" size 18 color "#444"
                                    text "[a.points] points" size 18 color ("#ffd700" if unlocked else "#555")
                        
                        null height 10
                        
                        # Description
                        text "[a.description]" size 20 color ("#ffffff" if unlocked else "#888888")
                        
                        null height 20
                        
                        # Status
                        if unlocked:
                            hbox:
                                spacing 10
                                text "✓" size 24 color "#50fa7b"
                                text "UNLOCKED" size 20 color "#50fa7b" bold True
                        else:
                            hbox:
                                spacing 10
                                text "🔒" size 24 color "#666"
                                text "LOCKED" size 20 color "#666" bold True
                else:
                    text "Select an achievement to view details." align (0.5, 0.5) color "#666666"
