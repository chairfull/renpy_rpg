screen navigation_screen():
    add "gui/overlay/main_menu.png" # Placeholder for background

    default current_loc = rpg_world.current_location

    vbox:
        align (0.5, 0.1)
        text "[current_loc.name]" size 40 color "#fff"
        text "[current_loc.description]" italic True size 20 color "#ccc"

    # Navigation Buttons
    vbox:
        align (0.9, 0.5)
        spacing 10
        label "Navigation"
        for dest_id, desc in current_loc.connections.items():
            textbutton desc action Function(rpg_world.move_to, dest_id)

    # Entity Buttons
    vbox:
        align (0.1, 0.5)
        spacing 10
        label "Interact"
        for entity in current_loc.entities:
            if entity.label:
                textbutton entity.name action Jump(entity.label)
            else:
                textbutton entity.name action Function(entity.interact)

    # Character Stats Summary
    vbox:
        align (0.05, 0.05)
        text "HP: [pc.stats.hp]/[pc.stats.max_hp]" size 18
        text "Strength: [pc.stats.strength]" size 16

    # Open Inventory/Character and Gallery Buttons
    hbox:
        align (0.95, 0.05)
        spacing 10
        textbutton "Character" action Show("character_management_screen")
        textbutton "Gallery" action Show("gallery_screen")

screen character_management_screen():
    modal True
    add Solid("#000b")

    vbox:
        align (0.5, 0.5)
        spacing 20
        text "Character Sheet" size 50

        hbox:
            spacing 50
            vbox:
                label "Stats"
                text "Strength: [pc.stats.strength]"
                text "Dexterity: [pc.stats.dexterity]"
                text "Intelligence: [pc.stats.intelligence]"
                text "Charisma: [pc.stats.charisma]"

            vbox:
                label "Inventory"
                if not pc.items:
                    text "Empty"
                else:
                    for item in pc.items:
                        textbutton item.name action [pc.equip(item), SelectedIf(pc.equipped_items.get(item.outfit_part) == item)]

        textbutton "Close" action Hide("character_management_screen")
