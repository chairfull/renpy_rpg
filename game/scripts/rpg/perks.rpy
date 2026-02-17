init 10 python:
    onstart(add_meta_menu_tab, "perks", "✨", "Perks",
        selected_perk=None)

    def perk_add(perk_id, duration_minutes=None):
        p = perk_manager.get(perk_id)
        if not p:
            renpy.notify("Unknown perk")
            return False
        duration = duration_minutes if duration_minutes is not None else p.duration_minutes
        ok, msg = character.add_perk(perk_id, duration)
        renpy.notify(msg)
        return ok

    def perk_remove(perk_id):
        ok = character.remove_perk(perk_id)
        if ok:
            renpy.notify("Perk removed")
        return ok

    class Perk:
        def __init__(self, id, name, desc="", mods=None, tags=None, **kwargs):
            self.id = id
            self.name = name
            self.desc = desc
            self.mods = mods or {}
            self.tags = set(tags or [])

screen perks_screen():
    vbox:
        spacing 10
        xfill True
        yfill True
        if not character.perks:
            text "No perks acquired." size 16 color "#888"
        else:
            for perk_id in character.perks:
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