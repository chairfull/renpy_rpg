# Character Interaction Popup for Top-Down View
# Shows when clicking on a character in the top-down view

screen td_char_popup(char):
    modal True
    
    # Darken background
    add Solid("#00000099")
    
    # Main panel
    frame:
        align (0.5, 0.5)
        background "#1a1a2e"
        padding (40, 30)
        xsize 450
        
        vbox:
            spacing 20
            xalign 0.5
            
            # Character portrait & name
            hbox:
                spacing 20
                xalign 0.5
                
                # Character image
                add Transform("images_topdown/chars/theo.png", zoom=0.4):
                    yalign 0.5
                
                vbox:
                    spacing 5
                    yalign 0.5
                    text "[char.name]" size 32 color "#ffd700" bold True
                    if char.description:
                        text "[char.description]" size 16 color "#aaaaaa" italic True
            
            null height 10
            
            # Action buttons
            vbox:
                spacing 12
                xalign 0.5
                xsize 300
                
                # Speak button
                button:
                    xfill True
                    background "#2a4a6a"
                    hover_background "#3a5a8a"
                    padding (20, 12)
                    action [Hide("td_char_popup"), Function(char.interact)]
                    
                    hbox:
                        spacing 15
                        xalign 0.5
                        text "💬" size 24 yalign 0.5
                        text "Speak" size 22 color "#ffffff" yalign 0.5
                
                # Give Item button
                button:
                    xfill True
                    background "#4a2a6a"
                    hover_background "#5a3a8a"
                    padding (20, 12)
                    action Show("give_item_screen", target_char=char)
                    
                    hbox:
                        spacing 15
                        xalign 0.5
                        text "🎁" size 24 yalign 0.5
                        text "Give Item" size 22 color "#ffffff" yalign 0.5
            
            null height 10
            
            # Close button
            textbutton "Close":
                xalign 0.5
                text_size 18
                text_color "#888888"
                text_hover_color "#ffffff"
                action Hide("td_char_popup")
    
    # Click outside to close
    key "game_menu" action Hide("td_char_popup")


# Give Item Screen - select an item from inventory to give
screen give_item_screen(target_char):
    modal True
    
    add Solid("#00000099")
    
    frame:
        align (0.5, 0.5)
        background "#1a2e1a"
        padding (30, 25)
        xsize 500
        ysize 450
        
        vbox:
            spacing 15
            
            text "Give item to [target_char.name]" size 24 color "#aaffaa" bold True xalign 0.5
            
            null height 10
            
            # Item list from player inventory
            viewport:
                xfill True
                ysize 280
                scrollbars "vertical"
                mousewheel True
                
                vbox:
                    spacing 8
                    
                    if pc.items:
                        for item in pc.items:
                            button:
                                xfill True
                                background "#2a3a2a"
                                hover_background "#3a4a3a"
                                padding (15, 10)
                                action [
                                    Function(pc.transfer_to, item, target_char),
                                    Hide("give_item_screen"),
                                    Hide("td_char_popup"),
                                    Notify(f"Gave {item.name} to {target_char.name}")
                                ]
                                
                                hbox:
                                    spacing 10
                                    text "[item.name]" size 18 color "#ffffff"
                                    text "[item.description]" size 14 color "#888888" yalign 0.5
                    else:
                        text "No items in inventory" size 18 color "#666666" xalign 0.5 yalign 0.5
            
            null height 10
            
            # Cancel button
            textbutton "Cancel":
                xalign 0.5
                text_size 18
                text_color "#888888"
                text_hover_color "#ffffff"
                action Hide("give_item_screen")
    
    key "game_menu" action Hide("give_item_screen")
