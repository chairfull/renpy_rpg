# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")


# The game starts here.

label start:
    "Welcome to the AI RPG."
    # Reload data to ensure latest changes are picked up
    $ instantiate_all()
    
    # Character Selection
    call screen character_select_screen
    
    # After selection, the screen jumps to the intro label.
    # The world_loop will be called after the intro finishes.
    return

    jump world_loop

label world_loop:
    window hide
    $ loc = rpg_world.current_location
    call screen top_down_map(loc)
    jump world_loop
