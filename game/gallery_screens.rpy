screen gallery_screen():
    modal True
    add Solid("#000b")

    vbox:
        align (0.5, 0.5)
        spacing 20
        text "Gallery & Achievements" size 50

        hbox:
            spacing 50
            # Achievement List
            vbox:
                label "Achievements"
                viewport id "achievement_vp":
                    mousewheel True
                    draggable True
                    scrollbars "vertical"
                    xsize 300 ysize 400
                    vbox:
                        # We would ideally have a list of all possible achievements to show locked ones too
                        if not persistent.achievements:
                            text "None yet!"
                        else:
                            for ach in sorted(list(persistent.achievements)):
                                text "[ach]" size 18 color "#fff"

            # Scene List
            vbox:
                label "Unlocked Scenes"
                viewport id "scene_vp":
                    mousewheel True
                    draggable True
                    scrollbars "vertical"
                    xsize 300 ysize 400
                    vbox:
                        if not persistent.unlocked_scenes:
                            text "Explore the world to unlock scenes!"
                        else:
                            for scene_id in sorted(list(persistent.unlocked_scenes)):
                                if scene_id in scene_manager.scenes:
                                    $ sc = scene_manager.scenes[scene_id]
                                    textbutton "[sc.name]" action Function(scene_manager.play, scene_id)

        textbutton "Close" action Hide("gallery_screen") align (0.5, 1.0)

# Add skip button to a generic scene screen if needed, 
# or just add to the dialogue screen.
screen scene_skip(end_label):
    textbutton "Skip Scene" action Jump(end_label) align (0.95, 0.95)
