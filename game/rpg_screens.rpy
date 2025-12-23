screen navigation_screen():
    tag menu
    add "#0a0a0a"
    
    $ loc = rpg_world.current_location
    
    hbox:
        spacing 20
        align (0.5, 0.5)
        
        # Location Info
        frame:
            background "#1a1a1a"
            xsize 400
            ysize 600
            padding (20, 20)
            vbox:
                spacing 10
                text "[loc.name]" size 40 color "#ffffff"
                text "[loc.description]" size 18 color "#cccccc" italic True
                null height 20
                text "Time: [time_manager.time_string]" size 20 color "#ffd700"
                
                null height 30
                text "Available Paths:" size 24 color "#ffffff"
                for dest_id, desc in loc.connections.items():
                    textbutton "[desc]":
                        action Function(rpg_world.move_to, dest_id)
                        text_size 20

        # Entities at location
        frame:
            background "#1a1a1a"
            xsize 400
            ysize 600
            padding (20, 20)
            vbox:
                spacing 10
                text "Interactions:" size 24 color "#ffffff"
                for entity in loc.entities:
                    textbutton "[entity.name]":
                        action Function(entity.interact)
                        text_size 20
                
                for char in loc.characters:
                    textbutton "[char.name]":
                        action Function(char.interact)
                        text_size 20

        # Side Menu
        frame:
            background "#1a1a1a"
            xsize 200
            ysize 600
            padding (10, 10)
            vbox:
                spacing 15
                xfill True
                textbutton "Inventory":
                    action ShowMenu("inventory_screen")
                    xfill True
                textbutton "Character":
                    action ShowMenu("character_sheet")
                    xfill True
                textbutton "Gallery":
                    action ShowMenu("gallery_screen")
                    xfill True
                textbutton "Quests":
                    action ShowMenu("quest_log_screen")
                    xfill True
                
                null height 20
                textbutton "Quit":
                    action Quit(confirm=True)
                    xfill True

screen notify(message):
    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        background "#2a2a2a"
        padding (20, 10)
        xalign 0.5
        ypos 50
        
        text "[message!t]":
            color "#ffd700"
            size 20

    timer 3.2 action Hide('notify')

transform notify_appear:
    on show:
        alpha 0.0 yoffset -20
        linear .25 alpha 1.0 yoffset 0
    on hide:
        linear .5 alpha 0.0 yoffset -20

style notify_frame is empty
style notify_text is empty
