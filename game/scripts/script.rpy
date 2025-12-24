# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")


# The game starts here.

label start:
    "Welcome to the AI RPG."
    # Initialize Player location
    $ rpg_world.actor.location_id = "home"
    $ td_manager.setup(rpg_world.current_location)
    
    # SAFE JUMP: Check if the generated label exists before jumping
    python:
        target_label = "SCENE__intro__start"
        if renpy.has_label(target_label):
            renpy.jump(target_label)
        else:
            renpy.say(None, "Generation in progress... Scripts are being updated. If the game does not automatically reload, please restart.")

    jump world_loop

label world_loop:
    window hide
    $ loc = rpg_world.current_location
    call screen top_down_map(loc)
    jump world_loop
