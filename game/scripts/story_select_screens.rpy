# Character selection screen at the start of the game



init python:
    def finish_story_selection(origin):
        # Set global PC from the origin's character ID
        if origin.pc_id:
            char = rpg_world.characters.get(origin.pc_id)
            if char:
                renpy.store.pc = char
                # Ensure starting location is set from character
                if renpy.store.pc.location_id:
                    rpg_world.current_location_id = renpy.store.pc.location_id
        
        renpy.hide_screen("story_select_screen")
        renpy.transition(fade)
        renpy.jump(origin.intro_label)

screen story_select_screen():
    modal True
    zorder 150
    
    add Solid("#000000")
    
    vbox:
        align (0.5, 0.5)
        spacing 100
        
        text "CHOOSE YOUR ORIGIN" size 60 color "#ffd700" xalign 0.5
        
        hbox:
            spacing 40
            xalign 0.5
            
            $ origins = story_origin_manager.get_all()
            
            for origin in origins:
                button:
                    background Frame("#3a3a5a", 8, 8)
                    xsize 400
                    ysize 600
                    padding (30, 30)
                    at phone_visual_hover
                    action Function(finish_story_selection, origin)
                    
                    vbox:
                        spacing 20
                        
                        # Placeholder Preview Image
                        frame:
                            background "#222"
                            xsize 340
                            ysize 200
                            xalign 0.5
                            text "🖼️" size 80 align (0.5, 0.5)
                        
                        text "[origin.name]" size 36 color "#fff" xalign 0.5
                        
                        null height 10
                        
                        text "[origin.description]" size 20 color "#ccc" xalign 0.5 text_align 0.5
                        
                        null height 20
                        
                        # Stats removed from StoryOrigin object
                        # Just show description
