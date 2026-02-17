default meta_menu = MetaMenu()

init -1900 python:
    class MetaMenuTab:
        def __init__(self, id, emoji, name, **kwargs):
            self.id = id
            self.emoji = emoji
            self.name = name
            for kwarg in kwargs:
                setattr(self, kwarg, kwargs[kwarg])
        
        def get_screen(self):
            return renpy.display.screen.screens.get(self.id + "_screen")

    class MetaMenu:
        def __init__(self):
            self.tabs = {}
            self.selected = None
            self.minimised = True
    
    def add_meta_menu_tab(mm_id, emoji, name, **kwargs):
        meta_menu.tabs[mm_id] = MetaMenuTab(mm_id, emoji, name, **kwargs)

    def open_meta_menu(to = None):
        meta_menu.selected = to
        meta_menu.minimised = False

screen meta_menu_screen():
    modal (meta_menu.minimised == False) # Only block input when the menu is open
    zorder 150

    # Click-outside closes to mini
    if meta_menu.minimised == False:
        button:
            action Function(meta_menu.close)
            xfill True
            yfill True

    frame:
        background "#1a1a2a"
        xsize 1680
        ysize 900
        padding (16, 16)
        
        vbox:
            spacing 12
            
            hbox:
                spacing 12
                xfill True
                for mm_id in meta_menu.tabs:
                    $ mm_data = meta_menu.tabs[mm_id]
                    textbutton f"{mm_data.emoji} {mm_data.name}" action Function(open_meta_menu, to=mm_id) style "phone_button":
                        if meta_menu.selected == mm_id:
                            background "#3a3a4a"
                        else:
                            background "#2a2a3a"
                        hover_background "#3a3a4a"
                        padding (15, 10)
                        text_size 16
                        text_color "#ffffff"
                text "[time_manager.time_string]" size 16 color "#9bb2c7" xalign 1.0
            
            fixed:
                xsize 1680
                ysize 900
                align (0.5, 0.5)
                at phone_landscape_static
                # Block clicks inside the phone frame so they don't close the phone.
                button:
                    xfill True
                    yfill True
                    background None
                    action NullAction()
                
                if meta_menu.selected:
                    $ mm = meta_menu.tabs[meta_menu.selected]
                    $ mms = mm.screen
                    use expression mms(mm)
                else:
                    text "Select an app above." size 18 color "#888" xalign 0.5

transform bg_blur:
    blur 10

transform bg_unblur:
    blur 0

screen meta_menu_mini_button():
    button:
        action [Function(renpy.show_layer_at, bg_blur, layer="topdown"), Function(renpy.notify, "Pee"), SetVariable("phone_state", "portrait"), SetVariable("phone_transition", "to_portrait"), SetVariable("current_meta_menu", None)]
        align (0.06, 0.94)
        padding (12, 8)
        background Frame(Solid("#0f141bcc"), 8, 8)
        hover_background Frame(Solid("#1b2733"), 8, 8)
        hbox:
            spacing 6
            text "📱" size 18
            text "PHONE" size 14 color "#c9d3dd"

style phone_button:
    background "#2a2a3a"
    hover_background "#3a3a4a"
    padding (15, 10)

style phone_button_text:
    size 16
    color "#ffffff"

