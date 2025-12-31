# Character selection screen at the start of the game

screen character_select_screen():
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
            
            $ archetypes = archetype_manager.get_all()
            
            for arch in archetypes:
                frame:
                    background Frame("#1a1a1a", 8, 8)
                    xsize 400
                    ysize 600
                    padding (30, 30)
                    
                    vbox:
                        spacing 20
                        
                        text "[arch.name]" size 36 color "#fff" xalign 0.5
                        
                        null height 10
                        
                        text "[arch.description]" size 20 color "#ccc" justify True
                        
                        null height 20
                        
                        # Show some key stats
                        vbox:
                            spacing 5
                            for s_name, s_val in arch.stats.items():
                                if s_name in ["strength", "dexterity", "intelligence", "charisma"]:
                                    hbox:
                                        text "[s_name!c]:" size 18 color "#888"
                                        text " [s_val]" size 18 color "#fff" xalign 1.0
                        
                        null height 20
                        
                        textbutton "CHOOSE":
                            action [
                                Function(pc.apply_archetype, arch),
                                Hide("character_select_screen"),
                                Jump(arch.intro_label)
                            ]
                            xalign 0.5
                            padding (40, 15)
                            background "#2a2a2a"
                            hover_background "#4a4a4a"
                            text_size 24
                            at phone_visual_hover
