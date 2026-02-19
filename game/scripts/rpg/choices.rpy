# Dialogue choice system with tags, emojis, and hover descriptions
default hovered_dialogue_option = None
default hovered_dialogue_reason = None

init 10 python:
    class Choice:
        """Dialogue choices when talking to characters or interacting w objects."""
        def __init__(self, _id, menu, short, long=None, emoji=None, cond=None):
            self.id = _id
            self.menu = menu
            self.short = short
            self.long = long
            self.emoji = emoji
            self.cond = cond
            CHOICES_REQUESTED.connect(self._choices_requested)
        
        def _choices_requested(menu, choices):
            if self.menu != menu:
                return
            if self.cond and not test_condition(self.cond):
                return
            choices.append(self)
    
    def request_choices(menu):
        choices = []
        CHOICES_REQUESTED.emit(menu=menu, choices=choices)
        return choices
    
    CHOICES_REQUESTED = create_signal(menu=str, choices=list)
 
transform dialogue_fade:
    on show:
        alpha 0.0
        easein 0.2 alpha 1.0
    on hide:
        easeout 0.2 alpha 0.0

screen choice_screen(menu):
    modal True
    zorder 160

    button:
        action Return(None)
        background None
    
    vbox at dialogue_fade:
        align (0.5, 0.6)
        spacing 30
        xsize 1000
        
        frame:
            background None
            padding (40, 40)
            xfill True
            
            vbox:
                spacing 20
                $ choices = request_choices(menu)
                python:
                    option_rows = []
                    for opt in choices:
                        avail, reason = opt.availability_status(char)
                        option_rows.append((opt, avail, reason))
                
                if not option_rows:
                    text "Nothing to discuss." italic True color "#666" xalign 0.5
                else:
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        ymaximum 400
                        vbox:
                            spacing 10
                            for opt, is_avail, reason in option_rows:
                                $ is_seen = opt.id in character.dialogue_history
                                $ tag_prefix = "".join([f"[{t}] " for t in opt.tags])
                                
                                button:
                                    action (
                                        [
                                            Function(character.dialogue_history.add, opt.id),
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
                                    
                                    at button_hover_effect
                                    
                                    hbox:
                                        spacing 15
                                        text "[opt.emoji]" size 24 yalign 0.5
                                        text "[tag_prefix][opt.short_text]" size 22 color ("#fff" if is_avail and (not is_seen or not opt.memory) else "#777") yalign 0.5

        vbox:
            spacing 20
            null height 20