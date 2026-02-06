# Dialogue choice system with tags, emojis, and hover descriptions

default hovered_dialogue_option = None
default hovered_dialogue_reason = None
 
screen dialogue_choice_screen(char):
    modal True
    zorder 160
    
    # Background dismissal
    button:
        action Return(None)
        background Solid("#000000cc")
    
    # Description Box (Tooltip)
    if hovered_dialogue_option:
        frame:
            align (0.5, 0.15)
            background Frame("#1a1a25", 8, 8)
            padding (25, 20)
            xsize 900
            
            vbox:
                spacing 5
                text "[hovered_dialogue_option.long_text]" size 24 italic True color "#ddd" text_align 0.5 xalign 0.5
                if hovered_dialogue_reason:
                    text "[hovered_dialogue_reason]" size 16 color "#ffcc66" xalign 0.5
                if hovered_dialogue_option.tags:
                    $ tags_str = ", ".join(hovered_dialogue_option.tags)
                    text "Properties: [tags_str]" size 16 color "#888" xalign 0.5
    
    vbox:
        align (0.5, 0.6)
        spacing 30
        xsize 1000
        
        frame:
            background "#1a1a1a"
            padding (40, 40)
            xfill True
            
            vbox:
                spacing 20
                text "Conversation with [char.name]" size 36 color "#ffd700" xalign 0.5
                
                $ options = dialogue_manager.get_for_char(char)
                python:
                    option_rows = []
                    for opt in options:
                        avail, reason = opt.availability_status(char)
                        option_rows.append((opt, avail, reason))
                
                if not option_rows:
                    text "You have nothing special to discuss." italic True color "#666" xalign 0.5
                else:
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        ymaximum 400
                        vbox:
                            spacing 10
                            for opt, is_avail, reason in option_rows:
                                $ is_seen = opt.id in pc.dialogue_history
                                $ tag_prefix = "".join([f"[{t}] " for t in opt.tags])
                                
                                button:
                                    action (
                                        [
                                            Function(pc.dialogue_history.add, opt.id),
                                            Return(opt.label)
                                        ] if is_avail else NullAction()
                                    )
                                    hovered [SetVariable("hovered_dialogue_option", opt), SetVariable("hovered_dialogue_reason", (None if is_avail else reason))]
                                    unhovered [SetVariable("hovered_dialogue_option", None), SetVariable("hovered_dialogue_reason", None)]
                                    sensitive is_avail
                                    
                                    xfill True
                                    padding (20, 15)
                                    background ("#252535" if is_avail and not is_seen else "#151520")
                                    hover_background ("#353545" if is_avail else "#2a2a2a")
                                    
                                    at phone_visual_hover # Reuse our consistent hover logic
                                    
                                    hbox:
                                        spacing 15
                                        text "[opt.emoji]" size 24 yalign 0.5
                                        text "[tag_prefix][opt.short_text]" size 22 color ("#fff" if is_avail and (not is_seen or not opt.memory) else "#777") yalign 0.5

        vbox:
            spacing 20
            # Removed END CONVERSATION button, clicking outside now works.
            null height 20

# Give Item Screen (Restored)
screen give_item_screen(target_char):
    modal True
    zorder 170
    
    # Background dismissal
    button:
        action Return()
        background Solid("#00000099")
    
    frame:
        align (0.5, 0.5)
        background "#1a2e1a"
        padding (30, 25)
        xsize 600
        ysize 500
        
        vbox:
            spacing 15
            
            text "Give item to [target_char.name]" size 30 color "#aaffaa" bold True xalign 0.5
            
            null height 10
            
            viewport:
                xfill True
                ysize 320
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
                                    Return(),
                                    Notify(f"Gave {item.name} to {target_char.name}")
                                ]
                                
                                hbox:
                                    spacing 20
                                    text "[item.name]" size 20 color "#ffffff"
                                    text "[item.description]" size 16 color "#888888" yalign 0.5
                    else:
                        text "No items in inventory" size 20 color "#666666" xalign 0.5 yalign 0.5
            
            null height 10
            
            # Removed Cancel button as background clicking is now the dismissal method.
            null height 10
    
    key "game_menu" action Return()
