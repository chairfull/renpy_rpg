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
                    rpg_world.move_to(renpy.store.pc.location_id)
        # Core origin bootstrapping lives here.
        flag_set("origin", origin.id)
        event_manager.dispatch("GAME_STARTED", origin=origin.id)

        renpy.hide_screen("story_select_screen")
        # Auto-start quest if ID matches origin
        if origin.id in quest_manager.quests:
            quest_manager.start_quest(origin.id)
        else:
            renpy.notify("Origin quest not found; starting world loop.")
        
        renpy.transition(fade)
        renpy.jump("world_loop")

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
                    ysize 720 # Made slightly taller
                    padding (0, 0)
                    at phone_visual_hover
                    action Function(finish_story_selection, origin)
                    
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
                                text "[origin.description]" size 22 color "#ffffff" xalign 0.5 text_align 0.5 outlines [(1, "#000", 0, 0)]

                        # 3. Title at the Top (Drawn LAST to be on TOP)
                        frame:
                            background None
                            padding (20, 30)
                            xfill True
                            text "[origin.name!u]" size 40 color "#ffd700" xalign 0.5 outlines [(3, "#000", 0, 0)]
                        # Just show description
