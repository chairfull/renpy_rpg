default craft_manager = CraftManager()

init 10 python:
    onstart(add_meta_menu_tab, "crafting", "🪡", "Craft",
        selected_craft=None)

    class Craft:
        def __init__(self, id, name, inputs, output, req_skill=None, tags=None):
            self.id = id
            self.name = name
            self.inputs = inputs # {item_id: count}
            self.output = output # {item_id: count}
            self.req_skill = req_skill # {skill_name: level}
            self.tags = set(tags or [])
    
    class CraftManager:
        def __init__(self):
            self.crafts = {}
    
    def reload_craft_manager(data):
        craft_manager.crafts = {}
        for craft_id, p in data.get("crafts", {}).items():
            craft_manager.crafts[craft_id] = from_dict(Craft, p)
    
    def can_craft(recipe, inventory):
        for item_id, count in recipe.inputs.items():
            current_count = inventory.get_item_count(item_id=item_id)
            if current_count < count:
                return False, f"Missing {item_id}"
        
        if recipe.req_skill:
            for skill, level in recipe.req_skill.items():
                if character.stats.get(skill) < level:
                    return False, f"Need {skill} {level}"
        
        return True, "OK"

    def craft(recipe, inventory):
        can, msg = self.can_craft(recipe, inventory)
        if not can:
            renpy.notify(msg)
            return False
        
        # Consume inputs
        for item_id, count in recipe.inputs.items():
            inventory.remove_items_by_id(item_id, count=count, reason="craft")
        
        # Grant outputs
        for item_id, count in recipe.output.items():
            new_item = item_manager.get(item_id)
            if new_item:
                inventory.add_item(new_item, count=count, force=True, reason="craft")
        
        renpy.notify(f"Crafted {recipe.name}")
        signal("ITEM_CRAFTED", item=recipe.output, recipe=recipe.id)
        return True

screen crafting_screen(mmtab=None):
    hbox:
        spacing 20
        # Recipe List
        frame:
            background "#222"
            xsize 400
            ysize 600
            viewport:
                scrollbars "vertical"
                mousewheel True
                vbox:
                    spacing 5
                    for recipe in crafting_manager.get_all():
                        textbutton "[recipe.name]":
                            action SetVariable("selected_recipe", recipe)
                            xfill True
                            background ("#333" if globals().get("selected_recipe") == recipe else "#111")
                            text_style "inventory_item_text"

        # Recipe Details
        frame:
            background "#222"
            xsize 620
            ysize 600
            padding (20, 20)
            
            if globals().get("selected_recipe"):
                $ rec = selected_recipe
                vbox:
                    spacing 15
                    text "[rec.name]" size 30 color "#ffd700"
                    
                    text "Requires:" size 24 color "#ffffff"
                    for i_id, count in rec.inputs.items():
                        $ itm = item_manager.get(i_id)
                        $ itm_name = itm.name if itm else i_id
                        # Check count in inventory
                        $ have = character.get_item_count(item_id=i_id)
                        
                        hbox:
                            text "• [itm_name] x[count]" size 20 color ("#50fa7b" if have >= count else "#ff5555")
                            text " (Have [have])" size 18 color "#888"
                            
                    null height 20
                    
                    textbutton "CRAFT":
                        action [Function(crafting_manager.craft, rec, character), Function(renpy.restart_interaction)]
                        background "#444" padding (30, 15)
                        text_style "tab_button_text"

            else:
                text "Select a recipe to view details." align (0.5, 0.5) color "#666666"