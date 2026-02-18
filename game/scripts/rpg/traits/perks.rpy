init 10 python:
    onstart(add_meta_menu_tab, "perks", "✨", "Perks",
        selected_perk=None)
    
    class Perk(Trait):
        def __init__(self, *args, **kwargs):
            Trait.__init__(self, *args, **kwargs)

screen perks_screen():
    $ perks = character.get_traits(Perk)
    vbox:
        spacing 10
        xfill True
        yfill True
        if not perks:
            text "No perks acquired." size 16 color "#888"
        else:
            for perk_id in perks:
                $ p = perk_manager.perks.get(perk_id)
                if not p:
                    continue
                frame:
                    background "#1a1a25"
                    xfill True
                    padding (10, 8)
                    hbox:
                        xfill True
                        vbox:
                            text p.name size 16 color "#fff"
                            if p.desc:
                                text p.desc size 12 color "#aaa"
                        textbutton "Remove":
                            action Function(perk_remove, perk_id)
                            text_size 14