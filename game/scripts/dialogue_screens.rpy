# Dialogue choice system with tags, emojis, and hover descriptions

default hovered_dialogue_option = None

screen dialogue_choice_screen(char):
    modal True
    zorder 160
    
    # Backdrop
    add Solid("#000000cc")
    
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
                
                $ options = dialogue_manager.get_available(char)
                
                if not options:
                    text "You have nothing special to discuss." italic True color "#666" xalign 0.5
                else:
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        ymaximum 400
                        vbox:
                            spacing 10
                            for opt in options:
                                $ is_seen = opt.id in pc.dialogue_history
                                $ tag_prefix = "".join([f"[{t}] " for t in opt.tags])
                                
                                button:
                                    action [
                                        Function(pc.dialogue_history.add, opt.id),
                                        Hide("dialogue_choice_screen"),
                                        Jump(opt.label)
                                    ]
                                    hovered SetVariable("hovered_dialogue_option", opt)
                                    unhovered SetVariable("hovered_dialogue_option", None)
                                    
                                    xfill True
                                    padding (20, 15)
                                    background ("#252535" if not is_seen else "#151520")
                                    hover_background "#353545"
                                    
                                    at phone_visual_hover # Reuse our consistent hover logic
                                    
                                    hbox:
                                        spacing 15
                                        text "[opt.emoji]" size 24 yalign 0.5
                                        text "[tag_prefix][opt.short_text]" size 22 color ("#fff" if not is_seen or not opt.memory else "#777") yalign 0.5

        textbutton "End Conversation":
            xalign 0.5
            action Hide("dialogue_choice_screen")
            background "#444"
            padding (25, 15)
            text_size 24
            at phone_visual_hover
