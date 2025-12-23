default gallery_tab = "achievements"

screen gallery_screen():
    modal True
    add Solid("#000000da") # Dark glassy background

    vbox:
        align (0.5, 0.4)
        spacing 10
        xsize 1000 ysize 700
        
        frame:
            background Frame(Solid("#222"), 4, 4)
            padding (20, 20)
            
            vbox:
                spacing 20
                text "Compendium":
                    size 50 
                    xalign 0.5 
                    at transform:
                        alpha 0.0
                        linear 0.5 alpha 1.0

                # Tab Buttons
                hbox:
                    xalign 0.5
                    spacing 10
                    textbutton "Achievements":
                        action SetScreenVariable("gallery_tab", "achievements")
                        selected (gallery_tab == "achievements")
                        text_size 24
                    textbutton "Scenes":
                        action SetScreenVariable("gallery_tab", "scenes")
                        selected (gallery_tab == "scenes")
                        text_size 24
                    textbutton "Characters":
                        action SetScreenVariable("gallery_tab", "wiki")
                        selected (gallery_tab == "wiki")
                        text_size 24

                # Content Area
                frame:
                    background Solid("#333")
                    padding (10, 10)
                    xfill True yfill True
                    
                    if gallery_tab == "achievements":
                        use achievement_view()
                    elif gallery_tab == "scenes":
                        use scene_view()
                    elif gallery_tab == "wiki":
                        use wiki_view()

        textbutton "Close" action Hide("gallery_screen") xalign 0.5 text_size 30 text_hover_color "#aaa"

screen achievement_view():
    vbox:
        spacing 10
        label "Tracked Achievements"
        viewport:
            mousewheel True
            draggable True
            scrollbars "vertical"
            vbox:
                if not persistent.achievements:
                    text "Explore more to earn achievements!" color "#888"
                else:
                    for ach in sorted(list(persistent.achievements)):
                        hbox:
                            spacing 10
                            text "★" color "#ffd700"
                            text "[ach]" color "#fff"

screen scene_view():
    vbox:
        spacing 10
        label "Story Gallery"
        viewport:
            mousewheel True
            draggable True
            scrollbars "vertical"
            vbox:
                if not persistent.unlocked_scenes:
                    text "Unlocked scenes will appear here." color "#888"
                else:
                    for scene_id in sorted(list(persistent.unlocked_scenes)):
                        if scene_id in scene_manager.scenes:
                            $ sc = scene_manager.scenes[scene_id]
                            textbutton "[sc.name]":
                                action Function(scene_manager.play, scene_id)
                                text_hover_color "#66ccff"

screen wiki_view():
    vbox:
        spacing 10
        label "Characters & Entities"
        viewport:
            mousewheel True
            draggable True
            scrollbars "vertical"
            vbox:
                if not persistent.met_characters:
                    text "You haven't met anyone interesting yet..." color "#888"
                else:
                    for name, desc in wiki_manager.met_list:
                        vbox:
                            spacing 5
                            text "[name]" size 28 color "#66ccff"
                            text "[desc]" size 18 color "#ccc" xoffset 10
                            null height 10
                            text "____________________" color "#444" size 10

screen scene_skip(end_label):
    textbutton "Skip Scene" action Jump(end_label) align (0.95, 0.95)
