
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
            
            text "LOCKED: [item_name]" size 30 color "#ff3333" xalign 0.5 font "gui/fonts/Almendra-Bold.ttf"
            
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
                $ key_name = "Unknown Key"
                python:
                    for key_id in lock_obj.keys:
                        # Check inventory (assuming pc.inventory or just pc.keys?)
                        # PC inherits Inventory, so pc.has_item(key_id)?
                        # Inventory logic: pc.items is list of Items.
                        # We need to scan items.
                        for item in pc.items:
                            if item.id == key_id:
                                has_key = True
                                key_name = item.name
                                break
                        if has_key: break
                
                textbutton "Use [key_name]":
                    action [
                        Function(lock_obj.unlock, key_id if has_key else None),
                        Show("notify", message="Unlocked!"),
                        Hide("lock_interaction_screen")
                    ]
                    sensitive has_key
                    xsize 200
                
                # 2. Pick Lock
                textbutton "Pick Lock":
                    action [
                        Function(attempt_lockpick, lock_obj),
                        Hide("lock_interaction_screen")
                    ]
                    sensitive (lock_obj.type == 'physical')
                    xsize 200

                # 3. Hack
                textbutton "Hack":
                    action [
                        Show("notify", message="Hacking tool required."),
                        Hide("lock_interaction_screen")
                    ]
                    sensitive (lock_obj.type == 'electronic')
                    xsize 200

                # 4. Cancel
                textbutton "Cancel":
                    action Hide("lock_interaction_screen")
                    xsize 200

init python:
    def attempt_lockpick(lock_obj):
        # Stat check: Dexterity + Random(1-20) vs Difficulty * 2 + 5?
        # User requested skill level.
        # Let's say difficulty 1-10.
        # Check: Dex (1-20) + Roll(1-20) >= Difficulty * 3 + 10
        roll = renpy.random.randint(1, 20)
        dex = pc.stats.dexterity
        target = lock_obj.difficulty * 3 + 5
        
        if dex + roll >= target:
            lock_obj.locked = False
            renpy.notify(f"Success! (Rolled {roll} + {dex} vs {target})")
        else:
            renpy.notify(f"Failed to pick lock. (Rolled {roll} + {dex} vs {target})")
