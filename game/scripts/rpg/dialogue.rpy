default dialogue_manager = DialogueManager()

init 10 python:
    class DialogueOption(object):
        def __init__(self, id, chars, short_text, long_text, emoji, label, cond=None, tags=None, memory=False, reason=None):
            self.id = id
            self.chars = set(chars or [])
            self.short_text = short_text
            self.long_text = long_text
            self.emoji = emoji
            self.label = label
            self.cond = cond
            self.tags = tags or []
            self.memory = memory
            self.reason = reason
        
        def is_available(self, char):
            if self.chars and char.id not in self.chars and "*" not in self.chars:
                return False
            if self.cond and str(self.cond).strip() and str(self.cond) != "True":
                return safe_eval_bool(self.cond, {"character": character, "char": char, "world": world, "quest_manager": quest_manager, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation})
            return True

        def availability_status(self, char):
            if self.chars and char.id not in self.chars and "*" not in self.chars:
                return False, "Not for this character."
            if self.cond and str(self.cond).strip() and str(self.cond) != "True":
                ok = safe_eval_bool(self.cond, {"character": character, "char": char, "world": world, "quest_manager": quest_manager, "flags": world_flags, "flag_get": flag_get, "faction_get": faction_manager.get_reputation})
                if not ok:
                    return False, self.reason or "Locked."
            return True, "Available."

    class DialogueManager:
        def __init__(self):
            self.options = {}
        def get_for_char(self, char):
            opts = [opt for opt in self.options.values() if (not opt.chars or char.id in opt.chars or "*" in opt.chars)]
            return sorted(opts, key=lambda x: x.id)
        def get_available(self, char):
            opts = [opt for opt in self.options.values() if opt.is_available(char)]
            return sorted(opts, key=lambda x: x.id)

    def reload_dialogue_manager(data):
        dialogue_manager.options = {}
        for oid, p in data.get("dialogue", {}).items():
            dialogue_manager.options[oid] = DialogueOption(
                oid,
                chars=p.get('chars', []),
                short_text=p.get('short', '...'),
                long_text=p.get('long', '...'),
                emoji=p.get('emoji', '💬'),
                label=p.get('label'),
                cond=p.get('cond'),
                tags=p.get('tags', []),
                memory=(str(p.get('memory', 'False')).lower() == 'true'),
                reason=p.get('reason')
            )

# Dialogue choice system with tags, emojis, and hover descriptions

default hovered_dialogue_option = None
default hovered_dialogue_reason = None
 
transform dialogue_fade:
    on show:
        alpha 0.0
        easein 0.2 alpha 1.0
    on hide:
        easeout 0.2 alpha 0.0

screen dialogue_choice_screen(char):
    modal True
    zorder 160
    
    # Background dismissal (no visible tint)
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
                $ options = dialogue_manager.get_for_char(char)
                python:
                    option_rows = []
                    for opt in options:
                        avail, reason = opt.availability_status(char)
                        option_rows.append((opt, avail, reason))
                
                if not option_rows:
                    text "You have nothing special to discuss." italic True color "#666" xalign 0.5
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
            # Removed END CONVERSATION button, clicking outside now works.
            null height 20

# Give Item Screen (Restored)
screen give_item_screen(target_char):
    modal True
    zorder 170
    
    # Background dismissal
    button:
        action Return()
        background Solid("#00000099")
    
    frame:
        align (0.5, 0.5)
        background "#1a2e1a"
        padding (30, 25)
        xsize 600
        ysize 500
        
        vbox:
            spacing 15
            
            text "Give item to [target_char.name]" size 30 color "#aaffaa" bold True xalign 0.5
            
            null height 10
            
            viewport:
                xfill True
                ysize 320
                scrollbars "vertical"
                mousewheel True
                
                vbox:
                    spacing 8
                    
                    if character.items:
                        python:
                            grouped = {}
                            for itm in character.items:
                                item_id = item_manager.get_id_of(itm)
                                key = (item_id, getattr(itm, "owner_id", None), bool(getattr(itm, "stolen", False)))
                                if key not in grouped:
                                    label = itm.name + (" [stolen]" if getattr(itm, "stolen", False) else "")
                                    grouped[key] = {"item": itm, "qty": 0, "label": label}
                                grouped[key]["qty"] += max(1, int(getattr(itm, "quantity", 1)))
                        for key, entry in grouped.items():
                            $ item = entry["item"]
                            $ count = entry["qty"]
                            button:
                                xfill True
                                background "#2a3a2a"
                                hover_background "#3a4a3a"
                                padding (15, 10)
                                action [
                                    Function(character.transfer_to, item, target_char, 1, "gift", True),
                                    Return(),
                                    Notify(f"Gave {item.name} to {target_char.name}")
                                ]
                                
                                hbox:
                                    spacing 20
                                    text "[entry['label']] (x[count])" size 20 color "#ffffff"
                                    text "[item.description]" size 16 color "#888888" yalign 0.5
                    else:
                        text "No items in inventory" size 20 color "#666666" xalign 0.5 yalign 0.5
            
            null height 10
            
            # Removed Cancel button as background clicking is now the dismissal method.
            null height 10
    
    key "game_menu" action Return()
