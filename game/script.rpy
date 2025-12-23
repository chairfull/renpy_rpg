# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")


# The game starts here.

label start:
    "Welcome to the AI RPG."
    # Initialize Player location (usually done in Markdown, but ensuring here)
    $ rpg_world.actor.location_id = "square"
    # Trigger the intro scene
    jump scene_intro_start

label world_loop:
    window hide
    # Using call screen is safer for interactions that should return here
    call screen navigation_screen
    jump world_loop
