
screen lock_interaction_screen(lock_obj, item_name):
    modal True
    zorder 200
    
    frame:
        align (0.5, 0.5)
        background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)
        padding (30, 30)
        xsize 500
        
        vbox:
            spacing 20
            xalign 0.5
            
            text "LOCKED: [item_name]" size 30 color "#ff3333" xalign 0.5
            
            hbox:
                spacing 10
                xalign 0.5
                if lock_obj.type == 'electronic':
                    text "🔒 Electronic Security (Level [lock_obj.difficulty])" size 18 color "#aaa"
                else:
                    text "🔒 Physical Lock (Level [lock_obj.difficulty])" size 18 color "#aaa"
            
            null height 20
            
            # Action Grid
            grid 2 2:
                spacing 15
                xalign 0.5
                
                # 1. Use Key
                # Check if player has any matching key
                $ has_key = False
                $ key_name = "Missing Key"
                $ key_id = None
                python:
                    for k_id in lock_obj.keys:
                        for item in pc.items:
                            item_id = getattr(item, 'id', None) or getattr(item, 'name', '').lower().replace(' ', '_')
                            if item_id == k_id:
                                has_key = True
                                key_name = item.name
                                key_id = k_id
                                break
                        if has_key:
                            break
                
                vbox:
                    spacing 6
                    textbutton "Use [key_name]":
                        action [
                            Function(lock_obj.unlock, key_id if has_key else None),
                            Show("notify", message="Unlocked!"),
                            Hide("lock_interaction_screen")
                        ]
                        sensitive has_key
                        xsize 200
                    text ("Requires key." if not has_key else "Guaranteed unlock.") size 12 color "#888"
                
                # 2. Pick Lock
                $ pick_skill = pc.get_stat_total("dexterity")
                $ pick_target = lock_obj.difficulty * 3 + 5
                $ pick_chance = check_chance(pick_skill, pick_target)
                vbox:
                    spacing 6
                    textbutton "Pick Lock":
                        action [
                            Function(attempt_lockpick, lock_obj),
                            Hide("lock_interaction_screen")
                        ]
                        sensitive (lock_obj.type == 'physical')
                        xsize 200
                    if lock_obj.type == 'physical':
                        text "Chance: [pick_chance]%" size 12 color "#888"
                    else:
                        text "Only for physical locks." size 12 color "#888"

                # 3. Hack
                $ hack_skill = pc.get_stat_total("intelligence")
                $ hack_target = lock_obj.difficulty * 3 + 5
                $ hack_chance = check_chance(hack_skill, hack_target)
                vbox:
                    spacing 6
                    textbutton "Hack":
                        action [
                            Function(attempt_hack, lock_obj),
                            Hide("lock_interaction_screen")
                        ]
                        sensitive (lock_obj.type == 'electronic')
                        xsize 200
                    if lock_obj.type == 'electronic':
                        text "Chance: [hack_chance]%" size 12 color "#888"
                    else:
                        text "Only for electronic locks." size 12 color "#888"

                # 4. Cancel
                textbutton "Cancel":
                    action Hide("lock_interaction_screen")
                    xsize 200

init python:
    def check_chance(skill, target):
        needed = max(1, target - skill)
        chance = (21 - needed) / 20.0
        chance = max(0.05, min(0.95, chance))
        return int(chance * 100)

    def _attempt_check(skill, target, success_msg, fail_msg):
        roll = renpy.random.randint(1, 20)
        if roll + skill >= target:
            renpy.notify(success_msg)
            return True
        renpy.notify(fail_msg)
        return False

    def attempt_lockpick(lock_obj):
        skill = pc.get_stat_total("dexterity")
        target = lock_obj.difficulty * 3 + 5
        if _attempt_check(skill, target, "Lock picked.", "Lockpick failed."):
            lock_obj.locked = False

    def attempt_hack(lock_obj):
        skill = pc.get_stat_total("intelligence")
        target = lock_obj.difficulty * 3 + 5
        if _attempt_check(skill, target, "Hack successful.", "Hack failed."):
            lock_obj.locked = False
