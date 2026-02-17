default persistent.achievements = set()
default persistent.achievement_progress = {}
default achievement_manager = AchievementManager()

init 10 python:
    onstart(add_meta_menu_tab, "achievements", "🏆", "Achievements",
        selected_achievement=None)

    class Achievement:
        def __init__(self, id, name, desc, icon="🏆", tags=None, trigger=None, ticks_required=1, **kwargs):
            self.id = id
            self.name = name
            self.desc = desc
            self.icon = icon
            self.tags = set(tags or [])
            self.trigger = trigger or {}  # {event: "EVENT_NAME", key: value, cond: "..."}
            self.ticks_required = max(1, int(ticks_required))
        
        def check_trigger(self, etype, **kwargs):
            """Check if an event matches this achievement's trigger."""
            if not self.trigger or self.trigger.get("event") != etype:
                return False
            # Check all key-value pairs in trigger (except reserved keys)
            for k, v in self.trigger.items():
                if k not in ["event", "cond"] and str(kwargs.get(k)) != str(v):
                    return False
            # Check condition if present
            if self.trigger.get("cond"):
                if not safe_eval_bool(self.trigger["cond"], {"player": character, "world": world, "kwargs": kwargs, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation}):
                    return False
            return True
    
    class AchievementManager:
        def __init__(self):
            self.achievements = {}
        
        def get_progress(self, ach_id):
            """Get current tick progress for an achievement."""
            if persistent.achievement_progress is None:
                persistent.achievement_progress = {}
            return persistent.achievement_progress.get(ach_id, 0)
        
        def add_tick(self, ach_id, count=1):
            """Add ticks to an achievement's progress. Auto-unlocks when complete."""
            if persistent.achievement_progress is None:
                persistent.achievement_progress = {}
            
            ach = self.achievements.get(ach_id)
            if not ach or self.is_unlocked(ach_id):
                return False
            
            current = persistent.achievement_progress.get(ach_id, 0)
            new_progress = current + count
            persistent.achievement_progress[ach_id] = new_progress
            
            if new_progress >= ach.ticks_required:
                self.unlock(ach_id)
                return True
            return False
        
        def handle_event(self, etype, **kwargs):
            """Check all achievements for matching triggers."""
            for ach in self.achievements.values():
                if not self.is_unlocked(ach.id) and ach.check_trigger(etype, **kwargs):
                    self.add_tick(ach.id)
        
        def unlock(self, ach_id):
            """Unlock an achievement for the player."""
            if persistent.achievements is None:
                persistent.achievements = set()
            
            if ach_id in self.achievements and ach_id not in persistent.achievements:
                persistent.achievements.add(ach_id)
                ach = self.achievements[ach_id]
                renpy.show_screen("achievement_toast", ach=ach)
                renpy.restart_interaction()
                return True
            return False
        
        def is_unlocked(self, ach_id):
            """Check if achievement is unlocked."""
            if persistent.achievements is None:
                return False
            return ach_id in persistent.achievements
        
        def get_all(self):
            """Get all registered achievements."""
            return sorted(self.achievements.values(), key=lambda x: (x.rarity != "legendary", x.rarity != "epic", x.name))
        
        def get_unlocked(self):
            """Get all unlocked achievements."""
            if persistent.achievements is None:
                return []
            return [self.achievements[aid] for aid in persistent.achievements if aid in self.achievements]
        
        def get_locked(self):
            """Get all locked achievements."""
            if persistent.achievements is None:
                return list(self.achievements.values())
            return [a for a in self.achievements.values() if a.id not in persistent.achievements]
        
        @property
        def total_points(self):
            """Calculate total achievement points."""
            return sum(a.points for a in self.get_unlocked())
        
        @property
        def progress_text(self):
            """Get progress as text (e.g., '3/10')."""
            unlocked = len(self.get_unlocked())
            total = len(self.achievements)
            return f"{unlocked}/{total}"
    
    def reload_achievement_manager(data):
        achievement_manager.achievements = {}
        for ach_id, ach_data in data.get("achievements", {}).items():
            achievement_manager.achievements[ach_id] = from_dict(Achievement, ach_data, id=ach_id)
    

# Beautiful toast notification for achievement unlock
screen achievement_toast(ach):
    zorder 200
    modal False
    
    timer 4.0 action Hide("achievement_toast")
    
    frame:
        at achievement_pop
        align (0.5, 0.1)
        background Frame("#1a1a2e", 8, 8)
        padding (30, 20)
        
        hbox:
            spacing 20
            align (0.5, 0.5)
            
            # Icon with glow effect
            frame:
                background Frame(ach.color + "40", 4, 4)
                padding (15, 15)
                text "[ach.icon]" size 50
            
            vbox:
                spacing 5
                text "ACHIEVEMENT UNLOCKED!" size 18 color "#ffd700" bold True
                text "[ach.name]" size 28 color ach.color bold True
                text "[ach.desc]" size 16 color "#aaaaaa"
                hbox:
                    spacing 10
                    text "[ach.rarity!u]" size 14 color ach.color
                    text "+" size 14 color "#ffd700"
                    text "[ach.points] pts" size 14 color "#ffd700"

transform achievement_pop:
    on show:
        alpha 0.0 yoffset -50
        easein 0.5 alpha 1.0 yoffset 0
    on hide:
        easeout 0.3 alpha 0.0 yoffset -30

screen achievements_screen(meta_menu):
    vbox:
        spacing 10
        xfill True
        yfill True

        # Header with points
        hbox:
            xfill True
            text "🏆 Achievements" size 28 color "#ffd700"
            hbox:
                xalign 1.0
                text "Total Points: " size 20 color "#aaa"
                text "[achievement_manager.total_points]" size 24 color "#ffd700" bold True
                text "  |  " size 20 color "#444"
                text "[achievement_manager.progress_text]" size 20 color "#aaa"

        null height 10

        frame:
            background "#222"
            xfill True
            yfill True
            padding (16, 16)
            $ cols = 3
            $ spacing = 16
            $ grid_w = 1600
            $ cell_w = int((grid_w - (cols - 1) * spacing) / cols)
            $ cell_h = 180
            $ unlocked = achievement_manager.get_unlocked()
            $ locked = achievement_manager.get_locked()
            $ all_ach = unlocked + locked
            viewport:
                scrollbars "vertical"
                mousewheel True
                draggable True
                xfill True
                yfill True
                vpgrid:
                    cols cols
                    xspacing spacing
                    yspacing spacing
                    xfill True
                    for ach in all_ach:
                        $ is_unlocked = achievement_manager.is_unlocked(ach.id)
                        $ hint = getattr(ach, "hint", None)
                        button:
                            action SetVariable("selected_achievement", ach)
                            xsize cell_w
                            ysize cell_h
                            background ("#2a2a2a" if is_unlocked else "#1a1a1a")
                            hover_background "#333333"
                            padding (14, 12)
                            vbox:
                                spacing 6
                                hbox:
                                    spacing 10
                                    text (ach.icon if is_unlocked else "🔒") size 28 color (ach.color if is_unlocked else "#666")
                                    vbox:
                                        spacing 2
                                        if is_unlocked:
                                            text "[ach.name]" size 20 color ach.color
                                            text "[ach.rarity!u] • [ach.points] pts" size 14 color "#aaa"
                                        else:
                                            text "?????" size 20 color "#666"
                                            if hint:
                                                text "[hint]" size 14 color "#777"
                                text ("[ach.desc]" if is_unlocked else "") size 16 color "#bbb"
