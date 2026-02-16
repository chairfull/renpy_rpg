default perk_manager = PerkManager()

init -10 python:
    add_meta_menu_tab("perks", "✨", "Perks", perks_screen,
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

    class Perk(object):
        def __init__(self, id, name, description="", mods=None, tags=None, duration_minutes=None):
            self.id = id
            self.name = name
            self.description = description
            self.mods = mods or {}
            self.tags = set(tags or [])
            self.duration_minutes = duration_minutes
    
    class PerkManager:
        def __init__(self): self.perks = {}
    
    def reload_perk_manager(data):
        perk_manager.perks = {}
        for perk_id, p in data.get("perks", {}).items():
            try:
                perk_manager.perks[perk_id] = from_dict(Perk, p, id=perk_id)
            except Exception as e:
                with open("debug_load.txt", "a") as df:
                    df.write("Perk Load Error ({}): {}\n".format(pid, str(e)))

screen perks_screen():
    vbox:
        spacing 10
        xfill True
        yfill True
        if not character.perks:
            text "No perks acquired." size 16 color "#888"
        else:
            for perk_id in character.perks:
                p = perk_manager.get(perk_id)
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
                            if p.description:
                                text p.description size 12 color "#aaa"
                        textbutton "Remove":
                            action Function(perk_remove, perk_id)
                            text_size 14