screen navigation_screen():
    add "gui/overlay/main_menu.png" # Placeholder for background

    default current_loc = rpg_world.current_location

    vbox:
        align (0.5, 0.1)
        text "[current_loc.name]" size 40 color "#fff"
        text "[current_loc.description]" italic True size 20 color "#ccc"

    # Single Action Buttons
    vbox:
        align (0.9, 0.5)
        spacing 10
        textbutton "Map" action Show("map_screen")
        textbutton "Inventory" action Show("character_management_screen")
        textbutton "Gallery" action Show("gallery_screen")

    # Entity and Character Buttons
    vbox:
        align (0.1, 0.5)
        spacing 10
        
        if current_loc.entities:
            label "Interact"
            for entity in current_loc.entities:
                if entity.label:
                    textbutton entity.name action Jump(entity.label)
                else:
                    textbutton entity.name action Function(entity.interact)

        if current_loc.characters:
            null height 20
            label "Characters"
            for char in current_loc.characters:
                # FIXED: Using Ren'Py If action for dynamic label/interaction logic
                textbutton char.name action If(char.label, Jump(char.label), Function(char.interact))

    # HUD (Stats & Time)
    vbox:
        align (0.05, 0.05)
        text "[time_manager.time_string]" size 20 color "#fb0"
        text "Actor: [rpg_world.active_actor_name]" size 16 color "#fff"
        text "HP: [rpg_world.actor.stats.hp]/[rpg_world.actor.stats.max_hp]" size 18
        text "Strength: [rpg_world.actor.stats.strength]" size 16

screen map_screen():
    modal True
    add Solid("#000a")
    
    label "World Map" align (0.5, 0.1)
    
    # We show connections from CURRENT location
    default current_loc = rpg_world.current_location
    
    vpgrid:
        cols 3
        spacing 20
        align (0.5, 0.5)
        draggable True
        mousewheel True
        
        for dest_id, desc in current_loc.connections.items():
            $ dest = rpg_world.locations.get(dest_id)
            vbox:
                spacing 5
                # Styling: unvisited locations are italicized and slightly dimmer
                if dest and not dest.visited:
                    textbutton "[desc]" action [Function(rpg_world.move_to, dest_id), Hide("map_screen")]:
                        text_italic True
                        text_color "#aaa"
                else:
                    textbutton "[desc]" action [Function(rpg_world.move_to, dest_id), Hide("map_screen")]
                
                # In the future, we can add a small image here
                frame:
                    xsize 200 ysize 120
                    background Solid("#333")
                    text "[dest_id]" align (0.5, 0.5)

    textbutton "Close Map" action Hide("map_screen") align (0.5, 0.9)

screen character_management_screen():
    modal True
    add Solid("#000b")

    vbox:
        align (0.5, 0.5)
        spacing 20
        text "Character Sheet: [rpg_world.active_actor_name]" size 50

        hbox:
            spacing 50
            vbox:
                label "Stats"
                text "Strength: [rpg_world.actor.stats.strength]"
                text "Dexterity: [rpg_world.actor.stats.dexterity]"
                text "Intelligence: [rpg_world.actor.stats.intelligence]"
                text "Charisma: [rpg_world.actor.stats.charisma]"

            vbox:
                label "Inventory"
                if not rpg_world.actor.items:
                    text "Empty"
                else:
                    for item in rpg_world.actor.items:
                        textbutton item.name action [Function(rpg_world.actor.equip, item), SelectedIf(rpg_world.actor.equipped_items.get(item.outfit_part) == item)]

        textbutton "Close" action Hide("character_management_screen")
