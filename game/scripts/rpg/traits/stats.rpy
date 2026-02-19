init 10 python:
    onstart(add_meta_menu_tab, "stats", "❤️", "Stats")
    
    class Stat(Trait):
        def __init__(self, *args, **kwargs):
            Trait.__init__(self, *args, **kwargs)

screen stats_screen():
    $ states = player.get_traits(Stat)
    hbox:
        spacing 40
        xalign 0.5
        vbox:
            spacing 20
            frame:
                background "#222"
                padding (20, 20)
                xsize 300
                ysize 400
                vbox:
                    align (0.5, 0.5)
                    text "👤" size 150 xalign 0.5
                    text "[player.name]" size 30 xalign 0.5 color "#ffd700"
            frame:
                background "#222"
                padding (20, 20)
                xsize 300
                vbox:
                    spacing 5
                    # text "Gold: [character.gold]" size 22 color "#ffd700"
                    null height 10
                    $ outfit_name = getattr(player, "current_outfit", "Default")
                    text "Outfit: [outfit_name.capitalize()]" size 20 color "#ffffff"
                    for part, item in player.equipped_items.items():
                        text "[part.capitalize()]: [item.name]" size 16 color "#cccccc"
        frame:
            background "#222"
            padding (30, 30)
            xsize 500
            vbox:
                spacing 15
                text "Attributes" size 28 color "#ffd700"
                $ stats = player.stats
                python:
                    # Filter out HP stats and anything else starting with underscore
                    display_stats = sorted([s for s in stats.keys() if s not in ('hp', 'max_hp') and not s.startswith('_')])
                
                if not display_stats:
                    text "No special attributes" size 18 italic True color "#666"
                else:
                    for s_key in display_stats:
                        $ sname = get_stat_display_name(s_key)
                        $ sicon = get_stat_icon(s_key)
                        $ total = player.get_stat_total(s_key)
                        $ mod = player.get_stat_mod(s_key)
                        hbox:
                            xfill True
                            text "[sicon] [sname]" size 22 color "#ffffff"
                            text "[total] ([mod:+])" size 22 color "#00bfff" xalign 1.0

                null height 20
                text "Vitals" size 28 color "#ffd700"
                vbox:
                    spacing 5
                text "HP: [stats.hp] / [stats.max_hp]" size 18 color "#ffffff"
                bar value stats.hp range stats.max_hp:
                    xsize 440
                    ysize 20
                    left_bar Solid("#ff4444")
                    right_bar Solid("#333")
                
                null height 10
                text "Perks" size 22 color "#ffd700"
                if character.active_perks:
                    for p in character.active_perks:
                        $ perk = perk_manager.get(p["id"])
                        text "[perk.name]" size 16 color "#ccc"
                else:
                    text "None" size 16 color "#666"
                
                text "Status Effects" size 22 color "#ffd700"
                if character.active_statuses:
                    for s in character.active_statuses:
                        $ st = status_manager.get(s["id"])
                        text "[st.name]" size 16 color "#ccc"
                else:
                    text "None" size 16 color "#666"