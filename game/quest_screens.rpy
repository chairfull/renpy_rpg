screen quest_log_screen():
    tag menu
    add "#1a1a1a"
    
    vbox:
        align (0.5, 0.5)
        spacing 20
        xsize 1000
        ysize 800
        
        label "Quest Log" xalign 0.5 text_size 40 text_color "#ffffff"
        
        hbox:
            spacing 20
            
            # Quest List
            frame:
                background "#2a2a2a"
                xsize 400
                ysize 600
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    vbox:
                        spacing 5
                        for qid, quest in quest_manager.quests.items():
                            if quest.state != "unknown":
                                textbutton "[quest.name]":
                                    action SetVariable("selected_quest_id", qid)
                                    xfill True
                                    text_color "#ffffff"
                                    background ("#3a3a3a" if quest.state == "active" else "#1a1a1a")
                                    text_size 20

            # Quest Details
            frame:
                background "#2a2a2a"
                xsize 580
                ysize 600
                padding (20, 20)
                
                if globals().get("selected_quest_id") and selected_quest_id in quest_manager.quests:
                    $ q = quest_manager.quests[selected_quest_id]
                    vbox:
                        spacing 15
                        text "[q.name]" size 30 color "#ffd700"
                        text "[q.state.upper()]" size 18 color ("#00ff00" if q.state == "passed" else "#00bfff")
                        text "[q.description]" size 20 #wrap_around True
                        
                        null height 10
                        text "Objectives:" size 22 color "#ffffff"
                        
                        viewport:
                            scrollbars "vertical"
                            mousewheel True
                            vbox:
                                spacing 10
                                for tick in q.ticks:
                                    if tick.state != "hidden":
                                        hbox:
                                            spacing 10
                                            if tick.state == "complete":
                                                text "●" color "#00ff00"
                                            elif tick.state == "active":
                                                text "○" color "#00bfff"
                                            else:
                                                text "○" color "#666666"
                                            
                                            text "[tick.name]" size 18 color ("#ffffff" if tick.state == "active" else "#999999")
                else:
                    text "Select a quest to see details." align (0.5, 0.5) color "#666666"

        textbutton "Back":
            align (0.5, 1.0)
            action Return()
            text_size 25
            background "#444"
            padding (20, 10)

default selected_quest_id = None
